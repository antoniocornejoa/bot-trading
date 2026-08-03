"""Bot DCA automático: compra una cantidad fija cada periodo, sin intervención.

Esto es lo más parecido a un "ingreso pasivo" honesto en cripto con poca
inversión: no intenta adivinar el mercado (ya demostramos que ahí no hay
ventaja fácil), solo acumula con disciplina. El "trabajo" del bot es la
constancia, no la predicción.

Funciona en paper (testnet, dinero de mentira) y en live (dinero real, con
los mismos seguros que el resto del bot). Guarda un historial de compras en
results/dca_historial.csv y recuerda el último periodo comprado en
results/dca_estado.json, así puede reiniciarse sin comprar dos veces.
"""
from __future__ import annotations

import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from .broker import Broker
from . import data

RUTA_ESTADO = Path("results/dca_estado.json")
RUTA_HISTORIAL = Path("results/dca_historial.csv")

# Formato de la "clave de periodo": si la clave cambia, toca comprar.
PERIODOS = {
    "diaria": "%Y-%m-%d",
    "semanal": "%G-W%V",   # año-semana ISO (p. ej. 2026-W29)
    "mensual": "%Y-%m",
}


def clave_periodo(fecha: datetime, frecuencia: str) -> str:
    """Devuelve la etiqueta del periodo al que pertenece una fecha.

    Dos fechas con la misma etiqueta = mismo periodo = una sola compra.
    """
    frecuencia = frecuencia.lower()
    if frecuencia not in PERIODOS:
        raise ValueError(f"Frecuencia inválida: {frecuencia!r}. "
                         f"Usa una de {list(PERIODOS)}.")
    return fecha.strftime(PERIODOS[frecuencia])


def _leer_estado() -> dict:
    if RUTA_ESTADO.exists():
        return json.loads(RUTA_ESTADO.read_text(encoding="utf-8"))
    return {}


def _guardar_estado(estado: dict) -> None:
    RUTA_ESTADO.parent.mkdir(parents=True, exist_ok=True)
    RUTA_ESTADO.write_text(json.dumps(estado, indent=2), encoding="utf-8")


def _registrar_compra(fecha: str, symbol: str, monto: float,
                      precio: float, cantidad: float) -> None:
    RUTA_HISTORIAL.parent.mkdir(parents=True, exist_ok=True)
    nueva = not RUTA_HISTORIAL.exists()
    with open(RUTA_HISTORIAL, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nueva:
            w.writerow(["fecha", "par", "monto_usdt", "precio", "cantidad"])
        w.writerow([fecha, symbol, f"{monto:.2f}", f"{precio:.2f}", f"{cantidad:.8f}"])


def _log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def ejecutar_dca(cfg) -> None:
    """Bucle principal: comprueba cada hora si empezó un periodo nuevo y compra."""
    exchange = data.crear_exchange(cfg)
    broker = Broker(exchange, cfg.symbol)

    monto = float(cfg.dca["monto_usdt"])
    frecuencia = str(cfg.dca["frecuencia"]).lower()

    etiqueta = "PAPER (testnet)" if cfg.use_testnet else "LIVE (DINERO REAL)"
    _log(f"Bot DCA iniciado en {etiqueta} | {cfg.symbol} | "
         f"{monto} USDT {frecuencia}")

    minimo = broker.minimo_operacion_usdt()
    if monto < minimo:
        raise SystemExit(
            f"\n[BLOQUEADO] El monto ({monto} USDT) está por debajo del mínimo "
            f"que exige el exchange para {cfg.symbol} ({minimo} USDT).\n"
            f"Sube 'monto_usdt' en config.yaml.\n"
        )

    estado = _leer_estado()
    clave_guardada = estado.get(cfg.symbol, {}).get(frecuencia)

    while True:
        try:
            ahora = datetime.now(timezone.utc)
            clave_actual = clave_periodo(ahora, frecuencia)

            if clave_actual != clave_guardada:
                saldo = broker.saldo_usdt()
                if saldo < monto:
                    _log(f"Saldo insuficiente ({saldo:.2f} USDT < {monto}). "
                         "Esperando al siguiente ciclo; deposita fondos.")
                else:
                    precio = broker.precio_actual()
                    cantidad = monto / precio
                    broker.comprar_mercado(cantidad)
                    _registrar_compra(ahora.isoformat(timespec="seconds"),
                                      cfg.symbol, monto, precio, cantidad)
                    clave_guardada = clave_actual
                    estado.setdefault(cfg.symbol, {})[frecuencia] = clave_actual
                    _guardar_estado(estado)
                    _log(f"COMPRA DCA: {monto} USDT de {cfg.symbol} a ~{precio:,.2f} "
                         f"({cantidad:.8f} uds) | periodo {clave_actual}")
            else:
                _log(f"Periodo {clave_actual} ya comprado. Todo en orden.")

        except Exception as e:  # noqa: BLE001 - el bot no debe morir por un fallo puntual
            _log(f"[ERROR] {type(e).__name__}: {e}")

        # Comprobar una vez por hora es de sobra para frecuencias de días/semanas.
        time.sleep(3600)
