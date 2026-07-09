"""Gestión de riesgo: lo que evita que un mal día te arruine.

Tres protecciones:
  1. Tamaño de posición basado en riesgo fijo por operación.
  2. Stop-loss y take-profit calculados con la volatilidad (ATR).
  3. Límite de pérdida diaria: si se supera, el bot deja de operar ese día.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NivelesOperacion:
    """Precios de entrada, stop-loss y take-profit de una operación."""

    entrada: float
    stop_loss: float
    take_profit: float
    cantidad: float  # unidades del activo (ej: BTC)


def calcular_niveles(
    precio_entrada: float,
    atr: float,
    equity: float,
    risk_cfg: dict,
) -> NivelesOperacion | None:
    """Calcula stop, objetivo y tamaño de posición para una compra.

    El tamaño se elige para que, si salta el stop-loss, la pérdida sea
    exactamente 'riesgo_por_operacion_pct' del capital. Así una operación
    mala nunca te hace un roto grande.

    Devuelve None si los números no son válidos (ej: ATR cero).
    """
    if atr <= 0 or precio_entrada <= 0 or equity <= 0:
        return None

    distancia_stop = risk_cfg["stop_loss_atr_mult"] * atr
    if distancia_stop <= 0:
        return None

    stop_loss = precio_entrada - distancia_stop
    take_profit = precio_entrada + risk_cfg["take_profit_atr_mult"] * atr

    # Cantidad de dinero que estamos dispuestos a perder en esta operación.
    riesgo_dinero = equity * (risk_cfg["riesgo_por_operacion_pct"] / 100.0)

    # Cantidad de activo tal que (distancia_stop * cantidad) == riesgo_dinero.
    cantidad = riesgo_dinero / distancia_stop

    # No podemos comprar más de lo que permite el capital (spot, sin margen).
    cantidad_max = equity / precio_entrada
    cantidad = min(cantidad, cantidad_max)

    if cantidad <= 0:
        return None

    return NivelesOperacion(
        entrada=precio_entrada,
        stop_loss=stop_loss,
        take_profit=take_profit,
        cantidad=cantidad,
    )


class ControlDiario:
    """Vigila la pérdida acumulada del día y corta si se pasa del límite."""

    def __init__(self, limite_perdida_diaria_pct: float):
        self.limite_pct = limite_perdida_diaria_pct
        self._fecha = None
        self._equity_inicio_dia = None

    def puede_operar(self, fecha, equity_actual: float) -> bool:
        """True si aún se puede abrir operaciones hoy."""
        if self._fecha != fecha:
            # Nuevo día: reiniciamos la referencia.
            self._fecha = fecha
            self._equity_inicio_dia = equity_actual
            return True

        perdida_pct = (
            (self._equity_inicio_dia - equity_actual)
            / self._equity_inicio_dia
            * 100.0
        )
        return perdida_pct < self.limite_pct
