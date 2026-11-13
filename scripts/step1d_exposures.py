"""Step 1(d): NVIDIA's disclosed AI-buildout exposures by type (configs/nvda_exposures.yaml).

Panels separate measure types, because a purchase commitment, a contingent guarantee's maximum
gross exposure and a recognized liability are not additive.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import yaml
from matplotlib.patches import Patch

from shockamp import CONFIGS, REPORTS

OUT = REPORTS / "step1"
cfg = yaml.safe_load((CONFIGS / "nvda_exposures.yaml").read_text(encoding="utf-8"))
df = pd.DataFrame(cfg["records"])
df.to_csv(OUT / "nvda_exposures.csv", index=False)
q = df[df.amount_usd_bn.notna()].copy()
SHORT = {
    "X01": "supply & capacity purchases",
    "X02": "AI-cloud service buy-back",
    "X03": "3rd-party DC leases (to reassign)",
    "X04": "AI-cloud lease guarantees",
    "X05": "SB Energy guarantee (OpenAI)",
    "X06": "cloud services, own R&D",
    "X07": "own DC leases not commenced",
    "X08": "equity investments + capex",
    "X09": "debt (notes)",
}
CHANGE = {"X01": "up from 119 one quarter earlier", "X09": "up from 8.5 at 2026-01-25"}
C = {"financial": "#8a8984", "operational": "#2a78d6", "resource_deployment": "#eb6834",
     "ink": "#0b0b0b", "ink2": "#52514e", "grid": "#e6e5e1", "surface": "#fcfcfb"}  # fmt: skip
plt.rcParams.update({"figure.facecolor": C["surface"], "axes.facecolor": C["surface"],
                     "axes.edgecolor": C["grid"], "font.size": 8.5, "axes.titleweight": "bold",
                     "axes.spines.top": False, "axes.spines.right": False})  # fmt: skip
groups = [("contractual_commitment", "Contractual commitments (future payments agreed)"),
          ("maximum_gross_exposure", "Contingent guarantees: maximum gross exposure (not expected loss)"),
          ("carrying_amount", "Recognized liability (balance sheet)")]  # fmt: skip
sizes = [max(1, (q.measure == m).sum()) for m, _ in groups]
fig, axes = plt.subplots(len(groups), 1, figsize=(11, 7.2), gridspec_kw={"height_ratios": sizes})
xmax = q.amount_usd_bn.max() * 1.35
for ax, (m, title) in zip(axes, groups, strict=True):
    s = q[q.measure == m].sort_values("amount_usd_bn")
    labels = [f"{r.id} {SHORT[r.id]}" for r in s.itertuples()]
    ax.barh(labels, s.amount_usd_bn, color=[C[f] for f in s.family], height=0.6)
    for i, r in enumerate(s.itertuples()):
        extra = f"  ({CHANGE[r.id]})" if r.id in CHANGE else ""
        inside = r.amount_usd_bn > 0.6 * xmax
        ax.text(r.amount_usd_bn - xmax * 0.01 if inside else r.amount_usd_bn + xmax * 0.01, i,
                f"USD {r.amount_usd_bn:g}B{extra}", va="center", ha="right" if inside else "left",
                fontsize=7.5, color=C["surface"] if inside else C["ink2"])  # fmt: skip
    ax.set_xlim(0, xmax)
    ax.set_title(title, loc="left", fontsize=9)
    ax.tick_params(axis="y", labelsize=8)
axes[-1].set_xlabel("USD billions (as of 2026-07-26; SB Energy guarantee signed August 2026)")
handles = [
    Patch(color=C[k], label=lab)
    for k, lab in [
        ("resource_deployment", "resource / deployment"),
        ("operational", "operational"),
        ("financial", "financial"),
    ]
]
axes[0].legend(
    handles=handles, frameon=False, loc="lower right", title="vulnerability family", fontsize=7.5
)
fig.suptitle("Step 1(d): NVIDIA's disclosed exposure to the AI buildout — 10-Q accepted 2026-08-26 "
             "16:36 ET\n(amounts are not additive across panels; unquantified: shortage-risk "
             "statement X10, customer concentration X11)", x=0.01, ha="left", fontsize=10.5)  # fmt: skip
fig.tight_layout(rect=(0, 0, 1, 0.93))
fig.savefig(OUT / "fig9_nvda_exposures.png", dpi=150)
print(df[["id", "category", "family", "amount_usd_bn", "measure"]].to_string(index=False))
