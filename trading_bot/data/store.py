"""Almacenamiento local de velas (Parquet) y reagrupación de timeframes.

Convención fija en todo el proyecto:
  - Índice = timestamp UTC de APERTURA de la vela.
  - Una vela solo es "conocida" en su cierre (apertura + duración). El motor de
    backtesting decide con el cierre de la vela t y ejecuta en la apertura de t+1,
    de modo que nunca usa información que no existía en el momento de decidir.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

COLUMNS = ["open", "high", "low", "close", "volume", "quote_volume", "trades"]

_PANDAS_FREQ = {"1m": "1min", "5m": "5min", "15m": "15min", "1h": "1h", "4h": "4h", "1d": "1D"}
BARS_PER_YEAR = {"1m": 525_600, "5m": 105_120, "15m": 35_040, "1h": 8_760, "4h": 2_190, "1d": 365}


def parquet_path(root: str | Path, market: str, symbol: str, kind: str = "klines_1m") -> Path:
    return Path(root) / market / f"{symbol}_{kind}.parquet"


def save(df: pd.DataFrame, path: str | Path) -> str:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = df.sort_index()
    df.to_parquet(path)
    return dataset_hash(df)


def load(path: str | Path) -> pd.DataFrame:
    df = pd.read_parquet(path)
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    return df.sort_index()


def dataset_hash(df: pd.DataFrame) -> str:
    """Huella del dataset para que cada informe diga sobre qué datos se calculó."""
    h = hashlib.sha256()
    h.update(str(df.index[0]).encode()); h.update(str(df.index[-1]).encode())
    h.update(str(len(df)).encode())
    h.update(pd.util.hash_pandas_object(df.select_dtypes("number").round(8)).values.tobytes())
    return h.hexdigest()[:16]


INTERVAL_ORDER = ["1m", "5m", "15m", "1h", "4h", "1d"]


def infer_interval(df: pd.DataFrame) -> str:
    """Intervalo base de un DataFrame de velas a partir de la mediana de sus saltos."""
    step = pd.Series(df.index[1:] - df.index[:-1]).median()
    for k, f in _PANDAS_FREQ.items():
        if pd.Timedelta(f) == step:
            return k
    raise ValueError(f"intervalo no reconocido: {step}")


def finest_available(root: str | Path, market: str, symbol: str) -> tuple[Path, str] | None:
    """Parquet de velas más fino disponible para un símbolo (1m si existe, si no 15m, ...)."""
    for k in INTERVAL_ORDER:
        path = parquet_path(root, market, symbol, f"klines_{k}")
        if path.exists():
            return path, k
    return None


def resample(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """Agrupa velas de un intervalo base en `timeframe` (mayor), etiquetando por apertura.

    Se descartan velas agregadas incompletas (menos del 90 % de las barras base), que solo
    aparecen en huecos del proveedor o en el último tramo del histórico.
    """
    base = infer_interval(df)
    if timeframe == base:
        return df.copy()
    freq = _PANDAS_FREQ[timeframe]
    if pd.Timedelta(freq) < pd.Timedelta(_PANDAS_FREQ[base]):
        raise ValueError(f"no se puede pasar de {base} a {timeframe}")
    agg = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    extra = {c: "sum" for c in ("quote_volume", "trades") if c in df.columns}
    r = df.resample(freq, label="left", closed="left")
    out = r.agg({**agg, **extra})
    barras = r["close"].count()
    esperadas = pd.Timedelta(freq) / pd.Timedelta(_PANDAS_FREQ[base])
    out = out[barras >= 0.9 * esperadas].dropna(subset=["open", "close"])
    return out
