import numpy as np
import pandas as pd
import pytest

from trading_bot.backtesting.engine import BacktestResult, Trade
from trading_bot.backtesting import metrics


def _trade(pnl, risk=5.0):
    t0 = pd.Timestamp("2024-01-01", tz="UTC")
    return Trade(t0, t0, 100, t0, 100 + pnl, 1.0, 90, 90, np.nan, risk, "x", 0.1, 0.05, pnl, pnl / risk, 3, 500)


def test_expectancy_pf_winrate_streaks():
    pnls = [10, -5, -5, 10, 10, -5]
    eq = pd.Series(500 + np.cumsum([0] + pnls), index=pd.date_range("2024-01-01", periods=7, freq="1D", tz="UTC"))
    r = BacktestResult(trades=[_trade(p) for p in pnls], equity=eq, initial_capital=500, scenario="zero")
    m = metrics.compute(r, bars_per_year=365)
    assert m["trades"] == 6 and m["win_rate_pct"] == pytest.approx(50.0)
    assert m["profit_factor"] == pytest.approx(30 / 15)
    assert m["expectancy_R"] == pytest.approx((3 * 2 + 3 * -1) / 6)   # avg win 2R, avg loss -1R
    assert m["payoff"] == pytest.approx(2.0)
    assert m["max_consec_losses"] == 2 and m["max_consec_wins"] == 2
    assert m["total_return_pct"] == pytest.approx(15 / 500 * 100)
    assert m["max_drawdown_pct"] == pytest.approx(-10 / 510 * 100)
