"""Synthetic tests for the Step 1(e) data layer (no network)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from shockamp import secrets
from shockamp.calendar import map_event, nyse_schedule
from shockamp.data import cache
from shockamp.data.fred import available_session, first_release, point_in_time_daily, vintage_asof
from shockamp.data.prices import validate_prices

# ------------------------------------------------------------------------------- calendar


def test_early_close_maps_afternoon_news_to_next_session() -> None:
    sch = nyse_schedule("2026-11-20", "2026-12-04")
    sessions = sch.index
    # 2026-11-27 closes 13:00 ET; 14:00 ET (19:00 UTC) news must hit the next session
    ev = map_event(pd.Timestamp("2026-11-27 19:00", tz="UTC"), sessions, closes_utc=sch.close_utc)
    assert ev.event_session == pd.Timestamp("2026-11-30")
    # without the schedule the naive 16:00 rule would get it wrong
    naive = map_event(pd.Timestamp("2026-11-27 19:00", tz="UTC"), sessions)
    assert naive.event_session == pd.Timestamp("2026-11-27")


def test_schedule_excludes_holidays() -> None:
    s = nyse_schedule("2026-11-20", "2026-11-30").index
    assert pd.Timestamp("2026-11-26") not in s  # Thanksgiving
    assert pd.Timestamp("2026-11-27") in s


# ------------------------------------------------------------------------------- ALFRED


def _vintages() -> pd.DataFrame:
    """Obs 01-02: published 01-08 as 1.0, revised 01-15 to 1.5. Obs 01-09: published 01-15."""
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-02", "2026-01-02", "2026-01-09"]),
            "realtime_start": pd.to_datetime(["2026-01-08", "2026-01-15", "2026-01-15"]),
            "realtime_end": pd.to_datetime(["2026-01-14", "2262-04-11", "2262-04-11"]),
            "value": [1.0, 1.5, 2.0],
        }
    )


def test_vintage_asof_returns_value_as_published() -> None:
    v = _vintages()
    assert vintage_asof(v, "2026-01-10").to_dict() == {pd.Timestamp("2026-01-02"): 1.0}
    later = vintage_asof(v, "2026-01-20")
    assert later[pd.Timestamp("2026-01-02")] == 1.5 and later[pd.Timestamp("2026-01-09")] == 2.0


def test_first_release_keeps_unrevised_value() -> None:
    fr = first_release(_vintages()).set_index("date")["value"]
    assert fr[pd.Timestamp("2026-01-02")] == 1.0


def test_one_session_lag_and_no_lookahead() -> None:
    sessions = pd.bdate_range("2026-01-05", "2026-01-23")
    lag = available_session(pd.Series(pd.to_datetime(["2026-01-08"])), sessions)
    assert lag.iloc[0] == pd.Timestamp("2026-01-09")  # strictly after the vintage date
    pit = point_in_time_daily(_vintages(), sessions)
    assert np.isnan(pit.loc["2026-01-08", "value"])  # released 01-08, usable only from 01-09
    assert pit.loc["2026-01-09", "value"] == 1.0
    assert pit.loc["2026-01-16", "value"] == 2.0  # obs 01-09, released 01-15, usable 01-16
    # perturbing a vintage published after a session must not change that session's value
    v2 = _vintages()
    v2.loc[2, "value"] = 99.0
    assert point_in_time_daily(v2, sessions).loc["2026-01-14", "value"] == 1.0


# ------------------------------------------------------------------------------- prices


def _bars(split_ok: bool = True) -> tuple[pd.DataFrame, pd.DatetimeIndex]:
    """Yahoo convention: Close is split-adjusted. split_ok=False = split not applied (raw drop)."""
    idx = pd.bdate_range("2026-01-05", periods=10)
    close = np.array([25.0, 25.2, 25.5, 25.8, 26.0, 26.2, 26.5, 26.4, 26.6, 26.8])
    if not split_ok:
        close[:5] *= 4  # history not adjusted: price appears to fall 75% on the split date
    adj = close.copy()
    df = pd.DataFrame(
        {"Close": close, "Adj Close": adj, "Volume": 1e6, "Dividends": 0.0, "Stock Splits": 0.0},
        index=idx,
    )
    df.loc[idx[5], "Stock Splits"] = 4.0
    return df, idx


def test_split_validation() -> None:  # 4:1 split on day 6
    df, idx = _bars(True)
    chk = validate_prices("SYN", df, idx)
    assert chk.splits == 1 and not chk.split_failures and chk.status == "PASS"
    bad, idx2 = _bars(False)
    assert validate_prices("SYN", bad, idx2).status == "FAIL"


def test_calendar_and_adjustment_warnings() -> None:
    df, idx = _bars(True)
    df.loc[idx[2], "Adj Close"] *= 1.10  # unexplained adjustment-factor jump
    sessions = idx.delete(7)  # a row on a non-session date
    chk = validate_prices("SYN", df, sessions)
    assert chk.extra_dates == 1 and chk.adj_jumps_off_action_dates and chk.status == "WARN"


# ------------------------------------------------------------------------------- cache, secrets


def test_cache_roundtrip_and_hash(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cache, "RAW", tmp_path / "raw")
    monkeypatch.setattr(cache, "MANIFEST", tmp_path / "raw" / "manifest.jsonl")
    monkeypatch.setattr(cache, "DATA", tmp_path)
    calls = []
    frame = pd.DataFrame({"x": [1.0, 2.0]}, index=pd.to_datetime(["2026-01-01", "2026-01-02"]))

    def fetch() -> pd.DataFrame:
        calls.append(1)
        return frame

    a = cache.cached("syn", "k", fetch)
    b = cache.cached("syn", "k", fetch)  # second call must come from disk
    assert len(calls) == 1
    assert cache.frame_sha256(a) == cache.frame_sha256(b)
    assert cache.manifest().iloc[0]["sha256"] == cache.frame_sha256(frame)


def test_secret_from_file_without_exposing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    f = tmp_path / "env.secrets"
    f.write_text("# comment\nSOME_KEY='abc123'\n", encoding="utf-8")
    monkeypatch.setattr(secrets, "SECRETS_FILE", f)
    monkeypatch.delenv("SOME_KEY", raising=False)
    assert secrets.get_secret("SOME_KEY") == "abc123"
    assert secrets.get_secret("MISSING") is None
    with pytest.raises(RuntimeError) as e:
        secrets.get_secret("MISSING", required=True)
    assert "abc123" not in str(e.value)


def test_fred_errors_never_contain_the_key(monkeypatch: pytest.MonkeyPatch) -> None:
    from shockamp.data import fred

    class Resp:
        ok = False
        status_code = 400
        text = "Bad Request for api_key=SECRETKEY123"

    monkeypatch.setattr(fred, "get_secret", lambda name, required=False: "SECRETKEY123")
    monkeypatch.setattr(fred.requests, "get", lambda *a, **k: Resp())
    with pytest.raises(RuntimeError) as e:
        fred._get_json(fred.API, {"series_id": "X"})
    assert "SECRETKEY123" not in str(e.value) and "<redacted>" in str(e.value)
