"""Step 0: source feasibility audit, NVIDIA exploratory chronology, panel feasibility, H1 power.

Outputs -> reports/step0/. Network needed. The NVIDIA abnormal-return panel here is EXPLORATORY
(not the preregistered Step 4 model). Power-simulation outcomes are SYNTHETIC.
"""

from __future__ import annotations

import hashlib
import json
import os
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import pandas as pd
import requests
import yaml
import yfinance as yf

from shockamp import CONFIGS, DATA, REPORTS
from shockamp.calendar import as_sessions, complete_sessions, map_event
from shockamp.power import mde, power_grid
from shockamp.returns import abnormal_returns, fit_market_model, log_returns

OUT = REPORTS / "step0"
OUT.mkdir(parents=True, exist_ok=True)
NOW = pd.Timestamp.now(tz="UTC")
GENTRY = DATA / "raw" / "ceo_dismissal" / "ceo_dismissal_26Nov25.xlsx"
UA = os.environ.get("SEC_USER_AGENT", "shockamp-research-prototype admin@example.org")

# reference palette (dataviz skill, light mode)
C = {
    "blue": "#2a78d6",
    "orange": "#eb6834",
    "aqua": "#1baf7a",
    "yellow": "#eda100",
    "violet": "#6250d6",
    "ink": "#0b0b0b",
    "ink2": "#52514e",
    "muted": "#8a8984",
    "grid": "#e6e5e1",
    "surface": "#fcfcfb",
}
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
        "grid.linewidth": 0.8,
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


def probe(name: str, fn) -> dict:
    t0 = time.time()
    try:
        info = fn()
        status = info.pop("status", "available")
    except Exception as e:  # noqa: BLE001 - audit records any failure
        info, status = {"error": f"{type(e).__name__}: {e}"[:300]}, "unavailable"
    return {"source": name, "status": status, "latency_s": round(time.time() - t0, 2), **info}


def p_yahoo():
    d = yf.download("NVDA", start="2015-01-01", progress=False, auto_adjust=True)
    return {
        "rows": len(d),
        "first": str(d.index.min().date()),
        "last": str(d.index.max().date()),
        "note": "unofficial API; last row may be an unfinished session",
    }


def p_fred():
    r = requests.get("https://fred.stlouisfed.org/graph/fredgraph.csv?id=STLFSI4", timeout=30)
    r.raise_for_status()
    d = pd.read_csv(pd.io.common.StringIO(r.text))
    return {
        "rows": len(d),
        "first": str(d.iloc[0, 0]),
        "last": str(d.iloc[-1, 0]),
        "note": "STLFSI4 weekly; current vintage only (ALFRED for vintages)",
    }


def p_sec():
    r = requests.get(
        "https://data.sec.gov/submissions/CIK0001045810.json",
        headers={"User-Agent": UA},
        timeout=30,
    )
    r.raise_for_status()
    rec = r.json()["filings"]["recent"]
    f = pd.DataFrame(rec)
    k = f[f.form == "8-K"]
    return {
        "rows": len(f),
        "eight_k": len(k),
        "last_8k_accepted": str(k.acceptanceDateTime.iloc[0]),
        "note": "acceptanceDateTime gives a second-resolution public timestamp",
    }


def p_gdelt():
    base = "https://api.gdeltproject.org/api/v2/doc/doc"
    res = {}
    for label, start, end in [
        ("recent", "20261101000000", "20261112000000"),
        ("2018", "20180601000000", "20180610000000"),
    ]:
        r = requests.get(
            base,
            params={
                "query": "nvidia",
                "mode": "artlist",
                "format": "json",
                "maxrecords": 10,
                "startdatetime": start,
                "enddatetime": end,
            },
            timeout=30,
        )
        try:
            n = len(r.json().get("articles", []))
        except ValueError:
            n = f"non-JSON response: {r.text[:120]!r}"
        res[f"articles_{label}"] = n
        time.sleep(6)  # GDELT asks for <= 1 request / 5 s
    ok_hist = isinstance(res["articles_2018"], int) and res["articles_2018"] > 0
    res["status"] = "available" if ok_hist else "conditional"
    res["note"] = "historical window works" if ok_hist else "historical query returned nothing"
    return res


def p_gentry():
    h = hashlib.sha256(GENTRY.read_bytes()).hexdigest()
    d = pd.read_excel(GENTRY)
    return {
        "rows": len(d),
        "sha256": h[:16],
        "license": "CC-BY-4.0",
        "url": "https://zenodo.org/records/23328926",
        "note": "archival version 26Nov25; announce dates non-randomly missing",
    }


# ---------------------------------------------------------------- 1. source audit
audit = [
    probe("Yahoo prices (yfinance)", p_yahoo),
    probe("FRED STLFSI4", p_fred),
    probe("SEC EDGAR submissions", p_sec),
    probe("GDELT DOC 2.0", p_gdelt),
    probe("CEO dismissal DB (Zenodo)", p_gentry),
]
(OUT / "source_audit.json").write_text(json.dumps(audit, indent=2, default=str))
print(pd.DataFrame(audit)[["source", "status", "latency_s"]].to_string(index=False))

# ---------------------------------------------------------------- 2. NVIDIA exploratory chronology
tick = yaml.safe_load((CONFIGS / "tickers.yaml").read_text())
semis = tick["semis_ex_nvda"]
px = yf.download(["NVDA", "SPY", *semis], start="2025-06-01", progress=False, auto_adjust=True)[
    "Close"
]
done = complete_sessions(as_sessions(px.index), NOW)
px = px.loc[done]
r = log_returns(px.ffill(limit=1))
r["SEMI_xNVDA"] = r[semis].mean(axis=1)
chron = yaml.safe_load((CONFIGS / "nvda_chronology.yaml").read_text())
ev = {
    e["id"]: map_event(pd.Timestamp(str(e["first_public_date"])), r.index, time_known=False)
    for e in chron["events"]
}
# estimation window anchored to E0 so nothing from the disclosure sequence enters the fit
mm = fit_market_model(r, "NVDA", ["SPY", "SEMI_xNVDA"], ev["E0"].event_session)
win = r.loc["2026-10-15":].index
ar = abnormal_returns(r, "NVDA", mm, win)
ar.to_csv(OUT / "nvda_exploratory_ar.csv")

fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 7.2), sharex=True, height_ratios=[1.3, 1])
base = r.loc[win]
for col, lab, c in [
    ("NVDA", "NVDA", C["blue"]),
    ("SEMI_xNVDA", "Semis ex-NVDA (EW, 9)", C["orange"]),
    ("SPY", "SPY", C["aqua"]),
]:
    idx = 100 * np.exp(base[col].cumsum())
    a1.plot(idx.index, idx, color=c, label=lab)
    a1.annotate(
        lab,
        (idx.index[-1], idx.iloc[-1]),
        xytext=(6, 0),
        textcoords="offset points",
        color=C["ink2"],
        va="center",
        fontsize=9,
    )
a1.set_ylabel("Index (Oct 14 close = 100)")
a1.set_title("NVIDIA vs ex-NVDA semis vs market, with leadership-news disclosure stages")
a1.legend(loc="lower left")
cols = [C["blue"] if v < 0 else C["muted"] for v in ar.AR]
a2.bar(ar.index, 100 * ar.AR, color=cols, width=0.7)
band = 1.96 * mm.resid_sd * 100
a2.axhspan(-band, band, color=C["grid"], alpha=0.7, zorder=0, label="±1.96 σ (normal-day range)")
a2.set_ylabel("Abnormal return, %")
a2.set_title("NVDA daily abnormal return (market + ex-NVDA sector model)")
a2.legend(loc="lower left")
for k, e in ev.items():
    for ax in (a1, a2):
        ax.axvline(e.event_session, color=C["ink2"], lw=1, ls="--")
    a1.annotate(
        k,
        (e.event_session, a1.get_ylim()[1]),
        xytext=(-3 if k == "E1" else 3, -12),
        textcoords="offset points",
        fontsize=9,
        color=C["ink"],
        ha="right" if k == "E1" else "left",
    )
a2.annotate(
    "Nov 5: sector crash\n(semis −14.6%), NVDA AR −0.7%",
    (pd.Timestamp("2026-11-05"), -0.7),
    xytext=(pd.Timestamp("2026-11-01"), -7.5),
    ha="center",
    fontsize=8,
    color=C["ink2"],
    arrowprops={"arrowstyle": "-", "color": C["muted"], "lw": 0.8},
)
fig.text(
    0.01,
    0.005,
    f"Source: Yahoo Finance adjusted closes through {done[-1].date()} (complete "
    f"sessions only). Model fit on sessions {mm.est_start.date()}–{mm.est_end.date()} "
    f"(n={mm.n_obs}). EXPLORATORY, not the preregistered model.",
    fontsize=7.5,
    color=C["muted"],
)
fig.tight_layout(rect=(0, 0.02, 1, 1))
fig.savefig(OUT / "fig1_nvda_chronology.png", dpi=150)
plt.close(fig)

stage_car = {}
for k, (a, b) in {
    "E0 [0,+1]": ("E0", 1),
    "E1 [0,+1]": ("E1", 1),
    "E2 [0,0]": ("E2", 0),
    "E1→E2 [E1,E2]": ("E1", None),
}.items():
    s0 = ev[a].event_session
    s1 = ev["E2"].event_session if b is None else r.index[r.index.get_loc(s0) + b]
    seg = ar.loc[s0:s1, "AR"]
    stage_car[k] = {
        "CAR_pct": round(100 * seg.sum(), 2),
        "z": round(seg.sum() / (mm.resid_sd * np.sqrt(len(seg))), 2),
        "n": len(seg),
    }
print(json.dumps(stage_car, indent=1))

# ---------------------------------------------------------------- 3. panel feasibility
g = pd.read_excel(GENTRY)
g = g[g.departure_code.notna() & (g.departure_code != 9)].copy()
g["year"] = g.date_departure_announced.fillna(g.left_ceo_office).dt.year
grp = {
    1: "Death/illness",
    2: "Death/illness",
    3: "Dismissed: performance",
    4: "Dismissed: misconduct/legal",
    5: "Voluntary",
    6: "Voluntary",
    7: "Other/M&A/interim",
}
g["group"] = g.departure_code.map(grp)
g["has_announce"] = g.date_departure_announced.notna()
g["has_8k"] = g.eight_ks.notna()
p = g[(g.year >= 2005) & (g.year <= 2025)]
tab = p.pivot_table(index="year", columns="group", values="gvkey", aggfunc="count").fillna(0)
tab.to_csv(OUT / "panel_counts_by_year.csv")
cov = p.groupby("group").agg(
    n=("gvkey", "size"), announce_date=("has_announce", "mean"), eight_k_links=("has_8k", "mean")
)
cov.to_csv(OUT / "panel_coverage.csv")
print(cov.round(2).to_string())

order = [
    "Voluntary",
    "Dismissed: performance",
    "Dismissed: misconduct/legal",
    "Death/illness",
    "Other/M&A/interim",
]
pal = [C["aqua"], C["orange"], C["blue"], C["violet"], C["muted"]]
fig, (b1, b2) = plt.subplots(1, 2, figsize=(11, 4.2), width_ratios=[1.6, 1])
for gname, c in zip(order, pal, strict=True):
    if gname in tab:
        b1.plot(tab.index, tab[gname], color=c, label=gname, marker="o", ms=3)
b1.set_title("CEO turnovers per year by departure reason (S&P 1500, 2005–2025)")
b1.set_ylabel("Events")
b1.legend(fontsize=8, ncol=1, loc="center left", bbox_to_anchor=(0.0, 0.62))
b1.set_ylim(0, 200)
b1.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
b1.axvspan(2022.5, 2025.5, color=C["grid"], alpha=0.6, zorder=0)
b1.annotate(
    "database lag:\nyears incomplete",
    (2024, 195),
    fontsize=8,
    color=C["ink2"],
    ha="center",
    va="top",
)
cc = cov.reindex(order)
y = np.arange(len(order))
b2.barh(y + 0.2, 100 * cc.announce_date, height=0.38, color=C["blue"], label="announcement date")
b2.barh(y - 0.2, 100 * cc.eight_k_links, height=0.38, color=C["orange"], label="8-K link(s)")
b2.set_yticks(y, [f"{o} (n={int(n)})" for o, n in zip(order, cc.n, strict=True)], fontsize=8)
b2.invert_yaxis()
b2.set_xlim(0, 100)
b2.set_xlabel("% of events with field present")
b2.set_title("Timestamp coverage")
b2.legend(fontsize=8, loc="lower right")
fig.text(
    0.01,
    0.005,
    "Source: Gentry et al. Open Sourced Database for CEO Dismissal (Zenodo 23328926, "
    "CC-BY-4.0). Year = announcement year, else left-office year.",
    fontsize=7.5,
    color=C["muted"],
)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(OUT / "fig2_panel_feasibility.png", dpi=150)
plt.close(fig)

# ---------------------------------------------------------------- 4. power simulation (SYNTHETIC)
n_by = p.groupby("departure_code").size()
results = {}
for rate in (0.5, 0.7):
    vol = int(rate * (n_by.get(5, 0) + n_by.get(6, 0)))
    perf, mis = int(rate * n_by.get(3, 0)), int(rate * n_by.get(4, 0))
    designs = {
        f"ordinal 0/1/2 (n={vol + perf + mis})": ([0, 1, 2], [vol, perf, mis]),
        f"misconduct vs voluntary (n={vol + mis}, {mis} misconduct)": ([0, 1], [vol, mis]),
    }
    betas = -np.array([0, 0.0025, 0.005, 0.0075, 0.01, 0.015, 0.02, 0.03, 0.04, 0.06])
    gr = power_grid(designs, betas, [0.05, 0.07, 0.09], reps=400)
    gr["match_rate"] = rate
    results[rate] = gr
grid = pd.concat(results.values())
grid.to_csv(OUT / "power_grid.csv", index=False)
m = pd.concat([mde(gr).assign(match_rate=k) for k, gr in results.items()])
m.to_csv(OUT / "power_mde.csv", index=False)
print(m.to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
sig_col = {0.05: C["aqua"], 0.07: C["blue"], 0.09: C["violet"]}
gr7 = results[0.7]
for ax, d in zip(axes, gr7.design.unique(), strict=True):
    for s, gs in gr7[gr7.design == d].groupby("sigma"):
        ax.plot(
            -100 * gs.beta_int,
            gs.power,
            color=sig_col[s],
            marker="o",
            ms=4,
            label=f"CAR noise σ = {s:.0%}",
        )
    ax.axhline(0.8, color=C["ink2"], lw=1, ls="--")
    ax.axhline(0.05, color=C["muted"], lw=1, ls=":")
    ax.set_title(d, fontsize=10)
    ax.set_xlim(-0.1, 4.1)
    ax.set_xlabel("|β(sev × stress)|, pp of CAR per severity step per 1 SD stress")
axes[0].set_ylabel("Power (α = 0.05, two-sided)")
axes[0].legend(fontsize=8, loc="center right")
axes[0].annotate("80%", (0, 0.81), fontsize=8, color=C["ink2"])
fig.suptitle(
    "H1 power: can the panel detect stress amplification? (70% of events matched to prices)",
    fontsize=11,
    fontweight="bold",
    color=C["ink"],
)
fig.text(
    0.01,
    0.005,
    "SYNTHETIC outcomes on the real 2005–2025 event counts; 400 reps per point; HC1 "
    "SEs; stress ~ N(0,1) independent of severity.",
    fontsize=7.5,
    color=C["muted"],
)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(OUT / "fig3_power.png", dpi=150)
plt.close(fig)

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "run_at_utc": str(NOW),
            "last_complete_session": str(done[-1].date()),
            "nvda_model": {
                "est": [str(mm.est_start.date()), str(mm.est_end.date())],
                "n": mm.n_obs,
                "params": mm.params.round(4).to_dict(),
                "resid_sd": round(mm.resid_sd, 4),
            },
            "nvda_stage_car": stage_car,
            "events": {k: str(v.event_session.date()) for k, v in ev.items()},
        },
        indent=2,
    )
)
print("wrote", sorted(x.name for x in OUT.iterdir()))
