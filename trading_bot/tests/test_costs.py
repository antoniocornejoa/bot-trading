import pytest

from trading_bot.backtesting.costs import CostScenario, load_scenarios


def test_fills_are_adverse():
    c = CostScenario("x", fee_pct=0.1, half_spread_pct=0.01, slippage_pct=0.03, impact_coef=0.05)
    assert c.buy_fill(100, notional=50, prev_quote_volume=1e6) > 100
    assert c.sell_fill(100, notional=50, prev_quote_volume=1e6) < 100
    assert c.sell_fill(100, 50, 1e6, is_stop=True) <= c.sell_fill(100, 50, 1e6)


def test_impact_scales_with_size():
    c = CostScenario("x", 0.1, 0.01, 0.03, impact_coef=0.05)
    small = c.buy_fill(100, notional=100, prev_quote_volume=1e6)
    big = c.buy_fill(100, notional=100_000, prev_quote_volume=1e6)
    assert big > small


def test_scenarios_ordered():
    s = load_scenarios()
    assert s["optimistic"].round_trip_pct() < s["base"].round_trip_pct() < s["pessimistic"].round_trip_pct()
    assert s["base"].round_trip_pct() == pytest.approx(0.28)
