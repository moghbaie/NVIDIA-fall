"""Every planning document carries a spec card identical to the preregistration's.

Guards against documents disagreeing on the primary hypothesis, sample, timestamps or gates.
"""

from __future__ import annotations

import re

import pytest
import yaml

from shockamp import CONFIGS, ROOT

DOCS = [
    "PLAN.md",
    "state_dependent_shock_amplification_research_plan.md",
    "nvidia_shock_amplification_colab_implementation_plan.md",
]
CARD = re.compile(r"```yaml spec-card\n(.*?)```", re.S)


def _prereg_card() -> dict:
    pre = yaml.safe_load((CONFIGS / "preregistration.yaml").read_text(encoding="utf-8"))
    return pre["spec_card"]


@pytest.mark.parametrize("doc", DOCS)
def test_doc_spec_card_matches_preregistration(doc: str) -> None:
    text = (ROOT / doc).read_text(encoding="utf-8")
    cards = CARD.findall(text)
    assert len(cards) == 1, f"{doc}: expected exactly one spec card, found {len(cards)}"
    assert yaml.safe_load(cards[0]) == _prereg_card(), f"{doc}: spec card differs from prereg"
