#!/usr/bin/env python3
"""Ejecuta el backtest: prueba la estrategia con datos históricos, SIN riesgo.

Uso:
    python run_backtest.py

Lee la configuración de config.yaml. Descarga velas de Binance (no necesita
claves) y muestra un informe con el rendimiento, la tasa de acierto, el
peor bajón (drawdown) y el número de operaciones.
"""
from __future__ import annotations

import sys

import ccxt

from src import data
from src.backtest import ejecutar_backtest
from src.config import load_config


def main() -> None:
    cfg = load_config()

    print("=" * 60)
    print("  BACKTEST — prueba histórica sin riesgo")
    print("=" * 60)
    print(f"  Par:        {cfg.symbol}")
    print(f"  Timeframe:  {cfg.timeframe}")
    print(f"  Velas:      {cfg.backtest['velas_historicas']}")
    print(f"  Capital:    {cfg.risk['capital_inicial']} USDT")
    print("-" * 60)
    print("  Descargando datos históricos de Binance...")

    exchange = data.crear_exchange(cfg)
    try:
        df = data.descargar_velas(
            exchange, cfg.symbol, cfg.timeframe, limite=cfg.backtest["velas_historicas"]
        )
    except (ccxt.NetworkError, ccxt.ExchangeError) as e:
        print("\n  [ERROR] No se pudo descargar datos de Binance.")
        print(f"  Detalle: {type(e).__name__}: {str(e)[:200]}")
        print("\n  Causas frecuentes:")
        print("   - Binance restringido en tu país (usa una IP permitida o Kraken).")
        print("   - Sin conexión a internet.")
        print("   - Nombre del par mal escrito en config.yaml (usa p.ej. BTC/USDT).")
        sys.exit(1)
    print(f"  {len(df)} velas descargadas "
          f"({df.index[0].date()} a {df.index[-1].date()}).")
    print("-" * 60)

    res = ejecutar_backtest(df, cfg)

    signo = "+" if res.rendimiento_pct >= 0 else ""
    print("  RESULTADOS")
    print(f"    Capital inicial:   {res.equity_inicial:,.2f} USDT")
    print(f"    Capital final:     {res.equity_final:,.2f} USDT")
    print(f"    Rendimiento:       {signo}{res.rendimiento_pct:.2f} %")
    print(f"    Operaciones:       {res.num_operaciones}")
    print(f"    Tasa de acierto:   {res.tasa_acierto_pct:.1f} %")
    print(f"    Profit factor:     {res.profit_factor:.2f}")
    print(f"    Peor bajón (DD):   -{res.max_drawdown_pct:.2f} %")
    print("=" * 60)

    _interpretar(res)


def _interpretar(res) -> None:
    """Traduce los números a lenguaje llano para no confundir."""
    print("\n  ¿Cómo leer esto?")
    if res.num_operaciones < 20:
        print("  - Pocas operaciones: el resultado NO es fiable estadísticamente.")
        print("    Prueba más velas históricas o un timeframe más corto.")
    if res.profit_factor < 1.0:
        print("  - Profit factor < 1: la estrategia PIERDE dinero tal cual está.")
        print("    NO la lleves a real. Ajusta parámetros o prueba otro par.")
    elif res.profit_factor < 1.3:
        print("  - Profit factor bajo: apenas cubre costes. Riesgo alto de que")
        print("    en real dé pérdidas. Trátala con mucha desconfianza.")
    else:
        print("  - Profit factor decente EN ESTE periodo. Ojo: pasado no garantiza")
        print("    futuro. El siguiente paso es 'paper' (testnet), NO real.")
    print("\n  Siguiente paso recomendado: modo 'paper' durante semanas.\n")


if __name__ == "__main__":
    main()
