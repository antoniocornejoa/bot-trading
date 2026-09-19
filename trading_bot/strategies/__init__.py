from .base import Strategy
from .benchmarks import MA200Momentum, RSI2MeanReversion, RandomSameFrequency, BuyAndHold
from .pullback import TrendPullback
from .trend import DonchianTrend

REGISTRY = {c.name: c for c in (DonchianTrend, TrendPullback, MA200Momentum, RSI2MeanReversion, RandomSameFrequency, BuyAndHold)}

__all__ = ["Strategy", "DonchianTrend", "TrendPullback", "MA200Momentum", "RSI2MeanReversion",
           "RandomSameFrequency", "BuyAndHold", "REGISTRY"]
