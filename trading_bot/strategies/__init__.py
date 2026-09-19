from .base import Strategy
from .pullback import TrendPullback
from .trend import DonchianTrend

REGISTRY = {DonchianTrend.name: DonchianTrend, TrendPullback.name: TrendPullback}

__all__ = ["Strategy", "DonchianTrend", "TrendPullback", "REGISTRY"]
