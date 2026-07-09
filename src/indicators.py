"""Indicadores técnicos calculados con pandas (sin dependencias externas).

Se calculan de forma "causal": cada valor usa solo información pasada,
para que el backtest no haga trampa mirando el futuro.
"""
from __future__ import annotations

import pandas as pd


def ema(series: pd.Series, period: int) -> pd.Series:
    """Media móvil exponencial."""
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Índice de fuerza relativa (0-100). Mide sobrecompra/sobreventa."""
    delta = series.diff()
    ganancia = delta.clip(lower=0)
    perdida = -delta.clip(upper=0)

    # Media exponencial de Wilder (equivalente a alpha = 1/period).
    media_ganancia = ganancia.ewm(alpha=1 / period, adjust=False).mean()
    media_perdida = perdida.ewm(alpha=1 / period, adjust=False).mean()

    rs = media_ganancia / media_perdida.replace(0, pd.NA)
    resultado = 100 - (100 / (1 + rs))
    # Si no hubo pérdidas, el RSI es 100 (fuerza máxima).
    return resultado.fillna(100.0)


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average True Range: mide la volatilidad. Se usa para el stop-loss.

    Espera columnas 'high', 'low', 'close'.
    """
    high = df["high"]
    low = df["low"]
    close_prev = df["close"].shift(1)

    tr = pd.concat(
        [
            high - low,
            (high - close_prev).abs(),
            (low - close_prev).abs(),
        ],
        axis=1,
    ).max(axis=1)

    return tr.ewm(alpha=1 / period, adjust=False).mean()
