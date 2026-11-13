"""Trading-session calendar and event-to-session mapping.

Unit of time = an exchange session (NYSE for US listings). A session is *complete* only after its
16:00 America/New_York close. Origin T for an event = the last complete session strictly before
the information became public; everything in sessions <= T is observable.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

EXCHANGE_TZ = "America/New_York"
CLOSE_HOUR = 16


def as_sessions(dates: pd.DatetimeIndex | pd.Series | list) -> pd.DatetimeIndex:
    """Normalize to a sorted, unique, tz-naive DatetimeIndex of session dates."""
    idx = pd.DatetimeIndex(pd.to_datetime(dates))
    if idx.tz is not None:
        idx = idx.tz_localize(None)
    return idx.normalize().unique().sort_values()


def session_close_utc(session: pd.Timestamp) -> pd.Timestamp:
    """UTC timestamp of the regular close of a session date."""
    local = pd.Timestamp(session).normalize().tz_localize(EXCHANGE_TZ) + pd.Timedelta(
        hours=CLOSE_HOUR
    )
    return local.tz_convert("UTC")


def complete_sessions(sessions: pd.DatetimeIndex, now_utc: pd.Timestamp) -> pd.DatetimeIndex:
    """Drop sessions whose close is after `now_utc` (an unfinished session is never used)."""
    now = pd.Timestamp(now_utc)
    if now.tz is None:
        raise ValueError("now_utc must be timezone-aware")
    keep = [s for s in sessions if session_close_utc(s) <= now]
    return pd.DatetimeIndex(keep)


@dataclass(frozen=True)
class EventSession:
    """Mapping of a public-information timestamp to the session grid."""

    event_session: pd.Timestamp  # first session whose close reflects the information
    origin: pd.Timestamp  # last complete session strictly before the information (T)
    time_known: bool  # False -> only a date is known; use a window covering [-1, +1]


def nyse_schedule(start: str | pd.Timestamp, end: str | pd.Timestamp) -> pd.DataFrame:
    """Official NYSE sessions with their scheduled close in UTC (early closes included).

    Source: `exchange_calendars` XNYS. Index = tz-naive session dates; column `close_utc`.
    """
    import warnings

    import exchange_calendars as xc  # local import: heavy dependency

    with warnings.catch_warnings():  # third-party pandas-4 deprecation inside exchange_calendars
        warnings.simplefilter("ignore", category=DeprecationWarning)
        warnings.filterwarnings("ignore", message=".*Series.values returning an ndarray.*")
        cal = xc.get_calendar("XNYS", start=pd.Timestamp(start), end=pd.Timestamp(end))
        sched = cal.schedule.loc[pd.Timestamp(start) : pd.Timestamp(end)]
    out = pd.DataFrame({"close_utc": sched["close"].dt.tz_convert("UTC")})
    out.index = as_sessions(pd.DatetimeIndex(out.index))
    return out


def map_event(
    public_at: pd.Timestamp | str,
    sessions: pd.DatetimeIndex,
    time_known: bool = True,
    closes_utc: pd.Series | None = None,
) -> EventSession:
    """Map the first-public timestamp of an event to (event session, origin T).

    Rules (America/New_York):
    - tz-aware timestamp on a session date before 16:00 -> that session is the event session
      (pre-market or intraday news moves that session's close).
    - at/after 16:00, or on a non-session day -> next session.
    - with `closes_utc` (from `nyse_schedule`), the session's actual close is used, so 14:00 ET
      on a 13:00 early-close day maps to the next session.
    - date-only (time_known=False): event session = first session on/after that date. Callers
      must then use a window that starts at -1 to absorb the timing ambiguity.
    Origin T is always the session immediately before the event session.
    """
    sessions = as_sessions(sessions)
    ts = pd.Timestamp(public_at)
    if time_known:
        if ts.tz is None:
            raise ValueError("time_known=True requires a timezone-aware timestamp")
        local = ts.tz_convert(EXCHANGE_TZ)
        day = local.tz_localize(None).normalize()
        if closes_utc is not None and day in closes_utc.index:
            after_close = ts.tz_convert("UTC") >= closes_utc.loc[day]  # early closes honoured
        else:
            after_close = local.hour >= CLOSE_HOUR
        candidates = sessions[sessions > day] if after_close else sessions[sessions >= day]
    else:
        day = (ts.tz_convert(EXCHANGE_TZ).tz_localize(None) if ts.tz else ts).normalize()
        candidates = sessions[sessions >= day]
    if len(candidates) == 0:
        raise ValueError(f"no session on/after {day.date()} in calendar")
    event_session = candidates[0]
    pos = sessions.get_loc(event_session)
    if not isinstance(pos, int) or pos == 0:
        raise ValueError("event session has no prior session in calendar")
    return EventSession(event_session, sessions[pos - 1], time_known)


def offset(sessions: pd.DatetimeIndex, anchor: pd.Timestamp, k: int) -> pd.Timestamp:
    """Session k steps from `anchor` (k<0 = earlier). Raises if out of range."""
    sessions = as_sessions(sessions)
    pos = sessions.get_loc(pd.Timestamp(anchor).normalize())
    if not isinstance(pos, int):
        raise KeyError(anchor)
    j = pos + k
    if j < 0 or j >= len(sessions):
        raise IndexError(f"offset {k} from {anchor} outside calendar")
    return sessions[j]
