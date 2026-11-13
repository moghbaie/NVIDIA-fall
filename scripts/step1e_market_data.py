"""Step 1(e): market data layer — fetch, cache, validate, reproduce Step 0 (writes reports/step1/).

Checks (each PASS / WARN / FAIL in reports/step1/validation_1e.json):
  1. NYSE sessions incl. early closes (exchange_calendars XNYS) vs every price index;
  2. prices: positivity, duplicates, split consistency, adjustment-factor jumps off action dates;
  3. ALFRED vintages: availability = first session strictly after realtime_start (one-session
     lag, because a vintage date carries no intraday release time); no look-ahead on a sample;
  4. reproducibility: a second pass from the cache gives identical content hashes, and the
     provisional Step 0 / 0c NVIDIA numbers are recomputed from the cached snapshot.
Snapshot end = last complete session at run time (no partial bars are cached).
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from shockamp import CONFIGS, REPORTS
from shockamp.calendar import complete_sessions, map_event, nyse_schedule
from shockamp.data.cache import frame_sha256, manifest
from shockamp.data.fred import fetch_alfred, first_release, point_in_time_daily
from shockamp.data.prices import fetch_prices, validate_prices
from shockamp.returns import abnormal_returns, fit_market_model, log_returns

OUT = REPORTS / "step1"
OUT.mkdir(parents=True, exist_ok=True)
NOW = pd.Timestamp.now(tz="UTC")
START = "2004-01-01"
sched = nyse_schedule(START, "2026-12-31")
done = complete_sessions(sched.index, NOW)
LAST = done[-1]
END = str((LAST + pd.Timedelta(days=1)).date())  # yfinance end is exclusive
SESS = done

tick_cfg = yaml.safe_load((CONFIGS / "tickers.yaml").read_text(encoding="utf-8"))
g = tick_cfg["h6_groups"]
TICKERS = sorted(
    {"NVDA", "SPY", "QQQ", "^VIX", "^VXN", *tick_cfg["semis_ex_nvda"]}
    | {
        t
        for k in (
            "G1_competitors",
            "G1_extended",
            "G2_suppliers",
            "G3_other_semis",
            "G4_cloud_customers",
        )
        for t in g[k]
    }  # fmt: skip
)
FRED = ["STLFSI4", "BAA10Y", "DGS2", "DGS10", "VIXCLS"]
checks: list[dict] = []


def add(item: str, kind: str, status: str, source: str, availability: str, detail: str) -> None:
    checks.append({"item": item, "classification": kind, "status": status, "source": source,
                   "availability": availability, "detail": detail})  # fmt: skip


# ------------------------------------------------------------------------- 1-2 prices
early = sched.index[sched.close_utc.dt.tz_convert("America/New_York").dt.hour < 16]
add("NYSE calendar", "calendar", "PASS", "exchange_calendars XNYS", "deterministic",
    f"{len(SESS)} complete sessions {SESS[0].date()}..{LAST.date()}; "
    f"{len(early[early <= LAST])} early closes in range")  # fmt: skip
prices: dict[str, pd.DataFrame] = {}
for t in TICKERS:
    df = fetch_prices(t, START, END)
    df = df[df.index <= LAST]
    prices[t] = df
    c = validate_prices(t, df, SESS)
    detail = (f"{c.first}..{c.last}, rows {c.n_rows}, missing sessions {c.missing_sessions}, "
              f"non-session rows {c.extra_dates}, splits {c.splits}"
              + (f", split failures {c.split_failures}" if c.split_failures else "")
              + (f", adj-factor jumps off action dates {c.adj_jumps_off_action_dates[:5]}"
                 if c.adj_jumps_off_action_dates else ""))  # fmt: skip
    add(f"price {t}", "market price", c.status, "Yahoo via yfinance (prototype source)",
        "close of each session (16:00 ET; 13:00 on early closes)", detail)  # fmt: skip

# ------------------------------------------------------------------------- 3 ALFRED
alfred: dict[str, pd.DataFrame] = {}
pol = yaml.safe_load((CONFIGS / "fred_series.yaml").read_text(encoding="utf-8"))["series"]
for sid in FRED:
    v = fetch_alfred(sid)
    alfred[sid] = v
    cfg = pol[sid]
    fr = first_release(v)
    fv = v.realtime_start.min()
    era = fr[fr.date >= fv]
    latest = v.sort_values("realtime_start").groupby("date").last()["value"]
    rev_share = float(np.mean(np.abs(latest.reindex(era.date).to_numpy() - era.value.to_numpy())
                              > 1e-9))  # fmt: skip
    placeholders = int((v.realtime_start < v.date).sum())
    pit = point_in_time_daily(v, SESS[SESS >= "2005-01-01"], policy=cfg["policy"]).dropna()
    leak = int((pit.available_session > pit.index).sum() + (pit.obs_date >= pit.index).sum())
    ok_policy = cfg["policy"] == "vintage" or rev_share <= cfg["max_revised_share"]
    status = "PASS" if leak == 0 and ok_policy else "FAIL"
    first_ok = pit.index.min().date() if len(pit) else None
    avail = ("session after realtime_start" if cfg["policy"] == "vintage"
             else "session after the observation date")  # fmt: skip
    add(f"ALFRED {sid}", f"macro series ({cfg['policy']})", status, "FRED/ALFRED API",
        f"{avail} (one-session lag; vintage dates carry no intraday time)",
        f"first vintage {fv.date()}; vintage-era share revised after first release "
        f"{rev_share:.1%}; holiday placeholders dropped {placeholders}; first usable session "
        f"since 2005: {first_ok}; look-ahead violations {leak}")  # fmt: skip

# ------------------------------------------------------------------------- 4 reproducibility
h1 = {t: frame_sha256(df) for t, df in prices.items()}
h2 = {t: frame_sha256(fetch_prices(t, START, END)[lambda d: d.index <= LAST]) for t in TICKERS}
same = all(h1[t] == h2[t] for t in TICKERS)
add("cache reproducibility", "reproducibility", "PASS" if same else "FAIL", "data/raw cache",
    "n/a", f"{sum(h1[t] == h2[t] for t in TICKERS)}/{len(TICKERS)} price hashes identical "
    "on a second pass from the cache")  # fmt: skip

adj = pd.DataFrame({t: prices[t]["Adj Close"] for t in TICKERS}).reindex(SESS)
r = log_returns(adj.dropna(subset=["NVDA", "SPY"]))  # no filling of gaps
r["OLD"] = r[tick_cfg["semis_ex_nvda"]].mean(axis=1)
r["G3"] = r[[str(x) for x in g["G3_other_semis"]]].mean(axis=1)
e0 = map_event("2026-10-29", r.index, time_known=False).event_session
step0 = pd.read_csv(REPORTS / "step0" / "nvda_exploratory_ar.csv", index_col=0, parse_dates=True)
mm_old = fit_market_model(r, "NVDA", ["SPY", "OLD"], e0)
re_ar = abnormal_returns(r, "NVDA", mm_old, step0.index.intersection(r.index)).AR
diff = (100 * (re_ar - step0.AR.reindex(re_ar.index))).abs()
st = "PASS" if diff.max() < 0.25 else "WARN"
add("reproduce Step 0 NVDA daily ARs", "reproducibility", st, "cached snapshot vs reports/step0",
    "n/a", f"max |diff| {diff.max():.3f} pp over {len(diff)} sessions "
    "(Step 0 used yfinance auto-adjusted closes pulled earlier the same day)")  # fmt: skip

s0c = pd.read_csv(REPORTS / "step0c" / "nvda_benchmark_sensitivity.csv")
bench = {"SPY + Step 0 basket (mixed)": ["SPY", "OLD"], "SPY only": ["SPY"],
         "SPY + G3 (unnamed semis)": ["SPY", "G3"]}  # fmt: skip
rows = []
for lab, f in bench.items():
    mm = fit_market_model(r, "NVDA", f, e0)
    for ev, d in {"E0 NYT report": "2026-10-29", "E1 board probe": "2026-11-08",
                  "E2 resignation": "2026-11-12"}.items():  # fmt: skip
        s = map_event(d, r.index, time_known=False).event_session
        p = r.index.get_loc(s)
        w = r.index[p - 1 : p + 2]
        w = w[w <= LAST]
        car = 100 * abnormal_returns(r, "NVDA", mm, w).AR.sum()
        old = s0c[(s0c.benchmark == lab) & (s0c.event == ev)].CAR_pct.iloc[0]
        rows.append({"benchmark": lab, "event": ev, "step0c": old, "step1": car, "diff": car - old})
rep = pd.DataFrame(rows)
rep.to_csv(OUT / "reproduce_step0c.csv", index=False)
st = "PASS" if rep["diff"].abs().max() < 0.25 else "WARN"
add("reproduce Step 0c NVDA CARs", "reproducibility", st, "cached snapshot vs reports/step0c",
    "n/a", f"max |diff| {rep['diff'].abs().max():.3f} pp, 9 benchmark x event cells")  # fmt: skip

# ------------------------------------------------------------------------- outputs
val = {
    "step": "1e",
    "generated_utc": NOW.isoformat(),
    "snapshot_last_session": str(LAST.date()),
    "summary": pd.Series([c["status"] for c in checks]).value_counts().to_dict(),
    "gate": "PASS" if all(c["status"] != "FAIL" for c in checks) else "FAIL",
    "checks": checks,
    "manifest": manifest().to_dict(orient="records"),
}
(OUT / "validation_1e.json").write_text(json.dumps(val, indent=2, default=str), encoding="utf-8")
print(json.dumps(val["summary"]), "gate:", val["gate"])
for c in checks:
    if c["status"] != "PASS":
        print(c["status"], c["item"], "|", c["detail"])

# figure: coverage + ALFRED revisions
C = {"blue": "#2a78d6", "orange": "#eb6834", "ink": "#0b0b0b", "ink2": "#52514e",
     "muted": "#8a8984", "grid": "#e6e5e1", "surface": "#fcfcfb"}  # fmt: skip
plt.rcParams.update({"figure.facecolor": C["surface"], "axes.facecolor": C["surface"],
                     "axes.edgecolor": C["grid"], "font.size": 8.5, "axes.titleweight": "bold",
                     "axes.spines.top": False, "axes.spines.right": False})  # fmt: skip
fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 6.5), gridspec_kw={"width_ratios": [1.35, 1]})
yrs = range(2004, LAST.year + 1)
cov = pd.DataFrame({t: [prices[t].index.year.value_counts().get(y, 0) /
                        max(1, (SESS.year == y).sum()) for y in yrs] for t in TICKERS},
                   index=list(yrs)).T  # fmt: skip
a1.imshow(cov.to_numpy(), aspect="auto", cmap=plt.matplotlib.colors.LinearSegmentedColormap
          .from_list("cov", [C["surface"], C["blue"]]), vmin=0, vmax=1)  # fmt: skip
a1.set_yticks(range(len(cov)), cov.index, fontsize=7)
a1.set_xticks(range(len(cov.columns)), cov.columns, rotation=90, fontsize=7)
a1.set_title("Share of NYSE sessions with a price row (white = not listed / no data)", loc="left")
fr = first_release(alfred["STLFSI4"]).set_index("date")["value"]
lt = alfred["STLFSI4"].sort_values("realtime_start").groupby("date").last()["value"]
fv = alfred["STLFSI4"].realtime_start.min()
a2.axvspan(pd.Timestamp("2019-01-01"), fv, color=C["grid"], alpha=0.7, lw=0)
note = f"before first ALFRED vintage ({fv.date()}):\nback-filled history, not point-in-time"
a2.text(pd.Timestamp("2019-02-01"), 0.97, note, transform=a2.get_xaxis_transform(), va="top",
        fontsize=8, color=C["ink2"])  # fmt: skip
a2.plot(lt.index, lt.to_numpy(), color=C["muted"], lw=1.2, label="latest vintage (revised)")
a2.plot(fr.index, fr.to_numpy(), color=C["blue"], lw=1.2, label="first archived value (used)")
a2.set_xlim(pd.Timestamp("2019-01-01"), LAST)
vis = pd.concat([lt, fr])[lambda x: x.index >= "2019-01-01"]
a2.set_ylim(vis.min() - 0.3, vis.max() + 0.6)
a2.axhline(0, color=C["ink2"], lw=0.6)
a2.legend(frameon=False, loc="upper right")
a2.set_title("STLFSI4: first release vs today's revised values", loc="left")
fig.suptitle(f"Step 1(e) data layer: snapshot through {LAST.date()}, gate {val['gate']} "
             f"({', '.join(f'{k} {v}' for k, v in val['summary'].items())})",
             x=0.01, ha="left", fontsize=11, color=C["ink"])  # fmt: skip
fig.tight_layout(rect=(0, 0, 1, 0.95))
fig.savefig(OUT / "fig7_data_layer.png", dpi=150)
print(rep.round(3).to_string(index=False))
