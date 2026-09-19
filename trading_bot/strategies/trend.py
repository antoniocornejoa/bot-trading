"""Familia A · Trend following por ruptura de canal (Donchian) con stop de volatilidad.

Hipótesis económica: los precios incorporan la información despacio (reacción
insuficiente, flujos escalonados, herding); una ruptura de un máximo de N barras con
tendencia de fondo alcista tiene continuación esperada positiva. Se acepta un win rate
bajo (35–45 %) a cambio de payoff alto: la expectativa viene de dejar correr.

Entrada: cierre > máximo de las n_entry barras anteriores y cierre > EMA(ema_filter).
Salida:  cierre < mínimo de las n_exit barras anteriores, o stop dinámico
         (máximo cierre reciente − atr_mult·ATR), o stop inicial (atr_mult·ATR).
Sin objetivo de beneficio.
Falla en rangos prolongados (muchas pérdidas pequeñas) y con costes altos.
"""
from __future__ import annotations

import pandas as pd

from ..features import ta
from .base import Strategy


class DonchianTrend(Strategy):
    name = "donchian_trend"

    @classmethod
    def default_params(cls) -> dict:
        return {"n_entry": 55, "n_exit": 20, "atr_n": 14, "atr_mult": 3.0, "ema_filter": 200}

    def generate(self, df: pd.DataFrame) -> pd.DataFrame:
        p = self.params
        s = self.empty_signals(df.index)
        upper = ta.donchian_high(df, p["n_entry"])
        lower = ta.donchian_low(df, p["n_exit"])
        a = ta.atr(df, p["atr_n"])
        filt = ta.ema(df["close"], p["ema_filter"])
        s["entry"] = (df["close"] > upper) & (df["close"] > filt)
        s["exit"] = df["close"] < lower
        s["stop_dist"] = p["atr_mult"] * a
        s["trail"] = df["close"].rolling(p["n_exit"], min_periods=1).max() - p["atr_mult"] * a
        s.loc[a.isna() | upper.isna() | filt.isna(), ["entry"]] = False
        return s
