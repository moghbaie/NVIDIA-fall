"""Step 1(c) news inventory: schema validation and label freezing.

Labels (channels, expected directions, importance, interpretation) must be frozen before any stock
reaction is computed. `freeze` writes the inventory's SHA-256 to a freeze record; `assert_frozen`
refuses to proceed if the inventory changed afterwards. This reduces hindsight bias; it cannot
remove it, because NVIDIA's overall decline was seen before the inventory was built.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
import yaml

CHANNELS = {
    "demand",
    "deployment",
    "supply",
    "regulation_export",
    "competition",
    "financing_credit",
    "governance_leadership",
    "m_and_a",
    "capex",
}
DIRECTIONS = {"+", "-", "0", "?"}  # effect on the named company's value; "?" = cannot sign ex ante
NOVELTY = {"new", "follow-up", "repeat"}
SOURCE_TYPES = {"primary", "major outlet", "aggregator"}
REQUIRED = [
    "id",
    "published",
    "time_et",
    "source",
    "source_type",
    "url",
    "headline",
    "facts",
    "companies",
    "novelty",
    "importance",
    "channels",
    "net_expected_nvda",
    "interpretation",
]


class FreezeError(RuntimeError):
    pass


def load_inventory(path: Path) -> list[dict]:
    items: list[dict] = yaml.safe_load(path.read_text(encoding="utf-8"))["items"]
    return items


def validate_inventory(items: list[dict]) -> list[str]:
    """Return a list of problems (empty = valid)."""
    errs: list[str] = []
    seen: set[str] = set()
    for it in items:
        iid = str(it.get("id"))
        for k in REQUIRED:
            if k not in it or it[k] in ("", None) and k != "time_et":
                errs.append(f"{iid}: missing {k}")
        if iid in seen:
            errs.append(f"{iid}: duplicate id")
        seen.add(iid)
        if it.get("novelty") not in NOVELTY:
            errs.append(f"{iid}: novelty {it.get('novelty')!r}")
        if it.get("source_type") not in SOURCE_TYPES:
            errs.append(f"{iid}: source_type {it.get('source_type')!r}")
        if it.get("importance") not in (1, 2, 3):
            errs.append(f"{iid}: importance must be 1-3")
        if it.get("net_expected_nvda") not in {"+", "-", "0", "mixed", "?"}:
            errs.append(f"{iid}: net_expected_nvda {it.get('net_expected_nvda')!r}")
        for ch in it.get("channels") or []:
            if ch.get("channel") not in CHANNELS or ch.get("direction") not in DIRECTIONS:
                errs.append(f"{iid}: bad channel {ch}")
            if not ch.get("company"):
                errs.append(f"{iid}: channel without company")
        t = it.get("time_et")
        if t is not None:
            try:
                pd.Timestamp(f"{it['published']} {t}")
            except ValueError:
                errs.append(f"{iid}: bad time_et {t!r}")
    return errs


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze(path: Path, record: Path) -> dict:
    """Record the inventory hash. Refuses to overwrite an existing freeze for a different hash."""
    items = load_inventory(path)
    errs = validate_inventory(items)
    if errs:
        raise FreezeError("inventory invalid: " + "; ".join(errs[:10]))
    h = file_sha256(path)
    if record.exists():
        old = json.loads(record.read_text(encoding="utf-8"))
        if old["sha256"] != h:
            raise FreezeError("a different inventory was already frozen; log a deviation first")
        return dict(old)
    rec = {
        "inventory": path.name,
        "sha256": h,
        "n_items": len(items),
        "frozen_at_utc": pd.Timestamp.now(tz="UTC").isoformat(),
    }
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(json.dumps(rec, indent=2), encoding="utf-8")
    return rec


def assert_frozen(path: Path, record: Path) -> dict:
    """Raise FreezeError unless the inventory is unchanged since it was frozen."""
    if not record.exists():
        raise FreezeError("inventory not frozen: run freeze() before computing reactions")
    rec: dict = json.loads(record.read_text(encoding="utf-8"))
    if rec["sha256"] != file_sha256(path):
        raise FreezeError("inventory changed after freezing; labels are no longer ex ante")
    return rec
