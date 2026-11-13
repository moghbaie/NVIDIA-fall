# Execution plan — Before the Headline: Pre-existing Exposure, Sector Shocks and Leadership News in NVIDIA's 2026 Decline

As-of 2026-11-13, **v1.9**. Design references: `state_dependent_shock_amplification_research_plan.md`
and `nvidia_shock_amplification_colab_implementation_plan.md` (both v1.9). **This file sets priority
and order; where they differ, this file wins.** The spec card below must be identical in all three
documents and in `configs/preregistration.yaml` (`tests/test_plan_consistency.py`). Every step ends
with data, figures, a `reports/<step>/validation.json`, a gate, and a joint decision on the next step;
models are run and reported one at a time.

**v1.9 was written after NVIDIA's October–November returns were seen** (Step 0 AR table, fig6). The
NVIDIA attribution is therefore exploratory with frozen rules, never confirmatory, and never a set of
exact causal percentages (D28).

```yaml spec-card
version: "1.9"
title: "Before the Headline: Pre-existing Exposure, Sector Shocks and Leadership News in NVIDIA's 2026 Decline"
primary_hypothesis: N1
primary_status: exploratory_frozen_rules_specified_after_outcome_seen
causal_share_claims: false
nvidia_cutoff: "2026-10-28 close"
nvidia_window: ["2026-10-29", "2026-11-16"]
nvidia_window_sessions: 13
counterfactuals_required: [A, B1, B2, B3, B4]
b_factors: {B1: [SPY, G3], B2: [SPY, dVIX, dDGS10, dBAA10Y], B3: [SPY], B4: [SPY, G3, G4]}
session_categories: [L, P, X, LP, LX, PX, N]
mixed_sessions: unresolved_never_assigned_to_leadership
leadership_scenarios: [leadership_only, leadership_inclusive_overlap]
inference: empirical_placebo_same_session_arrangement
placebo_primary: non_overlapping_13_session_blocks_fixed_offset
placebo_sensitivity: [all_origins_dependence_aware, regime_matched, excl_earnings_and_extraordinary_announcements, peer_firms]
interval_label: model_dependent_uncertainty_interval
equivalence_margin: median_abs_placebo_sum_leadership_arrangement
validation_gate: {b_band90_coverage: [0.80, 0.97], a_pit_ks_p_min: 0.05}
nvidia_families: [financial, leadership, operational, resource_deployment, political_regulatory]
nvidia_combined_score: false
secondary_study: ceo_departure_panel
panel_hypotheses: [H1a, H1b]
panel_outcome: "CAR[-1,+1]"
panel_moderator: leadership_concentration
panel_terms: ["performance:LC", "misconduct:LC"]
panel_term_labels: {"misconduct:LC": H1a_adverse_news_amplification, "performance:LC": H1b_attenuated_replacement_benefit}
panel_baseline: voluntary
panel_direction: negative
panel_adjustment: holm
panel_family_alpha: 0.05
panel_fixed_effects: event_month
panel_sample_period: ["2005-01-01", "2025-12-31"]
panel_moderator_lag_sessions: 30
panel_coverage_gate: {overall: 0.80, misconduct: 0.70}
panel_coverage_gate_failure: halt_and_decide_outcome_blind
panel_freeze_gate: step_4b
session_close: "NYSE scheduled close, America/New_York (16:00; 13:00 early close)"
event_time: earliest_public_source
date_only_window_start: -1
```

---

## 1. Objective, hypotheses and numbering

**Central question.** To what extent was NVIDIA's October–November 2026 stock decline explained by
pre-existing structural vulnerabilities and subsequent external shocks, rather than the reported
leadership controversy?

**Objective (operational).** Estimate how much of NVIDIA's decline is consistent with independently
observable non-leadership factors, and whether a material additional leadership-associated return
remains after accounting for them.

Four possible contributors are kept apart: (1) pre-existing business and financial exposures,
(2) political and regulatory developments, (3) broad market and semiconductor-sector repricing,
(4) incremental leadership-related news.

| ID | Statement | Status |
|---|---|---|
| **N1 (primary)** | After accounting for independently observable non-leadership factors (counterfactuals B1–B4), a material negative return remains, concentrated on leadership-news sessions. H0: no material leadership-associated residual. | Exploratory, frozen rules (§2) |
| N2 | NVIDIA's documented exposures before E0, assessed **separately** in five families (financial, leadership, operational, resource/deployment, political/regulatory) against its own earlier filings and peers. No beta or volatility thresholds; no combined score. | Descriptive |
| N3 | The stock decline is a valuation decline, not (yet) a deterioration in business fundamentals. | Descriptive; criteria fixed (§2.8) |
| N4 | Competitor spillover: G1 − G3 abnormal return, contaminated peers excluded (Step 1f). | Descriptive |
| **H1a / H1b (secondary statistical study)** | CEO-departure panel 2005–2025: misconduct × LC (H1a, adverse-news amplification) and performance × LC (H1b, attenuated replacement benefit). Specification, coverage gate, robustness, power analysis and Holm adjustment unchanged from v1.8 (§3). | Preregistered; outcomes unseen |
| H4 | Panel recovery by leadership concentration (R3). | Secondary |
| H5, H6-panel | Non-linearity; historical competitor-spillover panel. | Optional |

**Crosswalk from v1.8 numbering** (older reports keep resolving):

| v1.8 | v1.9 |
|---|---|
| H1 (panel, "primary") | H1a/H1b, secondary statistical study |
| H2 industry stress precedes leadership news | N2 (family exposure profile) |
| H3 incremental leadership effect; Q3 | N1 |
| H4 fragility vs repricing | N3 (NVIDIA) and H4 (panel recovery) |
| H5 non-linear interaction | H5 (optional) |
| H6 competitive spillover | N4 (NVIDIA) and H6-panel (optional) |
| Q1–Q5 | Q1 → H1a/H1b; Q2 → N2; Q3 → N1; Q4 → N3 + deferred persistence check; Q5 → N4 |

## 2. NVIDIA attribution design (N1–N4)

### 2.1 Window, outcomes, benchmarks
- **Cutoff:** close of 2026-10-28 (last complete session before E0). **Window:** 13 sessions,
  2026-10-29 .. 2026-11-16, ending before the 2026-11-17 earnings. Earnings window (Nov 17 → next
  sessions) analysed separately, for N3 only. Persistence check ≥ 60 sessions after E2 (≈ Feb 2027),
  deferred.
- **Outcomes:** cumulative log return R; R at E0, E1, E2; maximum drawdown from the cutoff;
  residual relative to each counterfactual; percentile under A. Market-value change in USD is
  descriptive.
- **Benchmarks:** SPY; G3 (ten unnamed semiconductors); G4 (cloud customers). No NVIDIA, G1 or G2
  firm in any benchmark.
- **Before the run:** verify the NYT E0 timestamp. If it is before the 2026-10-28 close, A and B are
  contaminated; recorded as a limitation, not fixed by moving the cutoff.

### 2.2 Session categories (mutually exclusive)
A second news inventory (2026-10-29 .. 2026-11-16; Step 1(c) schema and freeze) assigns each window
session to exactly one category. Labels are not blind (fig6 was seen) and are marked so.

| Code | Category |
|---|---|
| L | Leadership news only |
| P | Political/regulatory only (export controls, antitrust, government action) |
| X | Business/exposure news only (customer results, capex, financing, deployment) |
| LP, LX | Leadership coinciding with political or business news: **unresolved, never assigned to leadership** |
| PX | Political + business |
| N | No identified NVIDIA-specific news |

Residuals are summed within categories and are never double-counted: Σ over categories = total residual.

### 2.3 Estimands (per counterfactual version v)
| # | Estimand |
|---|---|
| E1 | Consistent part: cumulative predicted return R̂_v and R̂_v / R (reported per version; not a causal share). |
| E2 | Additional return Δ_v = R − R̂_v = Σ_c Δ_v,c. |
| E3 | Leadership-associated return under two **scenarios** (not identified causal bounds): **leadership-only** = Δ_v,L; **leadership-inclusive overlap** = Δ_v,L + Δ_v,LP + Δ_v,LX. |
| E4 | Economic size, reported separately: E3 in pp and USD market value (shares × cutoff price), next to NVIDIA's ordinary unexplained variation for the same arrangement (placebo) and its median absolute earnings-window move. No cutoff. |
| E5 | Counterfactual A: percentile of R and of the path at E0, E1, E2. |

### 2.4 Counterfactuals (all required)
- **A (unconditional):** information at the cutoff only; (i) 5-session block bootstrap and (ii)
  Student-t with EWMA (λ 0.94) volatility, both on the 252 sessions to the cutoff.
- **B (conditional no-leadership-news path):** factor model fitted on the 252 sessions to the cutoff,
  applied to realized factors. B1 SPY + G3; B2 SPY + daily changes in VIX, 10-year yield, BAA−Treasury
  spread (ALFRED-checked); B3 SPY only; B4 SPY + G3 + G4. Residual-bootstrap band per version.
  Political/regulatory news has no independent price measure; it is handled by the P/LP categories.
- **Limitations stated with every result:** G3/G4 may themselves react to NVIDIA's leadership news
  (contagion), making B1/B4 overstate the non-leadership part; sessions may hold unseen news; B is a
  conditional prediction, not causal identification. **Agreement among B versions is reported as low
  model dependence, never as causal confirmation.**

### 2.5 Inference: empirical placebo distribution
- **Placebo blocks.** For each origin t₀, fit version v on the 252 sessions before t₀ and apply it out
  of sample to the next 13 sessions; sum residuals at exactly the positions each category occupies in
  the real window. Contiguous blocks keep serial dependence and volatility clustering; same positions
  keep the arrangement and its overlaps.
- **Primary:** non-overlapping 13-session blocks, fixed starting offset = first session of 2010
  (2010-01-04), stride 13, last block ending on or before 2026-10-28; all blocks with complete data
  included. The eligible count is reported.
- **Sensitivities:** (i) all origins (overlapping), percentile with a block-bootstrap interval
  (dependence-aware); (ii) regime-matched: origins in the same tercile of VIX and NVIDIA 63-session
  realized volatility as the cutoff; (iii) blocks containing NVIDIA earnings (8-K 2.02) or
  extraordinary announcements (8-K Items 1.01, 2.01, 5.02, stock splits, announced acquisitions)
  excluded; (iv) the same procedure on G1 and G3 firms.
- **Outputs per version:** one-sided placebo p-value (rank of observed among placebo sums); 90%
  **model-dependent uncertainty interval** [Δ − q₀.₉₅, Δ − q₀.₀₅] (not a causal confidence interval);
  τ_v = 95th percentile of |placebo total Δ| (forecast-error benchmark only).
- **Equivalence margin δ** = median absolute placebo sum for the leadership-session arrangement,
  reported numerically. It measures ordinary unexplained price variation, **not** an independently
  established economic materiality threshold.

### 2.6 Validation and contamination checks
- **Gate per version:** coverage of the 90% band on placebo blocks within [0.80, 0.97]; for A,
  PIT uniformity KS p ≥ 0.05. Also reported on rule-selected historical shock blocks: sessions
  2010-01-01 .. 2026-08-25 where |G3 AR| or |SPY return| > 3σ (σ from the prior 252 sessions), both
  directions, plus BIS advanced-computing export-control announcements (Federal Register list built by
  rule), excluding blocks with NVIDIA earnings or leadership news and shocks within 13 sessions of the
  previous one. List frozen before any error is computed. Failed versions are reported, not used in
  verdicts.
- **Contamination:** G3 and G4 placebo-based abnormal returns on L, LP and LX sessions. If
  significantly negative, B1/B4 leadership estimates are labelled understated and B2/B3 carry the
  leadership reading.

### 2.7 Decision table (validated versions; each version also reported separately)
Every version reports: R̂_v, Δ_v by category, placebo p-value, 90% uncertainty interval, τ_v, and its
validation performance.

| Verdict | Condition | Allowed wording |
|---|---|---|
| Not assessable | < 2 versions pass validation | "The counterfactual models are not reliable for this window." |
| Material leadership-associated return | Leadership-only Δ_v,L < 0 with placebo p ≤ 0.05 in every validated version, primary and regime-matched placebo | "A leadership-associated return of [interval] remains after the non-leadership factors measured; model range [..]" + E4 |
| Leadership-associated, overlap unresolved | Only the leadership-inclusive overlap scenario is significant | "A negative return remains on sessions where leadership and other news coincide; attribution between them is unresolved." |
| Negligible | 90% intervals of **both** scenarios lie within (−δ, +δ) in every validated version (TOST at 5%) | "Any leadership-associated return is within ±δ, the size of ordinary unexplained NVIDIA variation over the same sessions." |
| Inconclusive | Neither significant nor equivalent | "The data cannot distinguish a material leadership-associated return from none." A non-significant result alone never supports "negligible". |
| Model-dependent | Validated versions disagree in sign or significance | Each version reported; no overall label. |

Separate line on the consistent part: "within the historical forecast-error range" if |Δ_v| ≤ τ_v in
every validated version; otherwise "exceeds it by [..]". Every verdict carries: exploratory; revised
after the outcome was seen; conditional on the models; not a causal share.

### 2.8 N2, N3, N4
- **N2:** per family, an evidence table from documents dated before E0; each indicator graded
  increased / stable / decreased / not assessable against NVIDIA's earlier filings and, where
  comparable, peers. Families: financial (debt, guarantees, investment commitments, vendor-financing
  items); leadership (LC components, as in the panel); operational (supply commitments, customer
  concentration, foundry dependence); resource/deployment (power/land/shell disclosures, AI-cloud
  agreements, third-party leases, reported idle capacity); political/regulatory (China and export
  status, antitrust probes, Taiwan exposure). Beta and volatility are market descriptors, not
  vulnerability. Step 1(c) (no detectable reaction to exposure news before E0) is reported as found.
- **N3:** "fundamental deterioration" only if, at the 2026-11-17 report or later: Q3 revenue below the
  USD 105.8B low end of guidance; Q4 guidance below the trajectory implied by the pre-E0 guide; or a
  disclosed customer cancellation/deferral or reduced top-customer demand. Otherwise "valuation
  decline (multiple or risk premium)".
- **N4:** G1 − G3 at E2 with contaminated peers excluded (Step 1f; exploratory).

## 3. Secondary statistical study: CEO-departure panel (H1a/H1b, unchanged from v1.8)
Across S&P 1500 CEO departures announced 2005–2025, CAR[−1,+1] around a forced departure differs with
pre-existing **leadership concentration** (LC, filings accepted before T−30), relative to voluntary
departures. LC is called "leadership vulnerability" only once validated.

- **H1a — adverse-news amplification:** misconduct × LC < 0. **H1b — attenuated replacement benefit:**
  performance × LC < 0 (never evidence of adverse-news amplification).
- **Model:** `CAR ~ type × LC + type × idio_vol + controls + event-month FE`; SEs clustered by month.
- **LC components** (equal weight, fixed; each also reported alone): founder CEO; no executive besides
  the CEO holding a President/COO title; CEO also board chair.
- **Tests:** H1a and H1b Holm-adjusted together (family α 0.05), each with its own verdict.
- **Coverage gate (Step 2, before any CAR):** LC for ≥ 80% of price-matched and ≥ 70% of misconduct
  events. No automatic fallback: a failed gate halts the panel for an outcome-blind joint decision.
- **Naming rule:** "vulnerability" only if LC without the founder item agrees (95% CI excluding 0) and
  the misconduct LC slope is below the non-event slope. A misconduct null is "not detectable at the
  preregistered MDE".
- **Secondary families:** financial (2009+); market stress (MSI). Volatility is a control.
- **Link to NVIDIA:** NVIDIA's leadership-only residual reported as a percentile among the panel's
  misconduct CARs; it does not feed N1.

## 4. Scope tiers
| Tier | Contents |
|---|---|
| **Core** | N1 (A, B1–B4, placebo inference, decision table); N2 five-family evidence tables; post-E0 session inventory; E0 timestamp |
| **Secondary** | H1a/H1b panel (statistical); N3; N4; H4; R2; financial family and MSI in the panel |
| **Deferred** | Persistence of NVIDIA's decline (≥ 60 sessions after E2) |
| **Optional** | Power and Utilities Stress Index; H5; H6-panel; H6b |

## 5. Steps
Each step (and each model inside a step) is reported with data, figures and results before the next
starts.

| Step | Content | Gate |
|---|---|---|
| 0 ✓ | Repo, configs, source audit, chronology, power (0), severity coding (0b), H6 first look (0c). | Done |
| 1 ✓ (a–f) | (a) Nov 4–5 selloff; (b) hyperscaler releases; (c) pre-E0 news inventory, frozen, reactions; (d) 10-Q exposures as typed records; (e) data layer; (f) competitor own news at E2. Remaining: Step 1 evidence table `reports/step1/validation.json`. | Evidence table complete; no unresolved data failures |
| **N-a** | E0 timestamp; post-E0 news inventory (Oct 29–Nov 16) frozen; session categories; requires the 2026-11-16 close. | Categories frozen |
| **N-b** | Placebo origin list (primary, fixed offset) and historical shock list frozen; eligible counts reported. | Lists frozen before any residual |
| **N-c** | Counterfactual A: calibration on placebo blocks, then NVIDIA. | Reported |
| **N-d** | B1, B2, B3, B4, one at a time: validation, placebo distribution, δ, NVIDIA result. | Each reported |
| **N-e** | Decision table; contamination checks; sensitivities. | Verdict + caveats |
| **N-f** | N2 family evidence tables; N4; N3 after the 2026-11-17 report. | Reported |
| 2 | Panel: event panel (database ⨝ ticker/CIK; earliest-public time; type; codability audit); LC extraction (DEF 14A / 10-K) at T−30, 60, 90; coverage gate decision; controls. | Coverage gate decided outcome-blind |
| 3 | Panel vulnerability (LC, financial), MSI, idio_vol; distributions by type. | Leakage tests pass |
| 4 | Normal-return model chosen on pre-2015 placebo events; panel CARs; matched non-event dates. | Placebo size ≈ nominal |
| 4b | Outcome-blind power re-run with real LC; **freeze the preregistration (panel part)**. | Frozen with MDEs |
| 5 | H1a/H1b estimation and pre-listed robustness. | Decision rule applied |
| 7 | Report; static site from frozen outputs; **publish only after your approval**. | Claims traced; attribution review |

## 6. Design rules (compact)
- **Time.** Unit = NYSE session, America/New_York, complete after the close; origin T = last
  complete session before the first public time; date-only events use windows starting at −1.
- **Pre-existing means dated before E0** (NVIDIA) or before T−30 (panel). Nothing caused by the news.
- **No combined scores across families.** NVIDIA's five families are never combined.
- **Point in time.** Inputs joined on availability; ALFRED vintages; leakage tests perturb everything
  after T.
- **No double counting.** Each session's residual belongs to one category; mixed stays unresolved.
- **Language.** "consistent with", "associated with"; never causal percentages.

## 7. What we know now (Step 0 + Step 1, exploratory)
| Topic | Finding | Consequence |
|---|---|---|
| Panel size | 2005–2025, types 3/4/5/6: 4,003 departures; misconduct 165. 2009+: 3,093; misconduct 110. | LC panel keeps 2005+; financial family 2009+. |
| Month fixed effects | 244 months; 1,448 of 1,455 forced and 164 of 165 misconduct events share a month with a voluntary one. | Event-month FE identified. |
| Power (synthetic outcomes, real counts) | Per SD of moderator: performance ≈ 0.6–1.1 pp, misconduct ≈ 1.3–2.6 pp. | Re-run with real LC in 4b. |
| NVIDIA reaction | E1 CAR −11.6% (SPY) / −11.9% (SPY + G3); E0 −2.7%; E2 −3.4%. | Seen before v1.9 (D28). |
| NVIDIA price-based state at E0 | VIX 43rd pct; 12-month return and idiosyncratic volatility ~31st pct of own history; beta 1.93. | Descriptors only, not vulnerability (N2). |
| Step 1(a) Nov 4–5 selloff | SOXX −3.1% (Nov 4) and −12.2% (Nov 5); reported drivers: Qualcomm guidance, Arm, memory shortage, AI-capex financing doubts, post-election worries; no source links it to the Oct 29 report. NVDA AR Nov 4 −6.4% vs G3 −6.9%. | Sector-wide; non-leadership. |
| Step 1(b) E0 confounders | Alphabet and Microsoft results → Oct 29 (E0 session); Amazon and Intel → Oct 30. NVDA AR Oct 29 0.0%, Oct 30 −0.8%. | E0 sessions are LX (mixed). |
| Step 1(c) pre-E0 news | 31 items (Aug 26–Oct 28) labelled and frozen before reactions; only the two post-earnings sessions fall outside ±1.96σ; 30 items show no detectable reaction, including deployment and financing warnings. Labels for Oct 20–28 not blind. | Exposure news was not priced as negative when public. |
| Step 1(d) 10-Q exposures | Supply commitments USD 279B (from 119B a quarter earlier); AI-cloud service commitments 36B; third-party DC leases 20B; land/power/shell guarantees 3.5B; SB Energy guarantee up to 105B (effective from FY2029); debt 33.4B (from 8.5B). | Documented exposure; not evidence it caused the decline. |
| Step 1(e) data layer | Gate PASS (41 PASS, 1 WARN); Step 0 reproduced exactly; STLFSI4 not point-in-time before 2022-11-10. | Market stress uses VIX, BAA10Y, DGS2/10. |
| Step 1(f) E2 competitors | AMD and INTC contaminated by own news, AVGO unclear, MRVL clean. G1 − G3 on Nov 12: +2.8 pp (all), +2.6 pp (excl. contaminated), −1.4 pp (MRVL only); none significant. Removal reports public by 06:40 ET Nov 12. | Competitor gain not established (N4). |

## 8. Known limits
- v1.9 was specified after NVIDIA's returns were seen; frozen rules limit, but cannot remove,
  hindsight.
- One firm, overlapping news: categories reduce, but do not solve, attribution; mixed sessions stay
  unresolved.
- Benchmarks may absorb contagion from NVIDIA's own news.
- δ is a statistical yardstick (ordinary unexplained variation), not an economic threshold.
- Panel: founder status mixes firm state and shock size; LC coverage unknown until Step 2; database
  dates non-randomly missing; Yahoo misses delisted firms.

## Appendix A. Decision index (details: `reports/decision_log.md`)
| # | Decision |
|---|---|
| D1–D3 | Unified hypotheses; panel from the Gentry et al. database; event type as categories. |
| D4 | Moderators: vulnerability families (D26); MSI secondary. |
| D5 | Power/utilities index optional. |
| D6–D10 | Power simulation first; Python package + Colab; disclosure sequence; NVIDIA outcomes seen; windows truncated before 2026-11-17 earnings. |
| D11–D15 | Earliest-public event time; −1 windows for date-only events; codability audit; vintages; NYSE calendar. |
| D16 | Two Holm-adjusted panel tests. |
| D17 | Outcomes R1, R2, R3. |
| D18 | Controls as of T. |
| D19 | `validation.json`; fresh-runtime runs; CI. |
| D20 | Normal-return model chosen on placebo events. |
| D21 | Total slopes vs matched non-event dates; wording rule. |
| D22 | R2 on the full sample. |
| D23 | Outcome-blind power re-run (4b) before freezing. |
| D24 | H6 groups from NVIDIA's 10-K; benchmark disjointness. |
| D25 | v1.6 scope tiers. |
| D26 | (v1.7) leadership moderator; NVIDIA families never combined. |
| D27 | (v1.8) leadership concentration naming rule; no automatic fallback; pre-E0 counterfactual required; H1a/H1b separated. |
| D28 | (v1.9, user decision, after NVIDIA's returns were seen) Primary question becomes NVIDIA attribution (N1, exploratory, frozen rules); counterfactuals A and B1–B4 required; mutually exclusive session categories with mixed sessions unresolved; placebo inference with the same session arrangement (non-overlapping primary, fixed offset); model-dependent uncertainty intervals; δ = median absolute placebo sum (ordinary unexplained variation); equivalence required for "negligible"; N2 five families incl. political/regulatory, no beta/volatility thresholds; panel H1a/H1b kept as secondary statistical study; hypothesis numbering N1–N4 / H1a, H1b, H4–H6. |

## Appendix B. Change log
- v1.2 `CLAUDE.md` alignment · v1.3 external review · v1.4 second review · v1.5 H6 · v1.6 tiers ·
  v1.7 vulnerability families · v1.8 leadership concentration, pre-E0 counterfactual.
- **v1.9 (2026-11-13)** — D28. Retitled; NVIDIA attribution primary (N1) with estimands, session
  categories, counterfactuals A/B1–B4, placebo inference, validation, equivalence and decision table
  fixed before further analysis; panel H1a/H1b secondary; five NVIDIA families; numbering crosswalk;
  §7 updated with Step 1(c)–(f). Completed work and results unchanged.
