"""Velas sintéticas deterministas para tests y para desarrollar sin acceso a los exchanges.

NO son datos reales y no sirven para evaluar ninguna estrategia: solo para verificar
que el código hace lo que dice. Incluyen un tramo de tendencia, uno lateral y uno de
alta volatilidad para que los tests cubran los tres regímenes.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def make_1m(n_days: int = 120, seed: int = 7, start: str = "2024-01-01", price0: float = 40_000.0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n = n_days * 1440
    tercio = n // 3
    drift = np.concatenate([np.full(tercio, 2e-6), np.zeros(tercio), np.full(n - 2 * tercio, -1e-6)])
    vol = np.concatenate([np.full(tercio, 3e-4), np.full(tercio, 2e-4), np.full(n - 2 * tercio, 8e-4)])
    ret = rng.normal(drift, vol)
    close = price0 * np.exp(np.cumsum(ret))
    open_ = np.concatenate([[price0], close[:-1]])
    wick = np.abs(rng.normal(0, vol)) * close
    high = np.maximum(open_, close) + wick
    low = np.minimum(open_, close) - wick
    volume = rng.lognormal(0, 0.5, n)
    idx = pd.date_range(start, periods=n, freq="1min", tz="UTC")
    return pd.DataFrame({
        "open": open_, "high": high, "low": low, "close": close, "volume": volume,
        "quote_volume": volume * close, "trades": rng.integers(1, 200, n),
    }, index=idx)
