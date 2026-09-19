"""Fase 1 · Fichas de mercado con datos reales (§1.3 del marco).

Se ejecuta en el equipo del propietario después de la descarga:

    python -m trading_bot.research.market_profile            # sobre data_store/parquet/spot
    python -m trading_bot.research.market_profile --synthetic # demo sin datos (NO concluye nada)

Produce research/reports/01_market_profile.md con, por activo y timeframe:
movimiento típico, ratio coste/movimiento por escenario, volatilidad, autocorrelación de
retornos, variance ratio, Hurst, colas, estacionalidad horaria y correlaciones cruzadas.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy import stats

from ..backtesting.costs import load_scenarios
from ..data import store, synthetic
from ..features import ta


def variance_ratio(r: np.ndarray, q: int) -> tuple[float, float]:
    """VR(q) de Lo–MacKinlay con z bajo iid. VR>1 → momentum, VR<1 → reversión."""
    n = len(r)
    mu = r.mean()
    var1 = ((r - mu) ** 2).sum() / (n - 1)
    rq = np.convolve(r, np.ones(q), "valid")
    varq = ((rq - q * mu) ** 2).sum() / (q * (n - q + 1) * (1 - q / n)) if n > q else np.nan
    vr = varq / var1 if var1 > 0 else np.nan
    z = (vr - 1) / np.sqrt(2 * (2 * q - 1) * (q - 1) / (3 * q * n))
    return float(vr), float(z)


def hurst_rs(x: np.ndarray, min_w: int = 16) -> float:
    """Exponente de Hurst por R/S sobre ventanas; 0,5 = paseo aleatorio."""
    n = len(x)
    sizes = [w for w in (16, 32, 64, 128, 256, 512, 1024) if w >= min_w and w <= n // 4]
    if len(sizes) < 3:
        return np.nan
    rs = []
    for w in sizes:
        chunks = [x[i:i + w] for i in range(0, n - w + 1, w)]
        vals = []
        for c in chunks:
            d = c - c.mean(); z = np.cumsum(d)
            s = c.std(ddof=1)
            if s > 0:
                vals.append((z.max() - z.min()) / s)
        rs.append(np.mean(vals))
    slope, _ = np.polyfit(np.log(sizes), np.log(rs), 1)
    return float(slope)


def profile_timeframe(df: pd.DataFrame, tf: str, scenarios: dict) -> dict:
    bpy = store.BARS_PER_YEAR[tf]
    r = np.log(df["close"]).diff().dropna().to_numpy()
    move = (df["close"] / df["open"] - 1).abs() * 100
    atrp = (ta.atr(df, 14) / df["close"] * 100).dropna()
    out = {"timeframe": tf, "bars": len(df), "years": round(len(df) / bpy, 2),
           "median_move_pct": float(move.median()), "median_atr_pct": float(atrp.median()),
           "rv_annual_pct": float(np.std(r, ddof=1) * np.sqrt(bpy) * 100)}
    for k, sc in scenarios.items():
        out[f"cost_ratio_{k}"] = sc.round_trip_pct() / out["median_move_pct"] if out["median_move_pct"] > 0 else np.nan
    band = 1.96 / np.sqrt(len(r))
    for lag in (1, 5, 20):
        ac = float(pd.Series(r).autocorr(lag))
        out[f"acf{lag}"] = ac
        out[f"acf{lag}_sig"] = abs(ac) > band
    for q in (2, 5, 10):
        vr, z = variance_ratio(r, q)
        out[f"vr{q}"] = vr; out[f"vr{q}_z"] = z
    out["hurst"] = hurst_rs(r)
    out["kurtosis"] = float(stats.kurtosis(r))
    out["skew"] = float(stats.skew(r))
    sig = pd.Series(r).rolling(100).std()
    out["jumps_gt4sigma_per_year"] = float(((np.abs(r) > 4 * sig.to_numpy()).sum()) / (len(r) / bpy))
    eq = df["close"] / df["close"].iloc[0]
    out["bh_max_dd_pct"] = float((eq / eq.cummax() - 1).min() * 100)
    ma = df["close"].rolling(200).mean()
    slope = ma.pct_change(20)
    out["pct_bars_bull"] = float((slope > 0.01).mean() * 100)
    out["pct_bars_bear"] = float((slope < -0.01).mean() * 100)
    return out


def hourly_seasonality(df_1h: pd.DataFrame) -> pd.DataFrame:
    r = np.log(df_1h["close"]).diff()
    g = pd.DataFrame({"r": r, "hour": df_1h.index.hour, "dow": df_1h.index.dayofweek}).dropna()
    by_hour = g.groupby("hour")["r"].std() * 100
    by_dow = g.groupby("dow")["r"].std() * 100
    return by_hour, by_dow


def render(symbol_profiles: dict, corr: pd.DataFrame | None, seasonal: dict, hashes: dict, synthetic_flag: bool) -> str:
    L = ["# Fase 1 · Fichas de mercado", ""]
    if synthetic_flag:
        L += ["> **DATOS SINTÉTICOS.** Este informe solo demuestra que el script funciona. No concluye nada sobre ningún mercado.", ""]
    L += ["Ratio coste/movimiento = coste de ida y vuelta del escenario / mediana de |cierre/apertura − 1|. "
          "Criterio del marco: candidato si < 0,25–0,30 en escenario base.", ""]
    for sym, rows in symbol_profiles.items():
        L += [f"## {sym}", f"hash dataset: `{hashes.get(sym, '?')}`", ""]
        df = pd.DataFrame(rows).set_index("timeframe")
        cols1 = ["bars", "years", "median_move_pct", "median_atr_pct", "rv_annual_pct",
                 "cost_ratio_optimistic", "cost_ratio_base", "cost_ratio_pessimistic"]
        L += ["**Coste y volatilidad**", "", df[cols1].round(3).to_markdown(), ""]
        cols2 = ["acf1", "acf1_sig", "acf5", "acf20", "vr2", "vr2_z", "vr5", "vr5_z", "vr10", "vr10_z", "hurst"]
        L += ["**Estructura de retornos** (acf con significación al 95 %; VR>1 y z>2 → momentum; VR<1 y z<−2 → reversión; Hurst 0,5 = aleatorio)", "",
              df[cols2].round(3).to_markdown(), ""]
        cols3 = ["kurtosis", "skew", "jumps_gt4sigma_per_year", "bh_max_dd_pct", "pct_bars_bull", "pct_bars_bear"]
        L += ["**Colas y régimen**", "", df[cols3].round(2).to_markdown(), ""]
        if sym in seasonal:
            bh, bd = seasonal[sym]
            L += ["**Volatilidad por hora UTC (desv. típica del retorno 1h, %)**", "",
                  bh.round(3).to_frame("std_pct").T.to_markdown(), "",
                  "**Por día de la semana (0 = lunes)**", "", bd.round(3).to_frame("std_pct").T.to_markdown(), ""]
    if corr is not None:
        L += ["## Correlación de retornos diarios", "", corr.round(2).to_markdown(), ""]
    return "\n".join(L)


def main(argv=None) -> None:
    cfg = yaml.safe_load(open(Path(__file__).resolve().parents[1] / "config" / "research.yaml"))
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--symbols", nargs="+", default=cfg["universe"]["spot"])
    p.add_argument("--synthetic", action="store_true")
    a = p.parse_args(argv)
    scenarios = load_scenarios()
    profiles, seasonal, hashes, daily = {}, {}, {}, {}
    for sym in a.symbols:
        if a.synthetic:
            df1 = synthetic.make_1m(400, seed=hash(sym) % 1000)
        else:
            path = store.parquet_path(Path(a.root) / cfg["paths"]["parquet"], "spot", sym)
            if not path.exists():
                print(f"{sym}: falta {path}; ejecuta primero trading_bot.data.binance_vision"); continue
            df1 = store.load(path)
        hashes[sym] = store.dataset_hash(df1)
        profiles[sym] = [profile_timeframe(store.resample(df1, tf), tf, scenarios) for tf in cfg["timeframes"]]
        seasonal[sym] = hourly_seasonality(store.resample(df1, "1h"))
        daily[sym] = np.log(store.resample(df1, "1d")["close"]).diff()
        print(f"{sym}: ok")
    corr = pd.DataFrame(daily).corr() if len(daily) > 1 else None
    out_dir = Path(a.root) / cfg["paths"]["reports"]; out_dir.mkdir(parents=True, exist_ok=True)
    name = "01_market_profile_SYNTHETIC.md" if a.synthetic else "01_market_profile.md"
    (out_dir / name).write_text(render(profiles, corr, seasonal, hashes, a.synthetic))
    print(f"informe: {out_dir / name}")


if __name__ == "__main__":
    main()
