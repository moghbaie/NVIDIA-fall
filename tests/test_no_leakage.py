"""Leakage tests (synthetic data): perturbing anything after origin T must not change the
estimation sample, fitted normal-return model, or as-of features."""

import numpy as np
import pandas as pd
import pytest

from shockamp.pit import LeakageError, asof_join, asof_value, assert_available
from shockamp.returns import abnormal_returns, fit_market_model, log_returns


def _synthetic_returns(n=400, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    m = rng.normal(0, 0.01, n)
    s = 0.5 * m + rng.normal(0, 0.01, n)
    y = 0.001 + 1.2 * m + 0.4 * s + rng.normal(0, 0.015, n)
    return pd.DataFrame({"Y": y, "M": m, "S": s}, index=idx)


@pytest.mark.parametrize("k_event", [300, 350])
def test_market_model_invariant_to_post_origin_data(k_event):
    r = _synthetic_returns()
    ev = r.index[k_event]
    m1 = fit_market_model(r, "Y", ["M", "S"], ev)
    r2 = r.copy()
    r2.iloc[k_event - 30 :] = 99.0  # destroy everything from the embargo onward
    m2 = fit_market_model(r2, "Y", ["M", "S"], ev)
    pd.testing.assert_series_equal(m1.params, m2.params)
    assert m1.resid_sd == m2.resid_sd
    assert m1.est_end == r.index[k_event - 31]


def test_market_model_recovers_betas():
    r = _synthetic_returns(n=2000, seed=1)
    m = fit_market_model(r, "Y", ["M", "S"], r.index[1500], est_start=-1200)
    assert abs(m.params["M"] - 1.2) < 0.1 and abs(m.params["S"] - 0.4) < 0.15


def test_abnormal_return_arithmetic():
    r = _synthetic_returns()
    m = fit_market_model(r, "Y", ["M", "S"], r.index[300])
    out = abnormal_returns(r, "Y", m, r.index[299:302])
    exp = (
        m.params["const"]
        + r.loc[out.index, ["M", "S"]].to_numpy() @ m.params[["M", "S"]].to_numpy()
    )
    np.testing.assert_allclose(out.AR.to_numpy(), r.loc[out.index, "Y"].to_numpy() - exp)


def test_too_few_obs_raises():
    r = _synthetic_returns()
    r.iloc[:290] = np.nan
    with pytest.raises(ValueError):
        fit_market_model(r, "Y", ["M"], r.index[300])


def test_log_returns_rejects_nonpositive():
    with pytest.raises(ValueError):
        log_returns(pd.DataFrame({"a": [1.0, 0.0]}))


def _macro():
    # synthetic weekly series: observed Friday, released next Thursday
    obs = pd.date_range("2026-01-02", periods=10, freq="7D")
    return pd.DataFrame({"obs": obs, "available_at": obs + pd.Timedelta(days=6), "v": range(10)})


def test_asof_uses_release_date_not_observation_date():
    t = _macro()
    cutoff = t.obs.iloc[5]  # value 5 observed but not yet released
    assert asof_value(t, cutoff, "v") == 4.0


def test_asof_invariant_to_future_rows():
    t = _macro()
    cutoff = t.available_at.iloc[5]
    t2 = t.copy()
    t2.loc[t2.available_at > cutoff, "v"] = -999
    cut = pd.Series([cutoff])
    assert asof_join(cut, t, "v").iloc[0] == asof_join(cut, t2, "v").iloc[0] == 5


def test_assert_available_raises():
    t = _macro()
    with pytest.raises(LeakageError):
        assert_available(t.available_at, t.available_at.iloc[3])
