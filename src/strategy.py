"""Estrategia de señales técnicas: cruce de EMAs filtrado por RSI.

Regla de entrada (COMPRA):
  - La EMA rápida cruza POR ENCIMA de la EMA lenta (impulso alcista), y
  - el RSI no está sobrecomprado (por debajo de rsi_max_entry).

Regla de salida (VENTA) por señal:
  - La EMA rápida cruza POR DEBAJO de la EMA lenta (impulso bajista).

Además, la gestión de riesgo (módulo risk) añade stop-loss y take-profit,
que suelen disparar la salida antes que la señal técnica.

Solo operamos en LARGO (comprar y luego vender) porque es spot, sin
apalancamiento. Esto limita el riesgo: como mucho pierdes lo invertido.
"""
from __future__ import annotations

import pandas as pd

from . import indicators as ind

# Valores posibles de la columna 'signal'.
BUY = 1
SELL = -1
HOLD = 0


def compute_indicators(df: pd.DataFrame, strategy_cfg: dict) -> pd.DataFrame:
    """Añade columnas de EMA, RSI y ATR al DataFrame de velas."""
    out = df.copy()
    out["ema_fast"] = ind.ema(out["close"], strategy_cfg["ema_fast"])
    out["ema_slow"] = ind.ema(out["close"], strategy_cfg["ema_slow"])
    out["rsi"] = ind.rsi(out["close"], strategy_cfg["rsi_period"])
    out["atr"] = ind.atr(out, strategy_cfg["atr_period"])
    return out


def generate_signals(df: pd.DataFrame, strategy_cfg: dict) -> pd.DataFrame:
    """Genera la columna 'signal' (BUY/SELL/HOLD) para cada vela.

    Detecta el CRUCE comparando la vela actual con la anterior, así que
    la señal aparece justo en la vela donde ocurre el cambio.
    """
    out = compute_indicators(df, strategy_cfg)

    fast = out["ema_fast"]
    slow = out["ema_slow"]
    fast_prev = fast.shift(1)
    slow_prev = slow.shift(1)

    cruce_alcista = (fast_prev <= slow_prev) & (fast > slow)
    cruce_bajista = (fast_prev >= slow_prev) & (fast < slow)
    rsi_ok = out["rsi"] < strategy_cfg["rsi_max_entry"]

    out["signal"] = HOLD
    out.loc[cruce_alcista & rsi_ok, "signal"] = BUY
    out.loc[cruce_bajista, "signal"] = SELL

    # Las primeras velas no tienen indicadores fiables -> sin señal.
    warmup = max(strategy_cfg["ema_slow"], strategy_cfg["rsi_period"],
                 strategy_cfg["atr_period"])
    out.iloc[:warmup, out.columns.get_loc("signal")] = HOLD

    return out
