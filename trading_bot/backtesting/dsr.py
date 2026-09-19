"""Deflated Sharpe Ratio (Bailey & López de Prado, 2014) — §6.5 del marco.

Dado el Sharpe observado (por periodo, sin anualizar), el número de pruebas M, la
varianza de los Sharpes entre pruebas y los momentos de los retornos, devuelve la
probabilidad de que el Sharpe real sea > 0 una vez descontado el "mejor de M".
"""
from __future__ import annotations

import numpy as np
from scipy import stats

EULER = 0.5772156649


def expected_max_sharpe(n_trials: int, var_sharpe: float) -> float:
    """Sharpe máximo esperado por puro azar entre n_trials pruebas con varianza var_sharpe."""
    if n_trials <= 1:
        return 0.0
    sd = np.sqrt(var_sharpe)
    return sd * ((1 - EULER) * stats.norm.ppf(1 - 1 / n_trials) + EULER * stats.norm.ppf(1 - 1 / (n_trials * np.e)))


def probabilistic_sharpe(sr: float, sr_benchmark: float, n_obs: int, skew: float, kurt: float) -> float:
    """PSR: P(SR real > sr_benchmark). kurt = curtosis NO excedente (normal = 3)."""
    denom = np.sqrt(1 - skew * sr + (kurt - 1) / 4 * sr ** 2)
    if not np.isfinite(denom) or denom <= 0 or n_obs < 2:
        return np.nan
    return float(stats.norm.cdf((sr - sr_benchmark) * np.sqrt(n_obs - 1) / denom))


def deflated_sharpe(returns: np.ndarray, n_trials: int, var_sharpe_trials: float) -> dict:
    r = np.asarray(returns, float)
    r = r[np.isfinite(r)]
    if len(r) < 3 or r.std(ddof=1) == 0:
        return {"sr": np.nan, "sr0": np.nan, "dsr": np.nan}
    sr = r.mean() / r.std(ddof=1)
    sr0 = expected_max_sharpe(n_trials, var_sharpe_trials)
    dsr = probabilistic_sharpe(sr, sr0, len(r), float(stats.skew(r)), float(stats.kurtosis(r, fisher=False)))
    return {"sr": float(sr), "sr0": float(sr0), "dsr": dsr, "n_obs": len(r), "n_trials": n_trials}
