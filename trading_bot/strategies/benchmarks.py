"""Benchmarks obligatorios (§6.8 del marco). No son candidatas: definen la referencia.

- BuyAndHold: entra en la primera barra y no sale (stop enorme, sin objetivo).
- MA200Momentum: largo si cierre > SMA(n), plano si no.
- RSI2MeanReversion: reversión clásica (RSI(2) < 10 con cierre > SMA(200); sale con RSI(2) > 70).
- RandomSameFrequency: entradas aleatorias con la misma probabilidad por barra y el mismo
  stop/objetivo/holding que la candidata; 1000 réplicas dan la distribución nula.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..features import ta
from .base import Strategy


class BuyAndHold(Strategy):
    name = "buy_and_hold"

    @classmethod
    def default_params(cls):
        return {}

    def generate(self, df):
        s = self.empty_signals(df.index)
        s.iloc[0, s.columns.get_loc("entry")] = True
        s["stop_dist"] = df["close"] * 0.999  # stop prácticamente en cero: nunca salta
        return s


class MA200Momentum(Strategy):
    """Largo si cierre > SMA(n); salida si cierre < SMA(n) o stop de volatilidad. Con los
    valores por defecto es el benchmark; con rejilla es la hipótesis H-A2 (familia A)."""
    name = "ma_momentum"

    @classmethod
    def default_params(cls):
        return {"n": 200, "atr_n": 14, "atr_mult": 3.0}

    def generate(self, df):
        p = self.params
        s = self.empty_signals(df.index)
        ma = ta.sma(df["close"], p["n"])
        a = ta.atr(df, p["atr_n"])
        s["entry"] = (df["close"] > ma) & ma.notna() & a.notna()
        s["exit"] = df["close"] < ma
        s["stop_dist"] = p["atr_mult"] * a
        return s


class RSI2MeanReversion(Strategy):
    name = "rsi2_meanrev"

    @classmethod
    def default_params(cls):
        return {"rsi_n": 2, "rsi_entry": 10.0, "rsi_exit": 70.0, "ma_n": 200, "atr_n": 14, "stop_atr": 3.0}

    def generate(self, df):
        p = self.params
        s = self.empty_signals(df.index)
        r = ta.rsi(df["close"], p["rsi_n"])
        ma = ta.sma(df["close"], p["ma_n"])
        a = ta.atr(df, p["atr_n"])
        s["entry"] = (r < p["rsi_entry"]) & (df["close"] > ma) & a.notna()
        s["exit"] = r > p["rsi_exit"]
        s["stop_dist"] = p["stop_atr"] * a
        return s


class RandomSameFrequency(Strategy):
    """Entradas aleatorias con probabilidad `p_entry` por barra; sale a `hold` barras o por stop/objetivo."""
    name = "random"

    @classmethod
    def default_params(cls):
        return {"p_entry": 0.02, "hold": 10, "atr_n": 14, "stop_atr": 2.0, "tp_atr": np.nan, "seed": 0}

    def generate(self, df):
        p = self.params
        rng = np.random.default_rng(p["seed"])
        s = self.empty_signals(df.index)
        a = ta.atr(df, p["atr_n"])
        entry = rng.random(len(df)) < p["p_entry"]
        s["entry"] = entry & a.notna().to_numpy()
        # salida `hold` barras después de cada entrada (causal: solo depende de entradas pasadas)
        ex = np.zeros(len(df), bool)
        idx = np.flatnonzero(entry) + p["hold"]
        ex[idx[idx < len(df)]] = True
        s["exit"] = ex
        s["stop_dist"] = p["stop_atr"] * a
        s["tp_dist"] = p["tp_atr"] * a if not np.isnan(p["tp_atr"]) else np.nan
        return s

    @classmethod
    def like(cls, trades_df: pd.DataFrame, n_bars: int, seed: int = 0, **kw):
        """Réplica con la misma frecuencia y holding medio que una candidata."""
        n = len(trades_df)
        hold = int(round(trades_df["bars_held"].mean())) if n else 10
        return cls(p_entry=n / max(n_bars, 1), hold=max(hold, 1), seed=seed, **kw)
