"""Bot en vivo: opera en tiempo real en paper (testnet) o live (real).

Bucle:
  1. Descarga las velas recientes.
  2. Calcula indicadores y señales.
  3. Si no hay posición y hay señal de COMPRA -> compra con tamaño según riesgo.
  4. Si hay posición -> vigila stop-loss, take-profit y señal de venta.
  5. Espera y repite.

La posición se guarda en memoria. Si paras el bot con una posición abierta,
al reiniciar la detecta por el saldo del activo, pero NO recuerda el stop/objetivo
originales: por seguridad los recalcula. Para trading serio conviene un
almacenamiento persistente; aquí se prioriza la claridad.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone

import pandas as pd

from . import data, risk, strategy
from .broker import Broker


def _log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def ejecutar_bot(cfg) -> None:
    exchange = data.crear_exchange(cfg)
    broker = Broker(exchange, cfg.symbol)
    control = risk.ControlDiario(cfg.risk["limite_perdida_diaria_pct"])

    etiqueta = "PAPER (testnet, dinero de mentira)" if cfg.use_testnet else "LIVE (DINERO REAL)"
    _log(f"Bot iniciado en modo {etiqueta} | par={cfg.symbol} tf={cfg.timeframe}")

    posicion: dict | None = None
    espera = cfg.live_bot["segundos_entre_ciclos"]
    velas_necesarias = max(cfg.strategy["ema_slow"], cfg.strategy["rsi_period"],
                           cfg.strategy["atr_period"]) + 50

    while True:
        try:
            df = data.descargar_velas(exchange, cfg.symbol, cfg.timeframe,
                                      limite=velas_necesarias)
            datos = strategy.generate_signals(df, cfg.strategy)
            ultima = datos.iloc[-1]
            precio = broker.precio_actual()
            equity = broker.saldo_usdt() + broker.saldo_activo() * precio
            hoy = datetime.now(timezone.utc).date()

            if posicion is not None:
                _gestionar_posicion(broker, posicion, ultima, precio)
                if _debe_cerrar(posicion, ultima, precio):
                    broker.vender_mercado(posicion["cantidad"])
                    _log(f"VENTA ejecutada a ~{precio:.2f} | motivo={posicion['_motivo']}")
                    posicion = None
            else:
                if ultima["signal"] == strategy.BUY and pd.notna(ultima["atr"]):
                    if not control.puede_operar(hoy, equity):
                        _log("Límite de pérdida diaria alcanzado. Sin operar hoy.")
                    else:
                        niveles = risk.calcular_niveles(precio, ultima["atr"],
                                                        equity, cfg.risk)
                        if niveles and _importe_valido(broker, precio, niveles.cantidad):
                            broker.comprar_mercado(niveles.cantidad)
                            posicion = {
                                "cantidad": niveles.cantidad,
                                "stop_loss": niveles.stop_loss,
                                "take_profit": niveles.take_profit,
                                "entrada": precio,
                                "_motivo": None,
                            }
                            _log(f"COMPRA a ~{precio:.2f} | cant={niveles.cantidad:.6f} "
                                 f"stop={niveles.stop_loss:.2f} obj={niveles.take_profit:.2f}")
                        else:
                            _log("Señal de compra pero importe por debajo del mínimo. Se ignora.")
                else:
                    _log(f"Sin señal. precio={precio:.2f} rsi={ultima['rsi']:.1f}")

        except Exception as e:  # noqa: BLE001 - queremos que el bot no muera por un fallo puntual
            _log(f"[ERROR] {type(e).__name__}: {e}")

        time.sleep(espera)


def _gestionar_posicion(broker, posicion, ultima, precio) -> None:
    """Marca el motivo de cierre si se cumple stop/objetivo/señal."""
    posicion["_motivo"] = None
    if precio <= posicion["stop_loss"]:
        posicion["_motivo"] = "stop-loss"
    elif precio >= posicion["take_profit"]:
        posicion["_motivo"] = "take-profit"
    elif ultima["signal"] == strategy.SELL:
        posicion["_motivo"] = "señal de venta"


def _debe_cerrar(posicion, ultima, precio) -> bool:
    return posicion.get("_motivo") is not None


def _importe_valido(broker, precio, cantidad) -> bool:
    minimo = broker.minimo_operacion_usdt()
    return precio * cantidad >= minimo
