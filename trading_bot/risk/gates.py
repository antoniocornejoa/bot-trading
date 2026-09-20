"""Gates de capital (Fase 10, §7.3 del marco). El bot NUNCA sube de nivel solo: evalúa y
propone; la subida la confirma el propietario. La bajada sí es automática.

Cada nivel exige un mínimo de operaciones desde el nivel anterior, profit factor, expectancy,
drawdown acumulado y ausencia de desviación entre lo operado y el backtest.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

LEVELS = [("paper", 0), (1, 500), (2, 750), (3, 1000), (4, 2000), (5, 5000), (6, 10000), (7, 25000), (8, 50000)]

REQUIREMENTS = {
    # nivel destino: (operaciones mínimas en el nivel actual, PF mínimo, expectancy mínima R, DD máximo %)
    1: (60, 1.2, 0.05, 15.0),   # de paper a US$500
    2: (100, 1.2, 0.05, 15.0),
    3: (60, 1.2, 0.05, 15.0),
    4: (80, 1.2, 0.05, 20.0),
    5: (100, 1.2, 0.05, 20.0),
    6: (150, 1.2, 0.05, 20.0),
    7: (200, 1.2, 0.05, 20.0),
    8: (200, 1.2, 0.05, 20.0),
}


@dataclass
class GateReport:
    current_level: object
    next_level: object
    trades: int
    profit_factor: float
    expectancy_R: float
    max_dd_pct: float
    divergence_p: float
    passes: bool
    reasons: list


def evaluate(trades_live: pd.DataFrame, backtest_R: np.ndarray, current_level, equity_curve: pd.Series) -> GateReport:
    """trades_live: operaciones reales del nivel actual con columnas pnl, r_multiple.
    backtest_R: R de las operaciones OOS del backtest (referencia). Divergencia: test de dos
    muestras (Mann-Whitney) sobre R; p < 0,10 marca desviación."""
    idx = [l for l, _ in LEVELS].index(current_level)
    nxt = LEVELS[idx + 1][0] if idx + 1 < len(LEVELS) else None
    n = len(trades_live)
    R = trades_live["r_multiple"].to_numpy(float) if n else np.array([])
    pnl = trades_live["pnl"].to_numpy(float) if n else np.array([])
    gp, gl = pnl[pnl > 0].sum() if n else 0.0, -pnl[pnl < 0].sum() if n else 0.0
    pf = gp / gl if gl > 0 else (np.inf if gp > 0 else 0.0)
    exp = float(R.mean()) if n else np.nan
    dd = float((equity_curve / equity_curve.cummax() - 1).min() * 100) if len(equity_curve) else 0.0
    p = float(stats.mannwhitneyu(R, backtest_R, alternative="two-sided").pvalue) if n >= 10 and len(backtest_R) >= 10 else np.nan
    reasons = []
    if nxt is None:
        return GateReport(current_level, None, n, pf, exp, dd, p, False, ["nivel máximo"])
    min_n, min_pf, min_exp, max_dd = REQUIREMENTS[nxt]
    if n < min_n: reasons.append(f"operaciones {n} < {min_n}")
    if not pf >= min_pf: reasons.append(f"PF {pf:.2f} < {min_pf}")
    if not exp >= min_exp: reasons.append(f"expectancy {exp:.3f} R < {min_exp}")
    if dd < -max_dd: reasons.append(f"drawdown {dd:.1f} % peor que −{max_dd} %")
    if p == p and p < 0.10: reasons.append(f"desviación respecto al backtest (p = {p:.3f})")
    return GateReport(current_level, nxt, n, pf, exp, dd, p, not reasons, reasons)


def should_downgrade(trades_recent: pd.DataFrame, mc_p5_expectancy: float, equity_curve: pd.Series, max_dd_pct: float = 20.0) -> tuple[bool, str]:
    """Bajada automática: expectancy de las últimas 100 operaciones por debajo del percentil 5 del
    Monte Carlo, o drawdown acumulado por encima del máximo del nivel."""
    if len(equity_curve) and (equity_curve / equity_curve.cummax() - 1).min() * 100 < -max_dd_pct:
        return True, "drawdown por encima del máximo del nivel"
    if len(trades_recent) >= 100 and trades_recent["r_multiple"].tail(100).mean() < mc_p5_expectancy:
        return True, "expectancy reciente por debajo del percentil 5 del Monte Carlo"
    return False, ""
