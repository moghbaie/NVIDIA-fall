"""H6 groups come from config with a source, and no H6 outcome firm sits in a benchmark."""

from __future__ import annotations

import yaml

from shockamp import CONFIGS


def _cfg() -> dict:
    return yaml.safe_load((CONFIGS / "tickers.yaml").read_text(encoding="utf-8"))


def test_groups_have_source_and_are_disjoint() -> None:
    g = _cfg()["h6_groups"]
    assert g["source"].startswith("https://www.sec.gov/")
    names = ["G1_competitors", "G2_suppliers", "G3_other_semis", "G4_cloud_customers"]
    seen: set[str] = set()
    for n in names:
        members = set(g[n])
        assert not members & seen, f"{n} overlaps another group"
        seen |= members
    assert "NVDA" not in seen


def test_nvda_primary_benchmark_excludes_competitors_and_suppliers() -> None:
    cfg = _cfg()
    g = cfg["h6_groups"]
    bench = cfg["nvda_benchmark"]["primary"]
    tickers = {t for b in bench for t in (g[b] if b in g else [b])}
    outcome = set(g["G1_competitors"]) | set(g["G1_extended"]) | set(g["G2_suppliers"])
    assert not tickers & outcome
