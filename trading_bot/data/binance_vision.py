"""Descarga masiva de histórico desde data.binance.vision (gratis, sin clave).

Se ejecuta en el equipo del propietario (esta sesión de desarrollo no tiene acceso
de red a Binance). Uso:

    python -m trading_bot.data.binance_vision --symbols BTCUSDT ETHUSDT SOLUSDT \
        --start 2017-08 --markets spot futures funding

Descarga ZIP mensuales de velas (spot y perpetuos USDT-M) y de funding, los guarda tal
cual en data_store/raw y produce un Parquet limpio por símbolo en
data_store/parquet/<mercado>/<SYMBOL>_klines_<intervalo>.parquet, junto con un informe
de validación y la huella (hash) del dataset.

`--intervals 1m` (por defecto) es la base ideal pero pesa 2-3 GB; `--intervals 15m 1h 4h 1d`
descarga directamente los timeframes de investigación (decenas de MB) y es lo que usa el
workflow de GitHub Actions. El resto del código trabaja con el intervalo más fino disponible.

Los meses que no existen (símbolo aún no listado) devuelven 404 y se saltan.
"""
from __future__ import annotations

import argparse
import io
import sys
import time
import urllib.error
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

import pandas as pd
import yaml

from . import store, validation

BASE = "https://data.binance.vision/data"
KLINE_COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time",
              "quote_volume", "trades", "taker_buy_base", "taker_buy_quote", "ignore"]


def _url(market: str, symbol: str, ym: str, interval: str = "1m") -> str:
    if market == "spot":
        return f"{BASE}/spot/monthly/klines/{symbol}/{interval}/{symbol}-{interval}-{ym}.zip"
    if market == "futures":
        return f"{BASE}/futures/um/monthly/klines/{symbol}/{interval}/{symbol}-{interval}-{ym}.zip"
    if market == "funding":
        return f"{BASE}/futures/um/monthly/fundingRate/{symbol}/{symbol}-fundingRate-{ym}.zip"
    raise ValueError(market)


def _months(start: str, end: str | None = None) -> list[str]:
    y, m = map(int, start.split("-"))
    hoy = date.today()
    if end:
        ey, em = map(int, end.split("-"))
    else:  # último mes completo
        ey, em = (hoy.year, hoy.month - 1) if hoy.month > 1 else (hoy.year - 1, 12)
    out = []
    while (y, m) <= (ey, em):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return out


def _fetch(url: str, dest: Path, retries: int = 4) -> bytes | None:
    if dest.exists():
        return dest.read_bytes()
    for i in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data = r.read()
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            return data
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(2 ** i)
        except (urllib.error.URLError, TimeoutError):
            time.sleep(2 ** i)
    print(f"  [aviso] no se pudo descargar {url}", file=sys.stderr)
    return None


def _to_utc(ts: pd.Series) -> pd.DatetimeIndex:
    """Binance usa milisegundos hasta 2024 y microsegundos en ficheros de 2025+."""
    ts = pd.to_numeric(ts, errors="coerce")
    unit = "us" if ts.iloc[0] > 1e14 else "ms"
    return pd.to_datetime(ts, unit=unit, utc=True)


def parse_klines_zip(data: bytes) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        raw = z.read(z.namelist()[0])
    df = pd.read_csv(io.BytesIO(raw), header=None, names=KLINE_COLS)
    if isinstance(df.iloc[0, 0], str) and not df.iloc[0, 0].lstrip("-").isdigit():
        df = df.iloc[1:]  # algunos ficheros recientes traen cabecera
    df.index = _to_utc(df["open_time"])
    df.index.name = "timestamp"
    out = df[["open", "high", "low", "close", "volume", "quote_volume", "trades"]].astype(float)
    out["trades"] = out["trades"].astype(int)
    return out


def parse_funding_zip(data: bytes) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        raw = z.read(z.namelist()[0])
    df = pd.read_csv(io.BytesIO(raw))
    df.columns = [c.strip().lower() for c in df.columns]
    tcol = "calc_time" if "calc_time" in df.columns else df.columns[0]
    rcol = "last_funding_rate" if "last_funding_rate" in df.columns else df.columns[-1]
    out = pd.DataFrame({"funding_rate": pd.to_numeric(df[rcol], errors="coerce").values},
                       index=_to_utc(df[tcol]))
    out.index.name = "timestamp"
    return out.dropna()


def download_symbol(market: str, symbol: str, months: list[str], raw_root: Path, pq_root: Path,
                    interval: str = "1m") -> None:
    frames = []
    for ym in months:
        url = _url(market, symbol, ym, interval)
        dest = raw_root / market / symbol / Path(url).name
        data = _fetch(url, dest)
        if data is None:
            continue
        frames.append(parse_funding_zip(data) if market == "funding" else parse_klines_zip(data))
        print(f"  {market} {symbol} {ym}: {len(frames[-1]):,} filas")
    if not frames:
        print(f"  {market} {symbol}: sin datos")
        return
    df = validation.clean(pd.concat(frames))
    kind = "funding" if market == "funding" else f"klines_{interval}"
    path = store.parquet_path(pq_root, market, symbol, kind)
    h = store.save(df, path)
    print(f"  -> {path}  hash={h}")
    if market != "funding":
        rep = validation.validate(df, freq=store._PANDAS_FREQ[interval])
        (path.with_suffix(".validation.md")).write_text(
            f"# Validación {market} {symbol}\n\nhash: `{h}`\n\n{rep.to_markdown()}\n")
        print(rep.to_markdown())


def main(argv=None) -> None:
    cfg = yaml.safe_load(open(Path(__file__).resolve().parents[1] / "config" / "research.yaml"))
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--symbols", nargs="+", default=cfg["universe"]["spot"])
    p.add_argument("--markets", nargs="+", default=["spot"], choices=["spot", "futures", "funding"])
    p.add_argument("--intervals", nargs="+", default=["1m"], choices=list(store._PANDAS_FREQ))
    p.add_argument("--start", default=cfg["universe"]["start"], help="YYYY-MM")
    p.add_argument("--end", default=None, help="YYYY-MM (por defecto, último mes completo)")
    p.add_argument("--root", default=".", help="carpeta base del proyecto")
    a = p.parse_args(argv)
    raw_root = Path(a.root) / cfg["paths"]["raw"]
    pq_root = Path(a.root) / cfg["paths"]["parquet"]
    months = _months(a.start, a.end)
    for market in a.markets:
        for symbol in a.symbols:
            for interval in (["1m"] if market == "funding" else a.intervals):
                print(f"== {market} {symbol} {interval if market != 'funding' else ''} ({months[0]} → {months[-1]})")
                download_symbol(market, symbol, months, raw_root, pq_root, interval)


if __name__ == "__main__":
    main()
