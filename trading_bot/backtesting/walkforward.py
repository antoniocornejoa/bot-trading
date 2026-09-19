"""Walk-forward (§6.6 del marco): re-selección periódica de parámetros en una ventana de
entrenamiento y evaluación en la ventana siguiente, encadenando la equity fuera de muestra.

Reporta, además de las métricas OOS combinadas:
  - eficiencia WF = expectancy OOS / expectancy IS (media entre ventanas)
  - fracción de ventanas OOS con beneficio positivo
  - concentración: máxima fracción del beneficio OOS aportada por una sola ventana
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ..strategies.base import Strategy
from . import metrics
from .costs import CostScenario
from .engine import BacktestResult, Trade
from .grid import expand_grid, run_config, select_best


@dataclass
class WFWindow:
    train: slice
    test: slice
    params: dict
    train_metrics: dict
    test_metrics: dict
    test_pnl: float


@dataclass
class WFResult:
    windows: list[WFWindow]
    trades: list[Trade]
    equity: pd.Series
    initial_capital: float
    scenario: str
    oos_metrics: dict = field(default_factory=dict)
    summary: dict = field(default_factory=dict)


def walk_forward(strategy_cls: type[Strategy], grid: dict, df: pd.DataFrame, costs: CostScenario,
                 bars_per_year: int, train_bars: int, test_bars: int, anchored: bool = False,
                 objective: str = "t_stat", min_trades: int = 30, initial_capital: float = 500.0,
                 **engine_kw) -> WFResult:
    n = len(df)
    configs = expand_grid(grid)
    signals = {i: strategy_cls(**p).generate(df) for i, p in enumerate(configs)}  # causales: una vez
    windows: list[WFWindow] = []
    trades: list[Trade] = []
    equity_parts: list[pd.Series] = []
    equity = initial_capital
    start = 0
    while start + train_bars + test_bars <= n:
        tr = slice(0 if anchored else start, start + train_bars)
        te = slice(start + train_bars, start + train_bars + test_bars)
        rows = []
        for i, p in enumerate(configs):
            res = run_config(strategy_cls, p, df, costs, tr, signals[i], initial_capital=initial_capital, **engine_kw)
            rows.append({"_i": i, **p, **metrics.compute(res, bars_per_year)})
        best = select_best(pd.DataFrame(rows), objective, min_trades)
        if best is None:  # sin configuración válida en train: no se opera esta ventana
            eq = pd.Series(equity, index=df.index[te])
            windows.append(WFWindow(tr, te, {}, {}, {"trades": 0}, 0.0))
        else:
            i = int(best["_i"]); p = configs[i]
            res = run_config(strategy_cls, p, df, costs, te, signals[i], initial_capital=equity, **engine_kw)
            tm = metrics.compute(res, bars_per_year)
            trm = {k: best[k] for k in ("trades", "expectancy_R", "t_stat", "profit_factor", "sharpe", "max_drawdown_pct")}
            windows.append(WFWindow(tr, te, p, trm, tm, res.equity.iloc[-1] - equity))
            trades.extend(res.trades)
            eq = res.equity
            equity = float(eq.iloc[-1])
        equity_parts.append(eq)
        start += test_bars
    if not equity_parts:
        raise ValueError("no hay barras suficientes para una ventana de walk-forward")
    eq_all = pd.concat(equity_parts)
    combined = BacktestResult(trades=trades, equity=eq_all, initial_capital=initial_capital, scenario=costs.name)
    oos = metrics.compute(combined, bars_per_year)
    return WFResult(windows, trades, eq_all, initial_capital, costs.name, oos, _summary(windows, oos))


def _summary(windows: list[WFWindow], oos: dict) -> dict:
    traded = [w for w in windows if w.params]
    pnls = np.array([w.test_pnl for w in windows])
    eff = [w.test_metrics["expectancy_R"] / w.train_metrics["expectancy_R"]
           for w in traded if w.train_metrics.get("expectancy_R", 0) > 0 and w.test_metrics.get("trades", 0) > 0]
    pos = pnls[pnls > 0].sum()
    return {
        "windows": len(windows), "windows_traded": len(traded),
        "pct_windows_positive": 100 * float((pnls > 0).mean()) if len(pnls) else np.nan,
        "wf_efficiency": float(np.median(eff)) if eff else np.nan,
        "max_window_share_pct": 100 * float(pnls.max() / pos) if pos > 0 else np.nan,
        "oos_trades": oos.get("trades", 0), "oos_expectancy_R": oos.get("expectancy_R"),
        "oos_t_stat": oos.get("t_stat"), "oos_sharpe": oos.get("sharpe"),
        "oos_max_dd_pct": oos.get("max_drawdown_pct"), "oos_profit_factor": oos.get("profit_factor"),
    }
