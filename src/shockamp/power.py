"""Simulation-based power for the H1 interaction  CAR ~ sev + stress + sev x stress.

All outcomes generated here are SYNTHETIC. Only the design (event counts per severity level) comes
from real data; the CAR noise level and effect sizes are swept assumptions.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd
from scipy import stats


def _ols_hc1_t(x: np.ndarray, y: np.ndarray, j: int) -> float:
    """t-statistic of coefficient j with HC1 robust standard errors."""
    n, k = x.shape
    xtx_inv = np.linalg.inv(x.T @ x)
    b = xtx_inv @ x.T @ y
    e = y - x @ b
    meat = (x * e[:, None] ** 2).T @ x
    cov = xtx_inv @ meat @ xtx_inv * n / (n - k)
    return float(b[j] / np.sqrt(cov[j, j]))


def simulate_power(
    sev_levels: Sequence[float],
    counts: Sequence[int],
    beta_int: float,
    sigma: float,
    reps: int = 400,
    alpha: float = 0.05,
    beta_sev: float = -0.01,
    rng: np.random.Generator | None = None,
) -> float:
    """Share of reps where the interaction is significant (two-sided) AND negative.

    Design: severity takes value sev_levels[i] for counts[i] events; standardized pre-event stress
    S ~ N(0,1) independent of severity; CAR = beta_sev*sev + beta_int*sev*S + N(0, sigma^2).
    Severity is centred so beta_int is the change in the severity slope per 1 SD of stress.
    """
    rng = rng or np.random.default_rng(0)
    sev = np.repeat(np.asarray(sev_levels, float), np.asarray(counts))
    sev_c = sev - sev.mean()
    n = len(sev)
    crit = stats.norm.ppf(1 - alpha / 2)
    hits = 0
    for _ in range(reps):
        s = rng.standard_normal(n)
        y = beta_sev * sev_c + beta_int * sev_c * s + rng.normal(0, sigma, n)
        x = np.column_stack([np.ones(n), sev_c, s, sev_c * s])
        t = _ols_hc1_t(x, y, 3)
        hits += (abs(t) > crit) and (np.sign(t) == np.sign(beta_int) if beta_int else True)
    return hits / reps


def simulate_power_categorical(
    counts: Sequence[int],
    gammas: Sequence[float],
    test: str,
    sigma: float,
    reps: int = 400,
    alpha: float = 0.05,
    rng: np.random.Generator | None = None,
) -> float:
    """Power when event type is categorical (no equal-spacing assumption). SYNTHETIC outcomes.

    Category 0 is the baseline (voluntary); categories 1..K-1 get dummies. True model:
    CAR = sum_k gamma_k * D_k * S + N(0, sigma^2), S ~ N(0,1), gamma_0 = 0 by construction.
    test="pooled": fit CAR ~ D + S + D*S with D = any non-baseline category; test D*S.
    test="ordinal": fit CAR ~ c + S + c*S with c = centred category index; test c*S.
    test="cat<k>": fit the full categorical model (dummies, S, dummies*S); test D_k*S.
    Rejection requires |t| > z_crit and the sign of the true pooled / category effect.
    """
    rng = rng or np.random.default_rng(0)
    cat = np.repeat(np.arange(len(counts)), np.asarray(counts))
    n = len(cat)
    g = np.asarray(gammas, float)
    dums = np.column_stack([(cat == k).astype(float) for k in range(1, len(counts))])
    crit = stats.norm.ppf(1 - alpha / 2)
    if test == "pooled":
        d = (cat > 0).astype(float)
        truth = float(np.average(g[1:], weights=np.asarray(counts[1:], float)))
    elif test == "ordinal":  # equally spaced score 0..K-1, centred (the v1.1 primary)
        d = cat - cat.mean()
        truth = float(g[-1])
    else:
        k = int(test.removeprefix("cat"))
        truth = float(g[k])
    hits = 0
    for _ in range(reps):
        s = rng.standard_normal(n)
        y = g[cat] * s + rng.normal(0, sigma, n)
        if test in ("pooled", "ordinal"):
            x = np.column_stack([np.ones(n), d, s, d * s])
            j = 3
        else:
            x = np.column_stack([np.ones(n), dums, s, dums * s[:, None]])
            j = 1 + dums.shape[1] + 1 + (k - 1)
        t = _ols_hc1_t(x, y, j)
        hits += (abs(t) > crit) and (np.sign(t) == np.sign(truth) if truth else True)
    return hits / reps


def power_grid(
    designs: dict[str, tuple[Sequence[float], Sequence[int]]],
    betas: Sequence[float],
    sigmas: Sequence[float],
    reps: int = 400,
    seed: int = 20261113,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for name, (levels, counts) in designs.items():
        for sigma in sigmas:
            for b in betas:
                p = simulate_power(levels, counts, b, sigma, reps=reps, rng=rng)
                rows.append({"design": name, "sigma": sigma, "beta_int": b, "power": p})
    return pd.DataFrame(rows)


def mde(grid: pd.DataFrame, target: float = 0.8) -> pd.DataFrame:
    """Smallest |beta_int| reaching `target` power per (design, sigma), linear interpolation."""
    out = []
    for (d, s), g in grid.groupby(["design", "sigma"]):
        g = g.assign(a=g.beta_int.abs()).sort_values("a")
        a = g["a"].to_numpy(float)
        pw = g["power"].to_numpy(float)
        hits = np.flatnonzero(pw >= target)
        if hits.size == 0:
            out.append({"design": d, "sigma": s, "mde": np.nan})
            continue
        i = int(hits[0])
        if i == 0:
            val = float(a[0])
        else:
            val = float(a[i - 1] + (target - pw[i - 1]) * (a[i] - a[i - 1]) / (pw[i] - pw[i - 1]))
        out.append({"design": d, "sigma": s, "mde": val})
    return pd.DataFrame(out)
