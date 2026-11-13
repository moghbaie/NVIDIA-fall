"""Step 1 evidence table: every event and data series with source, availability, class and status.

Sources: configs/nvda_chronology.yaml (disclosures, SEC releases, confounders, peer news),
configs/news_inventory.yaml (frozen pre-E0 news), configs/nvda_exposures.yaml (10-Q/10-K records),
reports/step1/validation_1e.json (price and FRED/ALFRED series checks). Writes
reports/step1/validation.json, evidence_table.csv and fig11_evidence_timeline.png.

Status: PASS = source and availability established; WARN = usable with a stated weakness (secondary
copy, unverified time, title only); FAIL = missing source or availability.
Contributor class follows the v1.9 contributors: leadership, political_regulatory, business_exposure,
market_sector, peer_own_news, pre_existing_exposure, immaterial, data.
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import pandas as pd
import yaml

from shockamp import CONFIGS, REPORTS
from shockamp.evidence import assert_frozen, load_inventory

OUT = REPORTS / "step1"
chron = yaml.safe_load((CONFIGS / "nvda_chronology.yaml").read_text(encoding="utf-8"))
expo = yaml.safe_load((CONFIGS / "nvda_exposures.yaml").read_text(encoding="utf-8"))
v1e = json.loads((OUT / "validation_1e.json").read_text(encoding="utf-8"))
frozen = assert_frozen(CONFIGS / "news_inventory.yaml", OUT / "inventory_freeze.json")
news = load_inventory(CONFIGS / "news_inventory.yaml")
PEERS = {"AMD", "INTC", "QCOM", "MRVL", "AVGO"}
rows: list[dict] = []


def add(**kw: object) -> None:
    rows.append(kw)


# 1. NVIDIA disclosures
for e in chron["events"]:
    src = e.get("sources") or []
    v = "yes" if e.get("verified") is True else str(e.get("verified"))  # YAML parses yes as True
    status = "PASS" if src and v == "yes" else ("WARN" if src else "FAIL")
    why = {"yes": "verified", "partial": "first-public time not verified (NYT original)",
           "title_only": "content not reviewed"}.get(v, v)  # fmt: skip
    add(id=e["id"], kind="NVIDIA disclosure", date=str(e["first_public_date"]),
        availability=f"{e['first_public_date']} (date only; window from -1)",
        source=src[0] if src else "", classification="leadership", status=status, note=why)  # fmt: skip

# 2. SEC releases of other firms (EDGAR acceptance = availability)
for s in chron["sec_releases"]:
    cls = "peer_own_news" if s["firm"] in PEERS else "business_exposure"
    if "5.02" in s["items"]:
        cls = "immaterial"
    add(id=f"SEC-{s['firm']}-{s['accepted'][:10]}", kind=f"8-K {s['items']}", date=s["accepted"][:10],
        availability=f"{s['accepted']} ET (EDGAR acceptance) -> session {s['reaction_session']}",
        source="SEC EDGAR", classification=cls, status="PASS", note=s["note"])  # fmt: skip

# 3. Market confounders
for c in chron["confounders"]:
    cls = "market_sector" if str(c["date"]) != "2026-11-17" else "business_exposure"
    add(id=f"CONF-{c['date']}", kind="confounder", date=str(c["date"]),
        availability=f"{c['date']} (date only)", source="secondary press (attributed)",
        classification=cls, status="WARN" if cls == "market_sector" else "PASS",
        note="causes attributed from secondary sources, not established")  # fmt: skip

# 4. Peer own news at E2
for p in chron["peer_contamination_e2"]:
    add(id=f"PEER-{p['ticker']}-E2", kind="peer news at E2", date="2026-11-12",
        availability="2026-11-12 (before open where reported)", source=p["sources"][0],
        classification="peer_own_news", status="PASS" if p["status"] != "UNCLEAR" else "WARN",
        note=p["status"])  # fmt: skip

# 5. Frozen pre-E0 news inventory (classification derived from frozen labels, not edited)
for it in news:
    chans = it["channels"]
    if all(c["direction"] == "0" for c in chans):
        cls = "immaterial"
    elif any(c["channel"] == "regulation_export" and c["direction"] != "0" for c in chans) and all(
        c["channel"] == "regulation_export" for c in chans
    ):
        cls = "political_regulatory"
    else:
        cls = "business_exposure"
    weak = it["source_type"] == "aggregator" or "not retrieved" in it["source"]
    avail = (f"{it['published']} {it['time_et']} ET ({it.get('time_source')})" if it["time_et"]
             else f"{it['published']} (date only; window from -1)")  # fmt: skip
    add(id=it["id"], kind="pre-E0 news", date=str(it["published"]), availability=avail,
        source=it["url"], classification=cls, status="WARN" if weak else "PASS",
        note=("secondary copy; original not retrieved; " if weak else "") + f"label {it['label_blindness']}")  # fmt: skip

# 6. Pre-existing exposure records (filing acceptance = availability)
for r in expo["records"]:
    f = expo["filings"][r["filing"]]
    add(id=r["id"], kind=f"{f['form']} exposure", date=f["accepted_utc"][:10],
        availability=f"{f['accepted_utc']} (EDGAR acceptance)", source=f["url"],
        classification="pre_existing_exposure", status="PASS", note=f"{r['category']}; {r['measure']}")  # fmt: skip

# 7. Data series (from the Step 1(e) gate)
for c in v1e["checks"]:
    add(id=c["item"], kind="data series", date="", availability=c["availability"], source=c["source"],
        classification="data", status=c["status"], note=c["detail"])  # fmt: skip

tab = pd.DataFrame(rows)
tab.to_csv(OUT / "evidence_table.csv", index=False)
counts = tab.groupby(["kind", "status"]).size().unstack(fill_value=0)
print(counts.to_string())
gate = "FAIL" if (tab.status == "FAIL").any() else "PASS"
report = {
    "step": "1",
    "generated_utc": pd.Timestamp.now(tz="UTC").isoformat(),
    "gate": gate,
    "n_rows": len(tab),
    "status_counts": tab.status.value_counts().to_dict(),
    "class_counts": tab.classification.value_counts().to_dict(),
    "inventory_freeze": frozen,
    "open_items": [
        "E0: NYT first-public time not verified (required before N1, PLAN.md 2.1)",
        "E1b: board statement content not reviewed",
        "post-E0 news inventory (2026-10-29..2026-11-16) not built; needs the 2026-11-16 close",
    ],
    "rows": rows,
}
(OUT / "validation.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
print(gate, report["status_counts"], report["class_counts"])

# figure: dated items by contributor class (Aug 20 .. Nov 18), marker = status
C = {"leadership": "#eb6834", "political_regulatory": "#6250d6", "business_exposure": "#2a78d6",
     "market_sector": "#1baf7a", "peer_own_news": "#8a8984", "pre_existing_exposure": "#0b0b0b",
     "immaterial": "#c9c8c3", "ink2": "#52514e", "grid": "#e6e5e1", "surface": "#fcfcfb"}  # fmt: skip
plt.rcParams.update({"figure.facecolor": C["surface"], "axes.facecolor": C["surface"],
                     "axes.edgecolor": C["grid"], "font.size": 8.5, "axes.titleweight": "bold",
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": C["grid"], "axes.axisbelow": True})  # fmt: skip
d = tab[tab.date != ""].copy()
d["dt"] = pd.to_datetime(d.date)
d = d[(d.dt >= "2026-08-20") & (d.dt <= "2026-11-18")]
order = ["pre_existing_exposure", "business_exposure", "political_regulatory", "market_sector",
         "peer_own_news", "leadership", "immaterial"]  # fmt: skip
labels = {"pre_existing_exposure": "pre-existing exposure (filings)",
          "business_exposure": "business / customer news", "political_regulatory": "political / regulatory",
          "market_sector": "market / sector shock", "peer_own_news": "competitors' own news",
          "leadership": "NVIDIA leadership news", "immaterial": "immaterial"}  # fmt: skip
fig, ax = plt.subplots(figsize=(13, 4.6))
for i, cls in enumerate(order):
    s = d[d.classification == cls]
    for st, mk in [("PASS", "o"), ("WARN", "D")]:
        z = s[s.status == st]
        ax.scatter(z.dt, [i] * len(z), s=46, marker=mk, color=C[cls],
                   facecolors=C[cls] if st == "PASS" else "none", linewidths=1.4, zorder=3)  # fmt: skip
ax.axvspan(
    pd.Timestamp("2026-10-29"), pd.Timestamp("2026-11-16"), color="#fbe3d6", alpha=0.6, zorder=0
)
ax.text(pd.Timestamp("2026-10-29"), len(order) - 0.45, " N1 window (13 sessions)", fontsize=7.5,
        color=C["ink2"], va="center")  # fmt: skip
ax.axvline(pd.Timestamp("2026-10-28"), color=C["ink2"], lw=0.8, ls="--")
ax.text(pd.Timestamp("2026-10-28"), -0.75, "cutoff ", ha="right", fontsize=7.5, color=C["ink2"])
ax.set_yticks(range(len(order)), [labels[o] for o in order])
ax.set_ylim(-1, len(order))
ax.scatter([], [], marker="o", color=C["ink2"], label="PASS (source + availability established)")
ax.scatter(
    [],
    [],
    marker="D",
    facecolors="none",
    color=C["ink2"],
    label="WARN (secondary copy / time unverified)",
)
ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=7.5)
ax.set_title(f"Step 1 evidence table: {len(tab)} rows ({len(d)} dated events shown), gate {gate}; "
             "data series not shown (41 PASS, 1 WARN)", loc="left", pad=22)  # fmt: skip
fig.tight_layout()
fig.savefig(OUT / "fig11_evidence_timeline.png", dpi=150)
print("saved fig11")
