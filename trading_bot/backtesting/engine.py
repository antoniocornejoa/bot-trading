"""Motor de backtesting dirigido por eventos sobre barras. Solo largos (spot).

Reglas (todas deliberadamente conservadoras):
  - La señal se decide con el cierre de la barra t y se ejecuta en la apertura de t+1.
  - Dentro de una barra el orden asumido es apertura → extremos → cierre. Si el stop y el
    objetivo se tocan en la misma barra, se asume que se ejecutó el STOP.
  - Si la apertura ya está por debajo del stop (gap), el stop se ejecuta a la apertura.
  - El stop dinámico (trail) calculado en t se aplica desde t+1 y solo puede subir.
  - Tamaño: fracción fija del capital arriesgada por operación, dividida por la distancia
    del stop; redondeo al paso de lote; se rechaza si no llega al nocional mínimo o al
    efectivo disponible. Con US$500 esto descarta operaciones reales, así que se cuenta.
  - Equity marcada a mercado al cierre de cada barra.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, asdict

import numpy as np
import pandas as pd

from .costs import CostScenario


@dataclass
class Trade:
    entry_signal_time: pd.Timestamp
    entry_time: pd.Timestamp
    entry_price: float
    exit_time: pd.Timestamp
    exit_price: float
    qty: float
    stop_initial: float
    stop_final: float
    take_profit: float
    risk_usd: float
    reason: str          # stop | take_profit | signal | end
    fees: float
    slippage_cost: float  # coste implícito de spread+slippage+impacto respecto al precio de referencia
    pnl: float            # neto, tras comisiones
    r_multiple: float     # pnl / riesgo inicial
    bars_held: int
    equity_at_entry: float


@dataclass
class BacktestResult:
    trades: list[Trade]
    equity: pd.Series
    initial_capital: float
    scenario: str
    params: dict = field(default_factory=dict)
    skipped_min_notional: int = 0
    skipped_no_cash: int = 0

    def trades_df(self) -> pd.DataFrame:
        if not self.trades:
            return pd.DataFrame(columns=list(Trade.__dataclass_fields__))
        return pd.DataFrame([asdict(t) for t in self.trades])


def _round_lot(qty: float, step: float) -> float:
    if step <= 0:
        return qty
    return round(math.floor(qty / step + 1e-9) * step, 12)


def run(df: pd.DataFrame, signals: pd.DataFrame, costs: CostScenario, *, initial_capital: float = 500.0,
        risk_pct: float = 1.0, min_notional: float = 5.0, lot_step: float = 1e-5,
        max_position_pct: float = 100.0, params: dict | None = None) -> BacktestResult:
    if not df.index.equals(signals.index):
        raise ValueError("df y signals deben compartir índice")
    o = df["open"].to_numpy(float); h = df["high"].to_numpy(float)
    lo = df["low"].to_numpy(float); c = df["close"].to_numpy(float)
    qv = (df["quote_volume"] if "quote_volume" in df else df["volume"] * df["close"]).to_numpy(float)
    entry = signals["entry"].to_numpy(bool); exit_ = signals["exit"].to_numpy(bool)
    stop_dist = signals["stop_dist"].to_numpy(float); tp_dist = signals["tp_dist"].to_numpy(float)
    trail = signals["trail"].to_numpy(float)
    idx = df.index

    n = len(df)
    cash = float(initial_capital)
    equity = np.empty(n)
    trades: list[Trade] = []
    pos = None  # dict con el estado de la posición
    skipped_min = skipped_cash = 0

    def close_position(i: int, ref: float, reason: str, is_stop: bool) -> None:
        nonlocal cash, pos
        notional = pos["qty"] * ref
        fill = costs.sell_fill(ref, notional, qv[i - 1] if i > 0 else 0.0, is_stop=is_stop)
        fee = costs.fee(fill, pos["qty"])
        proceeds = fill * pos["qty"] - fee
        cash += proceeds
        pnl = proceeds - pos["cost_basis"]
        slip = (pos["entry_price"] - pos["entry_ref"]) * pos["qty"] + (ref - fill) * pos["qty"]  # ambos ≥ 0: pagó más, cobró menos
        trades.append(Trade(
            entry_signal_time=idx[pos["signal_i"]], entry_time=idx[pos["entry_i"]],
            entry_price=pos["entry_price"], exit_time=idx[i], exit_price=fill, qty=pos["qty"],
            stop_initial=pos["stop_initial"], stop_final=pos["stop"], take_profit=pos["tp"],
            risk_usd=pos["risk_usd"], reason=reason, fees=pos["entry_fee"] + fee,
            slippage_cost=slip, pnl=pnl, r_multiple=pnl / pos["risk_usd"] if pos["risk_usd"] > 0 else 0.0,
            bars_held=i - pos["entry_i"], equity_at_entry=pos["equity_at_entry"],
        ))
        pos = None

    for i in range(n):
        exited_this_bar = False
        if pos is not None:
            if exit_[i - 1] if i > 0 else False:
                close_position(i, o[i], "signal", False); exited_this_bar = True
            else:
                if i > 0 and not np.isnan(trail[i - 1]) and trail[i - 1] > pos["stop"]:
                    pos["stop"] = trail[i - 1]
                stop, tp = pos["stop"], pos["tp"]
                if o[i] <= stop:
                    close_position(i, o[i], "stop", True); exited_this_bar = True
                elif not np.isnan(tp) and o[i] >= tp:
                    close_position(i, o[i], "take_profit", False); exited_this_bar = True
                elif lo[i] <= stop:
                    close_position(i, stop, "stop", True); exited_this_bar = True
                elif not np.isnan(tp) and h[i] >= tp:
                    close_position(i, tp, "take_profit", False); exited_this_bar = True

        if pos is None and not exited_this_bar and i > 0 and entry[i - 1]:
            sd = stop_dist[i - 1]
            if not (np.isnan(sd) or sd <= 0):
                equity_now = cash
                risk_usd = equity_now * risk_pct / 100.0
                qty = risk_usd / sd
                ref = o[i]
                fill = costs.buy_fill(ref, qty * ref, qv[i - 1])
                max_cost = min(cash, equity_now * max_position_pct / 100.0)
                qty_cash = max_cost / (fill * (1 + costs.fee_pct / 100.0))
                if qty > qty_cash:
                    skipped_cash += 1 if qty_cash * fill < min_notional else 0
                    qty = qty_cash
                qty = _round_lot(qty, lot_step)
                if qty * fill < min_notional or qty <= 0:
                    skipped_min += 1
                else:
                    fee = costs.fee(fill, qty)
                    cash -= fill * qty + fee
                    pos = {
                        "qty": qty, "entry_price": fill, "entry_ref": ref, "entry_fee": fee,
                        "cost_basis": fill * qty + fee, "stop": fill - sd, "stop_initial": fill - sd,
                        "tp": fill + tp_dist[i - 1] if not np.isnan(tp_dist[i - 1]) else np.nan,
                        "risk_usd": qty * sd, "entry_i": i, "signal_i": i - 1, "equity_at_entry": equity_now,
                    }
        equity[i] = cash + (pos["qty"] * c[i] if pos is not None else 0.0)

    if pos is not None:
        close_position(n - 1, c[n - 1], "end", False)
        equity[n - 1] = cash

    return BacktestResult(trades=trades, equity=pd.Series(equity, index=idx, name="equity"),
                          initial_capital=initial_capital, scenario=costs.name, params=params or {},
                          skipped_min_notional=skipped_min, skipped_no_cash=skipped_cash)
