"""The preregistration is the single source of truth; code and documents must not drift from it.

v1.9: NVIDIA attribution (N1) is primary and exploratory; the CEO-departure panel (H1a/H1b) is a
secondary statistical study whose specification is unchanged from v1.8.
"""

from __future__ import annotations

import yaml

from shockamp import CONFIGS


def _pre() -> dict:
    return yaml.safe_load((CONFIGS / "preregistration.yaml").read_text(encoding="utf-8"))


# ---- panel (secondary statistical study): v1.8 specification preserved
def test_panel_tests_are_categorical_holm_on_leadership_concentration() -> None:
    pre = _pre()
    pt = pre["panel_tests"]
    card = pre["spec_card"]
    assert pre["panel_hypotheses"] == card["panel_hypotheses"] == ["H1a", "H1b"]
    assert card["panel_moderator"] == "leadership_concentration"
    assert pt["baseline"] == card["panel_baseline"] == "voluntary"
    assert pt["terms"] == card["panel_terms"] == ["performance:LC", "misconduct:LC"]
    assert pt["direction"] == card["panel_direction"] == "negative"
    assert pt["adjustment"] == card["panel_adjustment"] == "holm"
    assert pt["family_alpha"] == card["panel_family_alpha"] == 0.05
    assert "C(event_month)" in pt["model"] and card["panel_fixed_effects"] == "event_month"
    assert pre["panel_outcome_window"] == [-1, 1] and card["panel_outcome"] == "CAR[-1,+1]"
    cats = pre["severity"]["primary_categories"]
    assert cats == {"voluntary": [5, 6], "performance": [3], "misconduct": [4]}
    assert "primary_ordinal" not in pre["severity"]


def test_h1a_h1b_labels_fixed_by_term() -> None:
    labels = _pre()["spec_card"]["panel_term_labels"]
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
    assert pre["spec_card"]["panel_coverage_gate"] == {"overall": 0.80, "misconduct": 0.70}
    assert pre["spec_card"]["panel_coverage_gate_failure"] == "halt_and_decide_outcome_blind"
    assert "idiosyncratic_volatility" in v["excluded_from_vulnerability"]
    assert "lc_ex_founder" in pre["required_robustness"]


# ---- NVIDIA attribution (primary N1, exploratory with frozen rules)
def test_primary_is_nvidia_attribution_and_exploratory() -> None:
    pre = _pre()
    card = pre["spec_card"]
    assert pre["primary_hypothesis"] == card["primary_hypothesis"] == "N1"
    assert card["primary_status"].startswith("exploratory")
    assert card["causal_share_claims"] is False
    na = pre["nvidia_attribution"]
    assert na["window"]["sessions"] == card["nvidia_window_sessions"] == 13
    assert str(na["window"]["start"]) == card["nvidia_window"][0] == "2026-10-29"
    assert str(na["window"]["end"]) == card["nvidia_window"][1] == "2026-11-16"
    assert na["cutoff"] == "close of 2026-10-28" and card["nvidia_cutoff"] == "2026-10-28 close"


def test_counterfactuals_all_required() -> None:
    pre = _pre()
    card, cf = pre["spec_card"], pre["nvidia_attribution"]["counterfactuals"]
    assert card["counterfactuals_required"] == ["A", "B1", "B2", "B3", "B4"]
    for v, factors in card["b_factors"].items():
        assert cf[v] == factors, v
    assert "G3" not in cf["B2"] and cf["B3"] == ["SPY"]
    assert {"A_unconditional", "B_conditional"} <= set(pre["nvidia"]["pre_e0_counterfactual"])


def test_sessions_mutually_exclusive_and_mixed_unresolved() -> None:
    pre = _pre()
    card, na = pre["spec_card"], pre["nvidia_attribution"]
    assert card["session_categories"] == list(na["session_categories"])
    assert card["mixed_sessions"] == "unresolved_never_assigned_to_leadership"
    sc = na["estimands"]["E3_leadership_scenarios"]
    assert sc["leadership_only"] == "Delta_v[L]"
    assert "not mathematically identified" in sc["label"]


def test_placebo_and_decision_rules() -> None:
    pre = _pre()
    card, pl = pre["spec_card"], pre["nvidia_attribution"]["placebo"]
    assert pl["primary"]["blocks"] == "non_overlapping" and pl["primary"]["length"] == 13
    assert str(pl["primary"]["offset"]) == "2010-01-04"
    assert set(pl["sensitivity"]) == {
        "all_origins",
        "regime_matched",
        "excl_earnings_and_extraordinary",
        "peer_firms",
    }
    assert "not a causal confidence interval" in pl["interval"]
    assert "not an independently established" in pl["delta_equivalence_margin"]
    assert card["interval_label"] == "model_dependent_uncertainty_interval"
    dt = pre["nvidia_attribution"]["decision_table"]
    assert "never supports negligible" in dt["inconclusive"]
    assert "TOST" in dt["negligible"] and "every validated version" in dt["negligible"]


def test_nvidia_five_families_never_combined() -> None:
    pre = _pre()
    card = pre["spec_card"]
    assert pre["nvidia"]["families_required"] == card["nvidia_families"]
    assert "political_regulatory" in card["nvidia_families"] and len(card["nvidia_families"]) == 5
    assert card["nvidia_combined_score"] is False
    assert "No thresholds on beta or volatility" in pre["nvidia"]["family_assessment"]
