"""Step 1(f): H6 competitor spillover at E2 (2026-11-12) with contaminated peers removed.

Peer status comes from configs/nvda_chronology.yaml (peer_contamination_e2). Same method as
Step 0c: SPY market model per series fitted on [-252,-31] before E0, equal-weight log-return
baskets. Reports session 0 (2026-11-12) and the [-1,0] window (2026-11-13 not yet complete).
EXPLORATORY: one event, peers classified after the price move was seen.
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from shockamp import CONFIGS, REPORTS
from shockamp.calendar import complete_sessions, map_event, nyse_schedule
from shockamp.data.prices import fetch_prices
from shockamp.returns import abnormal_returns, fit_market_model, log_returns

OUT = REPORTS / "step1"
chron = yaml.safe_load((CONFIGS / "nvda_chronology.yaml").read_text(encoding="utf-8"))
groups = yaml.safe_load((CONFIGS / "tickers.yaml").read_text(encoding="utf-8"))["h6_groups"]
status = {p["ticker"]: p["status"] for p in chron["peer_contamination_e2"]}
G1, G3 = groups["G1_competitors"], groups["G3_other_semis"]

sched = nyse_schedule("2024-01-01", "2026-12-31")
SESS = complete_sessions(sched.index, pd.Timestamp("2026-11-13 21:30", tz="UTC"))
SESS = SESS[SESS <= "2026-11-12"]
px = pd.DataFrame(
    {t: fetch_prices(t, "2004-01-01", "2026-11-13")["Adj Close"] for t in ["SPY", "NVDA", *G1, *G3]}
).reindex(SESS)
r = log_returns(px)
e0 = map_event("2026-10-29", SESS, time_known=False).event_session
e2 = map_event("2026-11-12", SESS, time_known=False).event_session
W = {"session 0 (Nov 12)": SESS[SESS.get_loc(e2) : SESS.get_loc(e2) + 1],
     "[-1,0] (Nov 11-12)": SESS[SESS.get_loc(e2) - 1 : SESS.get_loc(e2) + 1]}  # fmt: skip

VARIANTS = {
    "G1 all four (Step 0c)": G1,
    "excl. contaminated (AVGO, MRVL)": [t for t in G1 if status[t] != "CONTAMINATED"],
    "clean only (MRVL)": [t for t in G1 if status[t] == "CLEAN"],
    "excl. INTC only (AMD, AVGO, MRVL)": [t for t in G1 if t != "INTC"],
}
rows, firm_rows = [], []
r["G3"] = r[G3].mean(axis=1)
mm3 = fit_market_model(r, "G3", ["SPY"], e0)
for t in ["NVDA", *G1]:
    mm = fit_market_model(r, t, ["SPY"], e0)
    for wn, w in W.items():
        a = abnormal_returns(r, t, mm, w).AR.sum()
        firm_rows.append({"ticker": t, "status": status.get(t, "event firm"), "window": wn,
                          "CAR_pct": round(100 * a, 2),
                          "z": round(a / (mm.resid_sd * np.sqrt(len(w))), 2)})  # fmt: skip
for name, members in VARIANTS.items():
    col = f"B:{name}"
    r[col] = r[members].mean(axis=1)
    r[col + "-G3"] = r[col] - r["G3"]
    mm = fit_market_model(r, col, ["SPY"], e0)
    mmd = fit_market_model(r, col + "-G3", ["SPY"], e0)
    for wn, w in W.items():
        car = abnormal_returns(r, col, mm, w).AR.sum()
        g3 = abnormal_returns(r, "G3", mm3, w).AR.sum()
        d = abnormal_returns(r, col + "-G3", mmd, w).AR.sum()
        rows.append({"basket": name, "members": ",".join(members), "window": wn,
                     "basket_CAR_pct": round(100 * car, 2), "G3_CAR_pct": round(100 * g3, 2),
                     "diff_CAR_pct": round(100 * d, 2),
                     "diff_z": round(d / (mmd.resid_sd * np.sqrt(len(w))), 2)})  # fmt: skip
firm = pd.DataFrame(firm_rows)
tab = pd.DataFrame(rows)
firm.to_csv(OUT / "peer_ar_e2.csv", index=False)
tab.to_csv(OUT / "h6_e2_contamination.csv", index=False)
print(firm.to_string(index=False))
print(tab.drop(columns="members").to_string(index=False))
(OUT / "h6_e2_contamination.json").write_text(
    json.dumps({"status": status, "rows": rows}, indent=2), encoding="utf-8"
)

# figure: left = firm ARs on Nov 12 coloured by status; right = G1 - G3 under each variant
C = {"CLEAN": "#1baf7a", "UNCLEAR": "#8a8984", "CONTAMINATED": "#eb6834", "event firm": "#0b0b0b",
     "blue": "#2a78d6", "ink2": "#52514e", "grid": "#e6e5e1", "surface": "#fcfcfb"}  # fmt: skip
plt.rcParams.update({"figure.facecolor": C["surface"], "axes.facecolor": C["surface"],
                     "axes.edgecolor": C["grid"], "font.size": 8.5, "axes.titleweight": "bold",
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": C["grid"], "axes.axisbelow": True})  # fmt: skip
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw={"width_ratios": [1, 1.4]})
f0 = firm[firm.window == "session 0 (Nov 12)"]
a1.bar(f0.ticker, f0.CAR_pct, color=[C[s] for s in f0.status], width=0.6)
for i, rr in enumerate(f0.itertuples()):
    a1.text(i, rr.CAR_pct + (0.4 if rr.CAR_pct >= 0 else -0.4), f"{rr.CAR_pct:+.1f}\n({rr.status.lower()})",
            ha="center", va="bottom" if rr.CAR_pct >= 0 else "top", fontsize=7, color=C["ink2"])  # fmt: skip
a1.axhline(0, color=C["ink2"], lw=0.8)
lo, hi = f0.CAR_pct.min(), f0.CAR_pct.max()
a1.set_ylim(lo - 3, hi + 3)
a1.set_ylabel("abnormal return on 2026-11-12, % (vs SPY)")
a1.set_title("NVDA and G1 competitors on the resignation day", loc="left")
t0 = tab[tab.window == "session 0 (Nov 12)"].iloc[::-1]
a2.barh(t0.basket, t0.diff_CAR_pct, color=C["blue"], height=0.55)
for i, rr in enumerate(t0.itertuples()):
    a2.text(max(rr.diff_CAR_pct, 0) + 0.15, i, f"{rr.diff_CAR_pct:+.2f} pp  (z = {rr.diff_z:+.1f})",
            va="center", fontsize=7.5, color=C["ink2"])  # fmt: skip
a2.axvline(0, color=C["ink2"], lw=0.8)
a2.set_xlim(min(0, t0.diff_CAR_pct.min()) - 1, t0.diff_CAR_pct.max() + 4)
a2.set_xlabel("competitor basket minus G3 other semis, abnormal return on 2026-11-12, pp")
a2.set_title("H6 spillover (G1 - G3) with contaminated peers removed", loc="left")
fig.suptitle("Step 1(f), exploratory: AMD and INTC had own news on Nov 12 (AMD's upgrade itself cites "
             "NVIDIA's leadership news)", x=0.01, ha="left", fontsize=10)  # fmt: skip
fig.tight_layout(rect=(0, 0, 1, 0.94))
fig.savefig(OUT / "fig10_h6_contamination.png", dpi=150)
print("saved fig10")
