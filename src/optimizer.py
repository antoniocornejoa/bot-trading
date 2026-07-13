"""Explorador de estrategias: prueba muchas combinaciones y detecta cuáles
tienen ventaja REAL (no solo la que mejor encaja al pasado).

Idea clave contra el *overfitting*:
  - Se divide el histórico en dos tramos por tiempo: ENTRENAMIENTO (train, el
    70% más antiguo) y VALIDACIÓN (test, el 30% más reciente).
  - Se elige la configuración mirando el train, pero lo que decide si es buena
    es su comportamiento en el test, datos que "no ha visto".
  - Una estrategia solo es de fiar si funciona en AMBOS tramos.

Así evitamos el error clásico: encontrar el número mágico que brilla en el
pasado y fracasa en cuanto se usa de verdad.
"""
from __future__ import annotations

from itertools import product
from types import SimpleNamespace

import pandas as pd

from .backtest import ejecutar_backtest

# Rejilla de parámetros por defecto que se prueba en cada par/timeframe.
GRID_POR_DEFECTO = {
    "ema_fast": [9, 12, 20],
    "ema_slow": [21, 26, 50],
    "rsi_max_entry": [65, 70, 75],
}


def metricas_operaciones(operaciones: list, capital_inicial: float) -> dict:
    """Calcula métricas a partir de una lista de operaciones ya cerradas."""
    n = len(operaciones)
    if n == 0:
        return {"ops": 0, "aciertos": 0.0, "profit_factor": 0.0,
                "retorno_pct": 0.0, "pnl": 0.0}
    ganancias = sum(o.pnl for o in operaciones if o.pnl > 0)
    perdidas = -sum(o.pnl for o in operaciones if o.pnl < 0)
    if perdidas > 0:
        pf = ganancias / perdidas
    else:
        pf = float("inf") if ganancias > 0 else 0.0
    pnl = sum(o.pnl for o in operaciones)
    aciertos = sum(1 for o in operaciones if o.pnl > 0) / n * 100
    return {"ops": n, "aciertos": aciertos, "profit_factor": pf,
            "retorno_pct": pnl / capital_inicial * 100, "pnl": pnl}


def _construir_cfg(symbol, timeframe, params, riesgo) -> SimpleNamespace:
    return SimpleNamespace(
        mode="backtest", symbol=symbol, timeframe=timeframe,
        strategy={
            "ema_fast": params["ema_fast"], "ema_slow": params["ema_slow"],
            "rsi_period": 14, "rsi_max_entry": params["rsi_max_entry"],
            "atr_period": 14,
        },
        risk={
            "capital_inicial": riesgo["capital"],
            "riesgo_por_operacion_pct": riesgo["riesgo"],
            "stop_loss_atr_mult": riesgo["sl"], "take_profit_atr_mult": riesgo["tp"],
            "limite_perdida_diaria_pct": riesgo["limite"], "max_posiciones": 1,
        },
        costes={"comision_pct": 0.1, "slippage_pct": 0.05},
    )


# Mínimo de operaciones para que la estadística signifique algo. Con menos,
# el resultado es ruido (una buena/mala racha de suerte), no una ventaja.
MIN_TRADES_TRAIN = 15


def _veredicto(train: dict, test: dict, min_trades_test: int,
               min_trades_train: int = MIN_TRADES_TRAIN) -> str:
    """Etiqueta de robustez leyendo AMBOS tramos (train y test).

    Exige un mínimo de operaciones en LOS DOS tramos: así una config con
    profit factor altísimo pero basado en 1-2 operaciones (pura suerte) NO
    se marca como robusta.
    """
    if test["ops"] < min_trades_test or train["ops"] < min_trades_train:
        return "⚪ pocas ops"
    rentable_ambos = train["profit_factor"] > 1.0 and test["profit_factor"] > 1.0
    if not rentable_ambos:
        return "🔴 no robusta"
    if test["profit_factor"] >= 1.3:
        return "🟢 robusta"
    return "🟡 dudosa"


def explorar_par(
    df: pd.DataFrame,
    symbol: str,
    timeframe: str,
    riesgo: dict,
    grid: dict | None = None,
    split: float = 0.7,
    min_trades_test: int = 15,
) -> list[dict]:
    """Prueba todas las combinaciones de la rejilla sobre un histórico.

    Para cada combinación hace UN backtest sobre todo el histórico y luego
    reparte las operaciones en train (más antiguas) y test (más recientes)
    según la fecha de corte. Devuelve una fila por combinación.
    """
    grid = grid or GRID_POR_DEFECTO
    capital = riesgo["capital"]

    if len(df) < 100:
        return []
    split = min(max(split, 0.5), 0.95)  # evita índices fuera de rango
    corte = df.index[int(len(df) * split)]

    combos = [dict(zip(grid.keys(), vals)) for vals in product(*grid.values())]
    filas = []
    for params in combos:
        # Claves obligatorias con valores por defecto si el grid las omite.
        params = {"ema_fast": 12, "ema_slow": 26, "rsi_max_entry": 70, **params}
        if params["ema_fast"] >= params["ema_slow"]:
            continue  # la EMA rápida siempre debe ser menor que la lenta
        cfg = _construir_cfg(symbol, timeframe, params, riesgo)
        res = ejecutar_backtest(df, cfg)

        train_ops = [o for o in res.operaciones if o.entrada_fecha < corte]
        test_ops = [o for o in res.operaciones if o.entrada_fecha >= corte]
        mt = metricas_operaciones(train_ops, capital)
        me = metricas_operaciones(test_ops, capital)
        # Retorno del test sobre el capital REAL al llegar al corte (no el
        # inicial): así no se contamina con cuánto creció el capital en train.
        equity_corte = capital + mt["pnl"]
        retorno_test = me["pnl"] / equity_corte * 100 if equity_corte > 0 else 0.0

        filas.append({
            "par": symbol, "tf": timeframe,
            "ema_fast": params["ema_fast"], "ema_slow": params["ema_slow"],
            "rsi_max": params["rsi_max_entry"],
            "pf_train": mt["profit_factor"], "ops_train": mt["ops"],
            "pf_test": me["profit_factor"], "ops_test": me["ops"],
            "retorno_test_pct": retorno_test, "aciertos_test": me["aciertos"],
            "veredicto": _veredicto(mt, me, min_trades_test),
        })
    return filas


def _clave_orden(fila: dict) -> tuple:
    """Ordena: primero robustas; dentro de cada grupo, por PF de test ACOTADO
    y por tamaño de muestra. Acotar el PF evita que una racha afortunada de
    pocas operaciones (PF enorme o infinito) se presente como la mejor.
    """
    prioridad = {"🟢 robusta": 0, "🟡 dudosa": 1, "🔴 no robusta": 2, "⚪ pocas ops": 3}
    pf = fila["pf_test"]
    # Acotamos a 3.0: por encima de eso, más PF no significa "más fiable".
    pf_cap = 3.0 if pf == float("inf") else min(pf, 3.0)
    # Más operaciones = más fiable, por eso desempata a favor de la muestra grande.
    return (prioridad.get(fila["veredicto"], 9), -round(pf_cap, 2), -fila["ops_test"])


def ranking(filas: list[dict]) -> list[dict]:
    """Ordena las combinaciones de mejor a peor según robustez out-of-sample."""
    return sorted(filas, key=_clave_orden)
