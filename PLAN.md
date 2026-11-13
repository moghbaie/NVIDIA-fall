# Execution plan — Does pre-existing vulnerability amplify a negative shock? (NVIDIA, Nov 2026)

As-of 2026-11-13, **v1.7**. Design references: `state_dependent_shock_amplification_research_plan.md`
and `nvidia_shock_amplification_colab_implementation_plan.md` (both v1.7). **This file sets priority
and order; where they differ, this file wins.** The spec card below must be identical in all three
documents and in `configs/preregistration.yaml` (`tests/test_plan_consistency.py`). Every step ends
with figures, a `reports/<step>/validation.json`, a gate, and a joint decision on the next step.

```yaml spec-card
version: "1.7"
primary_hypothesis: H1
outcome: "CAR[-1,+1]"
primary_moderator: leadership_vulnerability
primary_terms: ["performance:LV", "misconduct:LV"]
baseline: voluntary
direction: negative
adjustment: holm
family_alpha: 0.05
fixed_effects: event_month
sample_period: ["2005-01-01", "2025-12-31"]
vulnerability_lag_sessions: 30
coverage_gate: {overall: 0.80, misconduct: 0.70}
fallback_primary_moderator: financial_vulnerability
freeze_gate: step_4b
session_close: "NYSE scheduled close, America/New_York (16:00; 13:00 early close)"
event_time: earliest_public_source
date_only_window_start: -1
nvidia_families: [financial, leadership, operational, resource_deployment]
nvidia_combined_score: false
```

---

## 1. Objective and questions

**Objective.** Understand whether a company's pre-existing vulnerability amplifies the impact of a
negative shock, using NVIDIA's Oct–Nov 2026 leadership crisis as the case. Five questions:

| # | Question | Evidence it can get | Tier |
|---|---|---|---|
| Q1 | Does pre-existing vulnerability amplify the shock? | Cross-firm panel of CEO departures (H1) — one case cannot show it | **Core, confirmatory** |
| Q2 | What created NVIDIA's vulnerability? | Four-family profile at E0, from dated filings and prices; no combined score | **Core, descriptive** |
| Q3 | Would the decline have happened without the leadership news? | Decomposition of NVDA's move + no-news path | **Core, quantified counterfactual** |
| Q4 | Is it temporary? | Panel: recovery by vulnerability (H4). NVIDIA: revisit ≥ 60 sessions after E2 (≈ Feb 2027) | Secondary / NVIDIA deferred |
| Q5 | Do competitors benefit? | H6 for NVIDIA (groups from its 10-K) | Secondary, descriptive |

**H1 (the only confirmatory hypothesis).** Across S&P 1500 CEO departures announced 2005–2025, the
abnormal return CAR[−1,+1] around a forced departure is more negative, or less positive, for firms
with higher pre-existing **leadership vulnerability** (LV, measured from filings accepted before
T−30), compared with voluntary departures.

- **Model:** `CAR ~ type × LV + type × idio_vol + controls + event-month FE`; type ∈ {voluntary
  (baseline), performance dismissal, misconduct dismissal}; SEs clustered by event month.
- **LV components (equal-weight, fixed now; each also reported alone):** founder CEO (founder
  dependence); no executive besides the CEO holding a President/COO title (succession readiness); CEO
  also board chair (governance concentration).
- **Primary tests:** performance × LV < 0 and misconduct × LV < 0, Holm-adjusted, family α = 0.05.
- **Coverage gate (Step 2, before any CAR is computed):** LV available for ≥ 80% of price-matched
  events and ≥ 70% of misconduct events; otherwise the primary family becomes **financial
  vulnerability** (2009+), with the same tests. Declared now.
- **Interpretation rules:**
  - A founder leaving is a bigger shock, not only a sign of a weaker firm. "Pre-existing vulnerability
    amplifies" is claimed only if LV without the founder component (succession + duality) has the
    same sign; otherwise the claim is "departures of more central CEOs move prices more".
  - A negative performance × LV term means "more negative or less positive"; "amplification of
    adverse news" needs a negative mean CAR and a slope below matched non-event dates.
  - A misconduct null is "not detectable at the preregistered MDE", not "no effect".
- **Secondary families:** financial vulnerability (2009+: valuation vs industry, leverage, cash,
  market-to-book); market stress (MSI). Volatility is a control, never vulnerability.
- **NVIDIA verdict:** does NVIDIA's CAR per disclosure lie inside the 95% prediction interval of the
  frozen model for a misconduct departure at NVIDIA's LV? A consistency check; NVIDIA is at the edge
  of the panel's support.

## 2. Scope tiers

| Tier | Contents |
|---|---|
| **Core** | H1; NVIDIA CAR per disclosure; Q2 four-family profile; Q3 decomposition and no-news path; cause of the Nov 4–5 selloff; NVIDIA verdict |
| **Secondary** | Financial family and MSI in the panel; H4 recovery by vulnerability; R2 additional damage; H6 NVIDIA |
| **Deferred** | Whether NVIDIA's decline is temporary (criteria fixed now: R3 and H5-style valuation check, run ≥ 60 sessions after E2) |
| **Optional** | Full Power and Utilities Stress Index; H2 non-linearity; H5 panel; H6 historical panel; H6b (contracts, orders, share); ex-ante forecast (counterfactual A) |

Optional designs stay fully specified in the reference plans.

## 3. Steps

| Step | Content | Gate |
|---|---|---|
| 0 ✓ | Repo, configs, source audit, chronology, power (0), severity coding (0b), H6 first look (0c). | Done |
| **1** | (a) **Cause of the Nov 4–5 chip selloff**: dated news; did it cite the Oct 29 report? (b) **Hyperscaler Q3 releases** (Alphabet, Amazon, Microsoft, Meta): exact dates/times, capex guidance changes — an E0 confounder and the main transmission channel. (c) **Dated news list, Aug 26 → Oct 28**, every NVIDIA-relevant item classified good / bad / ambiguous **before** its abnormal return is computed (includes the Oct 20 Amazon rack report). (d) NVIDIA 10-Q exposures recorded as dated observations. (e) Market data layer: NYSE calendar with early closes; prices (NVDA, H6 groups, panel firms); VIX/VXN; FRED via ALFRED; reproduce Step 0 numbers. (f) Own news of AMD/AVGO (Nov 12), INTC/MRVL (Oct 29–Nov 2). | Selloff and confounders documented; no unresolved data failures |
| 2 | Event panel (database ⨝ ticker/CIK; earliest-public event time; type; codability audit); **LV extraction from DEF 14A / 10-K** (founder, titles, chair) at T−30, 60, 90; coverage gate decision; controls; competing-event flags. | Coverage gate decided outcome-blind |
| 3 | Panel vulnerability (LV, financial), MSI, idio_vol; distributions by type (common support). NVIDIA four-family profile at E0, E1, E2, each vs its history and the S&P 500. | Leakage tests pass |
| 4 | Normal-return model chosen on pre-2015 placebo events; panel CARs; matched non-event dates; NVIDIA CARs (SPY + G3); Q3 decomposition (market / G3 sector / hyperscaler-capex days / leadership-news days / other NVIDIA days); H6 NVIDIA groups. | Placebo test size ≈ nominal |
| 4b | Outcome-blind power re-run with real LV, covariates, missingness, month FE and clustering. **Freeze the preregistration.** | Frozen with MDEs |
| 5 | H1 estimation and the four pre-listed robustness specs (LV without founder, 60/90 lags, quarter FE + MSI, common support) plus the rest of `required_robustness`. | Decision rule applied |
| 6 | NVIDIA verdict; Q2 profile; Q3 result; secondary tier. | — |
| 7 | Report; static site from frozen outputs; **publish only after your approval**. | Claims traced; attribution review |

## 4. Design rules (compact)

- **Time.** Unit = NYSE session, America/New_York, complete after the close; origin T = last complete
  session before the first public time; date-only events use windows starting at −1.
- **Vulnerability is pre-existing.** Structural measures from the latest filing accepted before T−30;
  market-based measures at T−30; 60/90 as sensitivity. Nothing caused by the departure news.
- **No combined scores across families.** One pre-declared equal-weight score within the primary
  family (needed for a single test); components reported; NVIDIA's four families never combined.
- **Point in time.** Inputs joined on availability; ALFRED vintages; `current_vintage_only` series
  out of confirmatory tests; leakage tests perturb everything after T.
- **Benchmarks.** NVIDIA: SPY + G3; no outcome firm in any benchmark.
- **Exploratory labels.** Anything found after looking at NVIDIA's decline (e.g. the Oct 20 report)
  is exploratory; the Aug 26 → Oct 28 news list is built by rule to avoid cherry-picking.

## 5. What we know now (Step 0 + checks, provisional data)

| Topic | Finding | Consequence |
|---|---|---|
| Panel size | 2005–2025, types 3/4/5/6: 4,003 departures; misconduct 165. 2009+ (financial data): 3,093; misconduct 110. | LV primary keeps 2005+; financial fallback costs pre-2009 events. |
| Month fixed effects | 244 months; 9 events alone in their month; 1,448 of 1,455 forced and 164 of 165 misconduct events share a month with a voluntary one. | Event-month FE identified. |
| Power (synthetic outcomes, real counts) | Per SD of moderator: performance ≈ 0.6–1.1 pp, misconduct ≈ 1.3–2.6 pp (more after Holm and fewer events). | Re-run with real LV in 4b. |
| NVIDIA reaction | E1 CAR −11.6% (SPY) / −11.9% (SPY + G3); E0 −2.7%; E2 −3.4%; Nov 5 was sector-wide. | E1 is the disclosure to explain. |
| NVIDIA price-based state at E0 | VIX 43rd pct; NVDA 12-month return 31st pct and idiosyncratic volatility 31st pct of its own history; drawdown −10%; beta 1.93. | Not fragile on price measures; vulnerability, if any, is structural (Q2). |
| NVIDIA structural exposure | 10-Q (2026-08-26): "any shortage" of land, power, shell or capital "could impact our future revenue"; land/power/shell guarantees for AI-cloud partners' leases; $56B commitments ($36B AI cloud agreements, $20B data-center leases not commenced for third parties). 10-K: three direct customers = 25%, 18%, 13% of receivables. | Documented pre-existing exposure to the AI buildout — not evidence that it caused the decline. |
| Oct 20 Amazon rack report | NVDA CAR[−1,+1] +1.2% (z 0.4); AMZN +3.1% (mostly Oct 17); PWR −7.2%. | Not priced as NVIDIA-negative; exploratory. |
| E0 window confounder | Hyperscaler Q3 releases around Oct 28–29 (Alphabet, Amazon fell; Microsoft reportedly trimmed 2026 capex); GOOGL AR −13% on Oct 29. | E0 mixes leadership and capex news; Step 1(b). |
| H6 first look | Nov 12: AMD +5.9%, AVGO +5.5%, NVDA −4.3% (raw). | Descriptive only. |

## 6. Known limits

- NVIDIA is likely outside the panel's support; the verdict is a consistency check.
- Founder status mixes firm state and shock size; handled by the LV-without-founder rule, not removed.
- LV coverage from proxy statements is unknown until Step 2; the fallback is declared.
- Database dates are non-randomly missing; its codes may use post-announcement coverage.
- Yahoo prices miss delisted firms; the 70% match rate is an assumption until Step 2.
- GPUs delivered vs installed are almost never disclosed; resource/deployment exposure is measured
  from what filings and dated reports state.

## Appendix A. Decision index (details: `reports/decision_log.md`; v1.5 text in git `f169fb5`)

| # | Decision |
|---|---|
| D1–D3 | Unified hypotheses; panel from the Gentry et al. database; event type as categories. |
| D4 | Moderators: v1.7 replaces MSI/FFI with vulnerability families (D26); MSI secondary. |
| D5 | Power/utilities index optional; NVIDIA resource/deployment family is core (D26). |
| D6–D10 | Power simulation first; Python package + Colab; disclosure sequence; NVIDIA outcomes seen; windows truncated before 2026-11-17 earnings. |
| D11–D15 | Earliest-public event time; −1 windows for date-only events; codability audit; vintages; NYSE calendar. |
| D16 | Two Holm-adjusted primary tests (performance, misconduct). |
| D17 | Outcomes R1 (primary), R2, R3. |
| D18 | Controls as of T; control × type robustness. |
| D19 | `validation.json`; fresh-runtime runs; CI. |
| D20 | Normal-return model chosen on placebo events. |
| D21 | Total slopes vs matched non-event dates; wording rule. |
| D22 | R2 on the full sample. |
| D23 | Outcome-blind power re-run (4b) before freezing. |
| D24 | H6 groups from NVIDIA's 10-K; benchmark disjointness. |
| D25 | v1.6 scope tiers; H1 the only confirmatory hypothesis. |
| D26 | (v1.7, user decision) Primary moderator = leadership vulnerability (founder, succession readiness, CEO-chair duality) at T−30, event-month FE, coverage gate with financial fallback, LV-without-founder rule; volatility a control; NVIDIA profile on four families incl. resource/deployment, never combined; Q2/Q3 core; spec cards checked across documents. |

## Appendix B. Change log
- v1.2 `CLAUDE.md` alignment · v1.3 external review · v1.4 second review · v1.5 H6 · v1.6 tiers.
- **v1.7 (2026-11-13)** — objective restated as five questions; H1 moderator = leadership
  vulnerability (user decision) with coverage gate and financial fallback; NVIDIA four-family profile
  (incl. resource/deployment from the 2026-08-26 10-Q); Q3 decomposition core; Step 1 adds
  hyperscaler capex releases and a rule-built news list; spec card + consistency test.
