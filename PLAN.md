# Execution plan — State-dependent shock amplification (NVIDIA, Nov 2026)

Author's working plan, written after a critical read of
`state_dependent_shock_amplification_research_plan.md` (research design) and
`nvidia_shock_amplification_colab_implementation_plan.md` (build spec). Those two documents remain
the reference; this file records **what I will actually do, in what order, and where I deviate and
why**. Every step ends with figures + a gate, and we decide the next step together.

As-of: 2026-11-13 (v1.5: H6 competitive spillover; v1.4: second review; v1.3: external review incorporated; v1.2: aligned with `CLAUDE.md`; see §7).

---

## 1. Critical read: what the source plans get right, and what I change

**Keep (the plans are right about these):**
- The primary identification must be a **cross-firm leadership-event panel**; one NVIDIA event cannot
  identify a state-dependent response function.
- Severity must be coded from event content, never from the price reaction.
- Stress must be measured strictly before the event; LUI is treatment, not moderator.
- Ex-ante forecast (A), conditional no-news (B) and stress transport (C) are different estimands and
  must stay separately labelled.
- Null and contradictory results are reported, not tuned away.

**Change (my deviations, each logged in `reports/decision_log.md`):**

| # | Issue in source plans | What I do instead |
|---|---|---|
| D1 | The two plans number hypotheses differently (research plan H2 = "industry stress precedes", Colab plan H2 = "interacting stresses", etc.). | One unified hypothesis table (§2). |
| D2 | The panel is to be built from GDELT/Yahoo news scraping + manual labels. This is the largest schedule risk. GDELT's historical coverage for a 2005–2025 panel is unverified: the probe on 2026-11-13 was rate-limited. | Build the panel from the **Gentry et al. open CEO-dismissal database** (CC-BY-4.0, 9,509 S&P 1500 CEO turnovers, outcome-blind `departure_code` written by researchers from press coverage). Announcement dates come from its own field where present and otherwise from the **SEC 8-K (Item 5.02) acceptance timestamp**, which must be filed within 4 business days. News scraping is used only for the NVIDIA chronology. |
| D3 | Severity rubric would need to be invented and annotated. | Primary severity = the database's departure code, as categories: misconduct dismissal (code 4), performance dismissal (3), voluntary / planned (5, 6); M&A (7) excluded. Deaths/illness (1, 2) analysed separately as a clean "exogenous" contrast. My own rubric is a robustness check, not the primary variable. (v1.3: the codes enter as categories, not as an ordinal score; see D16.) |
| D4 | Market-stress variables (VIX, STLFSI4) are common to all firms on a date, so `year_effects` absorb most of their variation. | Two moderators with different identifying variation: **MSI** (time-series, identified from within-year variation; no year FE in the primary spec, year FE as robustness) and **FFI** (firm-specific pre-event fragility: own 60-day volatility, drawdown from 52-week high, valuation, beta). They are tested separately and together. |
| D5 | Physical-resource disclosure index (RSI from HBM/CoWoS disclosures) is in the critical path. | HBM/CoWoS disclosures: out of the critical path (sparse, strategically worded). **Power and utilities: in scope by user decision (2026-11-13)** as PUSI, a separate RSI component with financial (PUSI-F) and physical (PUSI-P) families, built in a new Step 3b. Primary targets are H3 (NVIDIA time series, where it is feasible) and H2. My feasibility scan (§5) says the panel version of H2 is thin in the power era, so it is exploratory unless powered. |
| D6 | No power analysis before the expensive data work. | **Power simulation in Step 0** using the real event counts. If H1 is not powered, we know before building it. |
| D7 | Colab is the execution target. | Code is a normal Python package (`src/shockamp`) that runs locally (uv, Windows) and in Colab (`pip install git+…`). Notebooks are thin wrappers, added when useful. Everything here is CPU-sized. |
| D8 | "First disclosure" is treated as one date. | The NVIDIA case is a **disclosure sequence** (see §3), analysed stage by stage. The earliest credible report (NYT, 2026-10-29) defines the cutoff for the ex-ante forecast and for pre-event stress. |
| D9 | The NVIDIA outcome has now been looked at (exploratory AR table, 2026-11-13). | Preregistration binds the **panel** analysis (whose outcomes are unseen). The NVIDIA case is declared as already inspected; no NVIDIA-specific choices (windows, baskets, stress thresholds) may be tuned to it. |
| D11 | Event dates: "Gentry date, else 8-K acceptance". An 8-K may be filed up to 4 business days after the press release, so its acceptance time is when the *filing* became available, not necessarily the first public time. | Event time = **earliest** verified public time among: Gentry `date_departure_announced`, the 8-K's "date of earliest event reported", the date on its press-release exhibit (EX-99), and the acceptance timestamp. Only an event whose earliest source is the timestamped filing itself is `time_known=True`. |
| D12 | Windows starting at 0 assume the time of day is known. Gentry dates have no time of day. | Date-only events use windows starting at −1 (`[-1,+1]` primary, `[-1,+5]` secondary). `[0,+1]`, `[0,+5]` are computed only for `time_known=True` events. |
| D13 | Severity "outcome-blind" assumes the code could be assigned from announcement-day information. Gentry coders used media coverage that may postdate the announcement (and a bad price reaction can itself generate "ousted" coverage). | Step 2 audit: for a stratified sample of code 3/4/5 events, check whether the announcement-day 8-K/press release alone supports the code. Report agreement; primary H1 re-run on the audited-agreeing subset as robustness. Code 4's own definition ("the announcement cited an instance…") is announcement-based, which helps. |
| D14 | Series without vintages (all EIA data; FRED series fetched without ALFRED) carry *revised* values that were not available at T, which breaks Rule 2 strictly. | Such series are flagged `current_vintage_only`. The confirmatory M0–M3 comparison (8.7 decision rule) uses only point-in-time-valid inputs: market prices, ALFRED vintages, dated reports. Results that need `current_vintage_only` inputs are labelled "revised-data" and are exploratory. A FRED API key therefore becomes **required**. |
| D15 | The session grid comes from the Yahoo price index and ignores 13:00 early closes. | Step 1 builds the grid from the NYSE exchange calendar (with early closes) and checks the price index against it. Impact is small: 2 of 2,101 dated primary-code events (2005+) fall on early-close days. |
| D16 | (review) An ordinal 0/1/2 severity score assumes voluntary→performance and performance→misconduct are equal steps. | **Categorical event type in the primary model** (voluntary = baseline; performance and misconduct dummies, each × stress). **Primary = two pre-registered tests, Holm-adjusted at family α = 0.05:** performance × stress < 0 and misconduct × stress < 0 (H1 supported if either passes the decision rule). Secondary: pooled dismissal contrast, equality of the two, ordinal score. Step 0b power check (SYNTHETIC outcomes, σ=7%): the pooled contrast misses the case where only misconduct amplifies (MDE > 6 pp) and the ordinal score needs 3.4 pp there, while the separate misconduct test needs 1.9 pp (≈2.1 pp after Holm). Holm costs ≈10% in MDE vs a single test (performance ≈0.88 pp vs pooled 0.78 pp when dismissals are alike). |
| D17 | (review) Stress and abnormal returns measure the shock, not resilience directly. | Three resilience outcomes: **R1** immediate CAR[−1,+1] (H1 primary); **R2** additional damage = min over k∈[+2,+20] of CAR[−1,k] − CAR[−1,+1] (H1 secondary, H2 outcome), judged against its placebo distribution because its null mean is negative and grows with the window; **R3** recovery time (H4). Events with another scheduled disclosure in [+2,+20] are flagged; R2 drops them. For NVIDIA, R2 and R3 are censored by earnings on 2026-11-17. |
| D18 | (review) Event heterogeneity (founder, tenure, planned vs surprise, successor named, size, sector) may matter more than stress. | Controls measured as of T: tenure (derived from the CEO succession chain), founder status (proxy filings, verified by hand), planned vs surprise (announced effective date and interim appointment in the announcement), successor named in the announcement (8-K Item 5.02(c) / press release), size (log market value from SEC XBRL, 2009+; log dollar volume otherwise), sector (SIC). Robustness: each control × stress, so severity × stress cannot absorb, e.g., founder × stress. |
| D19 | (review) Stages must leave machine-readable evidence and run from a fresh runtime. | Each step writes `reports/<step>/validation.json` (schema in the implementation plan §20). Fresh-runtime check before each gate: a new venv/kernel runs the step end-to-end from configs plus cached raw data; on Colab, "Disconnect and delete runtime" then run the notebook top to bottom. CI runs the synthetic tests and `--smoke` steps on every push. |
| D20 | (review) The fixed [−252,−31] market model may be poor during fast regime changes. | Step 4 compares four normal-return models on historical placebo events (pre-2015, never on NVIDIA): fixed window; short window [−126,−11]; EWMA beta (half-life 63); volatility-scaled AR (EWMA σ). Criteria: placebo bias and test size, out-of-sample error, **and both by stress tercile** (a model that is biased only in high stress would bias H1). A volatility-scaled outcome divides by pre-event volatility, which is part of stress, so it is secondary only. |
| D21 | (review 2) A negative d_k relative to voluntary departures shows that event types differ, not that stress amplifies the *absolute* impact; voluntary exits (e.g. a founder leaving) are not neutral. | Keep the two primary tests. Also report each type's **total stress slope** (β_S for voluntary, β_S + d_k for the others) with CIs, against a **matched non-event baseline**: 5 pseudo-event dates per event from the same firm, same calendar year and stress tercile, ≥60 sessions from any leadership event and ±1 session from earnings, with CARs from the same normal-return model. Model: `CAR ~ type × stress` with non-event dates as baseline. Wording: "amplification relative to voluntary departures" if only d_k is significant; "absolute amplification" only if type slope − non-event slope < 0 is also significant. Robustness: baseline restricted to planned, non-founder voluntary departures. |
| D22 | (review 2) Dropping events with later disclosures from R2 can remove the most serious crises. | R2 keeps the **full sample** (primary R2 analysis). `competing_event` indicator and first date in [+2,+20]: scheduled earnings (known in advance), other 8-K items, further leadership filings, M&A. Sensitivity: (a) uncontaminated subsample; (b) R2 censored at the session before the first competing event, compared with a placebo distribution matched on window length. Unscheduled competing events can be caused by the crisis, so they are never regression controls (post-treatment); scheduled earnings may be. |
| D23 | (review 2) Step 0b power ignores controls, clustering, missing data and real residual variance. | **Step 4b, before any H1 estimate:** re-run power on the retained sample with its real covariates, missing-data pattern, real MSI at event dates (which clusters by month), cluster-robust SEs by event month, and residual variance from **estimation-window and placebo residuals only** (never event-window CARs, so outcomes stay unseen). Report Holm-adjusted MDEs separately for performance and misconduct. The preregistration is frozen after Step 4b, with the MDEs written into its decision rule. |
| D24 | (user, v1.5) H6 competitive spillover. The Step 0 benchmark basket mixed competitors (AMD, AVGO), suppliers (TSM, MU, AMKR) and equipment makers, so opposite effects could cancel, and using competitors in NVIDIA's own benchmark inflates NVIDIA's AR if competitors gain. | Groups fixed from NVIDIA's 10-K (§5 row). No H6 outcome firm in any benchmark. NVIDIA's primary benchmark becomes SPY + G3; the mixed basket is a sensitivity. Step 0c measured the inflation: E1 CAR −13.1% (mixed) vs −11.6% (SPY only) vs −11.9% (SPY + G3). |
| D10 | Post-event NVIDIA windows ≥ [0,+3] from Nov 12 overlap Q3 FY27 earnings (2026-11-17, after close). | NVIDIA windows truncated before earnings; flagged as confounded beyond that. H4 (recovery) and H5 (mean reversion) for NVIDIA are censored and reported as such. |

**Rules from `CLAUDE.md` applied here** (`CLAUDE.md` was rewritten for this project on 2026-11-13;
D11–D15 record what that changed):
- **Unit** = NYSE trading session. Day boundary: America/New_York; a session is complete after the
  16:00 ET close. The current, unfinished session is never used.
- **Origin T** = the last complete session strictly before the information arrives. Lag k = session
  T−k. Event timestamp after 16:00 ET or on a non-session day maps to the next session.
- **Estimation window** for normal returns: sessions [T−252, T−31] (≥120 valid obs), embargo of 30
  sessions, so no estimation data lies in the event window.
- **Pre-event stress** is computed from data available at or before T's close (macro series joined on
  release date; filings on SEC acceptance date). Scalers/z-scores/regime cut-points are fitted on
  past data only (expanding window).
- **Rolling-origin backtests** (expanding window, step S sessions) are used for every forecasting /
  model-selection choice (normal-return model, ex-ante NVIDIA forecast, H2 challengers).
- **Leakage tests**: perturb all data after T and require features, estimation samples and
  predictions to be unchanged.

## 2. Unified hypotheses

| ID | Statement | Primary test | Status |
|---|---|---|---|
| **H1** (primary) | The abnormal-return response to adverse leadership news is more negative when pre-event stress is higher. | Panel: `CAR[-1,+1] ~ type + stress + type×stress + controls` (type = voluntary / performance / misconduct); primary = performance × stress and misconduct × stress, Holm-adjusted (D16). | Confirmatory if powered (Step 0 decides) |
| H2 | Market stress and firm fragility interact (joint high states amplify more than additively), possibly non-linearly. | Additive vs interaction vs threshold/spline, rolling-origin out-of-sample. | Exploratory |
| H3 | NVIDIA was already vulnerable before the first leadership disclosure (stress elevated vs its own history; ex-ante forecast already skewed down). | Stress percentile at cutoff; frozen ex-ante forecast fan chart; placebo calibration. | Descriptive / predictive, not causal |
| H4 | Recovery (CAR back to ≥0) is slower after high-stress events. | Kaplan–Meier / Cox on the panel. NVIDIA: censored. | Secondary |
| H5 | Post-shock moves are temporary overshoot vs permanent repricing. | Valuation spread stationarity + break tests. NVIDIA: insufficient post-event data. | Deferred |
| H6 | A negative leadership shock at a dominant firm gives positive abnormal returns to close substitutes, more so with higher substitutability and leader fragility (net of industry contagion). | NVIDIA: G1 (10-K-named competitors) − G3 (unnamed semis) group CAR per disclosure, SPY-only benchmark, rebound control. Panel: rival CARs around dominant-firm CEO departures vs substitutability (TNIC) and leader stress. | NVIDIA: hypothesis-generating (outcomes seen in news). Panel: secondary; confirmatory only if powered at Step 4b. H6b (contracts, orders, share): deferred |

Also carried from the research plan: **incremental leadership effect** (NVIDIA AR per disclosure stage
net of market + ex-NVDA sector) — this is Step 4.

## 3. NVIDIA disclosure sequence (as verified 2026-11-13; see `configs/nvda_chronology.yaml`)

| Stage | Date | What became public | Source status |
|---|---|---|---|
| E0 | 2026-10-29 (Thu) | NYT reports Alice Huang (Megaspeed-linked) as alleged MSS asset with close relationship to Huang; NVIDIA pushes back. | CNBC 2026-10-29 confirms; exact NYT time unverified |
| E1 | 2026-11-08 (Sun) | Board opens independent investigation; Huang memo admits affair. First session: 2026-11-09. | NVIDIA newsroom; CNN/CNBC 11-08 |
| E1b | 2026-11-10 | Statement from independent board members. | NVIDIA newsroom (title only, content unread) |
| E2 | 2026-11-11 / 11-12 | Board accepts resignation (11-11); press release + 8-K (11-12). Interim CEO Colette Kress. | 8-K Item 5.02; press release |
| — | 2026-11-17 | Q3 FY27 earnings (confounder for later windows). | press release |

## 4. Steps (each ends in figures + gate + your decision)

| Step | Content | Key figures | Gate |
|---|---|---|---|
| **0** | Repo, configs, preregistration draft, source feasibility, NVIDIA chronology, exploratory AR snapshot, **H1 power simulation**. | Source audit; NVIDIA timeline with AR per session; power curves / MDE. | Sources viable; H1 powered enough to be confirmatory, else scope change. |
| 1 | Market data layer (gate: reproduce the provisional Step 0 numbers — NVDA ARs, event-window returns — or explain the difference): NYSE session grid from the exchange calendar incl. early closes (D15); prices for target, peers, panel firms; VIX/VXN; FRED via ALFRED vintages (STLFSI4, BAA10Y, DGS2/10; vintage counts logged). Validation + ex-NVDA baskets. E0 AR re-computed on `[-1,+1]` (date-only, D12). | Coverage/missingness heatmap; normalized prices; basket composition; flags. | No unresolved integrity failures for core series. |
| 2 | Event panel: Gentry ⨝ CRSP-free identifiers (gvkey→ticker/CIK via EDGAR), event time = earliest public source (D11), `time_known` flag; event type + announcement-day codability audit (D13); controls as of T (D18); overlap/confounder flags; sample attrition. | Attrition waterfall; events by year × code; announce-date agreement plot (Gentry vs 8-K event date vs acceptance); codability agreement table. | ≥ MDE-sized sample with dates validated on an audited subset; codability agreement reported. |
| 3 | Stress indices: MSI (time), FFI (firm), market-implied supplier stress; expanding z-scores; regimes. | Stress timelines w/ regime bands; NVIDIA percentile at E0/E1; component correlations. | Leakage tests pass; indices stable across weightings. |
| **3b** | **Power and utilities (PUSI).** Equities XLU, ^UTY, GRID, ETN, VRT, PWR (+ placebo XLP, XLV); FRED energy series; EIA API v2; curated grid reports; PUSI-F and PUSI-P; data-quality report. | Normalized utility/infra performance; utilities vs semis; rolling NVDA correlations (raw, residualized, placebo); electricity price/demand/capacity; PUSI-F/P timelines; F-vs-P divergence. | PUSI-F from 2005 (core basket); PUSI-P has ≥2 verified physical components with release rules; each component labelled point-in-time-valid or `current_vintage_only` (D14); leakage/unit/frequency tests pass. |
| 4 | H6 NVIDIA part: G1–G4 group CARs per disclosure, G1 − G3, rebound control, foreign suppliers as sensitivity (D24). Normal-return models chosen by rolling-origin backtest on placebo events among four candidates, incl. by stress tercile (D20); panel AR/CAR and R1/R2 (D17); placebo calibration; NVIDIA per-stage AR with contamination sensitivity (peer basket incl./excl. close competitors). | Backtest error by model; placebo CAR distribution; NVIDIA CAR per stage with CIs. | Placebo coverage ≈ nominal. |
| 4b | **Power re-run on the real sample (D23)**, outcome-blind; then freeze the preregistration with the MDEs. | MDE by type (performance, misconduct) vs Step 0b. | Preregistration frozen. |
| 5 | **H1**: categorical event-type × stress model, two Holm-adjusted primary tests (D16), total slopes vs matched non-event dates (D21), R2 full sample + sensitivity (D22), controls and control × stress (D18), R2 secondary; robustness (stress definition, windows, FE, leave-one-year-out, wild bootstrap), power-honest reporting. | Marginal-effect curve CAR vs stress by severity; forest plot. | Pre-registered decision rule applied. |
| 5b | **Power incremental value**: M0 vs M1 (+PUSI-F), M2 (+PUSI-P), M3, M1-orth; walk-forward; negative controls (market, AI sentiment, rates, valuation, placebo sectors, timing placebos, block permutation, exposure contrast). | Loss-difference per fold; coefficient stability; negative-control forest plot; NVDA predicted returns with vs without power variables. | Research plan 8.7 decision rule, on point-in-time-valid inputs only (D14). |
| 6 | NVIDIA counterfactuals: A ex-ante forecast frozen at E0 cutoff; B conditional on screened external factors; C transport of H1 estimate to Nov-2025 stress state, with support diagnostics (is NVDA inside the panel's support?). | Fan chart; no-news path; 2025 vs 2026 transported effect. | Results not dependent on a single basket / timestamp. |
| 7 | Secondary: H2 non-linearity, H4 recovery (panel), H5 if data allow, **H6 panel** (rival CARs around dominant-firm CEO departures vs TNIC similarity and leader stress). | Surfaces; KM curves; rival-response vs similarity. | — |
| 8 | Report + reproducibility run; static results site built from frozen outputs. **Publish (only after your approval):** GitHub Actions Pages deploy to `moghbaie.github.io/NVIDIA-fall/` + project card in the `_projects/` collection of the existing Jekyll site (`site-v2` branch). | Scorecard; site preview. | All claims traced; attribution and license review of the public page. |

## 5. Feasibility findings (Step 0 + power scan, 2026-11-13)

| Question | Finding | Consequence |
|---|---|---|
| Do sources work? | Yahoo, FRED, SEC EDGAR (8-K acceptance timestamps to the second), Zenodo: available. GDELT: rate-limited, so **untested**. | GDELT is not needed for the panel (D2). |
| Is H1 powered? | Simulated MDE at 80% power, 70% price-match: ordinal severity design (n≈2,800) **0.5–0.8 pp** of CAR per severity step per SD of stress; misconduct-vs-voluntary (115 misconduct) **1.4–2.5 pp**. | Superseded as a design choice by D16 (categorical primary: separate Holm-adjusted performance and misconduct tests); see the Step 0b row. Controls, month clustering and missing data will raise these MDEs; re-run on the real sample in Step 4b (D23). |
| Do the utility tickers exist? | XLU (1998), ^UTY (1990), GRID (2009-11), ETN (1990), VRT (2018-08), PWR (1998): yes. **S&P 500 Utilities (`^SP500-55`): no history on Yahoo**, so unavailable; XLU is the proxy. | Basket versions by listing date. |
| Do the FRED energy series exist? | APU000072610, CUSR0000SEHF01, PCU22112211, WPU0543, IPG2211S, CAPUTLG2211S, DHHNGSP: all verified by title. | Used in PUSI-P. |
| Power-era panel support | Events 2005+: 4,003 (165 misconduct). Since VRT (2018-08): 1,083 (31). Since 2023: 229 (6), over 28 distinct months. | Panel H2 with PUSI is **exploratory**; H3 (NVIDIA time series, ~3,000 sessions) is where PUSI can be tested properly. |
| Is the utilities signal distinct from defensives? | XLU's and ^UTY's market-adjusted correlation with NVDA ≈ that of the XLP placebo. VRT/PWR/ETN/GRID correlation with NVDA rose over 2018–2024. | Utilities look like the defensive sector; power equipment looks like the AI trade. Negative controls are essential. |
| What did power names do in the event window? | Oct 14 → Nov 12: XLU +5.0%, ^UTY +6.2%, ETN −11.9%, PWR −8.2%, GRID −7.5%, VRT −5.9%, NVDA −24.9%. | Fits an AI-trade unwind more than power stress, which a PUSI-F that ignores sign logic would misread. |
| Are panel dates usable? (v1.2) | 2005–2025, codes 3/4/5/6: 2,101 have a Gentry announce date; 3,475 have a date or 8-K links. Misconduct: 65 dated, 140 with date or 8-K. Gentry links are "collected without examining their content" (±270 days), so the right filing must be matched. Median effective-minus-announced gap: 0 days for dismissals, 67 days for voluntary. | Power numbers in this table assume 70% matching and still hold; for misconduct the 8-K route is required, not optional. |
| Severity coding (v1.3, Step 0b) | See D16 and `reports/step0b/fig4_severity_power.png`: no single coding wins everywhere: ordinal and pooled tests are best when dismissals amplify alike but fail when only misconduct does. Separate Holm-adjusted tests lose ≈10% MDE and are robust across all three scenarios. The misconduct test (115 events) detects only ≥1.3–2.6 pp (before Holm). | Primary = two separate Holm-adjusted tests; the NVIDIA-relevant misconduct test is primary but powered only for large effects. |
| Controls available? (v1.3) | Tenure derivable from the succession chain for 68% of 2005–2025 events (left-censored at the database start). Founder status is not in the database (388 notes mention "found*", including "found guilty"), so it needs proxy-filing checks. Successor/planned status needs announcement text. | Step 2 adds an 8-K text pass; founder status used on the verified subset if coverage < 80%. |
| Early-close exposure (v1.2) | 2 of 2,101 dated primary events fall on early-close days. 56 dated on weekends (→ next session). | Calendar fix is cheap and removes the manual check. |
| Are Step 0 market numbers final? (v1.3) | No. NVDA ARs and event-window returns came from exploratory yfinance pulls. | **Provisional** until the Step 1 pipeline reproduces them. |
| H6 first look (v1.5, Step 0c, provisional) | Reported Nov 12 moves confirmed: NVDA −4.34%, AMD +5.86%, AVGO +5.54%. Group CAR [−1,+1], SPY benchmark: E2 G1 +5.4% (z 1.4) vs G3 +1.1%; E1 G1 +8.7% (z 1.9) but G2 +6.1% and G3 +4.2% too, so mostly sector-wide; E0 G1 −13.4%, driven by Intel −29% and Marvell −13% on Oct 29–Nov 2 (own news not yet checked). Rebound check on Nov 9: slope on the Nov 4–5 selloff ≈ 0, G1 extra +0.8 pp (17 firms). | Selective substitution shows up only on Nov 12, in two firms, on an outcome seen before the hypothesis: suggestive, not evidence. Rival same-day news must be checked before any reading. |
| Is H3 forecasting meaningful? | Daily mean returns are close to unpredictable. | H3 targets the predictive distribution (volatility, lower quantiles) scored by CRPS/pinball; the mean is secondary. |

## 6. Known limits stated up front
- The panel is S&P 1500, 1992–~2025; NVIDIA (founder, mega-cap, national-security angle) is likely at
  the edge of or outside its support. Transport (6C) will report this, not hide it.
- Daily data cannot separate intraday sequences; E1 is a weekend disclosure, which helps.
- Gentry announcement dates are non-randomly missing (their own documentation says so) — hence the
  8-K timestamp route plus an agreement check.
- Yahoo prices are a research prototype source; spot-checked against a second source in Step 1.
- EIA data have no vintages: PUSI-P results using them are "revised-data" and exploratory (D14).
- Gentry severity codes may use post-announcement coverage; the codability audit (D13) bounds this,
  it does not remove it.

## 7. Change log
- **v1.2 (2026-11-13)** — `CLAUDE.md` rewritten for this project; plan aligned: D11 earliest-public
  event time, D12 window rule for date-only events, D13 severity codability audit, D14 point-in-time
  validity of non-vintaged series, D15 exchange calendar with early closes. Steps 1, 2, 3b, 5b and
  §5–6 updated. Preregistration draft updated to match.
- **v1.3 (2026-11-13)** — external review: D16 categorical event type with separate
  Holm-adjusted performance and misconduct tests as primary (Step 0b power check), D17 resilience outcomes R1–R3, D18 event controls as of
  T plus control × stress robustness, D19 per-step `validation.json` and fresh-runtime checks, D20
  normal-return model comparison on placebo events by stress tercile. Step 0 market numbers marked
  provisional.
- **v1.4 (2026-11-13)** — second review: D21 total stress slopes per type vs matched non-event dates
  (wording rule for "absolute" vs "relative" amplification), D22 R2 on the full sample with a
  competing-event indicator and censoring sensitivity, D23 outcome-blind power re-run on the real
  sample (Step 4b) before freezing the preregistration. Feasibility row "Is H1 powered?" no longer
  calls the ordinal design primary; the primary spec is now machine-readable in
  `configs/preregistration.yaml` (`primary_tests`) and checked by `tests/test_prereg.py`.
- **v1.5 (2026-11-13)** — H6 competitive spillover added (user request): D24 groups from NVIDIA's
  10-K, benchmark-disjointness rule (NVIDIA primary benchmark = SPY + G3), Step 4 and Step 7 scope,
  Step 0c exploratory check. H1–H5 unchanged.
