"""Análisis de sensibilidad (§6.3 y sección 24 del brief): cada parámetro numérico se
perturba ±5/10/20/30 % alrededor de la configuración elegida, uno a uno, y se mide la
expectancy. Una estrategia cuya expectancy cambia de signo con ±20 % se considera frágil."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..strategies.base import Strategy
from . import metrics
from .costs import CostScenario
from .grid import run_config

STEPS = (-0.30, -0.20, -0.10, -0.05, 0.0, 0.05, 0.10, 0.20, 0.30)


def _perturb(value, pct):
    if isinstance(value, bool) or not isinstance(value, (int, float, np.integer, np.floating)):
        return None
    v = value * (1 + pct)
    return int(round(v)) if isinstance(value, (int, np.integer)) else float(v)


def sensitivity(strategy_cls: type[Strategy], params: dict, df: pd.DataFrame, costs: CostScenario,
                bars_per_year: int, window: slice | None = None, **engine_kw) -> pd.DataFrame:
    rows = []
    for k, v in params.items():
        for pct in STEPS:
            nv = _perturb(v, pct)
            if nv is None or (pct != 0 and nv == v):
                continue
            p = {**params, k: nv}
            m = metrics.compute(run_config(strategy_cls, p, df, costs, window, **engine_kw), bars_per_year)
            rows.append({"param": k, "pct": pct, "value": nv, "trades": m["trades"],
                         "expectancy_R": m["expectancy_R"], "profit_factor": m["profit_factor"],
                         "sharpe": m["sharpe"], "max_drawdown_pct": m["max_drawdown_pct"]})
    return pd.DataFrame(rows)


def verdict(table: pd.DataFrame, base_expectancy: float) -> dict:
    """Frágil si alguna perturbación ≤ ±20 % cambia el signo, o si la caída media con ±30 % supera el 40 %."""
    near = table[table["pct"].abs() <= 0.20]
    sign_flip = bool(((near["expectancy_R"] > 0) != (base_expectancy > 0)).any()) if base_expectancy != 0 else True
    far = table[table["pct"].abs() == 0.30]
    drop = 1 - far["expectancy_R"].mean() / base_expectancy if base_expectancy > 0 and len(far) else np.nan
    return {"sign_flip_within_20pct": sign_flip, "avg_drop_at_30pct": float(drop) if drop == drop else np.nan,
            "fragile": sign_flip or (drop == drop and drop > 0.40)}
