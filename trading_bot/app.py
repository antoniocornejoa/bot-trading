"""Panel de pruebas demo del sistema cuantitativo (Streamlit).

    streamlit run trading_bot/app.py

Tres pestañas:
  1. Backtest: elige activo, timeframe, estrategia, parámetros, riesgo, costes y periodo; ve
     métricas, curva de equity frente a buy & hold, drawdown y operaciones.
  2. Demo del bot: el bot completo (motor de riesgo, escalones por drawdown, kill switch) opera
     sobre un tramo histórico con el exchange simulado, y muestra su diario de operaciones.
  3. Informes: los informes de investigación de las Fases 1 a 9.
Todo es simulación sobre datos históricos. No opera con dinero.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import streamlit as st
import yaml

from trading_bot.backtesting import CostScenario, load_scenarios, metrics, run
from trading_bot.data import store
from trading_bot.execution.bot import TradingBot
from trading_bot.execution.exchange import SimulatedExchange
from trading_bot.monitoring.alerts import Alerter
from trading_bot.portfolio.state import StateStore
from trading_bot.risk import RiskConfig, RiskEngine
from trading_bot.strategies import REGISTRY

st.set_page_config(page_title="Bot cuantitativo · pruebas demo", page_icon="📊", layout="wide")

PARAM_HELP = {
    "ma_momentum": {"n": "Velas de la media móvil lenta (200 = elegida por el walk-forward)", "atr_mult": "Stop en múltiplos del ATR", "atr_n": "Periodo del ATR"},
    "donchian_trend": {"n_entry": "Ruptura del máximo de N velas", "n_exit": "Salida por mínimo de N velas", "atr_mult": "Stop en múltiplos del ATR", "ema_filter": "Filtro de tendencia (EMA)", "atr_n": "Periodo del ATR"},
}


@st.cache_data(show_spinner=False)
def load_bars(symbol: str, tf: str) -> pd.DataFrame:
    found = store.finest_available(ROOT / "data_store" / "parquet", "spot", symbol)
    if found is None:
        return pd.DataFrame()
    return store.resample(store.load(found[0]), tf)


def params_form(strategy_name: str, defaults: dict, key: str) -> dict:
    out = {}
    cols = st.columns(min(len(defaults), 4) or 1)
    for i, (k, v) in enumerate(defaults.items()):
        help_ = PARAM_HELP.get(strategy_name, {}).get(k, "")
        with cols[i % len(cols)]:
            if isinstance(v, bool):
                out[k] = st.checkbox(k, v, key=f"{key}_{k}")
            elif isinstance(v, int):
                out[k] = st.number_input(k, min_value=1, value=int(v), step=1, help=help_, key=f"{key}_{k}")
            elif isinstance(v, float) and not np.isnan(v):
                out[k] = st.number_input(k, value=float(v), step=0.5, help=help_, key=f"{key}_{k}")
            else:
                out[k] = v
    return out


def fmt_pct(x):
    return "–" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:+.1f} %"


# ------------------------------------------------------------------ barra lateral
st.sidebar.title("📊 Pruebas demo")
st.sidebar.caption("Simulación sobre datos históricos de Binance guardados en el repositorio. No opera con dinero.")
symbol = st.sidebar.selectbox("Activo", ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
tf = st.sidebar.selectbox("Timeframe", ["4h", "1d", "1h"], index=0)
scenario_name = st.sidebar.selectbox("Escenario de costes", ["base", "optimistic", "pessimistic"], index=0,
                                     help="Base: comisión 0,1 % + spread + slippage. Pesimista: slippage ×3.")
capital = st.sidebar.number_input("Capital inicial (USD)", min_value=50.0, value=500.0, step=50.0)
risk_pct = st.sidebar.slider("Riesgo por operación (%)", 0.25, 3.0, 0.5, 0.25,
                             help="0,5 % es el nivel elegido por el Monte Carlo. A 1 % el riesgo de tocar el kill switch sube al 12 %.")
bars = load_bars(symbol, tf)
if bars.empty:
    st.error("No hay datos para este activo. Ejecuta el workflow de descarga (data_store/TRIGGER).")
    st.stop()
dmin, dmax = bars.index[0].date(), bars.index[-1].date()
rango = st.sidebar.slider("Periodo", dmin, dmax, (max(dmin, pd.Timestamp("2022-01-01").date()), dmax))
scen = load_scenarios()[scenario_name]
lim = yaml.safe_load(open(ROOT / "trading_bot" / "config" / "research.yaml"))["exchange_limits"].get(symbol, {"min_notional": 5.0, "lot_step": 1e-5})
st.sidebar.markdown("---")
st.sidebar.markdown("**Contexto**: el tramo posterior a nov-2024 fue el *test* de la investigación y ya se abrió una vez. "
                    "Cualquier ajuste de parámetros que hagas mirando ese tramo es sobreajuste. Úsalo para entender, no para optimizar.")

tab_bt, tab_bot, tab_rep = st.tabs(["📈 Backtest", "🤖 Demo del bot", "📄 Informes"])

# ------------------------------------------------------------------ backtest
with tab_bt:
    c1, c2 = st.columns([1, 3])
    with c1:
        strat_name = st.selectbox("Estrategia", list(REGISTRY), index=list(REGISTRY).index("ma_momentum"),
                                  help="ma_momentum es la candidata validada (H-A2). El resto son la otra candidata y los benchmarks.")
    S = REGISTRY[strat_name]
    with c2:
        params = params_form(strat_name, S.default_params(), "bt")
    df = bars[(bars.index.date >= rango[0]) & (bars.index.date <= rango[1])]
    warm = max(300, int(max([v for v in params.values() if isinstance(v, (int, float)) and not isinstance(v, bool)] + [0])) + 50)
    full = bars[bars.index <= df.index[-1]] if len(df) else bars
    sig = S(**params).generate(full)
    start_i = max(0, len(full) - len(df))
    res = run(full.iloc[start_i:], sig.iloc[start_i:], scen, initial_capital=capital, risk_pct=risk_pct,
              min_notional=lim["min_notional"], lot_step=lim["lot_step"])
    m = metrics.compute(res, store.BARS_PER_YEAR[tf])
    bh = df["close"] / df["close"].iloc[0] * capital
    bh_dd = (bh / bh.cummax() - 1).min() * 100

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Retorno", fmt_pct(m["total_return_pct"]), help=f"Buy & hold: {fmt_pct((bh.iloc[-1]/capital-1)*100)}")
    k2.metric("CAGR", fmt_pct(m["cagr_pct"]))
    k3.metric("Drawdown máx.", fmt_pct(m["max_drawdown_pct"]), help=f"Buy & hold: {bh_dd:+.1f} %")
    k4.metric("Operaciones", m["trades"])
    k5.metric("Expectancy", "–" if np.isnan(m["expectancy_R"]) else f"{m['expectancy_R']:.2f} R",
              help=f"t = {m['t_stat']:.2f}" if not np.isnan(m["t_stat"]) else "")
    k6.metric("Profit factor", "–" if np.isnan(m["profit_factor"]) else f"{m['profit_factor']:.2f}")
    k7, k8, k9, k10 = st.columns(4)
    k7.metric("Win rate", fmt_pct(m["win_rate_pct"]).replace("+", ""))
    k8.metric("Payoff", "–" if np.isnan(m["payoff"]) else f"{m['payoff']:.2f}")
    k9.metric("Sharpe", "–" if np.isnan(m["sharpe"]) else f"{m['sharpe']:.2f}")
    k10.metric("Coste / beneficio bruto", "–" if not np.isfinite(m["cost_ratio"]) else f"{100*m['cost_ratio']:.0f} %")

    curva = pd.DataFrame({"Estrategia": res.equity, "Buy & hold": bh.reindex(res.equity.index)})
    st.line_chart(curva, height=300)
    dd = pd.DataFrame({"Drawdown estrategia %": metrics.drawdown_series(res.equity) * 100,
                       "Drawdown buy & hold %": (bh / bh.cummax() - 1).reindex(res.equity.index) * 100})
    st.area_chart(dd, height=180)
    if m["trades"] and m["win_rate_pct"] > 75:
        st.warning("Win rate > 75 %: según el marco, esto exige auditar fugas de información, stops demasiado anchos o muestra pequeña antes de creérselo.")
    if m["trades"] and m["trades"] < 30:
        st.info("Menos de 30 operaciones: cualquier métrica de este tramo es ruido. Amplía el periodo.")
    with st.expander(f"Operaciones ({m['trades']})"):
        t = res.trades_df()
        if len(t):
            show = t[["entry_time", "exit_time", "entry_price", "exit_price", "qty", "reason", "pnl", "r_multiple", "bars_held", "fees", "slippage_cost"]].copy()
            show["entry_time"] = show["entry_time"].dt.strftime("%Y-%m-%d %H:%M"); show["exit_time"] = show["exit_time"].dt.strftime("%Y-%m-%d %H:%M")
            st.dataframe(show.round(4), width="stretch", hide_index=True)
            st.download_button("Descargar CSV", t.to_csv(index=False), f"trades_{symbol}_{tf}_{strat_name}.csv")
    if res.skipped_min_notional:
        st.caption(f"{res.skipped_min_notional} señales no se ejecutaron por no llegar al mínimo de orden de Binance ({lim['min_notional']} USD). Con {capital:.0f} USD y {risk_pct} % de riesgo esto pasa en la realidad.")

# ------------------------------------------------------------------ demo del bot
with tab_bot:
    st.markdown("El **bot completo** (motor de riesgo, escalones por drawdown, límites diarios, kill switch, registro de operaciones) "
                "opera sobre el tramo elegido con un exchange simulado, vela a vela, con la configuración de `config/live.yaml`. "
                "Es lo mismo que correría en paper, pero sobre el pasado.")
    live_cfg = yaml.safe_load(open(ROOT / "trading_bot" / "config" / "live.yaml"))
    cA, cB, cC = st.columns(3)
    with cA:
        bot_symbols = st.multiselect("Activos", ["BTC/USDT", "ETH/USDT", "SOL/USDT"], default=["BTC/USDT", "ETH/USDT"])
    with cB:
        dd_kill = st.slider("Kill switch por drawdown (%)", 10, 40, int(live_cfg["risk"]["dd_kill"] * 100), 5)
    with cC:
        max_bars = st.number_input("Máximo de velas a simular", 200, 6000, 1500, 100, help="Limita el tiempo de cálculo en el móvil.")
    if st.button("▶ Ejecutar demo del bot", type="primary"):
        feeds = {}
        for s in bot_symbols:
            b = load_bars(s.replace("/", ""), tf)
            b = b[(b.index.date >= rango[0]) & (b.index.date <= rango[1])]
            feeds[s] = b.iloc[: int(max_bars) + 300]
        if not feeds or min(len(f) for f in feeds.values()) < 320:
            st.error("Tramo demasiado corto para el calentamiento de indicadores (mínimo ~320 velas).")
        else:
            x = SimulatedExchange(feeds, cash=capital, slippage_pct=scen.slippage_pct + scen.half_spread_pct)
            x.cursor = {s: 300 for s in feeds}
            st_store = StateStore(":memory:")
            rc = RiskConfig(**{**live_cfg["risk"], "risk_pct": risk_pct, "dd_kill": dd_kill / 100, "dd_halt": min(live_cfg["risk"]["dd_halt"], dd_kill / 100 - 0.02)})
            risk = RiskEngine(rc, initial_equity=capital)
            strat = REGISTRY[live_cfg["strategy"]](**live_cfg["params"])
            alerter = Alerter(st_store, telegram=False)
            bot = TradingBot(x, strat, list(feeds), tf, risk, st_store, alerter, mode="demo")
            n = min(len(f) for f in feeds.values())
            prog = st.progress(0.0, "simulando…")
            import io, contextlib
            with contextlib.redirect_stdout(io.StringIO()):
                step = 0
                while max(x.cursor.values()) < n - 1:
                    x.phase = "open"; bot.run_once(); x.phase = "intrabar"; bot.run_once(); x.advance()
                    step += 1
                    if step % 50 == 0:
                        prog.progress(min(step / (n - 300), 1.0), f"vela {step} de {n-300}")
            prog.progress(1.0, "listo")
            x.phase = "open"
            eq, cash = bot.equity()
            t = st_store.trades()
            curve = st_store.equity_curve()
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Equity final", f"{eq:,.2f} USD", fmt_pct((eq / capital - 1) * 100))
            c2.metric("Operaciones cerradas", len(t))
            c3.metric("Drawdown máx.", fmt_pct((curve / curve.cummax() - 1).min() * 100) if len(curve) else "–")
            c4.metric("Win rate", fmt_pct(100 * (t["pnl"] > 0).mean()).replace("+", "") if len(t) else "–")
            c5.metric("Kill switch", "ACTIVADO" if risk.state.killed else "no", help=risk.state.kill_reason or "")
            if len(curve):
                st.line_chart(curve.rename("Equity del bot"), height=280)
            ev = st_store.events(200)
            st.markdown("**Diario del bot** (últimos eventos)")
            st.dataframe(ev[["timestamp", "level", "message"]], width="stretch", hide_index=True, height=320)
            if len(t):
                with st.expander("Operaciones registradas (todos los campos)"):
                    st.dataframe(t, width="stretch", hide_index=True)

# ------------------------------------------------------------------ informes
with tab_rep:
    rep_dir = ROOT / "research" / "reports"
    files = {"Marco de investigación": ROOT / "research" / "00_MARCO_INVESTIGACION.md"}
    files.update({p.name: p for p in sorted(rep_dir.glob("*.md"))} if rep_dir.exists() else {})
    choice = st.selectbox("Informe", list(files))
    st.markdown(files[choice].read_text(), unsafe_allow_html=False)
