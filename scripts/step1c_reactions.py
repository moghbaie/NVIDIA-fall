"""Step 1(c): stock reactions to the FROZEN pre-E0 news inventory (2026-08-26 .. 2026-10-28).

Refuses to run unless configs/news_inventory.yaml matches its freeze record. One SPY market model
per firm, fitted on [-252,-31] sessions before 2026-08-26 (before the inventory window, so no item
contaminates the estimation). Window: [0,+1] when the time of day is known, else [-1,+1].
Reaction vs ex-ante expectation: consistent / contrary / no detectable reaction / unsigned.
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
from shockamp.evidence import assert_frozen, load_inventory
from shockamp.returns import abnormal_returns, fit_market_model, log_returns

OUT = REPORTS / "step1"
INV = CONFIGS / "news_inventory.yaml"
REC = OUT / "inventory_freeze.json"
frozen = assert_frozen(INV, REC)  # hard stop if labels changed after freezing
items = load_inventory(INV)

START, END = "2004-01-01", "2026-11-13"
sched = nyse_schedule(START, "2026-12-31")
SESS = complete_sessions(sched.index, pd.Timestamp("2026-11-13 21:30", tz="UTC"))
SESS = SESS[SESS <= "2026-11-12"]
ANCHOR = pd.Timestamp("2026-08-26")

us = {"NVDA", "SPY"} | {c for it in items for c in it["companies"] if c.isalpha() and c.isupper()}
px = {}
for t in sorted(us):
    df = fetch_prices(t, START, END)
    if len(df) > 300:
        px[t] = df["Adj Close"]
adj = pd.DataFrame(px).reindex(SESS)
r = log_returns(adj.dropna(subset=["SPY"]))
models = {}
for t in px:
    if t == "SPY":
        continue
    try:
        models[t] = fit_market_model(r, t, ["SPY"], ANCHOR)
    except (ValueError, KeyError):
        pass

sec = yaml.safe_load((CONFIGS / "nvda_chronology.yaml").read_text(encoding="utf-8"))["sec_releases"]
sec_sessions = [
    (pd.Timestamp(s["reaction_session"]), s["firm"]) for s in sec
]  # list: same-day releases
rows = []
item_sessions = {}
item_event: dict = {}
for it in items:
    known = it["time_et"] is not None
    ts = (pd.Timestamp(f"{it['published']} {it['time_et']}", tz="America/New_York") if known
          else pd.Timestamp(str(it["published"])))  # fmt: skip
    ev = map_event(ts, SESS, time_known=known, closes_utc=sched.close_utc if known else None)
    p = SESS.get_loc(ev.event_session)
    w = SESS[p : p + 2] if known else SESS[p - 1 : p + 2]
    item_sessions[it["id"]] = set(w)
    item_event[it["id"]] = ev.event_session
    for t in ["NVDA"] + [c for c in it["companies"] if c != "NVDA"]:
        if t not in models:
            continue
        a = abnormal_returns(r, t, models[t], w).AR
        car, z = 100 * a.sum(), a.sum() / (models[t].resid_sd * np.sqrt(len(w)))
        rows.append({"id": it["id"], "published": str(it["published"]), "time_known": known,
                     "event_session": ev.event_session.date(), "window": f"{w[0].date()}..{w[-1].date()}",
                     "ticker": t, "CAR_pct": round(car, 2), "z": round(z, 2),
                     "headline": it["headline"], "net_expected_nvda": it["net_expected_nvda"],
                     "importance": it["importance"]})  # fmt: skip
ev_tab = pd.DataFrame(rows)


def verdict(row: pd.Series) -> str:
    if row.ticker != "NVDA":
        return ""
    exp = row.net_expected_nvda
    if exp in ("mixed", "?", "0"):
        return (
            "unsigned (mixed/unclear ex ante)" if abs(row.z) >= 1.96 else "no detectable reaction"
        )
    if abs(row.z) < 1.96:
        return "no detectable reaction"
    return "consistent" if np.sign(row.z) == (1 if exp == "+" else -1) else "contrary"


ev_tab["nvda_vs_expectation"] = ev_tab.apply(verdict, axis=1)
overl = []
for _, row in ev_tab.iterrows():
    other = [i for i, s in item_sessions.items() if i != row.id and s & item_sessions[row.id]]
    secs = [f for d, f in sec_sessions if d in item_sessions[row.id]]
    overl.append("; ".join(filter(None, [", ".join(other), ", ".join(f"{f} 8-K" for f in secs)])))
ev_tab["overlapping"] = overl
ev_tab.to_csv(OUT / "news_reactions.csv", index=False)
nv = ev_tab[ev_tab.ticker == "NVDA"]
print(nv[["id", "window", "CAR_pct", "z", "net_expected_nvda", "nvda_vs_expectation",
          "overlapping"]].to_string(index=False))  # fmt: skip
summary = {"frozen": frozen, "n_items": len(items),
           "nvda_verdicts": nv.nvda_vs_expectation.value_counts().to_dict()}  # fmt: skip
(OUT / "news_reactions_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary["nvda_verdicts"]))

# figure: NVDA daily AR over the window with items marked by ex-ante expectation
C = {"blue": "#2a78d6", "orange": "#eb6834", "violet": "#6250d6", "muted": "#8a8984",
     "ink": "#0b0b0b", "ink2": "#52514e", "grid": "#e6e5e1", "surface": "#fcfcfb"}  # fmt: skip
plt.rcParams.update({"figure.facecolor": C["surface"], "axes.facecolor": C["surface"],
                     "axes.edgecolor": C["grid"], "font.size": 8.5, "axes.titleweight": "bold",
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": C["grid"], "axes.axisbelow": True})  # fmt: skip
win = SESS[(SESS >= "2026-08-24") & (SESS <= "2026-10-30")]
ar = 100 * abnormal_returns(r, "NVDA", models["NVDA"], win).AR
fig, ax = plt.subplots(figsize=(14, 5.6))
band = 196 * models["NVDA"].resid_sd
ax.axhspan(-band, band, color=C["grid"], alpha=0.6, zorder=0, lw=0)
ax.bar(range(len(win)), ar.to_numpy(), color=C["muted"], width=0.7)
col = {"+": C["blue"], "-": C["orange"], "mixed": C["violet"], "?": C["ink"], "0": C["muted"]}
pos = {d: i for i, d in enumerate(win)}
top = ar.abs().max() * 1.15
k = 0
for it in sorted(items, key=lambda x: str(x["published"])):
    d = item_event[it["id"]]  # mark the event session (window may start at -1)
    if d not in pos:
        continue
    i = pos[d]
    y = top * (0.75 + 0.12 * (k % 3))
    ax.annotate(it["id"], (i, 0), (i, y if k % 2 == 0 else -y), fontsize=7,
                color=col[it["net_expected_nvda"]], ha="center",
                arrowprops={"arrowstyle": "-", "color": col[it["net_expected_nvda"]], "lw": 0.6})  # fmt: skip
    k += 1
ax.set_xticks(range(0, len(win), 2), [d.strftime("%b %d") for d in win[::2]], rotation=45,
              ha="right", rotation_mode="anchor", fontsize=7.5)  # fmt: skip
ax.set_ylim(-top * 1.25, top * 1.15)
ax.set_ylabel("NVDA daily abnormal return vs SPY, %")
for lab, c in [
    ("expected + for NVDA", C["blue"]),
    ("expected −", C["orange"]),
    ("mixed (opposing channels)", C["violet"]),
    ("cannot sign ex ante", C["ink"]),
    ("no effect expected", C["muted"]),
]:
    ax.plot([], [], color=c, lw=2, label=lab)  # fmt: skip
ax.legend(frameon=False, ncol=5, loc="lower left", fontsize=7.5)
ax.set_title(f"Pre-E0 news inventory ({len(items)} items, labels frozen "
             f"{frozen['frozen_at_utc'][:16]} UTC before reactions were computed); grey band = ±1.96σ",
             loc="left")  # fmt: skip
fig.tight_layout()
fig.savefig(OUT / "fig8_pre_e0_news.png", dpi=150)
print("saved fig8")
