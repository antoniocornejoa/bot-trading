import numpy as np
import pandas as pd
import pytest

from trading_bot.backtesting.costs import CostScenario

ZERO = CostScenario("zero", 0.0, 0.0, 0.0, 0.0)


def bars(rows: list[tuple[float, float, float, float]]) -> pd.DataFrame:
    """Construye velas a partir de (open, high, low, close) con volumen constante."""
    idx = pd.date_range("2024-01-01", periods=len(rows), freq="4h", tz="UTC")
    df = pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=idx)
    df["volume"] = 10.0
    df["quote_volume"] = 10.0 * df["close"]
    return df


def signals_for(df: pd.DataFrame, entry_at: list[int] = (), exit_at: list[int] = (),
                stop_dist: float = 10.0, tp_dist: float = np.nan, trail: dict | None = None) -> pd.DataFrame:
    n = len(df)
    s = pd.DataFrame({"entry": np.zeros(n, bool), "exit": np.zeros(n, bool),
                      "stop_dist": np.full(n, stop_dist), "tp_dist": np.full(n, tp_dist),
                      "trail": np.full(n, np.nan)}, index=df.index)
    s.iloc[list(entry_at), 0] = True
    s.iloc[list(exit_at), 1] = True
    for i, v in (trail or {}).items():
        s.iloc[i, 4] = v
    return s


@pytest.fixture
def zero_costs():
    return ZERO
