"""The preregistered primary test is the single source of truth; code must not drift from it."""

from __future__ import annotations

import yaml

from shockamp import CONFIGS


def test_primary_tests_are_categorical_holm() -> None:
    pre = yaml.safe_load((CONFIGS / "preregistration.yaml").read_text(encoding="utf-8"))
    pt = pre["primary_tests"]
    assert pt["baseline"] == "voluntary"
    assert pt["terms"] == ["performance:MSI", "misconduct:MSI"]
    assert pt["direction"] == "negative"
    assert pt["adjustment"] == "holm"
    assert pt["family_alpha"] == 0.05
    assert pre["primary_outcome_window"] == [-1, 1]
    cats = pre["severity"]["primary_categories"]
    assert cats == {"voluntary": [5, 6], "performance": [3], "misconduct": [4]}
    # the ordinal score may only appear as a secondary specification
    assert "primary_ordinal" not in pre["severity"]
