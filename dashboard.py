#!/usr/bin/env python3
"""Panel web interactivo del bot (backtesting visual).

Ejecuta la estrategia sobre datos históricos de Binance y muestra los
resultados con gráficos, ajustando los parámetros desde el navegador.

Cómo usarlo (no necesitas saber programar):
    1. Instala las dependencias:  pip install -r requirements.txt
    2. Arranca el panel:          streamlit run dashboard.py
    3. Se abre solo en tu navegador. Ajusta a la izquierda y pulsa
       "Ejecutar backtest".

Es solo para backtesting (sin riesgo). Para operar en tiempo real se usa
run_bot.py, como explica el README.
"""
from __future__ import annotations

from types import SimpleNamespace

import pandas as pd
import streamlit as st

from src import data
from src.backtest import ejecutar_backtest
from src.strategy import BUY, SELL, generate_signals

st.set_page_config(page_title="Bot de Trading · Panel", page_icon="📊", layout="wide")

st.title("📊 Bot de Trading — Panel de backtesting")
st.caption(
    "Prueba la estrategia con datos históricos reales de Binance. Sin riesgo, "
    "sin dinero real. Ningún resultado pasado garantiza ganancias futuras."
)

# --------------------------- Controles (barra lateral) ---------------------------
with st.sidebar:
    st.header("⚙️ Parámetros")

    st.subheader("Mercado")
    symbol = st.text_input("Par", value="BTC/USDT", help="Ej: BTC/USDT, ETH/USDT")
    timeframe = st.selectbox("Vela (timeframe)", ["15m", "1h", "4h", "1d"], index=1)
    velas = st.slider("Velas históricas", 300, 3000, 1500, step=100)

    st.subheader("Estrategia")
    ema_fast = st.slider("EMA rápida", 3, 50, 12)
    ema_slow = st.slider("EMA lenta", 10, 200, 26)
    rsi_period = st.slider("Periodo RSI", 5, 30, 14)
    rsi_max = st.slider("RSI máximo para comprar", 50, 90, 70)

    st.subheader("Riesgo")
    capital = st.number_input("Capital inicial (USDT)", 100, 1_000_000, 1000, step=100)
    riesgo = st.slider("Riesgo por operación (%)", 0.5, 5.0, 1.0, step=0.5)
    sl_mult = st.slider("Stop-loss (× ATR)", 1.0, 5.0, 2.0, step=0.5)
    tp_mult = st.slider("Take-profit (× ATR)", 1.0, 6.0, 3.0, step=0.5)
    limite_dia = st.slider("Límite pérdida diaria (%)", 1.0, 10.0, 3.0, step=0.5)

    ejecutar = st.button("▶️  Ejecutar backtest", use_container_width=True, type="primary")


def _construir_cfg() -> SimpleNamespace:
    """Crea un objeto de configuración compatible con el motor de backtest."""
    return SimpleNamespace(
        mode="backtest",
        symbol=symbol,
        timeframe=timeframe,
        use_testnet=False,
        api_key="",
        api_secret="",
        strategy={
            "ema_fast": ema_fast, "ema_slow": ema_slow, "rsi_period": rsi_period,
            "rsi_max_entry": rsi_max, "atr_period": 14,
        },
        risk={
            "capital_inicial": capital, "riesgo_por_operacion_pct": riesgo,
            "stop_loss_atr_mult": sl_mult, "take_profit_atr_mult": tp_mult,
            "limite_perdida_diaria_pct": limite_dia, "max_posiciones": 1,
        },
        costes={"comision_pct": 0.1, "slippage_pct": 0.05},
    )


@st.cache_data(show_spinner=False)
def _descargar(symbol: str, timeframe: str, velas: int) -> pd.DataFrame:
    """Descarga velas (cacheado para no repetir la misma petición)."""
    cfg = SimpleNamespace(use_testnet=False, api_key="", api_secret="")
    exchange = data.crear_exchange(cfg)
    return data.descargar_velas(exchange, symbol, timeframe, limite=velas)


# --------------------------------- Ejecución ------------------------------------
if not ejecutar:
    st.info("👈 Ajusta los parámetros a la izquierda y pulsa **Ejecutar backtest**.")
    st.stop()

if ema_fast >= ema_slow:
    st.error("La EMA rápida debe ser menor que la EMA lenta.")
    st.stop()

cfg = _construir_cfg()

try:
    with st.spinner(f"Descargando {velas} velas de {symbol}…"):
        df = _descargar(symbol, timeframe, velas)
except Exception as e:  # noqa: BLE001
    st.error(f"No se pudieron descargar datos: {type(e).__name__}: {str(e)[:200]}")
    st.info("Comprueba el nombre del par y que Binance no esté restringido en tu red.")
    st.stop()

if df.empty or len(df) < 60:
    st.error("Datos insuficientes. Prueba otro par o más velas.")
    st.stop()

res = ejecutar_backtest(df, cfg)

st.success(
    f"Backtest completado: {len(df)} velas "
    f"({df.index[0].date()} → {df.index[-1].date()})."
)

# --------------------------------- Métricas -------------------------------------
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Rendimiento", f"{res.rendimiento_pct:+.2f}%")
c2.metric("Capital final", f"{res.equity_final:,.0f}")
c3.metric("Operaciones", res.num_operaciones)
c4.metric("Aciertos", f"{res.tasa_acierto_pct:.1f}%")
pf = res.profit_factor
c5.metric("Profit factor", "∞" if pf == float("inf") else f"{pf:.2f}")
c6.metric("Peor bajón", f"-{res.max_drawdown_pct:.2f}%")

if pf < 1.0:
    st.warning(
        "⚠️ Profit factor < 1: con estos parámetros la estrategia **pierde dinero**. "
        "No la lleves a real. Ajusta los parámetros o prueba otro par/timeframe."
    )

# --------------------------------- Gráficos -------------------------------------
st.subheader("Evolución del capital")
if res.curva_equity is not None and not res.curva_equity.empty:
    st.area_chart(res.curva_equity, height=280, color="#0d9488")

st.subheader("Precio y operaciones")
señales = generate_signals(df, cfg.strategy)
precio_df = pd.DataFrame({"precio": df["close"]})
# Marcamos en columnas separadas los puntos de compra y venta.
precio_df["compra"] = df["close"].where(señales["signal"] == BUY)
precio_df["venta"] = df["close"].where(señales["signal"] == SELL)
st.line_chart(precio_df, height=320,
              color=["#8a97a1", "#15a34a", "#dc2626"])

# --------------------------------- Tabla ----------------------------------------
st.subheader("Operaciones")
if res.operaciones:
    tabla = pd.DataFrame([{
        "Entrada": o.entrada_fecha.strftime("%Y-%m-%d %H:%M"),
        "Compra": round(o.entrada_precio, 2),
        "Venta": round(o.salida_precio, 2),
        "Resultado (USDT)": round(o.pnl, 2),
        "Motivo": o.motivo_salida,
    } for o in reversed(res.operaciones)])
    st.dataframe(tabla, use_container_width=True, hide_index=True)
else:
    st.info("No hubo operaciones con estos parámetros en este periodo.")

st.caption(
    "Recuerda: simulación sobre datos pasados. Antes de usar dinero real, "
    "prueba en modo *paper* durante semanas (ver README)."
)
