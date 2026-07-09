#!/usr/bin/env python3
"""Demo SIN internet: corre el backtest sobre datos de ejemplo generados
localmente, para ver qué aspecto tiene el informe sin conectar a Binance.

Uso:  python demo_offline.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.backtest import ejecutar_backtest
from src.report import generar_informe_html


class _Cfg:
    symbol = "BTC/USDT (datos de ejemplo)"
    timeframe = "1h"
    mode = "demo"
    strategy = {"ema_fast": 12, "ema_slow": 26, "rsi_period": 14,
                "rsi_max_entry": 70, "atr_period": 14}
    risk = {"capital_inicial": 1000, "riesgo_por_operacion_pct": 1.0,
            "stop_loss_atr_mult": 2.0, "take_profit_atr_mult": 3.0,
            "limite_perdida_diaria_pct": 3.0, "max_posiciones": 1}
    costes = {"comision_pct": 0.1, "slippage_pct": 0.05}


def _datos_ejemplo(n=3000, seed=3):
    rng = np.random.default_rng(seed)
    retornos = rng.normal(0.0004, 0.018, n)
    precio = 30000 * np.exp(np.cumsum(retornos))
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    close = pd.Series(precio, index=idx)
    high = close * (1 + rng.uniform(0, 0.008, n))
    low = close * (1 - rng.uniform(0, 0.008, n))
    open_ = close.shift(1).fillna(close.iloc[0])
    return pd.DataFrame({"open": open_, "high": high, "low": low,
                         "close": close, "volume": rng.uniform(1, 100, n)}, index=idx)


def main():
    cfg = _Cfg()
    df = _datos_ejemplo()
    print("=" * 60)
    print("  DEMO OFFLINE — así se ve el informe del bot")
    print("=" * 60)
    print(f"  Par:       {cfg.symbol}")
    print(f"  Velas:     {len(df)}  ({df.index[0].date()} a {df.index[-1].date()})")
    print(f"  Capital:   {cfg.risk['capital_inicial']} USDT")
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
    print("-" * 60)
    print("  Últimas operaciones simuladas:")
    for op in res.operaciones[-5:]:
        pnl = f"{'+' if op.pnl >= 0 else ''}{op.pnl:.2f}"
        print(f"    {op.entrada_fecha.date()} compra {op.entrada_precio:8.1f} "
              f"-> vende {op.salida_precio:8.1f}  PnL {pnl:>8} USDT  ({op.motivo_salida})")
    print("=" * 60)

    ruta = generar_informe_html(df, res, cfg, "results/informe_demo.html")
    print(f"\n  📊 Informe visual generado: {ruta.resolve()}")
    print("     Ábrelo con doble clic para verlo en el navegador.")


if __name__ == "__main__":
    main()
