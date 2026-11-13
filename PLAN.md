# Execution plan — State-dependent shock amplification (NVIDIA, Nov 2026)

Author's working plan, written after a critical read of
`state_dependent_shock_amplification_research_plan.md` (research design) and
`nvidia_shock_amplification_colab_implementation_plan.md` (build spec). Those two documents remain
the reference; this file records **what I will actually do, in what order, and where I deviate and
why**. Every step ends with figures + a gate, and we decide the next step together.

As-of: 2026-11-13 (v1.2: aligned with the project `CLAUDE.md`, see §7).

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
| D3 | Severity rubric would need to be invented and annotated. | Primary severity = the database's departure code: misconduct dismissal (code 4) > performance dismissal (3) > voluntary / planned (5, 6, 7). Deaths/illness (1, 2) analysed separately as a clean "exogenous" contrast. My own rubric is a robustness check, not the primary variable. |
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
| **H1** (primary) | The abnormal-return response to adverse leadership news is more negative when pre-event stress is higher. | Panel: `CAR[-1,+1] ~ sev + stress + sev×stress + controls`, β(sev×stress) < 0. | Confirmatory if powered (Step 0 decides) |
| H2 | Market stress and firm fragility interact (joint high states amplify more than additively), possibly non-linearly. | Additive vs interaction vs threshold/spline, rolling-origin out-of-sample. | Exploratory |
| H3 | NVIDIA was already vulnerable before the first leadership disclosure (stress elevated vs its own history; ex-ante forecast already skewed down). | Stress percentile at cutoff; frozen ex-ante forecast fan chart; placebo calibration. | Descriptive / predictive, not causal |
| H4 | Recovery (CAR back to ≥0) is slower after high-stress events. | Kaplan–Meier / Cox on the panel. NVIDIA: censored. | Secondary |
| H5 | Post-shock moves are temporary overshoot vs permanent repricing. | Valuation spread stationarity + break tests. NVIDIA: insufficient post-event data. | Deferred |

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
| 1 | Market data layer: NYSE session grid from the exchange calendar incl. early closes (D15); prices for target, peers, panel firms; VIX/VXN; FRED via ALFRED vintages (STLFSI4, BAA10Y, DGS2/10; vintage counts logged). Validation + ex-NVDA baskets. E0 AR re-computed on `[-1,+1]` (date-only, D12). | Coverage/missingness heatmap; normalized prices; basket composition; flags. | No unresolved integrity failures for core series. |
| 2 | Event panel: Gentry ⨝ CRSP-free identifiers (gvkey→ticker/CIK via EDGAR), event time = earliest public source (D11), `time_known` flag; severity + announcement-day codability audit (D13); overlap/confounder flags; sample attrition. | Attrition waterfall; events by year × code; announce-date agreement plot (Gentry vs 8-K event date vs acceptance); codability agreement table. | ≥ MDE-sized sample with dates validated on an audited subset; codability agreement reported. |
| 3 | Stress indices: MSI (time), FFI (firm), market-implied supplier stress; expanding z-scores; regimes. | Stress timelines w/ regime bands; NVIDIA percentile at E0/E1; component correlations. | Leakage tests pass; indices stable across weightings. |
| **3b** | **Power and utilities (PUSI).** Equities XLU, ^UTY, GRID, ETN, VRT, PWR (+ placebo XLP, XLV); FRED energy series; EIA API v2; curated grid reports; PUSI-F and PUSI-P; data-quality report. | Normalized utility/infra performance; utilities vs semis; rolling NVDA correlations (raw, residualized, placebo); electricity price/demand/capacity; PUSI-F/P timelines; F-vs-P divergence. | PUSI-F from 2005 (core basket); PUSI-P has ≥2 verified physical components with release rules; each component labelled point-in-time-valid or `current_vintage_only` (D14); leakage/unit/frequency tests pass. |
| 4 | Normal-return models chosen by rolling-origin backtest; panel AR/CAR; placebo calibration; NVIDIA per-stage AR with contamination sensitivity (peer basket incl./excl. close competitors). | Backtest error by model; placebo CAR distribution; NVIDIA CAR per stage with CIs. | Placebo coverage ≈ nominal. |
| 5 | **H1**: panel interaction, robustness (stress definition, windows, FE, leave-one-year-out, wild bootstrap), power-honest reporting. | Marginal-effect curve CAR vs stress by severity; forest plot. | Pre-registered decision rule applied. |
| 5b | **Power incremental value**: M0 vs M1 (+PUSI-F), M2 (+PUSI-P), M3, M1-orth; walk-forward; negative controls (market, AI sentiment, rates, valuation, placebo sectors, timing placebos, block permutation, exposure contrast). | Loss-difference per fold; coefficient stability; negative-control forest plot; NVDA predicted returns with vs without power variables. | Research plan 8.7 decision rule, on point-in-time-valid inputs only (D14). |
| 6 | NVIDIA counterfactuals: A ex-ante forecast frozen at E0 cutoff; B conditional on screened external factors; C transport of H1 estimate to Nov-2025 stress state, with support diagnostics (is NVDA inside the panel's support?). | Fan chart; no-news path; 2025 vs 2026 transported effect. | Results not dependent on a single basket / timestamp. |
| 7 | Secondary: H2 non-linearity, H4 recovery (panel), H5 if data allow. | Surfaces; KM curves. | — |
| 8 | Report + reproducibility run; static results site built from frozen outputs. **Publish (only after your approval):** GitHub Actions Pages deploy to `moghbaie.github.io/NVIDIA-fall/` + project card in the `_projects/` collection of the existing Jekyll site (`site-v2` branch). | Scorecard; site preview. | All claims traced; attribution and license review of the public page. |

## 5. Feasibility findings (Step 0 + power scan, 2026-11-13)

| Question | Finding | Consequence |
|---|---|---|
| Do sources work? | Yahoo, FRED, SEC EDGAR (8-K acceptance timestamps to the second), Zenodo: available. GDELT: rate-limited, so **untested**. | GDELT is not needed for the panel (D2). |
| Is H1 powered? | Simulated MDE at 80% power, 70% price-match: ordinal severity design (n≈2,800) **0.5–0.8 pp** of CAR per severity step per SD of stress; misconduct-vs-voluntary (115 misconduct) **1.4–2.5 pp**. | Ordinal design is the primary design. A misconduct-only contrast detects only large amplification. Clustering by month will raise these MDEs; to be re-run with real CAR noise in Step 4. |
| Do the utility tickers exist? | XLU (1998), ^UTY (1990), GRID (2009-11), ETN (1990), VRT (2018-08), PWR (1998): yes. **S&P 500 Utilities (`^SP500-55`): no history on Yahoo**, so unavailable; XLU is the proxy. | Basket versions by listing date. |
| Do the FRED energy series exist? | APU000072610, CUSR0000SEHF01, PCU22112211, WPU0543, IPG2211S, CAPUTLG2211S, DHHNGSP: all verified by title. | Used in PUSI-P. |
| Power-era panel support | Events 2005+: 4,003 (165 misconduct). Since VRT (2018-08): 1,083 (31). Since 2023: 229 (6), over 28 distinct months. | Panel H2 with PUSI is **exploratory**; H3 (NVIDIA time series, ~3,000 sessions) is where PUSI can be tested properly. |
| Is the utilities signal distinct from defensives? | XLU's and ^UTY's market-adjusted correlation with NVDA ≈ that of the XLP placebo. VRT/PWR/ETN/GRID correlation with NVDA rose over 2018–2024. | Utilities look like the defensive sector; power equipment looks like the AI trade. Negative controls are essential. |
| What did power names do in the event window? | Oct 14 → Nov 12: XLU +5.0%, ^UTY +6.2%, ETN −11.9%, PWR −8.2%, GRID −7.5%, VRT −5.9%, NVDA −24.9%. | Fits an AI-trade unwind more than power stress, which a PUSI-F that ignores sign logic would misread. |
| Are panel dates usable? (v1.2) | 2005–2025, codes 3/4/5/6: 2,101 have a Gentry announce date; 3,475 have a date or 8-K links. Misconduct: 65 dated, 140 with date or 8-K. Gentry links are "collected without examining their content" (±270 days), so the right filing must be matched. Median effective-minus-announced gap: 0 days for dismissals, 67 days for voluntary. | Power numbers in this table assume 70% matching and still hold; for misconduct the 8-K route is required, not optional. |
| Early-close exposure (v1.2) | 2 of 2,101 dated primary events fall on early-close days. 56 dated on weekends (→ next session). | Calendar fix is cheap and removes the manual check. |
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
