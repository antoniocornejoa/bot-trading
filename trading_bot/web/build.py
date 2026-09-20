"""Construye la página autocontenida del Laboratorio Cuant (motor JS + datos embebidos).

    python -m trading_bot.web.build            # → trading_bot/web/dist/app.html
    python -m trading_bot.web.build --validate # además verifica el motor JS contra el Python (node)

La página se publica como artefacto privado en claude.ai. El motor JS (engine.js) es una
réplica del motor Python; validate.js lo comprueba operación por operación.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from ..backtesting import load_scenarios, metrics, run
from ..data import store
from ..strategies import REGISTRY

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LIMITS = {"BTCUSDT": (5, 1e-5), "ETHUSDT": (5, 1e-4), "SOLUSDT": (5, 1e-3)}


def export_data() -> dict:
    out = {}
    for s in ("BTCUSDT", "ETHUSDT", "SOLUSDT"):
        found = store.finest_available(ROOT / "data_store" / "parquet", "spot", s)
        base = store.load(found[0])
        dec = 3 if s == "SOLUSDT" else 2
        out[s] = {}
        for tf in ("4h", "1d"):
            df = store.resample(base, tf)
            out[s][tf] = [[int(ts.value // 3_600_000_000_000), round(float(o), dec), round(float(h), dec), round(float(l), dec), round(float(c), dec), int(qv)]
                          for ts, o, h, l, c, qv in zip(df.index, df.open, df.high, df.low, df.close, df.quote_volume)]
    return out


def python_cases(data: dict) -> list:
    cases = []
    for symbol, tf, strat, params, scen, risk, start in [
        ("BTCUSDT", "4h", "ma_momentum", {"n": 200, "atr_mult": 2.0, "atr_n": 14}, "base", 0.5, "2022-01-01"),
        ("ETHUSDT", "4h", "ma_momentum", {"n": 100, "atr_mult": 3.0, "atr_n": 14}, "pessimistic", 1.0, "2019-06-01"),
        ("SOLUSDT", "4h", "donchian_trend", {"n_entry": 55, "n_exit": 20, "atr_n": 14, "atr_mult": 3.0, "ema_filter": 200}, "base", 1.0, "2021-03-01"),
        ("BTCUSDT", "1d", "donchian_trend", {"n_entry": 20, "n_exit": 10, "atr_n": 14, "atr_mult": 2.0, "ema_filter": 100}, "optimistic", 2.0, "2018-01-01"),
        ("ETHUSDT", "1d", "ma_momentum", {"n": 150, "atr_mult": 4.0, "atr_n": 14}, "base", 0.5, "2020-01-01"),
    ]:
        rows = data[symbol][tf]
        df = pd.DataFrame(rows, columns=["ts", "open", "high", "low", "close", "quote_volume"])
        df.index = pd.to_datetime(df["ts"] * 3600, unit="s", utc=True); df["volume"] = df["quote_volume"] / df["close"]
        sig = REGISTRY[strat](**params).generate(df)
        start_i = int(np.argmax(df.index >= pd.Timestamp(start, tz="UTC")))
        res = run(df.iloc[start_i:], sig.iloc[start_i:], load_scenarios()[scen], initial_capital=500, risk_pct=risk,
                  min_notional=LIMITS[symbol][0], lot_step=LIMITS[symbol][1])
        m = metrics.compute(res, store.BARS_PER_YEAR[tf])
        cases.append({"symbol": symbol, "tf": tf, "strategy": strat, "params": params, "scenario": scen, "risk": risk,
                      "start_ms": int(pd.Timestamp(start, tz="UTC").value // 1e6), "expR": float(m["expectancy_R"]) if res.trades else 0.0,
                      "final_equity": float(res.equity.iloc[-1]),
                      "trades": [[int(t.entry_time.value // 1e6), int(t.exit_time.value // 1e6), t.reason, round(float(t.pnl), 6), round(float(t.r_multiple), 6)] for t in res.trades]})
    return cases


def main(argv=None):
    p = argparse.ArgumentParser(); p.add_argument("--validate", action="store_true"); a = p.parse_args(argv)
    dist = HERE / "dist"; dist.mkdir(exist_ok=True)
    data = export_data()
    (dist / "data.json").write_text(json.dumps(data, separators=(",", ":")))
    if a.validate:
        (dist / "py_cases.json").write_text(json.dumps(python_cases(data)))
        for f in ("engine.js", "validate.js"):
            (dist / f).write_text((HERE / f).read_text())
        subprocess.run(["node", str(dist / "validate.js")], check=True)
    html = (HERE / "app.tpl.html").read_text().replace("/*__ENGINE__*/", (HERE / "engine.js").read_text().replace("</script>", "<\\/script>")) \
        .replace("/*__DATA__*/", (dist / "data.json").read_text())
    (dist / "app.html").write_text(html)
    print(f"{dist / 'app.html'}: {len(html)/1e6:.2f} MB")


if __name__ == "__main__":
    main()
