"""Rejilla de parámetros y utilidades de partición temporal."""
from __future__ import annotations

from itertools import product

import pandas as pd

from ..strategies.base import Strategy
from . import metrics
from .costs import CostScenario
from .engine import BacktestResult, run


def expand_grid(grid: dict) -> list[dict]:
    keys = list(grid)
    return [dict(zip(keys, vals)) for vals in product(*(grid[k] for k in keys))]


def split_by_time(df: pd.DataFrame, train: float = 0.6, validation: float = 0.2) -> dict[str, slice]:
    n = len(df)
    a, b = int(n * train), int(n * (train + validation))
    return {"train": slice(0, a), "validation": slice(a, b), "test": slice(b, n)}


def run_config(strategy_cls: type[Strategy], params: dict, df: pd.DataFrame, costs: CostScenario,
               window: slice | None = None, signals: pd.DataFrame | None = None, **engine_kw) -> BacktestResult:
    """Ejecuta una configuración. Las señales se calculan sobre todo `df` (son causales, y
    así los indicadores del tramo evaluado disponen del histórico previo) y se recortan."""
    strat = strategy_cls(**params)
    sig = signals if signals is not None else strat.generate(df)
    if window is not None:
        df, sig = df.iloc[window], sig.iloc[window]
    res = run(df, sig, costs, params=params, **engine_kw)
    return res


def run_grid(strategy_cls: type[Strategy], grid: dict, df: pd.DataFrame, costs: CostScenario,
             bars_per_year: int, window: slice | None = None, **engine_kw) -> pd.DataFrame:
    rows = []
    for params in expand_grid(grid):
        res = run_config(strategy_cls, params, df, costs, window, **engine_kw)
        m = metrics.compute(res, bars_per_year)
        rows.append({**params, **m})
    return pd.DataFrame(rows)


def select_best(table: pd.DataFrame, objective: str = "t_stat", min_trades: int = 30) -> pd.Series | None:
    ok = table[table["trades"] >= min_trades].dropna(subset=[objective])
    if ok.empty:
        return None
    return ok.sort_values(objective, ascending=False).iloc[0]
