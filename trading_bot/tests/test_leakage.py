import pandas as pd

from trading_bot.backtesting import check_no_lookahead
from trading_bot.data import store, synthetic
from trading_bot.strategies import DonchianTrend, TrendPullback
from trading_bot.strategies.base import Strategy


class Leaky(Strategy):
    name = "leaky"

    @classmethod
    def default_params(cls):
        return {}

    def generate(self, df):
        s = self.empty_signals(df.index)
        s["entry"] = df["close"] < df["close"].shift(-1)  # mira la barra siguiente
        s["stop_dist"] = 1.0
        return s


def _df():
    return store.resample(synthetic.make_1m(90), "4h")


def test_registered_strategies_are_causal():
    df = _df()
    for S in (DonchianTrend, TrendPullback):
        assert check_no_lookahead(S(), df) == []


def test_leaky_strategy_is_detected():
    assert check_no_lookahead(Leaky(), _df()) != []
