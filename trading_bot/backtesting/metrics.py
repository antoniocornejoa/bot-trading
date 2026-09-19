"""Métricas de evaluación (§7.1 del marco). Todas a partir de operaciones cerradas y de
la curva de equity; nunca de retornos "teóricos" sin costes.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats

from .engine import BacktestResult


def _streaks(wins: np.ndarray) -> tuple[int, int]:
    best_w = best_l = cur_w = cur_l = 0
    for w in wins:
        if w:
            cur_w += 1; cur_l = 0
        else:
            cur_l += 1; cur_w = 0
        best_w = max(best_w, cur_w); best_l = max(best_l, cur_l)
    return best_w, best_l


def drawdown_series(equity: pd.Series) -> pd.Series:
    peak = equity.cummax()
    return equity / peak - 1.0


def compute(result: BacktestResult, bars_per_year: int, rf_annual: float = 0.0) -> dict:
    eq = result.equity.astype(float)
    tdf = result.trades_df()
    n = len(tdf)
    out: dict = {"trades": n, "scenario": result.scenario,
                 "skipped_min_notional": result.skipped_min_notional}

    years = len(eq) / bars_per_year if bars_per_year else np.nan
    total_ret = eq.iloc[-1] / result.initial_capital - 1.0
    out["total_return_pct"] = 100 * total_ret
    out["cagr_pct"] = 100 * ((eq.iloc[-1] / result.initial_capital) ** (1 / years) - 1) if years > 0 and eq.iloc[-1] > 0 else np.nan

    r = eq.pct_change().dropna()
    rf_bar = (1 + rf_annual) ** (1 / bars_per_year) - 1 if bars_per_year else 0.0
    ex = r - rf_bar
    sd = ex.std(ddof=1)
    out["volatility_pct"] = 100 * sd * math.sqrt(bars_per_year) if sd > 0 else 0.0
    out["sharpe"] = float(ex.mean() / sd * math.sqrt(bars_per_year)) if sd > 0 else np.nan
    dn = ex[ex < 0]
    dsd = math.sqrt((dn ** 2).sum() / max(len(ex), 1))
    out["sortino"] = float(ex.mean() / dsd * math.sqrt(bars_per_year)) if dsd > 0 else np.nan

    dd = drawdown_series(eq)
    out["max_drawdown_pct"] = 100 * dd.min()
    out["avg_drawdown_pct"] = 100 * dd[dd < 0].mean() if (dd < 0).any() else 0.0
    under = (dd < 0).astype(int)
    grp = (under.diff() != 0).cumsum()
    out["max_dd_duration_bars"] = int(under.groupby(grp).sum().max()) if under.any() else 0
    out["calmar"] = out["cagr_pct"] / abs(out["max_drawdown_pct"]) if out["max_drawdown_pct"] < 0 else np.nan
    out["var95_bar_pct"] = 100 * np.percentile(r, 5) if len(r) else np.nan
    out["cvar95_bar_pct"] = 100 * r[r <= np.percentile(r, 5)].mean() if len(r) else np.nan

    if n == 0:
        out.update({"win_rate_pct": np.nan, "avg_win_R": np.nan, "avg_loss_R": np.nan, "payoff": np.nan,
                    "profit_factor": np.nan, "expectancy_R": np.nan, "expectancy_usd": np.nan,
                    "t_stat": np.nan, "p_value": np.nan, "max_consec_wins": 0, "max_consec_losses": 0,
                    "avg_bars_held": np.nan, "costs_total": 0.0, "gross_pnl": 0.0, "cost_ratio": np.nan,
                    "recovery_factor": np.nan, "trades_per_year": 0.0})
        return out

    R = tdf["r_multiple"].to_numpy(float)
    pnl = tdf["pnl"].to_numpy(float)
    wins = pnl > 0
    out["win_rate_pct"] = 100 * wins.mean()
    out["avg_win_R"] = R[wins].mean() if wins.any() else 0.0
    out["avg_loss_R"] = R[~wins].mean() if (~wins).any() else 0.0
    out["payoff"] = abs(out["avg_win_R"] / out["avg_loss_R"]) if out["avg_loss_R"] < 0 else np.nan
    gp, gl = pnl[wins].sum(), -pnl[~wins].sum()
    out["profit_factor"] = gp / gl if gl > 0 else (np.inf if gp > 0 else 0.0)
    out["expectancy_R"] = R.mean()
    out["expectancy_usd"] = pnl.mean()
    if n > 1 and R.std(ddof=1) > 0:
        t, p = stats.ttest_1samp(R, 0.0)
        out["t_stat"], out["p_value"] = float(t), float(p)
    else:
        out["t_stat"], out["p_value"] = np.nan, np.nan
    out["max_consec_wins"], out["max_consec_losses"] = _streaks(wins)
    out["avg_bars_held"] = float(tdf["bars_held"].mean())
    costs_total = float(tdf["fees"].sum() + tdf["slippage_cost"].sum())
    gross = float(pnl.sum() + costs_total)
    out["costs_total"] = costs_total
    out["gross_pnl"] = gross
    out["cost_ratio"] = costs_total / gross if gross > 0 else np.inf
    out["recovery_factor"] = (eq.iloc[-1] - result.initial_capital) / abs(dd.min() * eq.cummax().max()) if dd.min() < 0 else np.nan
    out["trades_per_year"] = n / years if years > 0 else np.nan
    out["skew_R"], out["kurtosis_R"] = float(stats.skew(R)), float(stats.kurtosis(R))
    return out


def format_table(rows: list[dict], keys: list[str] | None = None) -> str:
    keys = keys or ["trades", "win_rate_pct", "expectancy_R", "t_stat", "profit_factor", "payoff",
                    "sharpe", "sortino", "max_drawdown_pct", "cagr_pct", "cost_ratio"]
    df = pd.DataFrame(rows)
    cols = [k for k in keys if k in df.columns]
    return df[cols].round(3).to_string(index=False)
