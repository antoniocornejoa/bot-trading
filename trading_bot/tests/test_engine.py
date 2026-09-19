import numpy as np
import pytest

from trading_bot.backtesting import run
from trading_bot.backtesting.costs import CostScenario
from .conftest import bars, signals_for

FLAT = [(100, 101, 99, 100)] * 3  # barras 0-2 planas; la entrada se decide en 1 y se ejecuta en 2


def test_stop_hit_fills_at_stop_level_and_R_is_minus_one(zero_costs):
    df = bars(FLAT + [(100, 102, 85, 95), (95, 96, 94, 95)])
    r = run(df, signals_for(df, entry_at=[1], stop_dist=10), zero_costs, initial_capital=500, risk_pct=1.0)
    assert len(r.trades) == 1
    t = r.trades[0]
    assert t.entry_price == 100 and t.qty == pytest.approx(0.5)  # 1 % de 500 = 5 USD / 10 de stop
    assert t.reason == "stop" and t.exit_price == 90
    assert t.pnl == pytest.approx(-5.0) and t.r_multiple == pytest.approx(-1.0)
    assert r.equity.iloc[-1] == pytest.approx(495.0)


def test_take_profit_fills_at_level(zero_costs):
    df = bars(FLAT + [(100, 125, 95, 110), (110, 111, 109, 110)])
    r = run(df, signals_for(df, entry_at=[1], stop_dist=10, tp_dist=20), zero_costs)
    t = r.trades[0]
    assert t.reason == "take_profit" and t.exit_price == 120 and t.r_multiple == pytest.approx(2.0)


def test_stop_and_tp_same_bar_assumes_stop(zero_costs):
    df = bars(FLAT + [(100, 125, 85, 110), (110, 111, 109, 110)])
    r = run(df, signals_for(df, entry_at=[1], stop_dist=10, tp_dist=20), zero_costs)
    assert r.trades[0].reason == "stop" and r.trades[0].r_multiple == pytest.approx(-1.0)


def test_gap_through_stop_fills_at_open(zero_costs):
    df = bars(FLAT + [(80, 82, 78, 80), (80, 81, 79, 80)])
    r = run(df, signals_for(df, entry_at=[1], stop_dist=10), zero_costs)
    t = r.trades[0]
    assert t.reason == "stop" and t.exit_price == 80 and t.r_multiple == pytest.approx(-2.0)


def test_exit_signal_executes_next_open(zero_costs):
    df = bars(FLAT + [(100, 101, 99, 100), (104, 105, 103, 104), (104, 105, 103, 104)])
    r = run(df, signals_for(df, entry_at=[1], exit_at=[3], stop_dist=10), zero_costs)
    t = r.trades[0]
    assert t.reason == "signal" and t.exit_time == df.index[4] and t.exit_price == 104
    assert t.pnl == pytest.approx(2.0)


def test_trailing_stop_only_rises(zero_costs):
    df = bars(FLAT + [(100, 110, 99, 108), (108, 112, 107, 110), (110, 111, 100, 101), (101, 102, 100, 101)])
    sig = signals_for(df, entry_at=[1], stop_dist=10, trail={3: 104.0, 4: 102.0})  # el trail baja en 4: se ignora
    r = run(df, sig, zero_costs)
    t = r.trades[0]
    assert t.stop_final == 104.0 and t.reason == "stop" and t.exit_price == 104.0


def test_min_notional_skips_trade(zero_costs):
    df = bars(FLAT + [(100, 101, 99, 100)] * 2)
    r = run(df, signals_for(df, entry_at=[1], stop_dist=10), zero_costs, min_notional=100.0)
    assert r.trades == [] and r.skipped_min_notional == 1


def test_lot_rounding(zero_costs):
    df = bars(FLAT + [(100, 101, 99, 100)] * 2)
    r = run(df, signals_for(df, entry_at=[1], stop_dist=9.0), zero_costs, lot_step=0.1)  # 5/9 = 0.555 -> 0.5
    assert r.trades[0].qty == pytest.approx(0.5)


def test_position_capped_by_cash(zero_costs):
    df = bars(FLAT + [(100, 101, 99, 100)] * 2)
    r = run(df, signals_for(df, entry_at=[1], stop_dist=0.5), zero_costs, initial_capital=500)  # 5/0.5 = 10 uds = 1000 USD
    assert r.trades[0].qty * 100 <= 500 + 1e-9


def test_accounting_closes_with_costs():
    costs = CostScenario("base", fee_pct=0.1, half_spread_pct=0.01, slippage_pct=0.03, impact_coef=0.0)
    df = bars(FLAT + [(100, 125, 95, 110), (110, 111, 109, 110)])
    r = run(df, signals_for(df, entry_at=[1], stop_dist=10, tp_dist=20), costs, initial_capital=500)
    t = r.trades[0]
    assert t.entry_price == pytest.approx(100 * 1.0004)
    assert t.exit_price == pytest.approx((t.entry_price + 20) * (1 - 0.0004))  # objetivo relativo al fill real
    assert r.equity.iloc[-1] == pytest.approx(500 + t.pnl)
    assert t.fees > 0 and t.slippage_cost > 0
    assert t.pnl == pytest.approx((t.exit_price - t.entry_price) * t.qty - t.fees)


def test_open_position_closed_at_end(zero_costs):
    df = bars(FLAT + [(100, 101, 99, 103)])
    r = run(df, signals_for(df, entry_at=[1], stop_dist=10), zero_costs)
    assert r.trades[0].reason == "end" and r.trades[0].exit_price == 103


def test_no_entry_without_stop_distance(zero_costs):
    df = bars(FLAT + [(100, 101, 99, 100)] * 2)
    r = run(df, signals_for(df, entry_at=[1], stop_dist=np.nan), zero_costs)
    assert r.trades == []
