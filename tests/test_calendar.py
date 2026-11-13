"""Event-to-session mapping (synthetic calendar)."""

import pandas as pd
import pytest

from shockamp.calendar import complete_sessions, map_event, offset

SESS = pd.bdate_range("2026-11-02", "2026-11-20")  # synthetic: weekdays only


def test_premarket_maps_same_session():
    e = map_event(pd.Timestamp("2026-11-10 08:00", tz="America/New_York"), SESS)
    assert e.event_session == pd.Timestamp("2026-11-10")
    assert e.origin == pd.Timestamp("2026-11-09")


def test_after_close_maps_next_session():
    e = map_event(pd.Timestamp("2026-11-10 16:05", tz="America/New_York"), SESS)
    assert e.event_session == pd.Timestamp("2026-11-11")
    assert e.origin == pd.Timestamp("2026-11-10")


def test_utc_input_converted():
    # 2026-11-10 21:30 UTC = 16:30 ET -> after close
    e = map_event(pd.Timestamp("2026-11-10 21:30", tz="UTC"), SESS)
    assert e.event_session == pd.Timestamp("2026-11-11")


def test_weekend_maps_monday():
    e = map_event(pd.Timestamp("2026-11-08"), SESS, time_known=False)
    assert e.event_session == pd.Timestamp("2026-11-09")
    assert e.origin == pd.Timestamp("2026-11-06")
    assert not e.time_known


def test_naive_with_time_known_rejected():
    with pytest.raises(ValueError):
        map_event(pd.Timestamp("2026-11-10 08:00"), SESS)


def test_unfinished_session_dropped():
    now = pd.Timestamp("2026-11-13 15:00", tz="America/New_York")
    done = complete_sessions(SESS, now)
    assert done[-1] == pd.Timestamp("2026-11-12")
    now2 = pd.Timestamp("2026-11-13 16:00", tz="America/New_York")
    assert complete_sessions(SESS, now2)[-1] == pd.Timestamp("2026-11-13")


def test_offset():
    assert offset(SESS, pd.Timestamp("2026-11-09"), -1) == pd.Timestamp("2026-11-06")
    with pytest.raises(IndexError):
        offset(SESS, SESS[0], -1)
