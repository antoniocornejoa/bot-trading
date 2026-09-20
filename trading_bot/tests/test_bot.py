"""Tests del bot de ejecución: órdenes duplicadas, reconexión, kill switch, reinicio con estado
y consistencia con el motor de backtest sobre las mismas velas."""
import numpy as np
import pandas as pd
import pytest

from trading_bot.backtesting import CostScenario, run
from trading_bot.data import store, synthetic
from trading_bot.execution.bot import TradingBot
from trading_bot.execution.exchange import ExchangeError, SimulatedExchange
from trading_bot.monitoring.alerts import Alerter
from trading_bot.portfolio.state import StateStore
from trading_bot.risk import RiskConfig, RiskEngine
from trading_bot.strategies import MA200Momentum
from trading_bot.strategies.base import Strategy


class AlwaysLong(Strategy):
    """Entra en cuanto puede, stop a 2 % del precio, sin salida por señal. Para tests de mecánica."""
    name = "always_long"

    @classmethod
    def default_params(cls):
        return {}

    def generate(self, df):
        s = self.empty_signals(df.index)
        s["entry"] = True
        s["stop_dist"] = df["close"] * 0.02
        return s


def make_bot(feed, strategy=None, risk_cfg=None, store_=None, cash=500.0, start=60):
    x = SimulatedExchange({"BTC/USDT": feed}, cash=cash)
    x.cursor = {"BTC/USDT": start}
    st = store_ or StateStore(":memory:")
    risk = RiskEngine(risk_cfg or RiskConfig(risk_pct=1.0, dd_tiers=((1.0, 1.0),), dd_halt=0.99, dd_kill=0.995,
                                             daily_loss_limit_pct=100, weekly_loss_limit_pct=100), initial_equity=cash)
    bot = TradingBot(x, strategy or AlwaysLong(), ["BTC/USDT"], "4h", risk, st, Alerter(st, telegram=False), mode="sim")
    return bot, x, st


@pytest.fixture
def feed():
    return store.resample(synthetic.make_1m(60, seed=11), "4h")


def test_no_duplicate_order_when_cycle_repeats_on_same_bar(feed):
    bot, x, st = make_bot(feed)
    bot.run_once(); bot.run_once(); bot.run_once()
    assert len(st.positions()) == 1 and len(x.orders) == 1


def test_restart_recovers_position_from_order_if_crash_before_persist(feed):
    bot, x, st = make_bot(feed)
    bot.run_once()
    pos = st.positions()["BTC/USDT"]
    st.delete_position("BTC/USDT")           # simula muerte entre la orden y el registro
    bot2 = TradingBot(x, AlwaysLong(), ["BTC/USDT"], "4h", bot.risk, st, Alerter(st, telegram=False), mode="sim")
    bot2.run_once()
    assert len(x.orders) == 1                 # no reenvía la orden
    assert st.positions()["BTC/USDT"]["qty"] == pytest.approx(pos["qty"])


def test_stop_closes_and_logs_full_trade(feed):
    bot, x, st = make_bot(feed)
    bot.run_once()
    pos = st.positions()["BTC/USDT"]
    # fuerza un mínimo por debajo del stop en la vela siguiente
    i = x.cursor["BTC/USDT"] + 1
    x.feeds["BTC/USDT"].iloc[i, x.feeds["BTC/USDT"].columns.get_loc("low")] = pos["stop"] * 0.99
    x.advance(); x.phase = "open"; bot.run_once(); x.phase = "intrabar"; bot.run_once()
    t = st.trades()
    assert len(t) == 1 and t.iloc[0]["reason"] == "stop"
    assert t.iloc[0]["exit_price"] == pytest.approx(pos["stop"] * (1 - 0.0003))
    for col in ("signal_time", "entry_time", "exit_time", "entry_price", "exit_price", "stop_initial", "qty", "risk_usd",
                "fees", "slippage_cost", "pnl", "r_multiple", "params", "features"):
        assert pd.notna(t.iloc[0][col])
    assert t.iloc[0]["r_multiple"] == pytest.approx(-1.0, abs=0.15)
    assert st.positions() == {}


def test_reconnection_counts_errors_and_recovers(feed):
    bot, x, st = make_bot(feed)
    x.fail_next = 3
    bot.run_once()                      # falla la primera llamada del ciclo
    assert bot.risk.state.consecutive_errors == 1 and not bot.risk.state.killed
    x.fail_next = 0
    bot.run_once()
    assert bot.risk.state.consecutive_errors == 0 and len(st.positions()) == 1


def test_repeated_errors_trigger_kill_switch(feed):
    bot, x, st = make_bot(feed)
    bot.run_once()
    assert len(st.positions()) == 1
    x.fail_next = 100
    for _ in range(5):
        bot.run_once()
    assert bot.risk.state.killed
    x.fail_next = 0
    bot.run_once()                      # con conexión de vuelta: cierra todo y no vuelve a abrir
    assert st.positions() == {} and st.trades().iloc[0]["reason"] == "kill"
    x.advance(); bot.run_once()
    assert st.positions() == {} and any(l == "kill" for l, _ in bot.alert.sent)


def test_drawdown_kill_switch_flattens(feed):
    bot, x, st = make_bot(feed, risk_cfg=RiskConfig(risk_pct=1.0, dd_kill=0.10, dd_halt=0.08))
    bot.run_once()
    x.cash -= 200                       # pérdida externa del 40 %
    x.advance(); bot.run_once()
    assert bot.risk.state.killed and st.positions() == {}


def test_state_persists_across_restart(feed, tmp_path):
    db = tmp_path / "state.sqlite"
    st = StateStore(db)
    bot, x, _ = make_bot(feed, store_=st)
    bot.run_once()
    st2 = StateStore(db)
    bot2 = TradingBot(x, AlwaysLong(), ["BTC/USDT"], "4h", RiskEngine(RiskConfig(), 500), st2, Alerter(st2, telegram=False))
    bot2.reconcile()
    assert "BTC/USDT" in st2.positions() and bot2.risk.state.peak_equity >= 500


def test_reconcile_detects_externally_closed_position(feed):
    bot, x, st = make_bot(feed)
    bot.run_once()
    x.holdings["BTC"] = 0.0             # alguien vendió fuera del bot
    bot.reconcile()
    assert st.positions() == {} and st.trades().iloc[0]["reason"] == "external"


def test_replay_matches_backtest_engine():
    """Mismo histórico, misma estrategia: las operaciones del bot en repetición deben coincidir con el motor."""
    feed = store.resample(synthetic.make_1m(400, seed=21), "4h")
    strat = MA200Momentum(n=50, atr_mult=2.0)
    bot, x, st = make_bot(feed, strategy=strat, start=100)
    x.slippage_pct = 0.03
    n = len(feed)
    while x.cursor["BTC/USDT"] < n - 1:
        x.phase = "open"; bot.run_once(); x.phase = "intrabar"; bot.run_once(); x.advance()
    tb = st.trades()
    sig = strat.generate(feed)
    r = run(feed.iloc[99:], sig.iloc[99:], CostScenario("sim", 0.1, 0.0, 0.03, 0.0), initial_capital=500, risk_pct=1.0)
    te = r.trades_df(); te = te[te["reason"] != "end"]
    bot_entries = pd.to_datetime(tb["entry_time"]).dt.tz_localize(None).tolist()
    eng_entries = te["entry_time"].dt.tz_localize(None).tolist()
    common = set(bot_entries) & set(eng_entries)
    assert len(common) >= 0.9 * max(len(bot_entries), len(eng_entries))
    tb_i = tb.assign(k=bot_entries).set_index("k"); te_i = te.assign(k=eng_entries).set_index("k")
    for k in common:
        assert tb_i.loc[k, "r_multiple"] == pytest.approx(te_i.loc[k, "r_multiple"], abs=0.05), k
