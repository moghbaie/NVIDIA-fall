"""Log returns and market-model abnormal returns with a leakage-safe estimation window."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

EST_START = -252  # sessions relative to event session (inclusive)
EST_END = -31  # inclusive; leaves a 30-session embargo before the event window
MIN_OBS = 120


def log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """ln(P_t / P_{t-1}) per column; first row dropped. Prices must be adjusted closes."""
    if (prices <= 0).any().any():
        raise ValueError("non-positive prices")
    logp: pd.DataFrame = prices.apply(np.log)
    return logp.diff().iloc[1:]


@dataclass(frozen=True)
class MarketModel:
    params: pd.Series  # const + factor betas
    resid_sd: float
    n_obs: int
    est_start: pd.Timestamp
    est_end: pd.Timestamp


def fit_market_model(
    returns: pd.DataFrame,
    target: str,
    factors: list[str],
    event_session: pd.Timestamp,
    est_start: int = EST_START,
    est_end: int = EST_END,
    min_obs: int = MIN_OBS,
) -> MarketModel:
    """OLS of target on factors over sessions [event+est_start, event+est_end] only.

    Uses positions in `returns.index` (the session grid); data at or after event+est_end+1 is never
    touched, so the fit is invariant to anything after the estimation window.
    """
    idx = returns.index
    pos = idx.get_loc(pd.Timestamp(event_session))
    if not isinstance(pos, int):
        raise KeyError(event_session)
    lo, hi = pos + est_start, pos + est_end
    if lo < 0:
        raise ValueError("estimation window starts before data")
    window = returns.iloc[lo : hi + 1][[target, *factors]].dropna()
    if len(window) < min_obs:
        raise ValueError(f"only {len(window)} valid estimation obs (< {min_obs})")
    x = np.column_stack([np.ones(len(window)), window[factors].to_numpy()])
    y = window[target].to_numpy()
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    resid = y - x @ beta
    sd = float(np.sqrt(resid @ resid / (len(y) - x.shape[1])))
    return MarketModel(
        pd.Series(beta, index=["const", *factors]), sd, len(window), idx[lo], idx[hi]
    )


def abnormal_returns(
    returns: pd.DataFrame, target: str, model: MarketModel, sessions: pd.DatetimeIndex
) -> pd.DataFrame:
    """AR_t = r_t - (a + b'f_t) on the given sessions, with z = AR / resid_sd and running CAR."""
    factors = [c for c in model.params.index if c != "const"]
    sub = returns.loc[sessions, [target, *factors]]
    pred = model.params["const"] + sub[factors].to_numpy() @ model.params[factors].to_numpy()
    ar = sub[target] - pred
    return pd.DataFrame({"ret": sub[target], "expected": pred, "AR": ar, "z": ar / model.resid_sd})


def car(ar: pd.Series, resid_sd: float) -> tuple[float, float]:
    """CAR and its standard error under iid residuals (sd * sqrt(L))."""
    return float(ar.sum()), float(resid_sd * np.sqrt(len(ar)))
