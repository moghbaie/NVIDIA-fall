"""Step 0c (EXPLORATORY, PROVISIONAL): H6 competitor spillover around the NVIDIA disclosures.

Groups come from NVIDIA's FY2026 10-K (accepted 2026-02-25), not from returns:
  G1 named data-center accelerator / networking competitors; G2 named suppliers; G3 semiconductor
  firms not named in either list; G4 cloud customers that also build in-house chips.
Benchmark: SPY-only market model fitted on [-252,-31] sessions before E0 (2026-10-29), so no group
member is ever in another firm's benchmark. Prices: yfinance (provisional until Step 1).
Outcomes for AMD/AVGO on Nov 12 were seen in news reports before this test was designed, so every
NVIDIA-sequence result here is hypothesis-generating, not confirmatory.
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

from shockamp import REPORTS
from shockamp.calendar import as_sessions, complete_sessions, map_event
from shockamp.returns import abnormal_returns, fit_market_model, log_returns

OUT = REPORTS / "step0c"
OUT.mkdir(parents=True, exist_ok=True)
NOW = pd.Timestamp.now(tz="UTC")

GROUPS = {
    "G1 competitors": ["AMD", "AVGO", "MRVL", "INTC"],
    "G2 suppliers": ["TSM", "MU", "FN"],
    "G3 other semis": ["TXN", "ADI", "NXPI", "ON", "MCHP", "AMKR", "ASML", "AMAT", "LRCX", "KLAC"],
    "G4 cloud customers": ["MSFT", "AMZN", "GOOGL", "META", "ORCL"],
}
OLD_BASKET = ["TSM", "ASML", "AMAT", "LRCX", "MU", "AMD", "AVGO", "AMKR", "KLAC"]  # Step 0 basket
EVENTS = {  # first public date; all date-only -> windows start at -1 (CLAUDE.md, PLAN.md D12)
    "E0 NYT report": "2026-10-29",
    "E1 board probe": "2026-11-08",
    "E2 resignation": "2026-11-12",
}
C = {"blue": "#2a78d6", "orange": "#eb6834", "aqua": "#1baf7a", "violet": "#6250d6",
     "yellow": "#eda100", "ink": "#0b0b0b", "ink2": "#52514e", "muted": "#8a8984",
     "grid": "#e6e5e1", "surface": "#fcfcfb", "mid": "#efeeea"}  # fmt: skip
GCOL = dict(zip(GROUPS, [C["blue"], C["aqua"], C["muted"], C["violet"]], strict=True))
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
        "font.size": 9.5,
        "axes.titlesize": 10.5,
        "axes.titleweight": "bold",
        "axes.titlecolor": C["ink"],
        "legend.frameon": False,
    }
)

firms = [t for g in GROUPS.values() for t in g]
px = yf.download(["NVDA", "SPY", *firms], start="2025-06-01", progress=False, auto_adjust=True)[
    "Close"
]
done = complete_sessions(as_sessions(px.index), NOW)
px = px.loc[px.index.isin(done)]
r = log_returns(px)
sessions = r.index
e0 = map_event("2026-10-29", sessions, time_known=False).event_session
last = sessions[-1]
print("last complete session:", last.date())

# ---- raw-return check of the reported Nov 12 moves
raw12 = (np.exp(r.loc["2026-11-12", ["NVDA", "AMD", "AVGO"]]) - 1) * 100
print("Nov 12 simple returns (%):", raw12.round(2).to_dict())


def ar_table(cols: list[str], factors: list[str], data: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    win = sessions[sessions >= pd.Timestamp("2026-10-22")]
    ars, sds = {}, {}
    for c in cols:
        mm = fit_market_model(data, c, factors, e0)
        ars[c] = abnormal_returns(data, c, mm, win).AR
        sds[c] = mm.resid_sd
    return pd.DataFrame(ars), sds


firm_ar, _ = ar_table(firms + ["NVDA"], ["SPY"], r)

# group portfolios: equal-weight log-return average, own market model (captures co-movement)
rg = r.copy()
for g, members in GROUPS.items():
    rg[g] = r[members].mean(axis=1)
grp_ar, grp_sd = ar_table(list(GROUPS) + ["NVDA"], ["SPY"], rg)


def window(name: str) -> pd.DatetimeIndex:
    ev = map_event(EVENTS[name], sessions, time_known=False).event_session
    pos = sessions.get_loc(ev)
    w = sessions[pos - 1 : pos + 2]
    return w[w <= last]


rows = []
for e in EVENTS:
    w = window(e)
    for g in [*GROUPS, "NVDA"]:
        car = float(grp_ar.loc[w, g].sum())
        se = grp_sd[g] * np.sqrt(len(w))
        rows.append({"event": e, "group": g, "start": w[0].date(), "end": w[-1].date(),
                     "n_sessions": len(w), "CAR_pct": 100 * car, "se_pct": 100 * se,
                     "z": car / se})  # fmt: skip
cars = pd.DataFrame(rows)
cars.to_csv(OUT / "group_cars.csv", index=False)
print(cars.round(2).to_string(index=False))

# ---- NVDA abnormal return under three benchmarks (contamination check)
r["OLD"] = r[OLD_BASKET].mean(axis=1)
r["G3"] = r[GROUPS["G3 other semis"]].mean(axis=1)
bench = {"SPY + Step 0 basket (mixed)": ["SPY", "OLD"], "SPY only": ["SPY"],
         "SPY + G3 (unnamed semis)": ["SPY", "G3"]}  # fmt: skip
nv = []
for lab, f in bench.items():
    a, s = ar_table(["NVDA"], f, r)
    for e in EVENTS:
        w = window(e)
        nv.append({"benchmark": lab, "event": e, "CAR_pct": 100 * a.loc[w, "NVDA"].sum(),
                   "z": a.loc[w, "NVDA"].sum() / (s["NVDA"] * np.sqrt(len(w)))})  # fmt: skip
nvdf = pd.DataFrame(nv)
nvdf.to_csv(OUT / "nvda_benchmark_sensitivity.csv", index=False)
print(nvdf.pivot(index="benchmark", columns="event", values="CAR_pct").round(2))

# ---- rebound check: Nov 9 AR vs Nov 4-5 AR across semiconductor firms
semis = [t for g in list(GROUPS)[:3] for t in GROUPS[g]]
drop = firm_ar.loc[["2026-11-04", "2026-11-05"], semis].sum()
bounce = firm_ar.loc["2026-11-09", semis]
g1 = pd.Series([t in GROUPS["G1 competitors"] for t in semis], index=semis, dtype=float)
x = np.column_stack([np.ones(len(semis)), drop, g1])
b, *_ = np.linalg.lstsq(x, bounce.to_numpy(), rcond=None)
rebound = {"slope_on_nov4_5_AR": float(b[1]), "G1_extra_AR_pct": float(100 * b[2]),
           "n_firms": len(semis)}  # fmt: skip
print("rebound regression:", {k: round(v, 3) for k, v in rebound.items()})

# ---------------------------------------------------------------------------------- figure
fig = plt.figure(figsize=(14, 9.4))
gs = fig.add_gridspec(2, 2, width_ratios=[1.25, 1], height_ratios=[1, 1], hspace=0.42, wspace=0.22)
ax1 = fig.add_subplot(gs[:, 0])
order = [t for g in GROUPS.values() for t in g] + ["NVDA"]
hm = 100 * firm_ar.loc[firm_ar.index >= "2026-10-27", order].T
cmap = LinearSegmentedColormap.from_list("div", [C["orange"], C["mid"], C["blue"]])
lim = 8
im = ax1.imshow(hm.clip(-lim, lim), aspect="auto", cmap=cmap,
                norm=TwoSlopeNorm(0, -lim, lim))  # fmt: skip
ax1.set_yticks(range(len(order)), order, fontsize=8)
ax1.set_xticks(range(hm.shape[1]), [d.strftime("%b %d") for d in hm.columns], rotation=60,
               fontsize=8)  # fmt: skip
ax1.grid(False)
y = 0
for g, m in GROUPS.items():
    ax1.axhline(y - 0.5, color=C["surface"], lw=3)
    for k in range(y, y + len(m)):
        ax1.get_yticklabels()[k].set_color(GCOL[g] if g != "G3 other semis" else C["ink2"])
    ax1.text(-0.7, y - 0.35, g, ha="right", va="bottom", fontsize=7.5, weight="bold",
             color=GCOL[g] if g != "G3 other semis" else C["ink2"])  # fmt: skip
    y += len(m)
ax1.axhline(y - 0.5, color=C["surface"], lw=3)
for e, d in EVENTS.items():
    ev = map_event(d, sessions, time_known=False).event_session
    if ev in hm.columns:
        k = list(hm.columns).index(ev)
        ax1.text(k, -1.1, e.split()[0], ha="center", fontsize=8, color=C["ink"], weight="bold")
for k, v in np.ndenumerate(hm.to_numpy()):
    if abs(v) >= 4:
        ax1.text(k[1], k[0], f"{v:+.0f}", ha="center", va="center", fontsize=6.5,
                 color=C["surface"])  # fmt: skip
cb = fig.colorbar(im, ax=ax1, orientation="horizontal", fraction=0.035, pad=0.09, shrink=0.7)
cb.set_label("daily abnormal return, % (SPY market model; clipped at ±8)")
ax1.set_title("Daily abnormal returns by firm (groups fixed from NVIDIA's 10-K)", pad=26)

ax2 = fig.add_subplot(gs[0, 1])
ev_names = list(EVENTS)
glist = [*GROUPS, "NVDA"]
wbar = 0.17
for j, g in enumerate(glist):
    sub = cars[cars.group == g].set_index("event").loc[ev_names]
    xs = np.arange(len(ev_names)) + (j - 2) * wbar
    col = GCOL.get(g, C["orange"])
    ax2.bar(xs, sub.CAR_pct, wbar * 0.9, color=col, label=g)
    ax2.errorbar(xs, sub.CAR_pct, yerr=1.96 * sub.se_pct, fmt="none", ecolor=C["ink2"], lw=1)
ax2.axhline(0, color=C["ink2"], lw=0.8)
lbl = []
for e in ev_names:
    s0 = cars[(cars.event == e)].iloc[0]
    lbl.append(f"{e}\n{s0.start:%b %d}–{s0.end:%b %d}")
ax2.set_xticks(range(len(ev_names)), lbl, fontsize=8)
ax2.set_ylabel("group CAR [−1,+1], % (95% CI)")
ax2.set_title("Group abnormal returns per disclosure (equal-weight portfolios)")
ax2.legend(fontsize=7.5, ncol=3, loc="lower left")

ax3 = fig.add_subplot(gs[1, 1])
for g in list(GROUPS)[:3]:
    m = GROUPS[g]
    ax3.scatter(100 * drop[m], 100 * bounce[m], s=42, color=GCOL[g], label=g,
                edgecolor=C["surface"], linewidth=1.5, zorder=3)  # fmt: skip
    for t in m:
        off = (-14, 5) if t == "ADI" else (3, 3)
        ax3.annotate(t, (100 * drop[t], 100 * bounce[t]), fontsize=7, color=C["ink2"],
                     xytext=off, textcoords="offset points")  # fmt: skip
xx = np.linspace(100 * drop.min(), 100 * drop.max(), 10)
ax3.plot(xx, 100 * b[0] + b[1] * xx, color=C["muted"], lw=1, ls="--",
         label=f"fit: slope {b[1]:.2f}, G1 extra {100 * b[2]:+.1f} pp")  # fmt: skip
ax3.axhline(0, color=C["ink2"], lw=0.6)
ax3.axvline(0, color=C["ink2"], lw=0.6)
ax3.set_xlabel("abnormal return Nov 4–5, % (the sector selloff)")
ax3.set_ylabel("abnormal return Nov 9, %")
ax3.set_title("Rebound or substitution? Nov 9 vs the prior selloff")
ax3.legend(fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2)
fig.suptitle("H6 exploratory check: did NVIDIA's leadership news move its competitors? "
             f"(PROVISIONAL yfinance data through {last:%b %d}; hypothesis-generating only)",
             x=0.01, ha="left", fontsize=11.5, color=C["ink"])  # fmt: skip
fig.savefig(OUT / "fig5_competitor_spillover.png", dpi=150, bbox_inches="tight")
(OUT / "summary.json").write_text(
    json.dumps(
        {
            "last_session": str(last.date()),
            "nov12_simple_returns_pct": raw12.round(2).to_dict(),
            "rebound": rebound,
        },
        indent=2,
    )  # fmt: skip
)
print("saved", OUT / "fig5_competitor_spillover.png")
