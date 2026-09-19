"""Monte Carlo sobre operaciones cerradas (§6.7 del marco).

Cada operación se expresa como fracción del capital en el momento de entrar (pnl /
equity_at_entry), de modo que la simulación compone y respeta el tamaño relativo. Se
remuestrea con reemplazo (iid o por bloques para conservar rachas) y se aplican
perturbaciones adversas. Se reportan percentiles, nunca solo la media.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class MCResult:
    final_equity: np.ndarray
    max_dd: np.ndarray
    max_consec_losses: np.ndarray
    ruin_prob: float
    summary: dict


def _max_dd(path: np.ndarray) -> float:
    peak = np.maximum.accumulate(path)
    return float((path / peak - 1).min())


def _consec_losses(x: np.ndarray) -> int:
    best = cur = 0
    for v in x:
        cur = cur + 1 if v < 0 else 0
        best = max(best, cur)
    return best


def simulate(trades_df: pd.DataFrame, initial_capital: float = 500.0, n_paths: int = 5000, n_trades: int | None = None,
             block: int = 1, seed: int = 0, ruin_dd: float = -0.25, win_rate_shift: float = 0.0,
             avg_win_mult: float = 1.0, avg_loss_mult: float = 1.0, extra_cost_pct: float = 0.0,
             drop_best_pct: float = 0.0) -> MCResult:
    """
    win_rate_shift: fracción de ganadoras convertidas en perdedoras (p. ej. 0,05 = −5 pp).
    avg_win_mult / avg_loss_mult: escalado de ganancias / pérdidas (p. ej. 0,9 y 1,1).
    extra_cost_pct: coste adicional por operación en % del capital (slippage extra).
    drop_best_pct: elimina el X % de mejores operaciones (dependencia de outliers).
    """
    rng = np.random.default_rng(seed)
    r = (trades_df["pnl"] / trades_df["equity_at_entry"]).to_numpy(float)
    if drop_best_pct > 0:
        k = int(len(r) * drop_best_pct)
        if k:
            r = np.sort(r)[:-k]
            rng.shuffle(r)
    r = np.where(r > 0, r * avg_win_mult, r * avg_loss_mult) - extra_cost_pct / 100.0
    if win_rate_shift > 0:
        # las ganadoras "perdidas" se convierten en una pérdida típica (el stop acota la pérdida),
        # no en una pérdida del tamaño de la ganancia (irreal para colas derechas gordas)
        wins = np.flatnonzero(r > 0)
        losses = r[r < 0]
        typical_loss = losses.mean() if len(losses) else -abs(r).mean()
        flip = rng.choice(wins, max(1, int(len(wins) * win_rate_shift)), replace=False) if len(wins) else []
        r[flip] = typical_loss
    n = n_trades or len(r)
    if n == 0:
        raise ValueError("sin operaciones")
    paths = np.empty((n_paths, n))
    if block <= 1:
        idx = rng.integers(0, len(r), size=(n_paths, n))
        paths = r[idx]
    else:
        nb = int(np.ceil(n / block))
        starts = rng.integers(0, max(len(r) - block, 1), size=(n_paths, nb))
        for i in range(n_paths):
            seq = np.concatenate([r[s:s + block] for s in starts[i]])[:n]
            paths[i, :len(seq)] = seq
    equity = initial_capital * np.cumprod(1 + paths, axis=1)
    equity = np.hstack([np.full((n_paths, 1), initial_capital), equity])
    max_dd = np.array([_max_dd(p) for p in equity])
    consec = np.array([_consec_losses(p) for p in paths])
    ruin = float((max_dd <= ruin_dd).mean())
    fe = equity[:, -1]
    pct = lambda a, q: float(np.percentile(a, q))
    summary = {
        "n_paths": n_paths, "n_trades": n,
        "final_p5": pct(fe, 5), "final_p50": pct(fe, 50), "final_p95": pct(fe, 95),
        "max_dd_p50_pct": 100 * pct(max_dd, 50), "max_dd_p95_pct": 100 * pct(max_dd, 5),  # p95 del DD = percentil 5 de la serie negativa
        "max_dd_worst_pct": 100 * float(max_dd.min()),
        "consec_losses_p50": pct(consec, 50), "consec_losses_p95": pct(consec, 95),
        "prob_loss": float((fe < initial_capital).mean()), "ruin_prob": ruin, "ruin_threshold_pct": 100 * ruin_dd,
    }
    return MCResult(fe, max_dd, consec, ruin, summary)


STRESS = {
    "base": {},
    "win_rate_-5pp": {"win_rate_shift": 0.05},
    "avg_win_-10%": {"avg_win_mult": 0.9},
    "avg_loss_+10%": {"avg_loss_mult": 1.1},
    "slippage_x2": {"extra_cost_pct": 0.06},
    "drop_best_5%": {"drop_best_pct": 0.05},
    "blocks_5": {"block": 5},
}


def profit_concentration(trades_df: pd.DataFrame, top_pct: float = 0.10) -> float:
    """Fracción del beneficio neto total aportada por el top X % de operaciones (dependencia de outliers)."""
    pnl = np.sort(trades_df["pnl"].to_numpy(float))[::-1]
    k = max(1, int(len(pnl) * top_pct))
    total = pnl.sum()
    return float(pnl[:k].sum() / total) if total > 0 else np.nan


def stress_table(trades_df: pd.DataFrame, **kw) -> pd.DataFrame:
    rows = []
    for name, over in STRESS.items():
        s = simulate(trades_df, **{**kw, **over}).summary
        rows.append({"scenario": name, **{k: s[k] for k in ("final_p5", "final_p50", "max_dd_p50_pct", "max_dd_p95_pct", "consec_losses_p95", "ruin_prob")}})
    return pd.DataFrame(rows)
