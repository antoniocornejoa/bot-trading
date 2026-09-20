"""Fase 6 · Walk-forward sobre TRAIN+VALIDATION (el TEST sigue cerrado salvo --open-test).

    python -m trading_bot.research.run_phase6 --hypotheses H-A1 H-A2 --timeframes 4h

Para cada hipótesis, símbolo y timeframe:
  - Walk-forward rodante (train_years de entrenamiento, test_months de evaluación) dentro del
    80 % inicial del histórico. En cada ventana se elige la configuración por t-stat en train
    y se evalúa en la ventana siguiente.
  - Se agrupan las operaciones OOS de todos los símbolos: expectancy, t-stat, PF, DSR.
  - Desglose por régimen de cada ventana (bull/bear/lateral por pendiente de MA200 del activo;
    vol alta/baja por percentil de volatilidad realizada) y por año.
  - Distribución nula: N réplicas aleatorias con la misma frecuencia y holding en las mismas
    ventanas OOS (misma exposición a la deriva del activo).
Escribe research/reports/03_phase6_walkforward.md.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from ..backtesting import dsr, grid, load_scenarios, metrics, walkforward
from ..backtesting.engine import BacktestResult
from ..data import store
from ..features import ta
from ..strategies import REGISTRY, RandomSameFrequency

ROOT = Path(__file__).resolve().parents[1]


def regime_labels(df: pd.DataFrame, bars_per_year: int) -> pd.DataFrame:
    ma = df["close"].rolling(200).mean()
    slope = ma.pct_change(20)
    trend = pd.Series(np.where(slope > 0.01, "bull", np.where(slope < -0.01, "bear", "lateral")), index=df.index)
    rv = ta.realized_vol(df["close"], 30, bars_per_year)
    pct = rv.rolling(1000, min_periods=200).rank(pct=True)
    vol = pd.Series(np.where(pct > 0.7, "vol_alta", np.where(pct < 0.3, "vol_baja", "vol_media")), index=df.index)
    return pd.DataFrame({"trend": trend, "vol": vol})


def run_symbol(S, h: dict, df: pd.DataFrame, tf: str, costs, engine_kw: dict, train_bars: int, test_bars: int,
               end: int, min_trades: int) -> walkforward.WFResult:
    return walkforward.walk_forward(S, h["grid"], df.iloc[:end], costs, store.BARS_PER_YEAR[tf],
                                    train_bars=train_bars, test_bars=test_bars, anchored=False,
                                    objective="t_stat", min_trades=min_trades, **engine_kw)


def random_null(df: pd.DataFrame, wf: walkforward.WFResult, tf: str, costs, engine_kw: dict, n: int, seed0: int) -> pd.DataFrame:
    """Réplicas aleatorias en las MISMAS ventanas OOS, con la frecuencia y holding de la candidata."""
    tdf = pd.DataFrame([asdict(t) for t in wf.trades]) if wf.trades else pd.DataFrame()
    n_bars = sum(w.test.stop - w.test.start for w in wf.windows)
    rows = []
    bpy = store.BARS_PER_YEAR[tf]
    for k in range(n):
        R = RandomSameFrequency.like(tdf, n_bars, seed=seed0 + k, stop_atr=2.0)
        trades, parts, eq = [], [], engine_kw.get("initial_capital", 500.0)
        for w in wf.windows:
            res = grid.run_config(RandomSameFrequency, R.params, df, costs, w.test, **{**engine_kw, "initial_capital": eq})
            trades += res.trades; parts.append(res.equity); eq = float(res.equity.iloc[-1])
        m = metrics.compute(BacktestResult(trades, pd.concat(parts), engine_kw.get("initial_capital", 500.0), costs.name), bpy)
        rows.append({"expectancy_R": m["expectancy_R"], "total_return_pct": m["total_return_pct"], "sharpe": m["sharpe"], "trades": m["trades"]})
    return pd.DataFrame(rows)


def trial_sharpe_variance(hyps: dict, data: dict, tf: str, costs, cfg: dict, end_frac: float = 0.8) -> dict:
    """Sharpe por operación de TODAS las configuraciones registradas y ejecutables (train+validation
    agrupando símbolos), agrupado por hipótesis. Entrada del Deflated Sharpe.

    Devuelve {"all": (var, n), "<hid>": (var, n), ...}. La varianza "all" mezcla familias con
    Sharpe real distinto (p. ej. pullback negativo y tendencia positivo), lo que infla la varianza
    y penaliza de más; la varianza dentro de la familia refleja mejor el ruido de selección."""
    srs = {}
    for hid, h in hyps.items():
        if h.get("role") == "benchmark" or h["strategy"] not in REGISTRY or "grid" not in h or h["strategy"] == "filter_layer":
            continue
        S = REGISTRY[h["strategy"]]
        for params in grid.expand_grid(h["grid"]):
            fr = []
            for sym, base in data.items():
                df = store.resample(base, tf)
                end = grid.split_by_time(df)["validation"].stop
                ekw = {"initial_capital": 500.0, "risk_pct": 1.0, **cfg["exchange_limits"].get(sym, {})}
                res = grid.run_config(S, params, df, costs, slice(0, end), **ekw)
                t = res.trades_df()
                if len(t):
                    fr.append((t["pnl"] / t["equity_at_entry"]).to_numpy(float))
            if fr:
                r = np.concatenate(fr)
                if len(r) > 2 and r.std(ddof=1) > 0:
                    srs.setdefault(hid, []).append(r.mean() / r.std(ddof=1))
    out = {"all": np.concatenate([np.array(v) for v in srs.values()]) if srs else np.array([])}
    out.update({k: np.array(v) for k, v in srs.items()})
    return {k: ((float(np.var(v, ddof=1)) if len(v) > 1 else 0.0), len(v)) for k, v in out.items()}


def monthly_t(tdf: pd.DataFrame) -> tuple[float, float, int]:
    """t-stat sobre retornos MENSUALES agregados de todos los símbolos (unidad de independencia
    más honesta que la operación: BTC y ETH correlacionan 0,8 y operan a la vez)."""
    from scipy import stats
    m = (tdf["pnl"] / tdf["equity_at_entry"]).groupby(pd.to_datetime(tdf["exit_time"]).dt.tz_localize(None).dt.to_period("M")).sum()
    if len(m) < 3:
        return np.nan, np.nan, len(m)
    t, p = stats.ttest_1samp(m.to_numpy(float), 0)
    return float(t), float(p), len(m)


def main(argv=None) -> None:
    cfg = yaml.safe_load(open(ROOT / "config" / "research.yaml"))
    hyp = yaml.safe_load(open(ROOT / "research" / "hypotheses.yaml"))
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--hypotheses", nargs="+", default=["H-A1", "H-A2"])
    p.add_argument("--symbols", nargs="+", default=hyp["meta"]["universe"])
    p.add_argument("--timeframes", nargs="+", default=["4h"])
    p.add_argument("--train-years", type=float, default=2.0)
    p.add_argument("--test-months", type=int, default=6)
    p.add_argument("--n-random", type=int, default=100)
    p.add_argument("--open-test", action="store_true", help="usa TODO el histórico (abre el test). Solo una vez.")
    p.add_argument("--scenario", default=None, help="optimistic | base | pessimistic (por defecto el del registro)")
    a = p.parse_args(argv)
    costs = load_scenarios()[a.scenario or hyp["meta"]["cost_scenario_for_decisions"]]
    pq_root = Path(a.root) / cfg["paths"]["parquet"]
    hyps = {h["id"]: h for h in hyp["hypotheses"]}
    M = hyp["multiple_testing"]["M_registered"]

    L = ["# Fase 6 · Walk-forward", "",
         f"Escenario **{costs.name}**. Ventanas rodantes: {a.train_years} años de entrenamiento, {a.test_months} meses de evaluación. "
         + ("**TEST ABIERTO: se usa todo el histórico.**" if a.open_test else "Solo train+validation (80 % inicial): **el test sigue cerrado**."), ""]
    data = {}
    for sym in a.symbols:
        found = store.finest_available(pq_root, "spot", sym)
        if found:
            data[sym] = store.load(found[0])
    out_dir = Path(a.root) / cfg["paths"]["reports"]; out_dir.mkdir(parents=True, exist_ok=True)
    trial_var = {tf: trial_sharpe_variance(hyps, data, tf, costs, cfg) for tf in a.timeframes}
    for tf in a.timeframes:
        bpy = store.BARS_PER_YEAR[tf]
        train_bars, test_bars = int(a.train_years * bpy), int(a.test_months * bpy / 12)
        for hid in a.hypotheses:
            h = hyps[hid]; S = REGISTRY[h["strategy"]]
            L += [f"## {hid} · {h['strategy']} · {tf}", ""]
            pooled_trades, per_symbol, window_rows, null_rows = [], {}, [], []
            for sym, base in data.items():
                df = store.resample(base, tf)
                end = len(df) if a.open_test else grid.split_by_time(df)["validation"].stop
                ekw = {"initial_capital": 500.0, "risk_pct": 1.0, **cfg["exchange_limits"].get(sym, {})}
                wf = run_symbol(S, h, df, tf, costs, ekw, train_bars, test_bars, end, min_trades=20)
                per_symbol[sym] = wf
                pooled_trades += wf.trades
                reg = regime_labels(df, bpy)
                for w in wf.windows:
                    seg = reg.iloc[w.test]
                    window_rows.append({"symbol": sym, "start": df.index[w.test.start].date(), "end": df.index[w.test.stop - 1].date(),
                                        "params": w.params, "trades": w.test_metrics.get("trades", 0),
                                        "expectancy_R": w.test_metrics.get("expectancy_R", np.nan), "pnl_usd": w.test_pnl,
                                        "trend": seg["trend"].mode().iat[0], "vol": seg["vol"].mode().iat[0],
                                        "bh_ret_pct": 100 * (df["close"].iloc[w.test.stop - 1] / df["close"].iloc[w.test.start] - 1)})
                nr = random_null(df, wf, tf, costs, ekw, a.n_random, seed0=1000)
                nr["symbol"] = sym; null_rows.append(nr)
                s = wf.summary
                L += [f"### {sym}: {s['windows']} ventanas, {s['oos_trades']} operaciones OOS",
                      f"- expectancy OOS {s['oos_expectancy_R']:.3f} R, t = {s['oos_t_stat']:.2f}, PF {s['oos_profit_factor']:.2f}, Sharpe {s['oos_sharpe']:.2f}, DD {s['oos_max_dd_pct']:.1f} %",
                      f"- ventanas positivas {s['pct_windows_positive']:.0f} %, eficiencia WF (mediana) {s['wf_efficiency']:.2f}, ventana dominante {s['max_window_share_pct']:.0f} % del beneficio",
                      f"- nulo aleatorio ({a.n_random} réplicas, mismas ventanas): expectancy p50 {nr['expectancy_R'].median():.3f}, p95 {nr['expectancy_R'].quantile(0.95):.3f}; Sharpe p95 {nr['sharpe'].quantile(0.95):.2f}", ""]
            # agregado
            if pooled_trades:
                tdf = pd.DataFrame([asdict(t) for t in pooled_trades])
                tdf.to_csv(out_dir / f"trades_{hid}_{tf}_{costs.name}{'_TEST' if a.open_test else ''}.csv", index=False)
                R = tdf["r_multiple"].to_numpy(float)
                from scipy import stats
                t, pval = stats.ttest_1samp(R, 0)
                tm, pm, nm = monthly_t(tdf)
                r_frac = (tdf["pnl"] / tdf["equity_at_entry"]).to_numpy(float)
                tv = trial_var.get(tf, {})
                var_all, n_all = tv.get("all", (0.0, 0))
                var_fam, n_fam = tv.get(hid, (0.0, 0))
                n_families = sum(1 for k in tv if k != "all")
                d = dsr.deflated_sharpe(r_frac, n_trials=M, var_sharpe_trials=var_all)
                d_fam = dsr.deflated_sharpe(r_frac, n_trials=M, var_sharpe_trials=var_fam)
                d_clu = dsr.deflated_sharpe(r_frac, n_trials=max(n_families, 1), var_sharpe_trials=var_fam)
                wins = R > 0
                gp, gl = tdf.loc[tdf.pnl > 0, "pnl"].sum(), -tdf.loc[tdf.pnl < 0, "pnl"].sum()
                L += ["### Agregado (todos los símbolos)",
                      f"- {len(R)} operaciones OOS | win rate {100*wins.mean():.1f} % | avg win {R[wins].mean():.2f} R | avg loss {R[~wins].mean():.2f} R | payoff {abs(R[wins].mean()/R[~wins].mean()):.2f}",
                      f"- expectancy {R.mean():.3f} R | t = {t:.2f} (p = {pval:.4f}) | PF {gp/gl if gl else float('inf'):.2f} | coste/beneficio bruto {(tdf.fees.sum()+tdf.slippage_cost.sum())/max(tdf.pnl.sum()+tdf.fees.sum()+tdf.slippage_cost.sum(),1e-9):.2f}",
                      f"- t sobre retornos mensuales agregados: t = {tm:.2f} (p = {pm:.4f}, {nm} meses)",
                      f"- Deflated Sharpe, SR por operación {d['sr']:.3f}. Tres supuestos sobre el número y la varianza de las pruebas:",
                      f"  - conservador: M = {M}, varianza entre las {n_all} configuraciones de todas las familias = {var_all:.5f} → SR0 {d['sr0']:.3f}, **DSR = {d['dsr']:.3f}**",
                      f"  - dentro de familia: M = {M}, varianza entre las {n_fam} configuraciones de {hid} = {var_fam:.5f} → SR0 {d_fam['sr0']:.3f}, **DSR = {d_fam['dsr']:.3f}**",
                      f"  - por familias: M = {n_families} familias, varianza dentro de {hid} → SR0 {d_clu['sr0']:.3f}, **DSR = {d_clu['dsr']:.3f}**", ""]
                wr = pd.DataFrame(window_rows)
                L += ["### Por régimen (ventanas OOS)", "", wr.groupby("trend").agg(ventanas=("trades", "size"), ops=("trades", "sum"), exp_R=("expectancy_R", "mean"),
                      pnl_usd=("pnl_usd", "sum"), bh_ret_pct=("bh_ret_pct", "mean")).round(3).to_markdown(), "",
                      wr.groupby("vol").agg(ventanas=("trades", "size"), ops=("trades", "sum"), exp_R=("expectancy_R", "mean"), pnl_usd=("pnl_usd", "sum")).round(3).to_markdown(), ""]
                wr["year"] = pd.to_datetime(wr["start"]).dt.year
                L += ["### Por año", "", wr.groupby("year").agg(ventanas=("trades", "size"), ops=("trades", "sum"), exp_R=("expectancy_R", "mean"),
                      pnl_usd=("pnl_usd", "sum"), bh_ret_pct=("bh_ret_pct", "mean")).round(3).to_markdown(), ""]
                L += ["### Ventanas", "", wr.drop(columns=["year"]).round(3).to_markdown(index=False), ""]
                nn = pd.concat(null_rows)
                L += [f"### Nulo aleatorio agregado: expectancy p50 {nn['expectancy_R'].median():.3f}, p95 {nn['expectancy_R'].quantile(0.95):.3f}", ""]
            else:
                L += ["Sin operaciones OOS.", ""]
    out = out_dir
    name = f"03_phase6_walkforward_{costs.name}{'_TEST' if a.open_test else ''}.md"
    (out / name).write_text("\n".join(L))
    log_path = out / "executions.yaml"
    log = yaml.safe_load(open(log_path)) if log_path.exists() else {"executions": []}
    log["executions"].append({"phase": 6, "date": str(pd.Timestamp.now("UTC").date()), "hypotheses": a.hypotheses,
                              "symbols": list(data), "timeframes": a.timeframes, "test_used": bool(a.open_test)})
    yaml.safe_dump(log, open(log_path, "w"), sort_keys=False, allow_unicode=True)
    print(f"informe: {out / name}")


if __name__ == "__main__":
    main()
