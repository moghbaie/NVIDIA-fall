"""The preregistered primary test is the single source of truth; code must not drift from it."""

from __future__ import annotations

import yaml

from shockamp import CONFIGS


def _pre() -> dict:
    return yaml.safe_load((CONFIGS / "preregistration.yaml").read_text(encoding="utf-8"))


def test_primary_tests_are_categorical_holm_on_leadership_vulnerability() -> None:
    pre = _pre()
    pt = pre["primary_tests"]
    card = pre["spec_card"]
    assert pt["baseline"] == card["baseline"] == "voluntary"
    assert pt["terms"] == card["primary_terms"] == ["performance:LV", "misconduct:LV"]
    assert pt["direction"] == card["direction"] == "negative"
    assert pt["adjustment"] == card["adjustment"] == "holm"
    assert pt["family_alpha"] == card["family_alpha"] == 0.05
    assert "C(event_month)" in pt["model"] and card["fixed_effects"] == "event_month"
    assert pre["primary_outcome_window"] == [-1, 1] and card["outcome"] == "CAR[-1,+1]"
    cats = pre["severity"]["primary_categories"]
    assert cats == {"voluntary": [5, 6], "performance": [3], "misconduct": [4]}
    assert "primary_ordinal" not in pre["severity"]


def test_vulnerability_rules() -> None:
    pre = _pre()
    v = pre["vulnerability"]
    assert set(v["leadership"]["components"]) == {
        "founder_ceo",
        "no_designated_successor",
        "ceo_chair_duality",
    }
    assert "idiosyncratic_volatility" in v["excluded_from_vulnerability"]
    assert pre["spec_card"]["fallback_primary_moderator"] == "financial_vulnerability"
    assert "lv_ex_founder" in pre["required_robustness"]
    assert pre["nvidia"]["families_required"] == pre["spec_card"]["nvidia_families"]
    assert pre["spec_card"]["nvidia_combined_score"] is False
