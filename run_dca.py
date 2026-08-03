#!/usr/bin/env python3
"""Arranca el bot DCA automático (compra periódica) en paper o live.

Uso:
    python run_dca.py

- Con mode: paper en config.yaml -> compra en la testnet (dinero de mentira).
- Con mode: live -> compra con dinero REAL (requiere los mismos seguros que
  run_bot.py: i_understand_live_risk y confirmación escrita).

Configura la cantidad y la frecuencia en la sección 'dca' de config.yaml.
Déjalo corriendo (idealmente en un servidor o un PC siempre encendido) y
comprará solo, una vez por periodo. Detenerlo: Ctrl + C. Al reiniciarlo
recuerda qué periodos ya compró (results/dca_estado.json).
"""
from __future__ import annotations

import sys

from src.config import load_config
from src.dca_bot import ejecutar_dca


def main() -> None:
    cfg = load_config()

    if cfg.mode == "backtest":
        print("El modo actual es 'backtest'. El bot DCA opera en tiempo real:")
        print("cambia 'mode' a 'paper' (recomendado para empezar) o 'live'.")
        print("Para SIMULAR un DCA con histórico usa la pestaña DCA del panel:")
        print("  streamlit run dashboard.py")
        sys.exit(0)

    if cfg.mode == "live":
        print("\n" + "!" * 60)
        print("  ATENCIÓN: MODO REAL. Vas a comprar con DINERO DE VERDAD")
        print(f"  ({cfg.dca['monto_usdt']} USDT {cfg.dca['frecuencia']} en {cfg.symbol}).")
        print("  Escribe exactamente 'OPERAR CON DINERO REAL' para continuar.")
        print("!" * 60)
        confirm = input("  > ").strip()
        if confirm != "OPERAR CON DINERO REAL":
            print("  Cancelado. No se ha comprado nada.")
            sys.exit(0)

    try:
        ejecutar_dca(cfg)
    except KeyboardInterrupt:
        print("\nBot DCA detenido. El historial está en results/dca_historial.csv")


if __name__ == "__main__":
    main()
