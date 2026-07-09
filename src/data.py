"""Descarga de datos de precios (velas OHLCV) desde exchanges vía ccxt."""
from __future__ import annotations

import numpy as np
import ccxt
import pandas as pd

# Exchanges soportados para descargar datos públicos (backtesting).
# Kraken es útil cuando Binance está bloqueado (p. ej. IPs de EE. UU.).
EXCHANGES_PUBLICOS = {
    "binance": ccxt.binance,
    "kraken": ccxt.kraken,
}


def crear_exchange_publico(nombre: str = "binance") -> ccxt.Exchange:
    """Crea un cliente ccxt de solo lectura (sin claves) para datos públicos."""
    nombre = nombre.lower()
    if nombre not in EXCHANGES_PUBLICOS:
        raise ValueError(f"Exchange no soportado: {nombre}. "
                         f"Usa uno de {list(EXCHANGES_PUBLICOS)}.")
    return EXCHANGES_PUBLICOS[nombre]({"enableRateLimit": True})


def datos_demo(n: int = 1500, seed: int = 3) -> pd.DataFrame:
    """Genera velas sintéticas deterministas (sin internet).

    Sirve para ver el panel funcionando en cualquier sitio, incluso donde los
    exchanges estén bloqueados. NO son datos reales: solo para demostración.
    """
    rng = np.random.default_rng(seed)
    retornos = rng.normal(0.0004, 0.018, n)
    precio = 30000 * np.exp(np.cumsum(retornos))
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    close = pd.Series(precio, index=idx)
    high = close * (1 + rng.uniform(0, 0.008, n))
    low = close * (1 - rng.uniform(0, 0.008, n))
    open_ = close.shift(1).fillna(close.iloc[0])
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close,
         "volume": rng.uniform(1, 100, n)}, index=idx,
    )


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
