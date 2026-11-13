"""Point-in-time helpers: join values on their *availability* timestamp, never their event time."""

from __future__ import annotations

import pandas as pd


class LeakageError(AssertionError):
    """Raised when a value not yet available at the cutoff would be used."""


def assert_available(available_at: pd.Series, cutoff: pd.Timestamp, what: str = "value") -> None:
    """Fail loudly if any availability timestamp is after the cutoff."""
    late = available_at[available_at > cutoff]
    if len(late):
        raise LeakageError(f"{len(late)} {what}(s) available after cutoff {cutoff}: {late.min()}")


def asof_value(
    table: pd.DataFrame,
    cutoff: pd.Timestamp,
    value_col: str,
    available_col: str = "available_at",
    max_age: pd.Timedelta | None = None,
) -> float:
    """Last value whose availability timestamp is <= cutoff (NaN if none / too stale)."""
    known = table[table[available_col] <= cutoff]
    if known.empty:
        return float("nan")
    row = known.sort_values(available_col).iloc[-1]
    if max_age is not None and cutoff - row[available_col] > max_age:
        return float("nan")
    return float(row[value_col])


def asof_join(
    cutoffs: pd.Series,
    table: pd.DataFrame,
    value_col: str,
    available_col: str = "available_at",
) -> pd.Series:
    """Vectorized as-of join: for each cutoff, the latest value available at or before it."""
    left = pd.DataFrame({"cutoff": pd.to_datetime(cutoffs).values, "_i": range(len(cutoffs))})
    right = table[[available_col, value_col]].sort_values(available_col)
    merged = pd.merge_asof(
        left.sort_values("cutoff"),
        right,
        left_on="cutoff",
        right_on=available_col,
        direction="backward",
        allow_exact_matches=True,
    ).sort_values("_i")
    out = pd.Series(merged[value_col].to_numpy(), index=cutoffs.index, name=value_col)
    return out
