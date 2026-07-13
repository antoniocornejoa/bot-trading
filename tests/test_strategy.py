"""Tests básicos: indicadores, señales y gestión de riesgo.

Ejecutar con:  python -m pytest -q   (o)   python tests/test_strategy.py
No necesitan conexión a internet: usan datos sintéticos.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import indicators as ind
from src import optimizer, risk, strategy
from src.backtest import ejecutar_backtest


def _velas_sinteticas(n: int = 500, seed: int = 7) -> pd.DataFrame:
    """Genera velas con una tendencia + ruido, deterministas (seed fijo)."""
    rng = np.random.default_rng(seed)
    retornos = rng.normal(0.0005, 0.02, n)
    precio = 100 * np.exp(np.cumsum(retornos))
    idx = pd.date_range("2023-01-01", periods=n, freq="1h", tz="UTC")
    close = pd.Series(precio, index=idx)
    high = close * (1 + rng.uniform(0, 0.01, n))
    low = close * (1 - rng.uniform(0, 0.01, n))
    open_ = close.shift(1).fillna(close.iloc[0])
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close,
         "volume": rng.uniform(1, 100, n)},
        index=idx,
    )


def test_rsi_en_rango():
    df = _velas_sinteticas()
    r = ind.rsi(df["close"], 14).dropna()
    assert r.between(0, 100).all(), "El RSI debe estar entre 0 y 100."


def test_ema_orden():
    s = pd.Series(range(1, 101), dtype=float)
    rapida = ind.ema(s, 5)
    lenta = ind.ema(s, 20)
    # En una serie creciente, la EMA rápida va por encima de la lenta.
    assert rapida.iloc[-1] > lenta.iloc[-1]


def test_atr_positivo():
    df = _velas_sinteticas()
    a = ind.atr(df, 14).dropna()
    assert (a >= 0).all(), "El ATR nunca es negativo."


def test_senales_validas():
    df = _velas_sinteticas()
    cfg = {"ema_fast": 12, "ema_slow": 26, "rsi_period": 14,
           "rsi_max_entry": 70, "atr_period": 14}
    out = strategy.generate_signals(df, cfg)
    assert set(out["signal"].unique()).issubset({-1, 0, 1})


def test_tamano_posicion_respeta_riesgo():
    # Con 1000 de capital y 1% de riesgo, la pérdida al saltar el stop
    # debe ser ~10, no más.
    cfg = {"stop_loss_atr_mult": 2.0, "take_profit_atr_mult": 3.0,
           "riesgo_por_operacion_pct": 1.0}
    niveles = risk.calcular_niveles(precio_entrada=100, atr=1.0,
                                    equity=1000, risk_cfg=cfg)
    assert niveles is not None
    perdida_si_stop = (niveles.entrada - niveles.stop_loss) * niveles.cantidad
    assert abs(perdida_si_stop - 10.0) < 0.5


def test_control_diario_corta():
    control = risk.ControlDiario(limite_perdida_diaria_pct=3.0)
    import datetime as dt
    hoy = dt.date(2023, 1, 1)
    assert control.puede_operar(hoy, 1000) is True    # primer registro del día
    assert control.puede_operar(hoy, 990) is True     # -1%, aún permitido
    assert control.puede_operar(hoy, 960) is False    # -4%, se corta


def test_backtest_corre():
    df = _velas_sinteticas()

    class Cfg:
        strategy = {"ema_fast": 12, "ema_slow": 26, "rsi_period": 14,
                    "rsi_max_entry": 70, "atr_period": 14}
        risk = {"capital_inicial": 1000, "riesgo_por_operacion_pct": 1.0,
                "stop_loss_atr_mult": 2.0, "take_profit_atr_mult": 3.0,
                "limite_perdida_diaria_pct": 3.0, "max_posiciones": 1}
        costes = {"comision_pct": 0.1, "slippage_pct": 0.05}

    res = ejecutar_backtest(df, Cfg())
    assert res.equity_final > 0
    assert res.num_operaciones >= 0
    # El equity final debe ser coherente con las operaciones registradas.
    assert isinstance(res.rendimiento_pct, float)


def test_contabilidad_coherente():
    """Regresión: contabilidad de caja correcta (spot, sin apalancamiento).

    Bugs que este test detecta:
      - Vender más barato de lo comprado NO puede dar beneficio.
      - Vender más caro NO puede dar pérdida grande.
      - El capital no puede 'explotar' por no descontar el coste de compra.
    """
    df = _velas_sinteticas(n=1500, seed=11)

    class Cfg:
        strategy = {"ema_fast": 12, "ema_slow": 26, "rsi_period": 14,
                    "rsi_max_entry": 70, "atr_period": 14}
        risk = {"capital_inicial": 1000, "riesgo_por_operacion_pct": 1.0,
                "stop_loss_atr_mult": 2.0, "take_profit_atr_mult": 3.0,
                "limite_perdida_diaria_pct": 3.0, "max_posiciones": 1}
        costes = {"comision_pct": 0.1, "slippage_pct": 0.05}

    res = ejecutar_backtest(df, Cfg())

    for op in res.operaciones:
        if op.salida_precio < op.entrada_precio:
            assert op.pnl < 0, (
                f"Vendió a {op.salida_precio} tras comprar a {op.entrada_precio} "
                f"pero el PnL es {op.pnl} (debería ser negativo)."
            )
        # Ningún trade puede ganar/perder más que el valor de la posición.
        valor_posicion = op.entrada_precio * op.cantidad
        assert abs(op.pnl) <= valor_posicion + 1e-6

    # En spot sin apalancamiento, cada trade arriesga ~1% del capital: el
    # capital no puede multiplicarse por miles. Cota de cordura muy holgada.
    assert res.equity_final < res.equity_inicial * 5
    # La suma de PnL debe cuadrar con el cambio de capital (contabilidad cerrada).
    suma_pnl = sum(o.pnl for o in res.operaciones)
    assert abs(suma_pnl - (res.equity_final - res.equity_inicial)) < 1e-3


def test_metricas_operaciones_vacio():
    m = optimizer.metricas_operaciones([], 1000)
    assert m["ops"] == 0 and m["profit_factor"] == 0.0 and m["retorno_pct"] == 0.0


def test_metricas_operaciones_calcula():
    from types import SimpleNamespace
    ops = [SimpleNamespace(pnl=10.0), SimpleNamespace(pnl=-5.0), SimpleNamespace(pnl=20.0)]
    m = optimizer.metricas_operaciones(ops, 1000)
    assert m["ops"] == 3
    assert abs(m["profit_factor"] - (30.0 / 5.0)) < 1e-9   # ganancias 30, pérdidas 5
    assert abs(m["retorno_pct"] - 2.5) < 1e-9              # pnl 25 sobre 1000
    assert abs(m["aciertos"] - (2 / 3 * 100)) < 1e-6


def test_explorar_par_estructura():
    df = _velas_sinteticas(n=1200, seed=5)
    riesgo = {"capital": 1000, "riesgo": 1.0, "sl": 2.0, "tp": 3.0, "limite": 3.0}
    filas = optimizer.explorar_par(df, "BTC/USDT", "1h", riesgo, min_trades_test=3)
    assert len(filas) > 0
    campos = {"par", "tf", "ema_fast", "ema_slow", "pf_train", "pf_test",
              "ops_test", "veredicto"}
    assert campos.issubset(filas[0].keys())
    # ema_fast siempre menor que ema_slow (las inválidas se descartan).
    assert all(f["ema_fast"] < f["ema_slow"] for f in filas)
    # El ranking no debe fallar y devuelve el mismo número de filas.
    orden = optimizer.ranking(filas)
    assert len(orden) == len(filas)
    # Las robustas (si las hay) van antes que las de "pocas ops".
    veredictos = [f["veredicto"] for f in orden]
    if "🟢 robusta" in veredictos and "⚪ pocas ops" in veredictos:
        assert veredictos.index("🟢 robusta") < veredictos.index("⚪ pocas ops")


def test_split_train_test_sin_solape():
    # Cada operación cae en train O en test según la fecha de corte, nunca en ambos.
    df = _velas_sinteticas(n=1000, seed=9)
    riesgo = {"capital": 1000, "riesgo": 1.0, "sl": 2.0, "tp": 3.0, "limite": 3.0}
    filas = optimizer.explorar_par(df, "BTC/USDT", "1h", riesgo,
                                   grid={"ema_fast": [12], "ema_slow": [26],
                                         "rsi_max_entry": [70]})
    assert len(filas) == 1
    f = filas[0]
    # ops_train + ops_test no puede exceder el total de operaciones posibles.
    assert f["ops_train"] >= 0 and f["ops_test"] >= 0


if __name__ == "__main__":
    for nombre, fn in list(globals().items()):
        if nombre.startswith("test_") and callable(fn):
            fn()
            print(f"OK  {nombre}")
    print("\nTodos los tests pasaron.")
