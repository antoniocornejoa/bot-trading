"""Motor de backtesting: simula la estrategia sobre datos históricos.

Es REALISTA: aplica comisiones y slippage en cada operación, y respeta el
stop-loss, el take-profit y el límite de pérdida diaria. El objetivo no es
que salga bonito, sino que se parezca a lo que pasaría con dinero real.

Regla de oro: las decisiones se toman con el CIERRE de una vela y se
ejecutan al PRECIO DE APERTURA de la vela siguiente. Así evitamos el error
clásico de "mirar el futuro" que hace que backtests falsos parezcan mágicos.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from . import risk, strategy


@dataclass
class Operacion:
    entrada_fecha: pd.Timestamp
    entrada_precio: float
    salida_fecha: pd.Timestamp
    salida_precio: float
    cantidad: float
    pnl: float          # ganancia/pérdida en dinero, ya con comisiones
    motivo_salida: str  # 'stop', 'objetivo' o 'señal'


@dataclass
class ResultadoBacktest:
    equity_inicial: float
    equity_final: float
    operaciones: list = field(default_factory=list)
    curva_equity: pd.Series = None

    @property
    def rendimiento_pct(self) -> float:
        return (self.equity_final / self.equity_inicial - 1) * 100

    @property
    def num_operaciones(self) -> int:
        return len(self.operaciones)

    @property
    def ganadoras(self) -> int:
        return sum(1 for o in self.operaciones if o.pnl > 0)

    @property
    def tasa_acierto_pct(self) -> float:
        if not self.operaciones:
            return 0.0
        return self.ganadoras / self.num_operaciones * 100

    @property
    def max_drawdown_pct(self) -> float:
        """Mayor caída desde un pico. Mide cuánto sufrirías en la peor racha."""
        if self.curva_equity is None or self.curva_equity.empty:
            return 0.0
        pico = self.curva_equity.cummax()
        caida = (self.curva_equity - pico) / pico
        return abs(caida.min()) * 100

    @property
    def profit_factor(self) -> float:
        """Ganancias brutas / pérdidas brutas. >1 significa rentable."""
        ganancias = sum(o.pnl for o in self.operaciones if o.pnl > 0)
        perdidas = -sum(o.pnl for o in self.operaciones if o.pnl < 0)
        if perdidas == 0:
            return float("inf") if ganancias > 0 else 0.0
        return ganancias / perdidas


def ejecutar_backtest(df: pd.DataFrame, cfg) -> ResultadoBacktest:
    """Corre la simulación completa y devuelve las métricas."""
    datos = strategy.generate_signals(df, cfg.strategy)

    equity = float(cfg.risk["capital_inicial"])
    comision = cfg.costes["comision_pct"] / 100.0
    slippage = cfg.costes["slippage_pct"] / 100.0
    control = risk.ControlDiario(cfg.risk["limite_perdida_diaria_pct"])

    operaciones: list[Operacion] = []
    curva: list[tuple] = []
    posicion: dict | None = None

    filas = list(datos.itertuples())
    for i in range(len(filas) - 1):
        vela = filas[i]
        siguiente = filas[i + 1]  # aquí se ejecuta la orden (apertura siguiente)
        fecha = vela.Index.date()

        # --- Si hay posición abierta, comprobar salidas primero ---
        if posicion is not None:
            precio_salida = None
            motivo = None

            # El stop y el objetivo se comprueban con el rango de la vela actual.
            if vela.low <= posicion["stop_loss"]:
                precio_salida = posicion["stop_loss"]
                motivo = "stop"
            elif vela.high >= posicion["take_profit"]:
                precio_salida = posicion["take_profit"]
                motivo = "objetivo"
            elif vela.signal == strategy.SELL:
                precio_salida = siguiente.open * (1 - slippage)
                motivo = "señal"

            if precio_salida is not None:
                valor_salida = precio_salida * posicion["cantidad"]
                coste_salida = valor_salida * comision
                equity += valor_salida - coste_salida

                operaciones.append(
                    Operacion(
                        entrada_fecha=posicion["fecha"],
                        entrada_precio=posicion["entrada"],
                        salida_fecha=vela.Index,
                        salida_precio=precio_salida,
                        cantidad=posicion["cantidad"],
                        pnl=equity - posicion["equity_antes"],
                        motivo_salida=motivo,
                    )
                )
                posicion = None

        # --- Si no hay posición, comprobar entradas ---
        if posicion is None and vela.signal == strategy.BUY:
            if control.puede_operar(fecha, equity) and pd.notna(vela.atr):
                precio_entrada = siguiente.open * (1 + slippage)
                niveles = risk.calcular_niveles(
                    precio_entrada, vela.atr, equity, cfg.risk
                )
                if niveles is not None:
                    coste_entrada = (
                        precio_entrada * niveles.cantidad * comision
                    )
                    equity_antes = equity
                    equity -= coste_entrada  # la comisión se paga al comprar
                    posicion = {
                        "fecha": siguiente.Index,
                        "entrada": precio_entrada,
                        "stop_loss": niveles.stop_loss,
                        "take_profit": niveles.take_profit,
                        "cantidad": niveles.cantidad,
                        "equity_antes": equity_antes,
                    }

        # Valor de la cartera en cada momento (para la curva de equity).
        valor_actual = equity
        if posicion is not None:
            valor_actual = equity + posicion["cantidad"] * vela.close
        curva.append((vela.Index, valor_actual))

    # Cerrar cualquier posición abierta al final con el último precio.
    if posicion is not None:
        ultimo = filas[-1]
        precio_salida = ultimo.close * (1 - slippage)
        valor_salida = precio_salida * posicion["cantidad"]
        equity += valor_salida - valor_salida * comision
        operaciones.append(
            Operacion(
                entrada_fecha=posicion["fecha"],
                entrada_precio=posicion["entrada"],
                salida_fecha=ultimo.Index,
                salida_precio=precio_salida,
                cantidad=posicion["cantidad"],
                pnl=equity - posicion["equity_antes"],
                motivo_salida="fin",
            )
        )

    serie_equity = pd.Series(
        [v for _, v in curva], index=[t for t, _ in curva], dtype=float
    )

    return ResultadoBacktest(
        equity_inicial=float(cfg.risk["capital_inicial"]),
        equity_final=equity,
        operaciones=operaciones,
        curva_equity=serie_equity,
    )
