"""Bot de ejecución (paper / live / replay). Mismo pipeline que el backtest:

  velas cerradas → señales de la estrategia (cierre de t) → motor de riesgo → orden a mercado
  (≈ apertura de t+1) → posición persistida → vigilancia de stop/objetivo en cada ciclo.

Garantías:
  - Idempotencia: cada orden lleva un client_id determinista (símbolo + vela + acción). Si el
    proceso muere entre la orden y el registro, al reiniciar se recupera la orden en vez de
    duplicarla.
  - Un ciclo nunca lanza: los errores del exchange se cuentan en el motor de riesgo y, si se
    repiten, disparan el kill switch.
  - Reconciliación al arrancar: posiciones en base de datos frente a saldos del exchange.
  - Cada operación cerrada guarda precio de referencia y precio real para medir el slippage
    y comparar con el backtest.
"""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime

import numpy as np
import pandas as pd

from ..monitoring.alerts import Alerter
from ..portfolio.state import StateStore
from ..risk import RiskEngine
from ..strategies.base import Strategy
from .exchange import Exchange, ExchangeError


class TradingBot:
    def __init__(self, exchange: Exchange, strategy: Strategy, symbols: list[str], timeframe: str,
                 risk: RiskEngine, store: StateStore, alerter: Alerter, mode: str = "paper",
                 bars_limit: int = 400, fee_pct: float = 0.1):
        self.x, self.strategy, self.symbols, self.tf = exchange, strategy, symbols, timeframe
        self.risk, self.store, self.alert, self.mode = risk, store, alerter, mode
        self.bars_limit, self.fee_pct = bars_limit, fee_pct

    # ------------------------------------------------------------------ utilidades
    def _base(self, symbol: str) -> str:
        return symbol.split("/")[0]

    def equity(self) -> tuple[float, float]:
        bal = self.x.balances()
        cash = float(bal.get("USDT", 0.0))
        eq = cash
        for s in self.symbols:
            q = float(bal.get(self._base(s), 0.0))
            if q > 0:
                eq += q * self.x.ticker(s)["last"]
        return eq, cash

    def reconcile(self) -> None:
        """Al arrancar: posiciones registradas sin saldo → cerradas fuera del bot; saldo sin posición → aviso."""
        bal = self.x.balances()
        pos = self.store.positions()
        for s in self.symbols:
            held = float(bal.get(self._base(s), 0.0))
            p = pos.get(s)
            if p and held < p["qty"] * 0.5:
                price = self.x.ticker(s)["last"]
                self._record_close(s, p, price, price, 0.0, "external", self.x.now())
                self.alert.send("warning", f"{s}: posición registrada sin saldo en el exchange; se cierra como 'external' a {price:.2f}")
            elif not p and held * self.x.ticker(s)["last"] > 5:
                self.alert.send("warning", f"{s}: saldo {held:.6f} sin posición registrada; el bot no lo tocará")
        rs = self.store.get("risk_state")
        if rs:
            from ..risk import RiskState
            rs["events"] = rs.get("events", [])
            for k in ("start_of_day", "week_start"):
                rs[k] = pd.Timestamp(rs[k]).date() if rs.get(k) else None
            self.risk.state = RiskState(**rs)

    # ------------------------------------------------------------------ ciclo
    def run_once(self) -> None:
        now = self.x.now()
        try:
            equity, cash = self.equity()
        except ExchangeError as e:
            self.risk.record_error(str(e)); self.alert.send("error", f"sin conexión con el exchange: {e}", now)
            self._maybe_flatten(now); return
        self.risk.record_ok()
        if self.risk.state.killed:
            self._maybe_flatten(now); return
        self.risk.risk_multiplier(equity)  # actualiza el máximo de equity y evalúa el kill por drawdown
        for s in self.symbols:
            try:
                self._process_symbol(s, now, equity, cash)
            except ExchangeError as e:
                self.risk.record_error(str(e)); self.alert.send("error", f"{s}: {e}", now)
        self._maybe_flatten(now)
        n_pos = len(self.store.positions())
        self.store.snapshot(now, equity, cash, n_pos)
        self.store.set("risk_state", asdict(self.risk.state))

    def _maybe_flatten(self, now: datetime) -> None:
        if not self.risk.state.killed:
            return
        for s, p in list(self.store.positions().items()):
            try:
                price = self.x.ticker(s)["last"]
                self._close(s, p, "kill", price, now)
            except ExchangeError as e:
                self.alert.send("error", f"{s}: no se pudo cerrar tras kill switch: {e}", now)
        if self.store.get("kill_alerted") != self.risk.state.kill_reason:
            self.alert.send("kill", f"KILL SWITCH: {self.risk.state.kill_reason}. El bot no abrirá más operaciones hasta revisión manual.", now)
            self.store.set("kill_alerted", self.risk.state.kill_reason)

    def _process_symbol(self, s: str, now: datetime, equity: float, cash: float) -> None:
        df = self.x.fetch_ohlcv(s, self.tf, self.bars_limit)
        closed = df.iloc[:-1]                      # la última fila es la vela en curso
        if len(closed) < 50:
            return
        last_ts = closed.index[-1]
        new_bar = self.store.get(f"last_bar:{s}") != str(last_ts)
        sig = self.strategy.generate(closed)
        row, bar = sig.iloc[-1], closed.iloc[-1]
        tick = self.x.ticker(s)
        price = tick["last"]
        spread = (tick["ask"] - tick["bid"]) / price * 100 if price else None
        bar_move = (bar["close"] / bar["open"] - 1) * 100
        pos = self.store.positions().get(s)
        entry_cid = f"{s.replace('/', '')}-{last_ts:%Y%m%d%H%M}-E"

        if pos is None and self.store.order_seen(entry_cid):
            # el proceso murió entre la orden y el registro de la posición: reconstruir desde la orden
            fill = self.x.find_order(s, entry_cid)
            if fill:
                pos = self._position_from_fill(s, fill, row, bar, last_ts, equity, price)
                self.store.upsert_position(pos)
                self.alert.send("warning", f"{s}: posición reconstruida desde la orden {entry_cid}", now)

        if pos is not None:
            if new_bar and not np.isnan(row["trail"]) and row["trail"] > pos["stop"]:
                pos["stop"] = float(row["trail"]); self.store.upsert_position(pos)
            reason, ref = None, price
            if price <= pos["stop"]:
                reason, ref = "stop", pos["stop"]
            elif pos.get("take_profit") is not None and price >= pos["take_profit"]:
                reason, ref = "take_profit", pos["take_profit"]
            elif new_bar and bool(row["exit"]):
                reason = "signal"
            if reason:
                self._close(s, pos, reason, ref, now)
        elif new_bar and bool(row["entry"]) and not np.isnan(row["stop_dist"]) and row["stop_dist"] > 0:
            positions = self.store.positions()
            open_risk = sum(p["risk_usd"] for p in positions.values())
            ok, why, mult = self.risk.can_open(equity, now, len(positions), open_risk, spread, bar_move)
            if not ok:
                self.alert.send("info", f"{s}: señal de entrada no ejecutada: {why}", now)
            else:
                lim = self.x.limits(s)
                qty, risk_usd = self.risk.position_size(equity, float(row["stop_dist"]), mult, price, lim["lot_step"],
                                                        lim["min_notional"], cash, self.fee_pct)
                if qty <= 0:
                    self.alert.send("info", f"{s}: señal de entrada por debajo del mínimo de orden", now)
                else:
                    fill = self.x.market_order(s, "buy", qty, entry_cid)
                    self.store.record_order(fill)
                    pos = self._position_from_fill(s, fill, row, bar, last_ts, equity, price)
                    self.store.upsert_position(pos)
                    self.alert.send("trade", f"{s}: COMPRA {fill.qty:.6f} a {fill.price:.2f} (ref {price:.2f}) | stop {pos['stop']:.2f} | riesgo {pos['risk_usd']:.2f} USD | multiplicador {mult}", now)
        if new_bar:
            self.store.set(f"last_bar:{s}", str(last_ts))

    def _position_from_fill(self, s, fill, row, bar, last_ts, equity, ref_price) -> dict:
        sd = float(row["stop_dist"])
        tp = fill.price + float(row["tp_dist"]) if not np.isnan(row["tp_dist"]) else None
        return {"symbol": s, "qty": fill.qty, "entry_price": fill.price, "entry_ref": ref_price, "entry_fee": fill.fee,
                "entry_time": fill.timestamp, "signal_time": last_ts, "stop": fill.price - sd, "stop_initial": fill.price - sd,
                "take_profit": tp, "risk_usd": fill.qty * sd, "client_id": fill.client_id, "equity_at_entry": equity,
                "params": dict(self.strategy.params),
                "features": {"close": float(bar["close"]), "stop_dist": sd, "trail": None if np.isnan(row["trail"]) else float(row["trail"])},
                "p_win": None}

    def _close(self, s: str, pos: dict, reason: str, ref_price: float, now: datetime) -> None:
        cid = f"{pos['client_id']}-X"
        fill = self.x.market_order(s, "sell", pos["qty"], cid, ref_price=ref_price)
        self.store.record_order(fill)
        self._record_close(s, pos, fill.price, ref_price, fill.fee, reason, fill.timestamp)

    def _record_close(self, s, pos, exit_price, exit_ref, exit_fee, reason, when) -> None:
        proceeds = exit_price * pos["qty"] - exit_fee
        cost_basis = pos["entry_price"] * pos["qty"] + pos["entry_fee"]
        pnl = proceeds - cost_basis
        slip = (pos["entry_price"] - pos["entry_ref"]) * pos["qty"] + (exit_ref - exit_price) * pos["qty"]
        trade = {**{k: pos.get(k) for k in ("symbol", "signal_time", "entry_time", "entry_price", "entry_ref", "qty", "stop_initial",
                                             "take_profit", "risk_usd", "equity_at_entry", "params", "features", "p_win")},
                 "exit_time": when, "exit_price": exit_price, "exit_ref": exit_ref, "stop_final": pos["stop"], "reason": reason,
                 "fees": pos["entry_fee"] + exit_fee, "slippage_cost": slip, "pnl": pnl,
                 "r_multiple": pnl / pos["risk_usd"] if pos["risk_usd"] else 0.0, "mode": self.mode}
        self.store.record_trade(trade)
        self.store.delete_position(s)
        self.risk.record_close(pnl, when)
        self.alert.send("trade", f"{s}: VENTA {pos['qty']:.6f} a {exit_price:.2f} | motivo {reason} | PnL {pnl:+.2f} USD ({trade['r_multiple']:+.2f} R)", when)
