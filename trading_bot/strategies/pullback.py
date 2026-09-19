"""Familia G · Pullback en tendencia.

Hipótesis económica: en una tendencia alcista confirmada, los retrocesos de corto plazo
son sobre-reacciones de participantes de corto plazo; comprar el retroceso combina la
prima de tendencia (A) con la de reversión a corto (C) y evita comprar en extensión.

Entrada: EMA(fast) > EMA(slow), cierre > EMA(slow), y RSI(rsi_n) < rsi_entry.
Salida:  objetivo tp_atr·ATR, stop stop_atr·ATR, o RSI(rsi_n) > rsi_exit (media alcanzada),
         o pérdida de tendencia (EMA fast < EMA slow).
Falla cuando el retroceso es el inicio de un cambio de tendencia (stop) y en rangos
con tendencia falsa por filtro lento.
"""
from __future__ import annotations

import pandas as pd

from ..features import ta
from .base import Strategy


class TrendPullback(Strategy):
    name = "trend_pullback"

    @classmethod
    def default_params(cls) -> dict:
        return {"ema_fast": 20, "ema_slow": 100, "rsi_n": 3, "rsi_entry": 25.0, "rsi_exit": 70.0,
                "atr_n": 14, "stop_atr": 2.0, "tp_atr": 3.0}

    def generate(self, df: pd.DataFrame) -> pd.DataFrame:
        p = self.params
        s = self.empty_signals(df.index)
        ef = ta.ema(df["close"], p["ema_fast"])
        es = ta.ema(df["close"], p["ema_slow"])
        r = ta.rsi(df["close"], p["rsi_n"])
        a = ta.atr(df, p["atr_n"])
        trend = (ef > es) & (df["close"] > es)
        s["entry"] = trend & (r < p["rsi_entry"])
        s["exit"] = (r > p["rsi_exit"]) | (ef < es)
        s["stop_dist"] = p["stop_atr"] * a
        s["tp_dist"] = p["tp_atr"] * a
        s.loc[a.isna() | es.isna() | r.isna(), ["entry"]] = False
        return s
