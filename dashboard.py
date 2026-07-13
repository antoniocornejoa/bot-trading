#!/usr/bin/env python3
"""Panel web interactivo del bot (backtesting visual).

Dos pestañas:
  1. Backtest simple  -> prueba UNA configuración y ve los gráficos.
  2. Explorador       -> prueba MUCHAS combinaciones y detecta cuáles tienen
                         ventaja real (validación out-of-sample, anti-overfitting).

Cómo usarlo (no necesitas saber programar):
    1. Instala:   pip install -r requirements.txt
    2. Arranca:   streamlit run dashboard.py
    3. Se abre solo en el navegador.

Es solo para backtesting (sin riesgo). Para operar en tiempo real se usa
run_bot.py, como explica el README.
"""
from __future__ import annotations

from types import SimpleNamespace

import pandas as pd
import streamlit as st

from src import data, optimizer
from src.backtest import ejecutar_backtest
from src.strategy import BUY, SELL, generate_signals

st.set_page_config(page_title="Bot de Trading · Panel", page_icon="📊", layout="wide")


# ------------------------------- utilidades comunes -----------------------------
def _semilla_demo(symbol: str, timeframe: str) -> int:
    """Semilla estable a partir del par+timeframe, para que cada moneda tenga
    una serie de ejemplo DISTINTA (y no todas la misma serie inventada)."""
    return sum(ord(c) for c in f"{symbol}{timeframe}") % 100000


@st.cache_data(show_spinner=False)
def descargar(fuente: str, symbol: str, timeframe: str, velas: int) -> pd.DataFrame:
    """Descarga velas según la fuente elegida (cacheado)."""
    if fuente.startswith("Datos de ejemplo"):
        return data.datos_demo(n=velas, seed=_semilla_demo(symbol, timeframe))
    nombre = "kraken" if fuente == "Kraken" else "binance"
    exchange = data.crear_exchange_publico(nombre)
    return data.descargar_velas(exchange, symbol, timeframe, limite=velas)


def _fuente_selector(clave: str) -> str:
    return st.selectbox(
        "Fuente de datos", ["Binance", "Kraken", "Datos de ejemplo (demo)"],
        index=0, key=clave,
        help="Si Binance no funciona en tu red (p. ej. en la nube), prueba "
             "Kraken o el modo demo (siempre funciona, datos simulados).",
    )


# ================================ PESTAÑA 1: BACKTEST ============================
def pestaña_backtest() -> None:
    st.caption(
        "Prueba UNA estrategia con datos históricos reales. Sin riesgo, sin "
        "dinero real. Ningún resultado pasado garantiza ganancias futuras."
    )

    with st.sidebar:
        st.header("⚙️ Backtest simple")
        fuente = _fuente_selector("f_bt")
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

    if not ejecutar:
        st.info("👈 Ajusta los parámetros a la izquierda y pulsa **Ejecutar backtest**.")
        return
    if ema_fast >= ema_slow:
        st.error("La EMA rápida debe ser menor que la EMA lenta.")
        return

    cfg = SimpleNamespace(
        mode="backtest", symbol=symbol, timeframe=timeframe,
        strategy={"ema_fast": ema_fast, "ema_slow": ema_slow, "rsi_period": rsi_period,
                  "rsi_max_entry": rsi_max, "atr_period": 14},
        risk={"capital_inicial": capital, "riesgo_por_operacion_pct": riesgo,
              "stop_loss_atr_mult": sl_mult, "take_profit_atr_mult": tp_mult,
              "limite_perdida_diaria_pct": limite_dia, "max_posiciones": 1},
        costes={"comision_pct": 0.1, "slippage_pct": 0.05},
    )

    try:
        with st.spinner(f"Obteniendo {velas} velas ({fuente})…"):
            df = descargar(fuente, symbol, timeframe, velas)
    except Exception as e:  # noqa: BLE001
        st.error(f"No se pudieron descargar datos: {type(e).__name__}: {str(e)[:200]}")
        st.info("Prueba con **Kraken** o **Datos de ejemplo (demo)** en la barra lateral.")
        return

    if df.empty or len(df) < 60:
        st.error("Datos insuficientes. Prueba otro par o más velas.")
        return
    if fuente.startswith("Datos de ejemplo"):
        st.warning("Estás viendo **datos simulados** (demo), no precios reales.")

    res = ejecutar_backtest(df, cfg)
    st.success(f"Backtest completado: {len(df)} velas "
               f"({df.index[0].date()} → {df.index[-1].date()}).")

    c = st.columns(6)
    c[0].metric("Rendimiento", f"{res.rendimiento_pct:+.2f}%")
    c[1].metric("Capital final", f"{res.equity_final:,.0f}")
    c[2].metric("Operaciones", res.num_operaciones)
    c[3].metric("Aciertos", f"{res.tasa_acierto_pct:.1f}%")
    pf = res.profit_factor
    c[4].metric("Profit factor", "∞" if pf == float("inf") else f"{pf:.2f}")
    c[5].metric("Peor bajón", f"-{res.max_drawdown_pct:.2f}%")

    if pf < 1.0:
        st.warning("⚠️ Profit factor < 1: con estos parámetros la estrategia "
                   "**pierde dinero**. No la lleves a real.")
    if res.num_operaciones < 20:
        st.warning(f"⚠️ Solo {res.num_operaciones} operaciones: **muy pocas para "
                   "fiarte de estos números**. Un 'Aciertos 100%' o un 'Profit "
                   "factor ∞' con tan pocas operaciones es suerte, no una ventaja. "
                   "Sube las velas históricas o usa un timeframe más corto.")

    st.subheader("Evolución del capital")
    if res.curva_equity is not None and not res.curva_equity.empty:
        st.area_chart(res.curva_equity, height=280, color="#0d9488")

    st.subheader("Precio y operaciones")
    señales = generate_signals(df, cfg.strategy)
    precio_df = pd.DataFrame({"precio": df["close"]})
    precio_df["compra"] = df["close"].where(señales["signal"] == BUY)
    precio_df["venta"] = df["close"].where(señales["signal"] == SELL)
    st.line_chart(precio_df, height=320, color=["#8a97a1", "#15a34a", "#dc2626"])

    st.subheader("Operaciones")
    if res.operaciones:
        tabla = pd.DataFrame([{
            "Entrada": o.entrada_fecha.strftime("%Y-%m-%d %H:%M"),
            "Compra": round(o.entrada_precio, 2), "Venta": round(o.salida_precio, 2),
            "Resultado (USDT)": round(o.pnl, 2), "Motivo": o.motivo_salida,
        } for o in reversed(res.operaciones)])
        st.dataframe(tabla, use_container_width=True, hide_index=True)
    else:
        st.info("No hubo operaciones con estos parámetros en este periodo.")


# ================================ PESTAÑA 2: EXPLORADOR ==========================
def pestaña_explorador() -> None:
    st.caption(
        "Prueba MUCHAS combinaciones a la vez y descubre cuáles tienen ventaja "
        "**real**. Cada una se optimiza en el 70% más antiguo y se valida en el "
        "30% más reciente (datos que no ha visto). Fíate de la columna **test**."
    )

    col1, col2 = st.columns(2)
    with col1:
        fuente = _fuente_selector("f_ex")
        pares = st.multiselect(
            "Pares a probar", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"],
            default=["BTC/USDT", "ETH/USDT"],
        )
    with col2:
        timeframes = st.multiselect(
            "Timeframes a probar", ["15m", "1h", "4h", "1d"], default=["1h", "4h"],
        )
        velas = st.slider("Velas históricas por prueba", 500, 3000, 2000, step=100, key="v_ex")

    with st.expander("Ajustes de riesgo (opcional)"):
        rc1, rc2, rc3 = st.columns(3)
        capital = rc1.number_input("Capital (USDT)", 100, 1_000_000, 1000, step=100, key="cap_ex")
        riesgo_pct = rc1.slider("Riesgo/operación (%)", 0.5, 5.0, 1.0, step=0.5, key="r_ex")
        sl = rc2.slider("Stop-loss (× ATR)", 1.0, 5.0, 2.0, step=0.5, key="sl_ex")
        tp = rc2.slider("Take-profit (× ATR)", 1.0, 6.0, 3.0, step=0.5, key="tp_ex")
        limite = rc3.slider("Límite pérdida diaria (%)", 1.0, 10.0, 3.0, step=0.5, key="lim_ex")
        min_test = rc3.slider("Mín. operaciones en test", 10, 40, 15, key="mt_ex",
                              help="Cuantas menos, más probable es que un buen "
                                   "resultado sea suerte. 15+ es lo mínimo sensato.")

    buscar = st.button("🔎  Buscar las mejores estrategias", type="primary")
    if not buscar:
        st.info("Elige pares y timeframes y pulsa **Buscar las mejores estrategias**. "
                "Probará ~20 combinaciones de parámetros por cada par y timeframe.")
        return
    if not pares or not timeframes:
        st.error("Selecciona al menos un par y un timeframe.")
        return

    riesgo = {"capital": capital, "riesgo": riesgo_pct, "sl": sl, "tp": tp, "limite": limite}
    combinaciones = [(p, tf) for p in pares for tf in timeframes]
    barra = st.progress(0.0, text="Empezando…")
    filas: list[dict] = []
    errores: list[str] = []
    sin_datos: list[str] = []

    for i, (par, tf) in enumerate(combinaciones):
        barra.progress(i / len(combinaciones), text=f"Probando {par} · {tf}…")
        try:
            df = descargar(fuente, par, tf, velas)
            nuevas = optimizer.explorar_par(df, par, tf, riesgo, min_trades_test=min_test)
            if nuevas:
                filas.extend(nuevas)
            else:
                sin_datos.append(f"{par} {tf}")  # histórico demasiado corto
        except Exception as e:  # noqa: BLE001
            errores.append(f"{par} {tf}: {type(e).__name__}")
    barra.progress(1.0, text="Listo")

    if errores:
        st.warning("No se pudieron probar algunas combinaciones (datos no "
                   f"disponibles): {', '.join(errores)}. Prueba Kraken o demo.")
    if sin_datos:
        st.warning(f"Sin histórico suficiente (se omitieron, NO se probaron): "
                   f"{', '.join(sin_datos)}.")
    if not filas:
        st.error("No se obtuvieron resultados. Cambia la fuente de datos o los pares.")
        return

    if fuente.startswith("Datos de ejemplo"):
        st.error("🔬 Estás usando **datos SIMULADOS (demo)**, no precios reales. "
                 "Estos resultados no valen para decidir nada: solo sirven para ver "
                 "cómo funciona el explorador. Cambia a **Binance** o **Kraken** "
                 "para datos reales.")

    orden = optimizer.ranking(filas)
    robustas = sum(1 for f in orden if f["veredicto"].startswith("🟢"))
    st.success(f"Probadas {len(filas)} combinaciones. "
               f"**{robustas}** aguantan la validación (🟢 robusta).")

    # --- La advertencia MÁS importante: comparaciones múltiples (data dredging).
    if robustas > 0:
        st.warning(
            f"⚠️ **Cuidado, esto es clave:** has probado **{len(filas)} combinaciones**. "
            f"Al probar tantas, es NORMAL que unas pocas salgan 🟢 **por pura suerte**, "
            f"aunque no tengan ninguna ventaja real (es la 'trampa de las comparaciones "
            f"múltiples'). Un 🟢 con pocas operaciones NO es una estrategia ganadora "
            f"probada: es, como mucho, una **candidata a seguir investigando**. "
            f"Señal de alarma: si la misma configuración da 🟢 en un par y fatal en "
            f"otro, es ruido, no ventaja."
        )
    else:
        st.info("Ninguna combinación pasó la validación. Es lo más habitual y **honesto**: "
                "esta estrategia simple no muestra ventaja clara en estos mercados. Que "
                "un análisis riguroso diga «aquí no hay filón» vale más que un número "
                "bonito que te haga perder dinero.")

    def _fmt_pf(v):
        return "∞" if v == float("inf") else round(v, 2)

    tabla = pd.DataFrame([{
        "Veredicto": f["veredicto"], "Par": f["par"], "TF": f["tf"],
        "EMA ráp.": f["ema_fast"], "EMA lenta": f["ema_slow"], "RSI máx": f["rsi_max"],
        "PF train": _fmt_pf(f["pf_train"]), "PF test": _fmt_pf(f["pf_test"]),
        "Ops test": f["ops_test"], "Retorno test %": round(f["retorno_test_pct"], 2),
        "Aciertos test %": round(f["aciertos_test"], 1),
    } for f in orden])
    st.dataframe(tabla, use_container_width=True, hide_index=True)

    st.markdown(
        "**Cómo leer esta tabla (importante):**\n"
        "- 🟢 **robusta**: rentable en train **y** en test con suficientes operaciones. "
        "Es una **candidata a investigar**, NO una estrategia ganadora demostrada.\n"
        "- 🟡 dudosa / 🔴 no robusta / ⚪ pocas ops: descártalas.\n"
        "- **Ops test** es lo primero que hay que mirar: con menos de ~15-20 operaciones, "
        "cualquier resultado es ruido por muy bueno que parezca.\n"
        "- Si **PF train** es altísimo y **PF test** malo → *overfitting* (encaja al "
        "pasado, falla en el futuro).\n"
        "- **Ninguna 🟢 se lleva a dinero real directamente.** El único camino honesto: "
        "probarla en **paper** (dinero de mentira) durante **semanas o meses** y ver si "
        "de verdad aguanta. Casi siempre no aguanta — y eso es información valiosa."
    )


# ------------------------------------ layout ------------------------------------
st.title("📊 Bot de Trading — Panel")
tab1, tab2 = st.tabs(["📈 Backtest simple", "🔬 Explorador de estrategias"])
with tab1:
    pestaña_backtest()
with tab2:
    pestaña_explorador()
