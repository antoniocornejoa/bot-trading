import numpy as np
import pandas as pd
import pytest

from trading_bot.backtesting import check_no_lookahead, dsr, grid, load_scenarios, montecarlo, sensitivity, walkforward
from trading_bot.data import store, synthetic
from trading_bot.strategies import BuyAndHold, DonchianTrend, MA200Momentum, RSI2MeanReversion, RandomSameFrequency

BPY = store.BARS_PER_YEAR["4h"]


@pytest.fixture(scope="module")
def df():
    return store.resample(synthetic.make_1m(720, seed=3), "4h")


def test_benchmarks_are_causal(df):
    for S in (BuyAndHold, MA200Momentum, RSI2MeanReversion, RandomSameFrequency):
        assert check_no_lookahead(S(), df) == []


def test_expand_grid_and_split(df):
    assert len(grid.expand_grid({"a": [1, 2, 3], "b": [True, False]})) == 6
    s = grid.split_by_time(df)
    assert s["train"].stop == s["validation"].start and s["validation"].stop == s["test"].start == len(df) - s["test"].stop + s["test"].start


def test_signals_on_window_equal_full_signals_sliced(df):
    """La rejilla calcula señales sobre todo el histórico y recorta: debe coincidir con calcularlas en el tramo (causalidad)."""
    strat = DonchianTrend()
    full = strat.generate(df).iloc[1000:1500]
    sub = strat.generate(df.iloc[:1500]).iloc[1000:1500]
    pd.testing.assert_frame_equal(full, sub)


def test_walk_forward_chains_equity_and_windows(df):
    sc = load_scenarios()["base"]
    wf = walkforward.walk_forward(DonchianTrend, {"n_entry": [20, 55], "n_exit": [10, 20]}, df, sc, BPY,
                                  train_bars=1500, test_bars=500, min_trades=5)
    assert wf.summary["windows"] == (len(df) - 1500) // 500
    assert wf.equity.index.is_monotonic_increasing and wf.equity.iloc[0] == pytest.approx(500, rel=0.05)
    assert all(w.test.start == w.train.stop for w in wf.windows)
    assert len(wf.trades) == wf.summary["oos_trades"]


def test_random_like_matches_frequency(df):
    strat = DonchianTrend()
    sc = load_scenarios()["base"]
    res = grid.run_config(DonchianTrend, strat.params, df, sc)
    t = res.trades_df()
    r = RandomSameFrequency.like(t, len(df), seed=1)
    assert abs(r.params["p_entry"] * len(df) - len(t)) < 1


def test_montecarlo_percentiles_and_stress():
    t = pd.DataFrame({"pnl": [10, -5, -5, 10, 10, -5, 8, -4] * 10, "equity_at_entry": 500.0})
    mc = montecarlo.simulate(t, n_paths=300, seed=1)
    s = mc.summary
    assert s["final_p5"] <= s["final_p50"] <= s["final_p95"]
    assert s["max_dd_p95_pct"] <= s["max_dd_p50_pct"] <= 0
    assert 0 <= s["ruin_prob"] <= 1
    tab = montecarlo.stress_table(t, n_paths=200)
    assert len(tab) == len(montecarlo.STRESS)
    assert tab.set_index("scenario").loc["avg_loss_+10%", "final_p50"] < tab.set_index("scenario").loc["base", "final_p50"]


def test_sensitivity_detects_fragility(df):
    sc = load_scenarios()["base"]
    tab = sensitivity.sensitivity(DonchianTrend, {"n_entry": 55, "n_exit": 20, "atr_mult": 3.0}, df, sc, BPY)
    assert set(tab["param"]) == {"n_entry", "n_exit", "atr_mult"}
    v = sensitivity.verdict(tab, 0.5)
    assert "fragile" in v


def test_dsr_penalises_many_trials():
    rng = np.random.default_rng(0)
    r = rng.normal(0.08, 1.0, 400)
    one = dsr.deflated_sharpe(r, n_trials=1, var_sharpe_trials=0.01)
    many = dsr.deflated_sharpe(r, n_trials=500, var_sharpe_trials=0.01)
    assert one["dsr"] > many["dsr"]
    assert dsr.expected_max_sharpe(1, 0.01) == 0.0
