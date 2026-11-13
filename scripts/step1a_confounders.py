"""Step 1(a)/(b): dated confounders around the NVIDIA disclosures (PROVISIONAL prices).

Daily abnormal returns (SPY market model fitted on [-252,-31] before E0) for NVDA and the H6 groups,
with NVIDIA disclosures and SEC 8-K earnings/officer releases mapped to their reaction sessions
(configs/nvda_chronology.yaml: sec_releases). Writes reports/step1/.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
import yfinance as yf

from shockamp import CONFIGS, REPORTS
from shockamp.calendar import as_sessions, complete_sessions, map_event
from shockamp.returns import abnormal_returns, fit_market_model, log_returns

OUT = REPORTS / "step1"
OUT.mkdir(parents=True, exist_ok=True)
NOW = pd.Timestamp.now(tz="UTC")
chron = yaml.safe_load((CONFIGS / "nvda_chronology.yaml").read_text(encoding="utf-8"))
groups = yaml.safe_load((CONFIGS / "tickers.yaml").read_text(encoding="utf-8"))["h6_groups"]
SERIES = {
    "NVDA": ["NVDA"],
    "G1 competitors": groups["G1_competitors"],
    "G2 suppliers": groups["G2_suppliers"],
    "G3 other semis": groups["G3_other_semis"],
    "G4 cloud customers": groups["G4_cloud_customers"],
}
C = {"blue": "#2a78d6", "orange": "#eb6834", "aqua": "#1baf7a", "violet": "#6250d6",
     "ink": "#0b0b0b", "ink2": "#52514e", "muted": "#8a8984", "grid": "#e6e5e1",
     "surface": "#fcfcfb"}  # fmt: skip
COL = dict(zip(SERIES, [C["orange"], C["blue"], C["aqua"], C["muted"], C["violet"]], strict=True))
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
        "font.size": 9,
        "axes.titlesize": 9.5,
        "axes.titleweight": "bold",
        "axes.titlecolor": C["ink"],
    }
)

tick = sorted({t for m in SERIES.values() for t in m} | {"SPY"})
px = yf.download(tick, start="2025-06-01", progress=False, auto_adjust=True)["Close"]
px = px.loc[px.index.isin(complete_sessions(as_sessions(px.index), NOW))]
r = log_returns(px)
for name, members in SERIES.items():
    r[name] = r[members].mean(axis=1)
sessions = r.index
e0 = map_event("2026-10-29", sessions, time_known=False).event_session
win = sessions[(sessions >= "2026-10-20") & (sessions <= sessions[-1])]
ar = pd.DataFrame(
    {n: abnormal_returns(r, n, fit_market_model(r, n, ["SPY"], e0), win).AR for n in SERIES}
)
sd = {n: fit_market_model(r, n, ["SPY"], e0).resid_sd for n in SERIES}
ar.to_csv(OUT / "daily_ar_groups.csv")

nv = {e["id"]: map_event(str(e["first_public_date"]), sessions, time_known=False).event_session
      for e in chron["events"]}  # fmt: skip
rel = pd.DataFrame(chron["sec_releases"])
rel["reaction_session"] = pd.to_datetime(rel.reaction_session)

x = np.arange(len(win))
pos = {d: i for i, d in enumerate(win)}
fig, axes = plt.subplots(len(SERIES) + 1, 1, figsize=(12, 10), sharex=True,
                         gridspec_kw={"height_ratios": [0.9] + [1] * len(SERIES)})  # fmt: skip
top = axes[0]
top.set_ylim(0, 1)
top.set_yticks([])
top.grid(False)
top.spines["left"].set_visible(False)
top.set_title(
    "What else became public, by reaction session (SEC 8-K acceptance times; 16:00 ET rule)",
    loc="left",
)
rel["kind"] = np.where(rel["items"].astype(str).str.contains("2.02"), "earnings", "officer chg")
for d, grp in rel.groupby("reaction_session"):
    if d not in pos:
        continue
    lines = [f"{k}: " + ", ".join(g.firm) for k, g in grp.groupby("kind")]
    yy = 0.80 if pos[d] % 2 == 0 else 0.42
    top.text(pos[d], yy, chr(10).join(lines), ha="center", va="top", fontsize=7,
             color=C["ink2"], bbox={"fc": C["surface"], "ec": C["grid"], "pad": 1.5})  # fmt: skip
for eid, d in nv.items():
    if d in pos:
        for ax in axes:
            ax.axvline(pos[d], color=C["orange"], lw=1, ls="--", alpha=0.6, zorder=0)
        top.text(pos[d], 1.02, eid, ha="center", va="top", fontsize=8.5, weight="bold",
                 color=C["orange"])  # fmt: skip
for ax, name in zip(axes[1:], SERIES, strict=True):
    v = 100 * ar[name].to_numpy()
    ax.bar(x, v, color=COL[name], width=0.7)
    band = 196 * sd[name]
    ax.axhspan(-band, band, color=C["grid"], alpha=0.6, zorder=0)
    ax.axhline(0, color=C["ink2"], lw=0.6)
    ax.set_ylabel("AR %", fontsize=8)
    ax.set_title(f"{name} (equal-weight)" if name != "NVDA" else "NVDA", loc="left")
    for i, val in enumerate(v):
        if abs(val) > band:
            ax.text(i, val + (0.6 if val > 0 else -0.6), f"{val:+.1f}", ha="center",
                    va="bottom" if val > 0 else "top", fontsize=7, color=C["ink2"])  # fmt: skip
    lim = max(abs(v).max() * 1.35, band * 1.5)
    ax.set_ylim(-lim, lim)
axes[-1].set_xticks(
    x,
    [d.strftime("%b %d") for d in win],
    rotation=45,
    fontsize=8,
    ha="right",
    rotation_mode="anchor",
)
fig.suptitle("Step 1: the E0 window is shared with Alphabet, Microsoft, Amazon and Intel results; "
             "the Nov 4–5 slide follows AMD and Qualcomm results\n(daily abnormal returns vs SPY, "
             "grey band = ±1.96 σ of normal days; PROVISIONAL yfinance prices)",
             x=0.01, ha="left", fontsize=10.5, color=C["ink"])  # fmt: skip
fig.tight_layout(rect=(0, 0, 1, 0.95))
fig.savefig(OUT / "fig6_confounders_timeline.png", dpi=150)
print("saved", OUT / "fig6_confounders_timeline.png")
print((100 * ar).round(1).to_string())
