#!/usr/bin/env python3
"""Arranca el bot en tiempo real (paper o live según config.yaml).

Uso:
    python run_bot.py

- Con mode: paper  -> opera en la testnet de Binance (dinero de mentira).
- Con mode: live   -> opera con dinero REAL (requiere confirmar el riesgo
  en config.yaml y tener claves reales en .env).

Detén el bot en cualquier momento con Ctrl + C.
"""
from __future__ import annotations

import sys

from src.bot import ejecutar_bot
from src.config import load_config


def main() -> None:
    cfg = load_config()

    if cfg.mode == "backtest":
        print("El modo actual es 'backtest'. Para operar en tiempo real cambia")
        print("'mode' a 'paper' (recomendado) o 'live' en config.yaml.")
        print("Para probar la estrategia con histórico usa: python run_backtest.py")
        sys.exit(0)

    if cfg.mode == "live":
        print("\n" + "!" * 60)
        print("  ATENCIÓN: MODO REAL. Vas a operar con DINERO DE VERDAD.")
        print("  Escribe exactamente 'OPERAR CON DINERO REAL' para continuar.")
        print("!" * 60)
        confirm = input("  > ").strip()
        if confirm != "OPERAR CON DINERO REAL":
            print("  Cancelado. No se ha operado.")
            sys.exit(0)

    try:
        ejecutar_bot(cfg)
    except KeyboardInterrupt:
        print("\nBot detenido por el usuario. (Revisa si quedó alguna posición abierta.)")


if __name__ == "__main__":
    main()
