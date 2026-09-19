"""Fase 5 · Evaluación de candidatas en TRAIN y VALIDATION (el TEST no se toca).

    python -m trading_bot.research.run_phase5 [--timeframes 4h 1d] [--symbols ...]

Para cada hipótesis registrada (no benchmark) y cada símbolo/timeframe:
  1. Verifica que la estrategia es causal sobre los datos reales (test de look-ahead).
  2. Ejecuta toda la rejilla en TRAIN (escenario base) y evalúa cada configuración en VALIDATION.
  3. Reporta las mejores por t-stat en train con su resultado en validation, y la vista de
     "meseta": qué fracción de la rejilla es positiva en validation.
Además calcula los benchmarks (buy & hold, MA, RSI2, aleatoria con 200 réplicas) sobre
TRAIN+VALIDATION y escribe research/reports/02_phase5_candidates.md.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from ..backtesting import check_no_lookahead, grid, load_scenarios, metrics
from ..data import store
from ..strategies import REGISTRY, BuyAndHold, MA200Momentum, RSI2MeanReversion, RandomSameFrequency

ROOT = Path(__file__).resolve().parents[1]
KEYS = ["trades", "win_rate_pct", "expectancy_R", "t_stat", "profit_factor", "payoff", "sharpe",
        "max_drawdown_pct", "cagr_pct", "cost_ratio"]


def _engine_kw(cfg: dict, symbol: str) -> dict:
    lim = cfg["exchange_limits"].get(symbol, {"min_notional": 5.0, "lot_step": 1e-5})
    return {"initial_capital": 500.0, "risk_pct": 1.0, "min_notional": lim["min_notional"], "lot_step": lim["lot_step"]}


def evaluate_hypothesis(h: dict, df: pd.DataFrame, tf: str, costs, engine_kw: dict) -> dict:
    S = REGISTRY[h["strategy"]]
    bpy = store.BARS_PER_YEAR[tf]
    sp = grid.split_by_time(df)
    leaks = check_no_lookahead(S(), df.iloc[sp["train"]])
    rows = []
    for params in grid.expand_grid(h["grid"]):
        sig = S(**params).generate(df)
        tr = metrics.compute(grid.run_config(S, params, df, costs, sp["train"], sig, **engine_kw), bpy)
        va = metrics.compute(grid.run_config(S, params, df, costs, sp["validation"], sig, **engine_kw), bpy)
        rows.append({**params, **{f"train_{k}": tr[k] for k in KEYS}, **{f"val_{k}": va[k] for k in KEYS}})
    tab = pd.DataFrame(rows)
    ok = tab[(tab["train_trades"] >= 30) & (tab["val_trades"] >= 10)]
    plateau = {
        "configs": len(tab), "configs_valid": len(ok),
        "pct_val_positive": 100 * float((ok["val_expectancy_R"] > 0).mean()) if len(ok) else np.nan,
        "median_val_expectancy_R": float(ok["val_expectancy_R"].median()) if len(ok) else np.nan,
        "median_train_expectancy_R": float(ok["train_expectancy_R"].median()) if len(ok) else np.nan,
        "n_val_t_ge_2": int((ok["val_t_stat"] >= 2).sum()) if len(ok) else 0,
    }
    top = ok.sort_values("train_t_stat", ascending=False).head(5) if len(ok) else tab.head(0)
    return {"leaks": leaks, "table": tab, "plateau": plateau, "top": top,
            "train_range": (df.index[sp["train"].start], df.index[sp["train"].stop - 1]),
            "val_range": (df.index[sp["validation"].start], df.index[sp["validation"].stop - 1])}


def benchmarks(df: pd.DataFrame, tf: str, costs, engine_kw: dict, n_random: int = 200, like: pd.DataFrame | None = None) -> dict:
    bpy = store.BARS_PER_YEAR[tf]
    sp = grid.split_by_time(df)
    w = slice(0, sp["validation"].stop)  # train + validation, nunca test
    out = {}
    for S in (BuyAndHold, MA200Momentum, RSI2MeanReversion):
        kw = {**engine_kw, "risk_pct": 100.0} if S is BuyAndHold else engine_kw  # B&H invierte todo el capital
        out[S.name] = metrics.compute(grid.run_config(S, S.default_params(), df, costs, w, **kw), bpy)
    rnd = []
    for seed in range(n_random):
        R = RandomSameFrequency.like(like, len(df.iloc[w]), seed=seed) if like is not None and len(like) else RandomSameFrequency(seed=seed)
        m = metrics.compute(grid.run_config(RandomSameFrequency, R.params, df, costs, w, **engine_kw), bpy)
        rnd.append({"expectancy_R": m["expectancy_R"], "total_return_pct": m["total_return_pct"], "sharpe": m["sharpe"]})
    r = pd.DataFrame(rnd)
    out["random"] = {"n": n_random, "expectancy_R_p50": float(r["expectancy_R"].median()),
                     "expectancy_R_p95": float(r["expectancy_R"].quantile(0.95)),
                     "total_return_p95": float(r["total_return_pct"].quantile(0.95)),
                     "sharpe_p95": float(r["sharpe"].quantile(0.95))}
    return out


def fmt(d: dict) -> str:
    return ", ".join(f"{k}={v:.3f}" if isinstance(v, (float, np.floating)) else f"{k}={v}" for k, v in d.items())


def main(argv=None) -> None:
    cfg = yaml.safe_load(open(ROOT / "config" / "research.yaml"))
    hyp_path = ROOT / "research" / "hypotheses.yaml"
    hyp = yaml.safe_load(open(hyp_path))
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--symbols", nargs="+", default=hyp["meta"]["universe"])
    p.add_argument("--timeframes", nargs="+", default=hyp["meta"]["timeframes"])
    p.add_argument("--n-random", type=int, default=200)
    a = p.parse_args(argv)
    costs = load_scenarios()[hyp["meta"]["cost_scenario_for_decisions"]]
    pq_root = Path(a.root) / cfg["paths"]["parquet"]

    L = ["# Fase 5 · Candidatas en train / validation", "",
         f"Escenario de costes: **{costs.name}** (ida y vuelta {costs.round_trip_pct():.2f} % sin impacto). "
         "Partición 60/20/20 por tiempo; el 20 % final (test) **no se ha usado**.", ""]
    executed = 0
    for sym in a.symbols:
        found = store.finest_available(pq_root, "spot", sym)
        if found is None:
            L.append(f"## {sym}: sin datos"); continue
        base = store.load(found[0])
        L += [f"## {sym}  (base {found[1]}, hash `{store.dataset_hash(base)}`)", ""]
        ekw = _engine_kw(cfg, sym)
        for tf in a.timeframes:
            df = store.resample(base, tf)
            L += [f"### {tf} · {len(df):,} velas ({df.index[0].date()} → {df.index[-1].date()})", ""]
            best_like = None
            for h in hyp["hypotheses"]:
                if h.get("role") == "benchmark" or h["strategy"] not in REGISTRY:
                    continue
                r = evaluate_hypothesis(h, df, tf, costs, ekw)
                executed += r["plateau"]["configs"]
                L += [f"#### {h['id']} · {h['strategy']}",
                      f"train {r['train_range'][0].date()} → {r['train_range'][1].date()} | validation {r['val_range'][0].date()} → {r['val_range'][1].date()}", ""]
                L += ["- Look-ahead: " + ("**VIOLACIÓN** " + "; ".join(r["leaks"]) if r["leaks"] else "ok")]
                L += ["- Meseta: " + fmt(r["plateau"]), ""]
                if len(r["top"]):
                    cols = list(h["grid"]) + ["train_trades", "train_expectancy_R", "train_t_stat", "train_profit_factor",
                                              "val_trades", "val_expectancy_R", "val_t_stat", "val_profit_factor", "val_sharpe", "val_cagr_pct", "val_max_drawdown_pct", "val_cost_ratio"]
                    L += ["Top 5 por t-stat en train:", "", r["top"][cols].round(3).to_markdown(index=False), ""]
                    if best_like is None:
                        bp = {k: r["top"].iloc[0][k] for k in h["grid"]}
                        bp = {k: (int(v) if float(v).is_integer() else float(v)) for k, v in bp.items()}
                        res = grid.run_config(REGISTRY[h["strategy"]], bp, df, costs, slice(0, grid.split_by_time(df)["validation"].stop), **ekw)
                        best_like = res.trades_df()
                else:
                    L += ["Ninguna configuración con ≥30 operaciones en train y ≥10 en validation.", ""]
            b = benchmarks(df, tf, costs, ekw, a.n_random, best_like)
            L += ["#### Benchmarks (train+validation)", ""]
            for k, v in b.items():
                L += [f"- **{k}**: " + fmt({kk: v[kk] for kk in (KEYS if k != "random" else v) if kk in v})]
            L += [""]
        print(f"{sym}: ok")
    out = Path(a.root) / cfg["paths"]["reports"]; out.mkdir(parents=True, exist_ok=True)
    log_path = out / "executions.yaml"
    log = yaml.safe_load(open(log_path)) if log_path.exists() else {"executions": []}
    log["executions"].append({"phase": 5, "date": str(pd.Timestamp.now("UTC").date()), "symbols": a.symbols,
                              "timeframes": a.timeframes, "configs_executed": executed, "test_used": False})
    yaml.safe_dump(log, open(log_path, "w"), sort_keys=False, allow_unicode=True)
    (out / "02_phase5_candidates.md").write_text("\n".join(L))
    print(f"informe: {out / '02_phase5_candidates.md'} | configuraciones ejecutadas: {executed}")


if __name__ == "__main__":
    main()
