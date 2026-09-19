"""Contraste de calidad con Kraken (REST público, sin clave).

La API devuelve como máximo 720 velas por llamada; a diario son ~2 años, suficiente
para cruzar cierres con Binance. Nota: Kraken cotiza contra USD y Binance contra USDT,
así que una desviación estable de unas décimas es el basis USDT/USD, no un error.

    python -m trading_bot.data.kraken --symbols BTCUSDT ETHUSDT SOLUSDT
"""
from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

import pandas as pd
import yaml

from . import store, validation

PAIRS = {"BTCUSDT": "XBTUSD", "ETHUSDT": "ETHUSD", "SOLUSDT": "SOLUSD"}


def fetch_daily(symbol: str) -> pd.DataFrame:
    pair = PAIRS[symbol]
    url = f"https://api.kraken.com/0/public/OHLC?pair={pair}&interval=1440"
    with urllib.request.urlopen(url, timeout=60) as r:
        payload = json.load(r)
    if payload.get("error"):
        raise RuntimeError(payload["error"])
    key = [k for k in payload["result"] if k != "last"][0]
    rows = payload["result"][key]
    df = pd.DataFrame(rows, columns=["time", "open", "high", "low", "close", "vwap", "volume", "count"])
    df.index = pd.to_datetime(df["time"].astype(int), unit="s", utc=True)
    df.index.name = "timestamp"
    return df[["open", "high", "low", "close", "volume"]].astype(float)


def main(argv=None) -> None:
    cfg = yaml.safe_load(open(Path(__file__).resolve().parents[1] / "config" / "research.yaml"))
    p = argparse.ArgumentParser()
    p.add_argument("--symbols", nargs="+", default=cfg["universe"]["spot"])
    p.add_argument("--root", default=".")
    a = p.parse_args(argv)
    pq_root = Path(a.root) / cfg["paths"]["parquet"]
    for s in a.symbols:
        kr = fetch_daily(s)
        store.save(kr, store.parquet_path(pq_root, "kraken", s, "klines_1d"))
        found = store.finest_available(pq_root, "spot", s)
        if found is None:
            print(f"{s}: Kraken guardado; falta Binance para cruzar")
            continue
        bn = store.resample(store.load(found[0]), "1d")
        dev = validation.cross_check(bn, kr, tol_pct=0.5)
        print(f"{s}: {len(dev)} días con desviación > 0.5 % entre Binance y Kraken")
        if len(dev):
            print(dev.tail(10))


if __name__ == "__main__":
    main()
