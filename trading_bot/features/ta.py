"""Indicadores técnicos causales: cada valor en t usa solo datos hasta t inclusive.

Ninguna función aquí usa `center=True`, `shift(-k)` ni estadísticas globales de la
serie (media/desviación de todo el histórico), que serían fugas de información.
Cada indicador lleva una nota de por qué se incluye (justificación económica).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def ema(s: pd.Series, n: int) -> pd.Series:
    """Media exponencial: proxy de "precio de consenso reciente"; base de filtros de tendencia."""
    return s.ewm(span=n, adjust=False, min_periods=n).mean()


def sma(s: pd.Series, n: int) -> pd.Series:
    return s.rolling(n, min_periods=n).mean()


def true_range(df: pd.DataFrame) -> pd.Series:
    prev_close = df["close"].shift(1)
    return pd.concat([df["high"] - df["low"], (df["high"] - prev_close).abs(),
                      (df["low"] - prev_close).abs()], axis=1).max(axis=1)


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    """ATR de Wilder: unidad de volatilidad para stops y tamaño. Sin ella, un stop fijo en % ignora el régimen."""
    return true_range(df).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()


def rsi(s: pd.Series, n: int = 14) -> pd.Series:
    """RSI de Wilder: mide sobre-extensión reciente (sobre-reacción → reversión a corto plazo)."""
    d = s.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    rs = up / dn.replace(0, np.nan)
    out = 100 - 100 / (1 + rs)
    return out.fillna(100.0).where(up.notna(), np.nan)


def adx(df: pd.DataFrame, n: int = 14) -> pd.Series:
    """ADX: intensidad de tendencia sin dirección; separa régimen tendencial de lateral."""
    up = df["high"].diff()
    dn = -df["low"].diff()
    plus_dm = up.where((up > dn) & (up > 0), 0.0)
    minus_dm = dn.where((dn > up) & (dn > 0), 0.0)
    tr = true_range(df).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    plus_di = 100 * plus_dm.ewm(alpha=1 / n, adjust=False, min_periods=n).mean() / tr
    minus_di = 100 * minus_dm.ewm(alpha=1 / n, adjust=False, min_periods=n).mean() / tr
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return dx.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()


def donchian_high(df: pd.DataFrame, n: int) -> pd.Series:
    """Máximo de las n barras ANTERIORES (excluye la actual): nivel de ruptura conocido antes de la barra."""
    return df["high"].shift(1).rolling(n, min_periods=n).max()


def donchian_low(df: pd.DataFrame, n: int) -> pd.Series:
    return df["low"].shift(1).rolling(n, min_periods=n).min()


def realized_vol(s: pd.Series, n: int, bars_per_year: int) -> pd.Series:
    """Volatilidad realizada anualizada de los últimos n retornos logarítmicos."""
    r = np.log(s).diff()
    return r.rolling(n, min_periods=n).std() * np.sqrt(bars_per_year)


def rel_volume(v: pd.Series, n: int = 20) -> pd.Series:
    """Volumen relativo a su media reciente: participación anormal (confirmación de rupturas)."""
    return v / v.shift(1).rolling(n, min_periods=n).mean()
