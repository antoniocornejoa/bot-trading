"""Fases 8 y 9 · Sensibilidad y Monte Carlo sobre una candidata.

    python -m trading_bot.research.run_phase8_9 --hypothesis H-A2 --params n=150 atr_mult=3 --timeframe 4h

- Sensibilidad (Fase 8): ±5/10/20/30 % por parámetro sobre train+validation, símbolos agrupados.
- Monte Carlo (Fase 9): sobre las operaciones OOS del walk-forward (research/reports/trades_*.csv),
  a 0,25 / 0,5 / 0,75 / 1 % de riesgo por operación: percentiles de drawdown, rachas, riesgo de
  ruina, tabla de estrés y simulación de crecimiento a 5 años con probabilidad de alcanzar cada
  nivel de capital. SIMULACIÓN, NO PREDICCIÓN.
Escribe research/reports/04_phase8_9_{hid}.md.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from ..backtesting import grid, load_scenarios, metrics, montecarlo, sensitivity
from ..data import store
from ..strategies import REGISTRY

ROOT = Path(__file__).resolve().parents[1]
LEVELS = [750, 1000, 2000, 5000, 10000, 25000, 50000]


def pooled_sensitivity(S, params: dict, data: dict, tf: str, costs, cfg: dict) -> pd.DataFrame:
    bpy = store.BARS_PER_YEAR[tf]
    rows = []
    for k, v in params.items():
        for pct in sensitivity.STEPS:
            nv = sensitivity._perturb(v, pct)
            if nv is None or (pct != 0 and nv == v):
                continue
            p = {**params, k: nv}
            trades, eq_parts = [], []
            for sym, base in data.items():
                df = store.resample(base, tf)
                end = grid.split_by_time(df)["validation"].stop
                ekw = {"initial_capital": 500.0, "risk_pct": 1.0, **cfg["exchange_limits"].get(sym, {})}
                res = grid.run_config(S, p, df, costs, slice(0, end), **ekw)
                trades += res.trades; eq_parts.append(res.equity)
            from ..backtesting.engine import BacktestResult
            m = metrics.compute(BacktestResult(trades, pd.concat(eq_parts).sort_index(), 500.0, costs.name), bpy)
            rows.append({"param": k, "pct": pct, "value": nv, "trades": m["trades"], "expectancy_R": m["expectancy_R"],
                         "t_stat": m["t_stat"], "profit_factor": m["profit_factor"]})
    return pd.DataFrame(rows)


def growth_simulation(tdf: pd.DataFrame, trades_per_year: float, risk_scale: float, years: int = 5, n_paths: int = 5000,
                      seed: int = 0, initial: float = 500.0, ruin_dd: float = -0.25) -> dict:
    rng = np.random.default_rng(seed)
    r = (tdf["pnl"] / tdf["equity_at_entry"]).to_numpy(float) * risk_scale
    n = int(trades_per_year * years)
    idx = rng.integers(0, len(r), size=(n_paths, n))
    eq = initial * np.cumprod(1 + r[idx], axis=1)
    eq = np.hstack([np.full((n_paths, 1), initial), eq])
    peak = np.maximum.accumulate(eq, axis=1)
    dd = eq / peak - 1
    ruined = (dd <= ruin_dd).any(axis=1)
    first_ruin = np.where(ruined, np.argmax(dd <= ruin_dd, axis=1), n + 1)
    out = {"risk_scale": risk_scale, "n_trades_5y": n, "ruin_prob": float(ruined.mean())}
    for lvl in LEVELS:
        hit = eq >= lvl
        reached = hit.any(axis=1)
        first = np.where(reached, np.argmax(hit, axis=1), n + 1)
        ok = reached & (first < first_ruin)   # alcanza el nivel antes de tocar el kill switch
        out[f"P({lvl})"] = float(ok.mean())
        out[f"t_med({lvl})_años"] = float(np.median(first[ok]) / trades_per_year) if ok.any() else np.nan
    fe = eq[:, -1]
    out.update({"final_p5": float(np.percentile(fe, 5)), "final_p50": float(np.percentile(fe, 50)), "final_p95": float(np.percentile(fe, 95)),
                "max_dd_p50": float(np.percentile(dd.min(axis=1), 50)), "max_dd_p95": float(np.percentile(dd.min(axis=1), 5))})
    return out


def main(argv=None) -> None:
    cfg = yaml.safe_load(open(ROOT / "config" / "research.yaml"))
    hyp = yaml.safe_load(open(ROOT / "research" / "hypotheses.yaml"))
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--hypothesis", default="H-A2")
    p.add_argument("--params", nargs="+", default=["n=150", "atr_mult=3.0"])
    p.add_argument("--timeframe", default="4h")
    p.add_argument("--scenario", default="base")
    a = p.parse_args(argv)
    hyps = {h["id"]: h for h in hyp["hypotheses"]}
    S = REGISTRY[hyps[a.hypothesis]["strategy"]]
    params = {}
    for kv in a.params:
        k, v = kv.split("="); params[k] = int(v) if v.isdigit() else float(v)
    costs = load_scenarios()[a.scenario]
    pq_root = Path(a.root) / cfg["paths"]["parquet"]
    data = {s: store.load(store.finest_available(pq_root, "spot", s)[0]) for s in hyp["meta"]["universe"] if store.finest_available(pq_root, "spot", s)}
    reports = Path(a.root) / cfg["paths"]["reports"]

    L = [f"# Fases 8 y 9 · {a.hypothesis} {params} · {a.timeframe} · escenario {costs.name}", ""]
    # --- sensibilidad
    sens = pooled_sensitivity(S, params, data, a.timeframe, costs, cfg)
    base_row = sens[sens["pct"] == 0].iloc[0]
    v = sensitivity.verdict(sens, float(base_row["expectancy_R"]))
    L += ["## Sensibilidad (train+validation, símbolos agrupados)", "",
          f"Base: {int(base_row['trades'])} operaciones, expectancy {base_row['expectancy_R']:.3f} R, t = {base_row['t_stat']:.2f}, PF {base_row['profit_factor']:.2f}", "",
          sens.round(3).to_markdown(index=False), "",
          f"Veredicto: cambio de signo con ±20 %: **{v['sign_flip_within_20pct']}**; caída media a ±30 %: {v['avg_drop_at_30pct']:.0%}; frágil: **{v['fragile']}**", ""]
    # --- monte carlo
    tpath = reports / f"trades_{a.hypothesis}_{a.timeframe}_{costs.name}.csv"
    tdf = pd.read_csv(tpath, parse_dates=["entry_time", "exit_time"])
    years = (tdf["exit_time"].max() - tdf["entry_time"].min()).days / 365.25
    tpy = len(tdf) / years
    L += [f"## Monte Carlo sobre {len(tdf)} operaciones OOS del walk-forward ({years:.1f} años, {tpy:.0f} op/año agrupando símbolos)", "",
          "Las operaciones OOS se generaron con 1 % de riesgo; los demás niveles escalan proporcionalmente el retorno por operación.", ""]
    rows = []
    for risk in (0.25, 0.5, 0.75, 1.0):
        scaled = tdf.copy(); scaled["pnl"] = scaled["pnl"] * risk
        mc = montecarlo.simulate(scaled, n_paths=5000, seed=1, block=5)
        s = mc.summary
        rows.append({"riesgo_%": risk, "final_p5": s["final_p5"], "final_p50": s["final_p50"], "final_p95": s["final_p95"],
                     "DD_p50_%": s["max_dd_p50_pct"], "DD_p95_%": s["max_dd_p95_pct"], "DD_peor_%": s["max_dd_worst_pct"],
                     "rachas_p95": s["consec_losses_p95"], "P(perder)": s["prob_loss"], "P(ruina -25%)": s["ruin_prob"]})
    L += ["### Por nivel de riesgo (bloques de 5 operaciones, 5.000 caminos, misma cantidad de operaciones que el histórico OOS)", "",
          pd.DataFrame(rows).round(3).to_markdown(index=False), ""]
    L += [f"Concentración del beneficio: el 10 % mejor de las operaciones aporta el {montecarlo.profit_concentration(tdf, 0.10):.0%} del beneficio neto; el 5 % mejor, el {montecarlo.profit_concentration(tdf, 0.05):.0%}. "
          "Es la naturaleza del seguimiento de tendencia (payoff alto, win rate bajo): la ventaja está en dejar correr pocas operaciones grandes.", ""]
    L += ["### Estrés a 0,5 % de riesgo", ""]
    half = tdf.copy(); half["pnl"] *= 0.5
    L += [montecarlo.stress_table(half, n_paths=3000, seed=2).round(3).to_markdown(index=False), ""]
    L += ["## Simulación de crecimiento a 5 años desde US$500 (NO es una predicción)", "",
          "Remuestreo de las operaciones OOS a la frecuencia histórica; kill switch a −25 % desde el máximo; "
          "P(nivel) = probabilidad de alcanzar el nivel antes de tocar el kill switch; t_med = mediana de años hasta alcanzarlo entre los caminos que lo alcanzan.", ""]
    g = [growth_simulation(tdf, tpy, rs, seed=3) for rs in (0.25, 0.5, 0.75, 1.0)]
    L += [pd.DataFrame(g).round(3).to_markdown(index=False), ""]
    (reports / f"04_phase8_9_{a.hypothesis}.md").write_text("\n".join(L))
    print(f"informe: {reports / f'04_phase8_9_{a.hypothesis}.md'}")


if __name__ == "__main__":
    main()
