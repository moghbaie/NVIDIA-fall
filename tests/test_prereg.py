"""The preregistered primary test is the single source of truth; code must not drift from it."""

from __future__ import annotations

import yaml

from shockamp import CONFIGS


def _pre() -> dict:
    return yaml.safe_load((CONFIGS / "preregistration.yaml").read_text(encoding="utf-8"))


def test_primary_tests_are_categorical_holm_on_leadership_concentration() -> None:
    pre = _pre()
    pt = pre["primary_tests"]
    card = pre["spec_card"]
    assert card["primary_moderator"] == "leadership_concentration"
    assert pt["baseline"] == card["baseline"] == "voluntary"
    assert pt["terms"] == card["primary_terms"] == ["performance:LC", "misconduct:LC"]
    assert pt["direction"] == card["direction"] == "negative"
    assert pt["adjustment"] == card["adjustment"] == "holm"
    assert pt["family_alpha"] == card["family_alpha"] == 0.05
    assert "C(event_month)" in pt["model"] and card["fixed_effects"] == "event_month"
    assert pre["primary_outcome_window"] == [-1, 1] and card["outcome"] == "CAR[-1,+1]"
    cats = pre["severity"]["primary_categories"]
    assert cats == {"voluntary": [5, 6], "performance": [3], "misconduct": [4]}
    assert "primary_ordinal" not in pre["severity"]


def test_h1a_h1b_labels_fixed_by_term() -> None:
    labels = _pre()["spec_card"]["term_labels"]
    assert labels["misconduct:LC"] == "H1a_adverse_news_amplification"
    assert labels["performance:LC"] == "H1b_attenuated_replacement_benefit"


def test_gate_and_naming_rules() -> None:
    pre = _pre()
    v = pre["vulnerability"]
    assert set(v["leadership"]["components"]) == {
        "founder_ceo",
        "no_designated_successor",
        "ceo_chair_duality",
    }
    assert "naming_rule" in v["leadership"]
    assert "fallback_primary_moderator" not in pre["spec_card"]
    assert pre["spec_card"]["coverage_gate_failure"] == "halt_and_decide_outcome_blind"
    assert "idiosyncratic_volatility" in v["excluded_from_vulnerability"]
    assert "lc_ex_founder" in pre["required_robustness"]


def test_nvidia_requirements() -> None:
    pre = _pre()
    card = pre["spec_card"]
    assert pre["nvidia"]["families_required"] == card["nvidia_families"]
    assert card["nvidia_combined_score"] is False
    assert card["nvidia_pre_e0_counterfactual"] == "required"
    cf = pre["nvidia"]["pre_e0_counterfactual"]
    assert cf["cutoff"].startswith("close of 2026-10-28")
    assert {"A_unconditional", "B_conditional", "freeze"} <= set(cf)
