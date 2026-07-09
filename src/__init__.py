"""Bot de trading de cripto para Binance (spot, solo compras).

Módulos:
  config    -> carga config.yaml y las claves del .env
  data      -> descarga datos de precios (velas OHLCV) vía ccxt
  indicators-> cálculo de EMA, RSI y ATR
  strategy  -> genera señales de compra/venta a partir de los indicadores
  risk      -> tamaño de posición, stop-loss, límite de pérdida diaria
  backtest  -> simula la estrategia sobre datos históricos con comisiones
  broker    -> ejecuta órdenes reales o de testnet vía ccxt
  bot       -> bucle en vivo (paper/live)
"""
