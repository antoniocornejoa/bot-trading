import numpy as np
import pandas as pd

from trading_bot.data import store, synthetic, validation


def test_resample_labels_by_open_and_drops_incomplete():
    df = synthetic.make_1m(3)
    h4 = store.resample(df, "4h")
    assert h4.index[0] == df.index[0]
    assert h4.iloc[0]["open"] == df.iloc[0]["open"]
    assert h4.iloc[0]["close"] == df.iloc[239]["close"]
    assert h4.iloc[0]["high"] == df.iloc[:240]["high"].max()
    assert len(h4) == 18
    partial = store.resample(df.iloc[:-100], "4h")  # última vela de 4h con 140 minutos: se descarta
    assert len(partial) == 17


def test_validation_detects_problems():
    df = synthetic.make_1m(1)
    bad = pd.concat([df, df.iloc[[10]]])            # duplicado
    bad = bad.drop(bad.index[100:160])              # hueco de 60 min
    bad.iloc[200, bad.columns.get_loc("low")] = bad.iloc[200]["high"] * 2  # OHLC incoherente
    rep = validation.validate(bad)
    assert rep.duplicates == 1 and rep.gaps == 1 and rep.gap_minutes == 60 and rep.bad_ohlc == 1
    assert len(validation.clean(bad)) == len(bad) - 1


def test_dataset_hash_changes_with_data():
    df = synthetic.make_1m(1)
    h1 = store.dataset_hash(df)
    df2 = df.copy(); df2.iloc[5, 3] *= 1.01
    assert h1 != store.dataset_hash(df2) and h1 == store.dataset_hash(df.copy())


def test_cross_check_flags_deviation():
    a = synthetic.make_1m(5)
    b = a.copy(); b.iloc[1440 * 2:1440 * 3, :4] *= 1.02
    dev = validation.cross_check(a, b, tol_pct=0.5)
    assert len(dev) == 1
