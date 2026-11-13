"""Step 1 evidence tables: required fields, allowed types, availability timestamps."""

from __future__ import annotations

import pandas as pd
import yaml

from shockamp import CONFIGS

MEASURES = {
    "contractual_commitment",
    "maximum_gross_exposure",
    "carrying_amount",
    "notional",
    "not_quantified",
}
FAMILIES = {"financial", "leadership", "operational", "resource_deployment"}


def test_exposure_records_are_typed_and_dated() -> None:
    cfg = yaml.safe_load((CONFIGS / "nvda_exposures.yaml").read_text(encoding="utf-8"))
    for f in cfg["filings"].values():
        assert f["accession"].startswith("0001045810-")
        assert pd.Timestamp(f["accepted_utc"]).tzinfo is not None
    ids = set()
    for r in cfg["records"]:
        assert r["id"] not in ids
        ids.add(r["id"])
        assert r["filing"] in cfg["filings"]
        assert r["measure"] in MEASURES and r["family"] in FAMILIES
        for k in ("category", "counterparty", "trigger", "quote", "mechanism", "timing"):
            assert r.get(k), f"{r['id']} missing {k}"
        assert (r["amount_usd_bn"] is None) == (r["measure"] == "not_quantified")


def test_inventory_freeze_blocks_later_edits(tmp_path) -> None:  # type: ignore[no-untyped-def]
    import pytest

    from shockamp.evidence import FreezeError, assert_frozen, freeze, validate_inventory

    item = {
        "id": "N01",
        "published": "2026-10-20",
        "time_et": None,
        "source": "Example",
        "source_type": "major outlet",
        "url": "https://example.org/a",
        "headline": "h",
        "facts": "f",
        "companies": ["NVDA", "AMZN"],
        "novelty": "new",
        "importance": 2,
        "channels": [
            {"channel": "demand", "direction": "+", "company": "NVDA"},
            {"channel": "deployment", "direction": "-", "company": "NVDA"},
        ],
        "net_expected_nvda": "mixed",
        "interpretation": "two opposing channels",
    }
    assert validate_inventory([item]) == []
    inv = tmp_path / "inv.yaml"
    rec = tmp_path / "freeze.json"
    inv.write_text(yaml.safe_dump({"items": [item]}), encoding="utf-8")
    with pytest.raises(FreezeError):
        assert_frozen(inv, rec)  # not frozen yet
    freeze(inv, rec)
    assert_frozen(inv, rec)
    item["net_expected_nvda"] = "-"  # relabel after freezing
    inv.write_text(yaml.safe_dump({"items": [item]}), encoding="utf-8")
    with pytest.raises(FreezeError):
        assert_frozen(inv, rec)
    with pytest.raises(FreezeError):
        freeze(inv, rec)  # cannot silently re-freeze a different inventory
    bad = dict(item, channels=[{"channel": "vibes", "direction": "+", "company": "NVDA"}])
    assert validate_inventory([bad])
