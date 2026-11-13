"""Statistical tests of the power simulator (synthetic)."""

import numpy as np

from shockamp.power import mde, power_grid, simulate_power

LEVELS, COUNTS = [0, 1, 2], [600, 300, 60]


def test_null_size_near_alpha():
    p = simulate_power(LEVELS, COUNTS, 0.0, 0.06, reps=600, rng=np.random.default_rng(1))
    assert 0.02 <= p <= 0.09


def test_large_effect_detected():
    p = simulate_power(LEVELS, COUNTS, -0.05, 0.06, reps=200, rng=np.random.default_rng(2))
    assert p > 0.95


def test_mde_monotone_in_sigma():
    g = power_grid(
        {"d": (LEVELS, COUNTS)}, [-0.002, -0.005, -0.01, -0.02, -0.04], [0.04, 0.08], reps=150
    )
    m = mde(g).set_index("sigma").mde
    assert m[0.04] < m[0.08]
