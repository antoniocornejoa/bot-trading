"""Descarga de datos de precios (velas OHLCV) desde Binance vía ccxt."""
from __future__ import annotations

import ccxt
import pandas as pd


def crear_exchange(cfg) -> ccxt.Exchange:
    """Crea el cliente de ccxt para Binance según el modo (testnet o real)."""
    params: dict = {"enableRateLimit": True}
    if cfg.api_key and cfg.api_secret:
        params["apiKey"] = cfg.api_key
        params["secret"] = cfg.api_secret

    exchange = ccxt.binance(params)

    if cfg.use_testnet:
        # Modo sandbox: apunta a la testnet, dinero de mentira.
        exchange.set_sandbox_mode(True)

    return exchange


def descargar_velas(
    exchange: ccxt.Exchange,
    symbol: str,
    timeframe: str,
    limite: int = 2000,
) -> pd.DataFrame:
    """Descarga las últimas `limite` velas y las devuelve como DataFrame.

    Columnas: timestamp (índice), open, high, low, close, volume.
    ccxt limita a ~1000 velas por llamada, así que paginamos hacia atrás.
    """
    tf_ms = exchange.parse_timeframe(timeframe) * 1000
    por_llamada = 1000
    ahora = exchange.milliseconds()

    velas: list = []
    restantes = limite
    desde = ahora - limite * tf_ms

    while restantes > 0:
        lote = exchange.fetch_ohlcv(
            symbol, timeframe=timeframe, since=desde, limit=min(por_llamada, restantes)
        )
        if not lote:
            break
        velas.extend(lote)
        desde = lote[-1][0] + tf_ms
        restantes -= len(lote)
        if len(lote) < por_llamada:
            break

    df = pd.DataFrame(
        velas, columns=["timestamp", "open", "high", "low", "close", "volume"]
    )
    df = df.drop_duplicates("timestamp").reset_index(drop=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df = df.set_index("timestamp")
    return df
