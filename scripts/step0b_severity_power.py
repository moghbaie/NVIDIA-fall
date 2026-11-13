"""Step 0b: power of categorical vs ordinal severity designs (review point 1).

All outcomes are SYNTHETIC. Event counts per category are real (Gentry et al., codes 3/4/5/6,
2005-2025, 70% assumed price-match rate). Writes reports/step0b/.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from shockamp import DATA, REPORTS
from shockamp.power import mde, simulate_power_categorical

OUT = REPORTS / "step0b"
OUT.mkdir(parents=True, exist_ok=True)
GENTRY = DATA / "raw" / "ceo_dismissal" / "ceo_dismissal_26Nov25.xlsx"
MATCH = 0.7
REPS = 300
SEED = 20261113

C = {"blue": "#2a78d6", "orange": "#eb6834", "aqua": "#1baf7a", "violet": "#6250d6",
     "ink": "#0b0b0b", "ink2": "#52514e", "muted": "#8a8984", "grid": "#e6e5e1",
     "surface": "#fcfcfb"}  # fmt: skip
plt.rcParams.update(
    {
        "figure.facecolor": C["surface"],
        "axes.facecolor": C["surface"],
        "axes.edgecolor": C["grid"],
        "axes.labelcolor": C["ink2"],
        "xtick.color": C["ink2"],
        "ytick.color": C["ink2"],
        "axes.grid": True,
        "grid.color": C["grid"],
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.axisbelow": True,
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.titlecolor": C["ink"],
        "lines.linewidth": 2,
        "legend.frameon": False,
    }
)

g = pd.read_excel(GENTRY)
for c in ("left_ceo_office", "date_departure_announced"):
    g[c] = pd.to_datetime(g[c], errors="coerce")
g["year"] = g.date_departure_announced.fillna(g.left_ceo_office).dt.year
p = g[g.year.between(2005, 2025) & g.departure_code.isin([3, 4, 5, 6])]
n = p.departure_code.value_counts()
counts = [int(MATCH * (n[5] + n[6])), int(MATCH * n[3]), int(MATCH * n[4])]  # vol, perf, misc
print("counts (voluntary, performance, misconduct):", counts)

SCEN = {  # true interaction per category, as multiples of g (voluntary = 0)
    "equal spacing true\n(perf = g, misconduct = 2g)": (0, 1, 2),
    "dismissals alike\n(perf = misconduct = g)": (0, 1, 1),
    "only misconduct amplifies\n(perf = 0, misconduct = g)": (0, 0, 1),
}
TESTS = {
    "ordinal 0/1/2 (v1.1 primary)": "ordinal",
    "dismissal vs voluntary (pooled)": "pooled",
    "performance vs voluntary": "cat1",
    "misconduct vs voluntary": "cat2",
}
COL = dict(zip(TESTS, [C["blue"], C["aqua"], C["orange"], C["violet"]], strict=True))
mags = np.array([0, 0.0025, 0.005, 0.0075, 0.01, 0.015, 0.02, 0.03, 0.04, 0.06])
rng = np.random.default_rng(SEED)
rows = []
for sname, mult in SCEN.items():
    for tname, code in TESTS.items():
        if code == "cat1" and mult[1] == 0:
            continue  # no true effect to detect
        for sigma in (0.05, 0.07, 0.09):
            for m in mags:
                gam = [-m * k for k in mult]
                pw = simulate_power_categorical(counts, gam, code, sigma, reps=REPS, rng=rng)
                rows.append({"scenario": sname, "test": tname, "sigma": sigma,
                             "beta_int": -m, "power": pw})  # fmt: skip
grid = pd.DataFrame(rows)
grid.to_csv(OUT / "severity_power_grid.csv", index=False)
out = []
for sname, gs in grid.groupby("scenario", sort=False):
    m = mde(gs.rename(columns={"test": "design"})).assign(scenario=sname)
    out.append(m)
mdes = pd.concat(out).rename(columns={"design": "test"})
mdes["mde_pp"] = 100 * mdes.mde
mdes.to_csv(OUT / "severity_mde.csv", index=False)
print(mdes.pivot_table(index=["scenario", "test"], columns="sigma", values="mde_pp").round(2))

fig, axes = plt.subplots(1, 3, figsize=(13, 4.3), sharey=True)
for ax, (sname, gs) in zip(axes, grid[grid.sigma == 0.07].groupby("scenario", sort=False),
                           strict=True):  # fmt: skip
    for tname, gt in gs.groupby("test", sort=False):
        ax.plot(100 * gt.beta_int.abs(), gt.power, color=COL[tname], label=tname, marker="o",
                markersize=4)  # fmt: skip
    ax.axhline(0.8, color=C["muted"], lw=1, ls="--")
    ax.set_title(sname, fontsize=10)
    ax.set_xlabel("g: extra CAR loss per 1 SD stress (pp)")
    ax.set_xlim(0, 4)
    ax.set_xticks([0, 1, 2, 3, 4], ["0", "1", "2", "3", "4"])
axes[0].set_ylabel("power (share of 300 synthetic reps)")
axes[0].text(3.95, 0.82, "80%", ha="right", color=C["muted"], fontsize=8)
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=9)
fig.suptitle("Which severity coding detects stress amplification? (SYNTHETIC outcomes, "
             f"real counts {counts}, residual sd 7%)", fontsize=11, color=C["ink"], x=0.01,
             ha="left")  # fmt: skip
fig.tight_layout(rect=(0, 0.08, 1, 0.95), w_pad=2.5)
fig.savefig(OUT / "fig4_severity_power.png", dpi=150)
print("saved", OUT / "fig4_severity_power.png")
