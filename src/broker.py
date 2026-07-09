"""Ejecución de órdenes reales o de testnet vía ccxt.

En modo 'paper' apunta a la testnet de Binance (dinero de mentira).
En modo 'live' apunta a Binance real (dinero de verdad).
El código es el MISMO; solo cambia a dónde se conecta.
"""
from __future__ import annotations

import ccxt


class Broker:
    def __init__(self, exchange: ccxt.Exchange, symbol: str):
        self.exchange = exchange
        self.symbol = symbol
        self.exchange.load_markets()

    def precio_actual(self) -> float:
        """Último precio de mercado del par."""
        return float(self.exchange.fetch_ticker(self.symbol)["last"])

    def saldo_usdt(self) -> float:
        """Saldo disponible en USDT."""
        bal = self.exchange.fetch_balance()
        return float(bal.get("USDT", {}).get("free", 0.0))

    def saldo_activo(self) -> float:
        """Saldo disponible del activo base (ej: BTC en BTC/USDT)."""
        base = self.symbol.split("/")[0]
        bal = self.exchange.fetch_balance()
        return float(bal.get(base, {}).get("free", 0.0))

    def comprar_mercado(self, cantidad: float) -> dict:
        """Orden de compra a mercado. Devuelve la respuesta del exchange."""
        cantidad = float(self.exchange.amount_to_precision(self.symbol, cantidad))
        return self.exchange.create_market_buy_order(self.symbol, cantidad)

    def vender_mercado(self, cantidad: float) -> dict:
        """Orden de venta a mercado."""
        cantidad = float(self.exchange.amount_to_precision(self.symbol, cantidad))
        return self.exchange.create_market_sell_order(self.symbol, cantidad)

    def minimo_operacion_usdt(self) -> float:
        """Importe mínimo por orden que exige Binance para este par."""
        mercado = self.exchange.market(self.symbol)
        coste_min = mercado.get("limits", {}).get("cost", {}).get("min")
        return float(coste_min) if coste_min else 0.0
