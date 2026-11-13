# NVIDIA State-Dependent Shock Amplification: Colab Implementation Plan

**Version:** 1.9 (v1.1 power/utilities; v1.2 point-in-time alignment with `CLAUDE.md`; v1.3 external review; v1.4 second review; v1.5 H6; v1.6 scope tiers; v1.7 vulnerability families; v1.8 leadership concentration; v1.9 NVIDIA attribution primary; change log in Section 26) | **Date:** 2026-11-13 | **Execution target:** Google Colab | **Coding agent:** Claude Code | **Companion:** `state_dependent_shock_amplification_research_plan.md` v1.9

> **Execution priority (v1.9):** `PLAN.md` sets scope and order and wins where documents differ. Retitled *Before the Headline: Pre-existing Exposure, Sector Shocks and Leadership News in NVIDIA's 2026 Decline*. **Primary (N1, exploratory with frozen rules):** how much of NVIDIA's 2026-10-29 .. 2026-11-16 decline is consistent with independently observable non-leadership factors (counterfactual A, frozen at the 2026-10-28 close; conditional counterfactuals B1–B4), and whether a material additional leadership-associated return remains. Sessions are assigned to mutually exclusive news categories; mixed leadership/other sessions stay unresolved. Inference uses an empirical placebo distribution with the same session arrangement; intervals are model-dependent uncertainty intervals; "negligible" requires equivalence within δ (ordinary unexplained variation). No causal percentages. v1.9 was written after NVIDIA's November returns were seen (PLAN.md D28). **Secondary statistical study:** the CEO-departure panel, H1a (misconduct × leadership concentration) and H1b (performance × LC), unchanged from v1.8. NVIDIA exposures are described in five separate families (financial, leadership, operational, resource/deployment, political/regulatory), never combined. Sections below that call the panel H1 "primary" or define the NVIDIA counterfactual differently are superseded by PLAN.md §2 and the crosswalk below. The spec card must match `configs/preregistration.yaml`.

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

**v1.9 hypothesis crosswalk** (supersedes the numbering in older sections; code and reports use v1.9 IDs):

| v1.9 | Research plan (v1.0–v1.8) | Implementation plan (v1.0–v1.8) |
|---|---|---|
| **N1** primary: leadership-associated residual after non-leadership counterfactuals | H3 incremental leadership effect | H3 pre-news vulnerability / no-news counterfactual |
| N2 five-family exposure profile (descriptive) | H2 industry stress precedes news | H3 (pre-disclosure stress part) |
| N3 valuation vs fundamental decline | H4 fragility vs repricing (NVIDIA) | H5 mean reversion vs repricing (NVIDIA) |
| N4 competitor spillover at E2 | H6 (NVIDIA sequence) | H6 (NVIDIA sequence) |
| H1a / H1b secondary panel study | H1 amplification | H1 shock amplification |
| H4 panel recovery | H4 (recovery part) | H4 recovery duration |
| H5 optional non-linearity | H5 | H2 interacting stresses |
| H6-panel optional | H6 (panel) | H6 (panel) |

## 0. Mission and non-negotiable research rules

Build a reproducible, publicly sourced empirical study of whether **pre-existing market, resource, and firm stress amplifies negative leadership-news shocks**. NVIDIA is the motivating case, but the primary interaction must be estimated across many companies and leadership events. Test six hypotheses: H1 shock amplification, H2 interacting stresses, H3 pre-news vulnerability, H4 recovery duration, H5 temporary mean reversion versus structural repricing, H6 competitive spillover to rivals and suppliers (v1.5).

**Never optimize the analysis to obtain a preferred conclusion.** Preserve null and contradictory results. Do not describe forecast accuracy as causal identification. Do not call a price fall mean reversion without an independently estimated, demonstrably stable equilibrium. No claim about a particular individual or event without independently verified dated sources. All examples in tests must be labeled synthetic. No fabricated historical market data, news, publication timestamps, analyst expectations, capacity, or p-values.

### Core identification distinctions

- **Stress:** observable before an event, measured from independent or lagged indicators.
- **Shock:** new, timestamped leadership information, distinct from subsequent commentary.
- **Outcome:** stock abnormal returns, volatility, or recovery following the shock.
- **Severity:** event content and surprise, not magnitude of stock return. Never label severity from price reaction.
- **Mediation/contamination:** market and peer prices after an NVIDIA shock may themselves respond to the shock. Flag and sensitivity-test these controls.
- **Counterfactual A:** unconditional ex-ante forecast frozen before first public disclosure.
- **Counterfactual B:** conditional no-news estimate using external shocks, with explicit exclusion/contamination assumptions.
- **Transport:** apply the *same standardized leadership shock* under historical 2025 versus 2026 pre-event stress states. It is a modeled scenario, not a historical fact.

## 1. Claude Code operating contract

Claude Code should treat this document as the build specification. Work sequentially by stage. **Do not proceed to the next stage unless the gate passes or a documented waiver explains the deviation.** Produce executable source modules, tests, notebook entrypoints, charts, and an audit log. Keep all transformations in `src/`, not hidden in notebook cells. Prefer CPU-friendly methods and modest Colab memory usage; no GPU needed for core econometrics. Optional FinBERT inference can use GPU, with CPU fallback and batching.

At the start of each session:
1. Read this plan, companion research plan, `README.md`, `configs/study.yaml`, and `reports/progress.md`.
2. Print stage status, latest dataset snapshot, last test results, and current blocking issues.
3. Run `pytest -q tests/unit` before changing code.
4. Implement only the next incomplete task, including its tests and visualizations.
5. Update `reports/progress.md`, `reports/data_manifest.json`, and `reports/decision_log.md` before stopping.

**Stage completion format:** objective, inputs, exact command/notebook cell, generated files, row counts and date ranges, validation results, charts before/after, test output, methodological caveats, gate PASS/FAIL, next action. Never silently skip a failed source or invent a replacement series.

### Deliverables

- `notebooks/00_setup.ipynb` through `notebooks/12_report.ipynb`, runnable in order using a fresh Colab runtime and a persistent Google Drive project directory.
- `src/` reusable Python package, `tests/` automated tests, `configs/` pinned study settings, `data/` raw/processed artifacts, `reports/` validation, plots, tables, and model cards.
- `run_pipeline.py` or `python -m src.pipeline --through STAGE` orchestration with resumable checkpoints.
- `README.md` with Colab setup, Drive mount, secrets, dataset licenses, reproducibility, runtime estimates, and troubleshooting.
- A machine-readable event dataset and preregistered hypothesis decision table.
- Final report that distinguishes association, prediction, and causal claims.

## 2. Colab execution and persistence architecture

**Persistent root:** `/content/drive/MyDrive/nvidia_shock_study/` (configurable). **Scratch:** `/content/nvidia_shock_work/`. **Repository:** clone from a user-configured Git repository, or copy a source archive into scratch. Do not assume Claude Code itself is installed inside Colab: Claude Code edits the repository in its supported environment; Colab executes the resulting notebooks and scripts. If using Claude Code with Colab via GitHub, commit/push code and pull in Colab.

**First notebook:** mount Drive; verify free space and CPU/RAM; install from pinned `requirements-colab.txt`; print Python/library versions; configure `PROJECT_ROOT`, `CACHE_ROOT`, `FRED_API_KEY` (required from v1.2 for ALFRED vintages), `EIA_API_KEY` (free registration, required for EIA API v2) and `SEC_USER_AGENT` through Colab Secrets or environment variables. If `EIA_API_KEY` is absent, EIA-dependent stages report `WARN: source unavailable` and PUSI-P runs on the remaining verified sources. Nothing is synthesized to fill the gap. Never hardcode secrets or put them in Drive notebooks. Avoid storing raw licensed news text if terms prohibit it. Store article IDs, URLs, permitted excerpts, labels, and provenance.

**Execution strategy:** raw immutable downloads in Drive, intermediate Parquet and DuckDB in scratch, checkpoint back to Drive after each successful stage. Parquet partitioned by source/year/ticker. Use `pyarrow`, `duckdb`, `pandas`, `numpy`, `scipy`, `statsmodels`, `scikit-learn`, `matplotlib`, `plotly`, `pytest`, `pandera` or `pydantic`, `requests`, `tenacity`, `yfinance` for exploratory prices, `fredapi` or FRED REST, EIA API v2 via `requests` (paged, at most 5,000 rows per call, cached per route and parameter hash), `pdfplumber` for manual-review extraction of tables from grid-operator/NERC PDFs (extracted values always human-verified), `beautifulsoup4`, `transformers` optional, `linearmodels` optional, `ruptures` optional, `lifelines` optional, `pymc` optional. Pin compatible versions after a Colab smoke test, not arbitrarily here.

**Colab operational controls:** bounded downloads, exponential backoff, explicit HTTP User-Agent where required, source-specific rate limits, checkpoint every successful batch, idempotent retries, safe Drive writes (temporary file then atomic rename when supported), chunked processing, deterministic seeds, runtime restart test, notebook execution via `nbclient` or `papermill` where feasible. Make optional heavy dependencies lazy. Do not assume free Colab guarantees GPU, long-running sessions, or stable package versions.

### Repository contract

```text
nvidia_shock_study/
  README.md  requirements-colab.txt  pyproject.toml  .gitignore
  configs/
    study.yaml  sources.yaml  tickers.csv  event_schema.yaml  preregistration.yaml
    power_sources.yaml  power_stress.yaml          # v1.1
  notebooks/
    00_setup.ipynb  01_source_audit.ipynb  02_prices.ipynb
    03_macro_fundamentals.ipynb  04_resources.ipynb  04b_power_utilities.ipynb  05_news.ipynb
    06_events.ipynb  07_stress.ipynb  08_baselines.ipynb
    09_H3_counterfactual.ipynb  10_H1_H2_interactions.ipynb
    11_H4_H5_long_horizon.ipynb  12_report.ipynb
  src/
    config.py  pipeline.py  storage.py  provenance.py
    ingest/{prices,fred,sec,resources,news,x_optional,eia,power_reports}.py
    validate/{schemas,calendar,point_in_time,events,coverage,power}.py
    features/{returns,benchmarks,stress,power_stress,valuation,news_labels}.py
    models/{factor,event_study,forecast,synthetic_control,panel,recovery,regimes}.py
    evaluation/{backtest,placebo,robustness,power,uncertainty,incremental_value,negative_controls}.py
    viz/{data_quality,stress,events,counterfactual,results,power_utilities}.py
  tests/{unit,integration,statistical,smoke}/
    # v1.1: unit/test_power_validation.py, unit/test_power_pit.py, unit/test_units.py,
    #       statistical/test_incremental_value.py, statistical/test_negative_controls.py,
    #       fixtures/synthetic_power/ (labelled SYNTHETIC)
  data/{raw,interim,processed,external}/
  reports/{figures,tables,validation,model_cards,progress.md,decision_log.md,data_manifest.json}
```

`data/`, secrets, downloaded articles, and large binaries are excluded from Git. A small synthetic test fixture is committed. Source file SHA256, retrieval UTC time, URL, license, schema version, and processing version go in the manifest. Every output table must be reproducible from source snapshot and config.

## 3. Data inventory, exact fields, access routes, and source risk

**Data policy:** public does not necessarily mean freely redistributable. Check each provider's access terms and retain provenance. First run a source audit before building any downstream model. Where historical point-in-time coverage is unavailable, record `unavailable` and use a prespecified lower-fidelity proxy rather than implying precise history.

| Dataset | Preferred public route | Fields, cadence | Purpose | Limitations / fallback |
|---|---|---|---|---|
| Daily adjusted prices and volume | Yahoo Finance via `yfinance` for research prototype | ticker, session date, open/high/low/close, adjusted close or adjustment flags, volume, currency, exchange | returns, peer factors, drawdown, volatility | Unofficial API; revisions/adjustments; validate against Nasdaq/Stooq or another independently available source for sample dates |
| Broad market and sector | SPY, QQQ, SOXX, SMH, S&P 500, SOX where available | daily price/total-return proxy | market baseline | Sector ETFs include NVDA; construct ex-NVDA peer basket; ETF history/inception and weights matter |
| Foundry, equipment, packaging | TSM, ASML, AMAT, LRCX, AMKR | daily returns, quarterly fundamentals | supply-chain factors | supplier stocks also reflect their own news |
| HBM/memory | MU, SK Hynix `000660.KS`, Samsung `005930.KS` | daily local-currency prices, quarterly commentary | memory constraint proxy | align calendars, FX, local holidays; equities are not physical HBM capacity |
| Power and cooling | VRT, ETN, PWR, EQIX, DLR | daily returns and disclosed capacity | infrastructure factor | EQIX/DLR are REITs, with rate exposure |
| AI demand customers | MSFT, AMZN, GOOGL, META | daily returns, quarterly capex | demand factor | endogeneity with NVDA; use lagged capex announcements and ex-event screens |
| Treasury, spreads, market stress | FRED REST/CSV: DGS10, DGS2, BAA10Y or selected investment-grade/high-yield spreads, STLFSI4 or equivalent, DFF | date, vintage if available, value, units | macro stress | mixed publication lags, revisions, frequency; verify series IDs and availability in audit |
| Implied volatility | CBOE public VIX/VXN history or Yahoo `^VIX`, `^VXN` | trading date, close | forward-looking market fear | historical availability and redistribution terms; VIX is not NVIDIA-specific |
| Corporate fundamentals | SEC EDGAR submissions and XBRL companyfacts API, investor-relations filings | filing accession, accepted date, period end, revenue, gross margin, operating income, cash flow, shares | valuation, operating stress | filing date vs period end, restatements, XBRL tag variations; point-in-time reconstruction required |
| Supplier resource disclosures | SEC filings and public investor presentations of TSMC, Micron, ASML, SK Hynix, power firms | disclosed HBM capacity, CoWoS/packaging, lead times, capex, constraints, guidance, as-of/announcement date | resource stress | patchy nonstandard text, estimates often unavailable; manually curated disclosure table with source and units |
| Industry demand | Hyperscaler SEC filings, earnings releases, official transcripts if licensed | capex, guidance, revenue growth, announced date | demand stress | point-in-time dates and revised estimates |
| Leadership news | Company IR, SEC 8-K, Reuters/AP where accessible, GDELT DOC API, Yahoo Finance news metadata | article ID, URL, title, source, publication UTC, first-seen UTC, company, person, event type | event chronology, shock classification | historical Yahoo feeds incomplete, GDELT coverage varies, paywalls, syndicated duplicates |
| Utilities and power-equipment equities (v1.1) | Yahoo via `yfinance`: XLU, ^UTY, GRID, ETN, VRT, PWR; placebo XLP, XLV | daily OHLCV, adjusted close | PUSI-F, rolling correlations, negative controls | S&P 500 Utilities Index (`^SP500-55`) has no free history (Yahoo returns only the current bar), so it is **unavailable** and XLU is the proxy; ^UTY is a price index (dividends excluded); VRT starts 2018-08-02, GRID 2009-11-17 |
| Physical electricity and grid (v1.1) | EIA API v2, FRED, grid-operator / NERC reports, IEA / LBNL context. Full specification in research plan Section 5.1 and `configs/power_sources.yaml` | monthly / hourly / annual / event-based | PUSI-P, context | release lags, revisions, regional scope, not specific to data centers; PDF tables need human-verified extraction |
| X / social media, optional | Official X API if authorized, public aggregate trends where lawful | post ID, timestamp, engagement, topic, author type | sensitivity and narrative diffusion | historic access cost, selection bias, bots, platform policy; not required for MVP |
| Trading liquidity, optional | Public daily OHLCV proxies | dollar volume, Amihud proxy | liquidity stress | true historical spreads/order book generally not public; label as proxy |

**Initial universe:** NVDA; peer technology firms and leadership-event controls including AMD, INTC, AVGO, QCOM, AAPL, MSFT, META, GOOGL, AMZN, TSLA, CRM, ORCL, IBM, and additional firms identified in event audit. Do not restrict the control sample to winners or to events that moved prices. Specify eligibility rules before collecting outcomes. For international firms, record primary exchange, currency, timezone, and local session alignment.

**Periods:** target daily data from 2015-01-01 through the latest reproducible as-of date; leadership events from 2015 onward subject to verified coverage; pre/post windows vary by test. Record exact event timestamp and first public report. Do not presume a single November 2026 announcement is the first disclosure.

**Data dictionaries (required):**

- `prices`: `ticker, exchange, currency, session_date, open, high, low, close, adjusted_close, volume, source, retrieved_at_utc, snapshot_id, adjustment_method`.
- `macro`: `series_id, observation_date, release_date_utc, vintage_date, value, units, source, retrieved_at_utc`.
- `fundamentals`: `cik, ticker, metric, fiscal_period_end, filed_at_utc, accession, value, unit, taxonomy_tag, restatement_flag, source`.
- `resource_disclosures`: `entity, resource_type, metric, value, unit, valid_period, announced_at_utc, source_url, excerpt_or_page, confidence, reviewer`.
- `articles`: `article_id, canonical_url, publisher, headline, published_at_utc, first_seen_at_utc, retrieved_at_utc, source, ticker_mentions, person_mentions, license_class, duplicate_cluster`.
- `events`: `event_id, firm, person_role, event_family, event_subtype, first_public_at_utc, first_source_id, followup_ids, severity_label, surprise_label, verified_status, contamination_flags, annotator_ids, adjudication_status`.
- `event_panel`: `firm, event_id, pre_stress_asof, event_date, horizon, abnormal_return, CAR, shock_severity, controls, sample_flags`.
- `power_physical` (v1.1): `series_key, source, route_or_series_id, region, sector, frequency, period_start, period_end, value, unit, unit_canonical, value_canonical, release_date_utc (or rule), vintage_date, retrieved_at_utc, revision_flag, evidence_quality (direct/indirect/proxy), staleness_sessions, missing_reason`.
- `power_reports` (v1.1): `report_id, issuer (PJM/NERC/LBNL/IEA/...), report_type, metric, value, unit, delivery_or_reference_period, published_at_utc, source_url, page_or_table, extraction_method (api/csv/manual_pdf), reviewer, confidence, is_projection`.
- `power_stress` (v1.1): `asof_session, family (PUSI_F/PUSI_P), component, raw_value, transformed, zscore, fit_window_end, weight, n_components_present, staleness_max, basket_version`.

## 4. Cross-stage data quality and statistical acceptance standards

Every ingestion module returns a validation object with `PASS`, `WARN`, or `FAIL`, reasons, counts, and output paths. `FAIL` blocks downstream stages. Thresholds below are *engineering defaults* and must be configurable, not treated as scientific truths.

**Market data:** unique `(ticker, session_date)`; sorted sessions; positive OHLC; high >= max(open,close,low); low <= min(open,close,high); nonnegative volume; no weekend session for US-listed equities except documented exceptions; missing-session ratio <= 2% within expected exchange trading calendar for active listed periods, otherwise flag; zero volume and extreme >25% daily moves flagged for corporate-action/manual review, never automatically deleted; adjustment consistency check on splits/dividends; ticker start/end dates validated. Coverage report per ticker and year.

**Time leakage:** every feature has `information_available_at_utc`. At prediction/event cutoff, assert `available_at <= cutoff`. Quarterly figures must use filing/publication dates, not quarter end. For revised macro data use historical vintages when available, otherwise disclose current-vintage limitation. Never standardize using future observations; fit scalers only on training folds. Event labels must not use future stock reactions.

**News:** normalized UTC and exchange-local times; deduplicate syndication; check source timestamp vs retrieval timestamp; manually review earliest report; exclude post-event commentary from pre-event stress; distinguish rumors, allegations, confirmed company disclosures, and independent corroboration. Article relevance and event extraction must be evaluated on a held-out human-labeled set, not only LLM self-judgment.

**Models:** chronological splits, event-level or firm-level grouping where needed, no overlapping windows between train/test without embargo; report coefficient, confidence interval, effect size, sample size, diagnostics, missingness, and model assumptions. For rare-event inference report minimum detectable effect or simulation-based power; do not interpret non-significance as proof of zero effect. Multiple hypotheses/horizons: declare primary estimand and use multiplicity adjustment or clearly exploratory labels.

**Power and electricity data (v1.1):**
- Unique `(series_key, period_start)`, and no duplicate trading dates for equities.
- Every value carries a canonical unit. Conversions are tested (cents/kWh ↔ $/MWh, MW ↔ GW, MWh ↔ TWh), and mixed units within a series cause a FAIL.
- Frequency conversion uses an as-of join on the release date. No linear interpolation, no backfill and no centered smoothing are allowed. The last released value carries forward up to a per-series `max_age` (configured), then becomes missing.
- Seasonal monthly series are transformed (year-over-year or seasonal difference) inside the training window only.
- Outliers are flagged (robust z > 6 on the transformed series) for manual review and never deleted automatically.
- Revisions: use ALFRED vintages for FRED series where available; otherwise flag the series as `current_vintage_only`. Values that were revised after T were not available at T: `current_vintage_only` series are excluded from the confirmatory incremental-value comparison and their results are labelled "revised-data, exploratory" (v1.2).
- Regional series must state their aggregation (sum or demand-weighted).
- Physical values extracted from PDFs need a reviewer and a page/table reference.
- Projections (IEA/LBNL) are flagged `is_projection` and are never used as observed time-series regressors.
- Corporate actions for XLU/^UTY/GRID/ETN/VRT/PWR are checked as for other equities. ^UTY is a price index, so return comparisons with total-return ETFs are flagged.

**Charts:** every stage saves at least one *before* diagnostic chart and one *after* output chart to `reports/figures/stage_##/`, both PNG and interactive HTML where useful. Captions include sample period, units, source, and whether the data are empirical or synthetic. Charts must never use invented returns.

## 5. Stage 00: bootstrap, preregistration, and source feasibility

**Notebook:** `00_setup.ipynb` and `01_source_audit.ipynb` | **Priority:** blocker.

**Inputs:** companion research plan, proposed ticker list, public source endpoints, Colab environment.

**Tasks:** create repo and package; establish Drive/scratch paths; build YAML configs; preregister H1 primary interaction, event windows (e.g. [-1,+1], [0,+1], [0,+5] sessions), abnormal-return benchmark, stress cutoff (e.g. end of prior trading day), primary comparison cohort, severity rubric, exclusions, and multiplicity policy. Test one tiny download from each provider; verify SEC User-Agent and source terms. Generate a source-access matrix (available, conditional, unavailable), and an explicit fallback tree.

**Before charts:** source coverage feasibility by provider and year, expected vs accessible sample matrix. **After charts:** actual returned date ranges, missingness and rate-limit summary.

**Tests:** config schema, paths, no hardcoded secrets, deterministic seed, Colab mount failure handling, API error retry, source schema smoke tests, notebook restart, manifest integrity.

**Gate:** at least one lawful working source each for prices, macro, filings, and event chronology; verified primary-event timestamp methodology; no unreviewed source assumptions. If event coverage insufficient, revise estimand/sample before continuing.

## 6. Stage 01: prices, corporate actions, calendars, and benchmark baskets

**Notebook:** `02_prices.ipynb`.

**Download:** OHLCV and adjusted price history for all configured tickers, broad market and volatility proxies; exchange metadata, corporate-action records where accessible.

**Transform:** use adjusted close consistently for return analysis, avoid double adjusting; log returns `ln(P_t/P_{t-1})`; maintain local exchange session and USD-converted sensitivity series for non-US stocks using independently sourced FX. Construct ex-NVDA semiconductor benchmark using preregistered equal-weight or fixed pre-event weights; avoid survivorship bias by documenting historical eligibility. Compare equal-weight, value-weight when reliable historical market caps exist, and sector ETF with explicit NVDA contamination warning. Lag weights and rebalance monthly.

**Before charts:** raw price levels, ticker coverage timeline, missing-date heatmap, raw split-jump flags. **After charts:** normalized adjusted prices (base 100), weekly and daily returns, rolling 20/60-day vol, sector benchmark composition, benchmark correlation heatmap.

**Tests:** synthetic split/dividend adjustment, duplicate dates, bad OHLC, missing sessions, timezone, FX alignment, no NVDA in ex-NVDA index, no forward-weight leakage, identical returns from independently recomputed sample.

**v1.1 power/utilities additions:** Download XLU, ^UTY, GRID, ETN, VRT, PWR and placebo XLP, XLV. Record `^SP500-55` as unavailable. Build PUSI-F baskets by version: core (XLU, ^UTY, ETN, PWR) from 2005, + GRID from 2009-11-17, + VRT from 2018-08-02. Never backfill a ticker before its listing date.
- *Before:* raw levels and listing-date coverage timeline for the power/utility tickers.
- *After:*
  - utility and power-equipment performance normalized to 100 at a common start (core basket since 2005; full basket since 2018-08);
  - utilities vs ex-NVDA semiconductor relative performance;
  - rolling 60/120-session correlation of NVDA with each power/utility series, raw and residualized on SPY/QQQ, with XLP/XLV placebo lines;
  - data-quality report `reports/validation/stage_01_power_equities.json`.
- *Tests:* listing-date backfill guard, basket-version log, price-index vs total-return flag, placebo tickers excluded from PUSI.

**Gate:** coverage and adjustment reports PASS for core NVDA, SPY/QQQ, and minimum viable peer basket; all exceptions logged. v1.1: the core power/utility basket PASSes coverage and adjustment checks from 2005, otherwise PUSI-F is restricted to the period that passes.

## 7. Stage 02: macroeconomic stress and point-in-time fundamentals

**Notebook:** `03_macro_fundamentals.ipynb`.

**Download:** FRED interest rates, spreads, stress indexes, VIX/VXN, SEC XBRL companyfacts and filing indexes for NVDA and selected controls, hyperscaler capex filings.

**Transform:** maintain observation date, publication/release date, retrieval date, vintage. Build trailing financial ratios: revenue growth, gross margin, free-cash-flow proxy, cash/debt, capex/revenue, valuation multiples only when contemporaneous price and share/earnings information are available. Distinguish trailing earnings from forward consensus; do not fabricate forward estimates. Daily join via last information publicly available, with staleness indicator.

**Before charts:** frequency mismatch and release lag distributions, missing macro values, XBRL tag/units inconsistencies. **After charts:** yields/spreads/VIX timelines, financial ratio trends with vertical filing dates, macro-fundamental stress heatmap.

**Tests:** quarter-end leakage fixture, filing date precedence, unit conversion, SEC accession dedup, revisions, forward-fill maximum age, extreme ratio guards, point-in-time joins.

**v1.1:** Add the FRED energy series verified on 2026-11-13: `APU000072610` (average price of electricity per kWh, US city average, monthly), `CUSR0000SEHF01` (CPI electricity, SA), `PCU22112211` (PPI electric power generation, transmission and distribution), `WPU0543` (PPI industrial electric power), `IPG2211S` (industrial production, electric power G/T/D), `CAPUTLG2211S` (capacity utilization, electric power G/T/D), `DHHNGSP` (Henry Hub gas spot, daily). Each gets a release-date rule from its release calendar (BLS CPI/PPI, Fed G.17, EIA). The release date, not the observation month, is `available_at`.

**Gate:** all core features have `available_at` and documented data vintage. Missing forward consensus must remain missing or explicitly omitted.

## 8. Stage 03: physical-resource and industry-demand stress

**Notebook:** `04_resources.ipynb`.

**Download:** supplier SEC filings, official TSMC/Micron/ASML/SK Hynix disclosures where accessible, hyperscaler capex releases, electricity/grid indicators from public official datasets when relevant, and supplier stock returns from Stage 01.

**Transform:** create two independent families: (A) observed resource disclosures, with units, source and announcement dates; (B) *market-implied resource factor* from supplier baskets. Do not call stock-price movements direct measures of HBM capacity or power shortages. Code evidence quality `direct/indirect/proxy/unavailable`. Create resource scarcity indicators only for disclosed comparable metrics. Preserve supply and demand sign logic: shortage may improve supplier pricing power while limiting shipments; test rather than impose a negative sign.

**Before charts:** source coverage and availability heatmap by resource, disclosure-lag histogram. **After charts:** resource disclosure timeline, AI capex growth, ex-NVDA supplier factor returns, cross-factor correlation, proxy-versus-disclosure comparison.

**Tests:** no mixed physical units, no future disclosures, no double counting across sources, currency conversion, supplier basket exclusions, manually audited sample.

**Gate:** every resource metric tagged by provenance and confidence; if physical capacity series fail, proceed with a clearly labeled proxy-only model and downgrade H2 interpretation.

## 8b. Stage 03b (v1.1): power, utilities and electricity infrastructure

**Notebook:** `04b_power_utilities.ipynb` (thin wrapper over `src/ingest/eia.py`, `src/ingest/power_reports.py`, `src/validate/power.py`, `src/features/power_stress.py`, `src/viz/power_utilities.py`). **CPU only.** No GPU is used anywhere in this stage, because the data are small tabular series.

**Inputs:**
- Stage 01 power/utility equities.
- Stage 02 FRED energy series.
- The verified physical sources in research plan Section 5.1, mirrored in `configs/power_sources.yaml`. Each entry gives source, route/ID, frequency, coverage, units, license, release rule, `max_age` and missing-data policy.

**Tasks:**
1. Source audit for each power source. Hit the endpoint, record status (`available` / `conditional` / `unavailable`), coverage and license. Anything not verified stays `unavailable`.
2. Ingest EIA API v2 routes with paging and caching, keyed by route and parameter hash.
3. Curate the low-frequency reports (capacity auctions, interconnection queues, NERC risk ratings) into `power_reports`. Every value needs a reviewer and a page/table reference.
4. Load IEA/LBNL data-center figures as `is_projection` context.
5. Canonicalize units, run the release-date as-of join onto the session grid, and apply staleness limits.
6. Build PUSI-F and PUSI-P (research plan 7.2.1) with fold-safe scaling.
7. Build the XLP/XLV placebo index with an identical recipe.

**Before charts:**
- release-lag distribution per physical series;
- coverage heatmap (series × year);
- raw-unit panel per series;
- outlier flags.

**After charts:**
- electricity prices, demand and capacity over time, with release-date markers;
- data-center electricity estimates/projections (labelled projections);
- PUSI-F and PUSI-P over time with regime bands and the NVIDIA disclosure stages;
- PUSI-F vs PUSI-P divergence;
- PUSI vs placebo-sector index.

**Data-quality report:** `reports/validation/stage_03b_power.json`, covering per-series row counts, date ranges, missing share, duplicate count, unit checks, staleness distribution, revision status and outlier flags.

**Tests:**
- missing values preserved (no interpolation);
- duplicate periods rejected;
- release-date alignment (a value is invisible before its release);
- monthly→session frequency conversion via as-of only;
- unit conversion round-trips;
- listing-date backfill guard;
- outlier flag without deletion;
- look-ahead: perturb all data after the cutoff, and PUSI at the cutoff must be unchanged;
- projection rows never enter regressors;
- placebo index excluded from PUSI;
- NVDA never in PUSI.

**Gate (PASS/FAIL):**
- PASS if PUSI-F is computable from 2005 (core basket) and PUSI-P has at least two independent verified physical components with documented release rules, and all tests pass.
- If PUSI-P cannot meet this, it is reported as unavailable and only PUSI-F proceeds, with H2/H3 power claims limited to market-implied indicators.

## 9. Stage 04: news collection, first-disclosure chronology, and labels

**Notebook:** `05_news.ipynb`.

**Download:** public SEC/IR disclosures, GDELT metadata and accessible article URLs, Yahoo Finance headline metadata where available, selected credible reporting; optional X API only if authorized. Query both firm/person and generic leadership terms. Record retrieval success, paywall/rights status, timestamp precision, and earliest verifiable public appearance.

**Event ontology:** `leadership_exit`, `succession`, `governance`, `investigation_or_allegation`, `strategy_dispute`, `health_or_unavailability`, `regulatory`, `earnings`, `product`, `industry`, `resource`, `macro`. Event flags: `leadership_specific`, `independent_external`, `potential_downstream`, `ambiguous`. Severity rubric independent of returns: role centrality, surprise, confirmation status, operational consequence, information novelty, credible-source corroboration. Mark unverified allegations as such. Record overlapping news and other confounders.

**Annotation:** stratified manually reviewed sample across firms, dates, publishers, severity and event types; double annotation for at least a configurable subset (default 20%); adjudicate disagreements. Baseline keyword/rules, then optional FinBERT for sentiment and lightweight text classifier/LLM-assisted labeling. Human review is authority for event chronology. News intensity alone is not event severity.

**Before charts:** daily headline counts, publisher coverage by year, duplicate clusters, UTC-to-market-session alignment. **After charts:** leadership-event timeline, category distribution, severity distribution, annotated confusion matrix, inter-annotator agreement, article-to-event provenance graph.

**Evaluation:** precision, recall, macro F1 per class, event-extraction F1, severity weighted kappa or ordinal MAE, timestamp agreement; target >=0.80 precision for high-confidence leadership events and >=0.75 macro F1 as provisional engineering gates, with CIs and error review. If targets fail, use human-only curated events for primary inference.

**Tests:** duplicate syndication, missing time, conflicting first timestamps, label leakage from returns, downstream-news exclusion, rate-limit fallback, malformed articles, no full-text storage where prohibited.

**Gate:** independently verified NVIDIA first-public-disclosure chronology; sufficient adjudicated events across firms or an explicit statistical-power limitation and narrower claims.

## 10. Stage 05: pre-event stress indices and regimes

**Notebook:** `07_stress.ipynb` (after `06_events.ipynb` assembles event registry).

**Construct:** Market Stress Index (MSI) from lagged realized volatility, implied volatility, credit spreads, drawdowns, and optionally liquidity proxies. Resource Stress Index (RSI) from dated disclosures and/or supplier-demand factors, separately labeled. Firm Fragility Index (FFI) from lagged financial ratios and valuation sensitivity. Leadership Uncertainty Index (LUI) from *prior* independent leadership-related information, separate from the event shock. Use winsorization and rolling expanding-window z-scores fitted only to past data; report equal-weight and PCA alternatives. Stress measured no later than prior session close for main event analysis.

**Regimes:** preregister low/medium/high stress quantiles from training data, plus optional two-state Markov-switching model as exploratory. Prevent circularity: exclude same-firm event-window returns and same-day leadership news from the stress score. PCA sign must be anchored by known stress direction and verified across folds.

**Before charts:** component distributions, missingness, pairwise correlations, raw stress components. **After charts:** MSI/RSI/FFI timelines, stress regime bands, index decomposition, historical stress-event alignment, leave-one-component-out stability.

**Tests:** lag availability, scaler fit boundaries, index sign, deterministic PCA, collinearity, missing component handling, historical fold reproducibility, component independence checks.

**v1.1:** RSI is reported as named components, and **PUSI-F and PUSI-P are separate RSI components** (not merged into MSI), each with its own regime bands. Charts add the PUSI component timelines and their correlation with MSI and FFI. Tests add PUSI fold-boundary and staleness checks.

**Gate:** pre-event stress score computable for an adequate number of historical events; no same-event outcome contamination; stress reliability and sensitivity documented.

## 11. Stage 06: event registry, severity, and abnormal-return baselines

**Notebooks:** `06_events.ipynb`, `08_baselines.ipynb`.

**Build event registry:** one row per information shock, with earliest verified source and disclosure timestamp. Assign trading-session event date based on exchange calendar and whether announcement was premarket, during market, or after close. Group multi-day related disclosures; flag overlapping earnings, product releases, macro shocks, and confounded events. Keep an inclusion/exclusion audit. Sample other firms' leadership shocks using predefined search criteria, not their observed returns.

**Baseline models:** market-adjusted returns, ex-NVDA industry-adjusted returns, OLS market model, regularized multi-factor model. Estimate normal returns on pre-event estimation window (default [-252,-31] trading sessions, with >=120 valid observations), embargo before event, and compute abnormal return AR and cumulative abnormal return CAR at preregistered windows [-1,+1], [0,+1], [0,+5], [0,+20]. Windows starting at 0 apply only to events with a known time of day; date-only events use the same windows started at −1 (v1.2). Use timestamp-specific intraday windows only when verified intraday data exist; daily windows otherwise. **v1.3 candidates:** fixed [-252,-31] market model; short window [-126,-11]; EWMA beta (half-life 63 sessions); volatility-scaled AR (EWMA sigma). Select on pre-2015 placebo events by bias, 5% test size and out-of-sample error, overall and by stress tercile; never on NVIDIA. Volatility-scaled outcomes divide by pre-event volatility (part of stress), so they are secondary. Compute resilience outcomes R1 CAR[-1,+1], R2 additional damage min_{k in [+2,+20]} CAR[-1,k] - CAR[-1,+1] with its placebo distribution, R3 recovery time (Stage 10).

**Before charts:** event coverage by year/firm/type, event overlaps, estimation window availability, benchmark residual distributions. **After charts:** event-aligned cumulative abnormal returns, model residual diagnostics, actual-versus-expected returns, placebo-date CAR distributions.

**Tests:** event-session mapping around holidays/after-close, AR/CAR arithmetic, overlapping events, embargo enforcement, minimum estimation observations, no benchmark contamination, clustered bootstrap reproducibility.

**Evaluation:** baseline fit (out-of-sample RMSE/MAE), residual autocorrelation, heteroskedasticity, beta stability, placebo calibration. Do not select factor model by maximizing the event's estimated effect.

**Gate:** abnormal-return baseline chosen using pre-event backtests and diagnostics, not post-event outcomes; event panel audit PASS.

## 12. Stage 07: H3, vulnerability and no-news counterfactuals

> **v1.9:** this stage is the primary analysis N1, specified in PLAN.md §2 (A; B1–B4; session categories; placebo inference; decision table) and run as steps N-a .. N-f, one model at a time with results reported before the next.

**Notebook:** `09_H3_counterfactual.ipynb` | **Priority:** first substantive hypothesis.

**Experiment A, ex-ante:** freeze data, features, and model at the earliest verified Jensen-related disclosure. Fit elastic-net/ridge factor regression and simple time-series baselines using prior market/industry/resource/macro data. Predict return distribution over 1, 3, 5, 10, 20 trading sessions from information *already known*. Never feed realized future market factors into this forecast and call it ex-ante.

**Experiment B, conditional:** use realized subsequent independent market and macro factors as conditioning information, with explicit contamination exclusions. Compare contaminated versus screened donor sets. Optional Bayesian structural time series and constrained synthetic control. Do not use NVDA-containing ETF as an uncontaminated control.

**Experiment C, stress transport:** fix standardized leadership-shock severity and firm attributes as far as defensible; set pre-event stress to historical 2025 and 2026 levels; calculate estimated effect and confidence interval using H1 model *after H1 is trained*. Mark as scenario analysis, not observed no-news truth.

**Before charts:** pre-cutoff factor histories, rolling forecast errors, candidate donor correlations, pre-treatment fit. **After charts:** actual versus ex-ante forecast fan chart, conditional no-news path with uncertainty, abnormal-return gap, placebo rank histogram, stress-transport comparison after H1.

**Evaluation:** walk-forward RMSE/MAE, direction accuracy as secondary, prediction interval coverage (e.g. 80/95%), pinball/CRPS if available, placebo p-values, pre-treatment RMSPE, sensitivity to donors, date cutoffs and horizon. Report base rates of predicted negative returns and uncertainty; a predicted decline is not proof of no leadership effect.

**Tests:** no future prices in A, donor exclusion, freeze timestamp, future-release leakage, time-series fold embargo, reproducible bootstrap, forecast-vs-conditional labels.

**v1.1, power variables in H3 (primary power target):**
- Fit M0 (market, ex-NVDA sector, MSI) against M1 (+PUSI-F), M2 (+PUSI-P), M3 (both) and M1-orth (PUSI-F residualized on SPY/QQQ, the AI-demand basket and rates).
- Use rolling-origin walk-forward with an expanding window: step 21 sessions, horizons 1/5/20 sessions, embargo of at least the horizon, nested tuning.
- Primary targets are the predictive distribution of NVDA returns: realized volatility and the 5%/10% quantiles. The mean return is secondary.
- Metrics: CRPS, pinball loss, 80/95% coverage, RMSE/MAE, Diebold-Mariano with HAC, block-bootstrap CI of the loss difference, fold-wise sign consistency.
- *After chart:* NVDA predicted returns and intervals with vs without power variables against realized returns, plus per-fold loss differences.
- *Tests:* identical samples across M0–M3, fold-boundary leakage, DM/bootstrap fixtures.

**Gate:** honest calibrated uncertainty and a clear statement of what the no-news experiment can and cannot identify. If forecasting fails placebo coverage, do not interpret the NVIDIA path causally. v1.1: a power-variable gain is reported only under the research plan 8.7 decision rule and after the negative controls in 8.8.

## 13. Stage 08: H1, stress-dependent amplification (primary causal question)

> **v1.9:** secondary statistical study H1a/H1b (leadership concentration moderator, PLAN.md §3); not the primary question.

**Notebook:** `10_H1_H2_interactions.ipynb`.

**Primary estimand (v1.3+):** d_P and d_M, the change in CAR[-1,+1] for a performance or misconduct dismissal relative to a voluntary departure per one SD of pre-event stress; two Holm-adjusted tests (`configs/preregistration.yaml: primary_tests`). The v1.1 estimand (one-unit standardized shock) is a secondary ordinal specification. Fit firm/time fixed-effect panel regression with severity, stress, severity×stress, event-family controls, firm attributes, pre-event valuation, and relevant calendar effects. Severity must vary independently of return. Cluster uncertainty by firm and/or event date as supported by sample size; use wild cluster/bootstrap sensitivity when clusters are few.

**Specification (v1.3, categorical):** `CAR_ie = alpha + g_P*Perf + g_M*Misc + beta2*stress_pre + d_P*Perf*stress_pre + d_M*Misc*stress_pre + theta'X_ie(as of T) + error_ie`, voluntary as baseline. Primary tests: d_P < 0 and d_M < 0, Holm-adjusted. Secondary: pooled contrast (count-weighted average of d_P, d_M), equality, ordinal score `beta3*(severity*stress_pre)` (the v1.1 form). X: tenure, founder, planned vs surprise, successor named, size, sector, prior return; robustness adds X × stress. R2 is a secondary outcome with the same design. **v1.4:** also report total slopes per type (beta2 + d_k) against matched non-event dates (5 per event; same firm, year, stress tercile; ≥60 sessions from leadership events, ±1 from earnings); R2 on the full sample with `competing_event` (+ first date) and sensitivities (uncontaminated; censored at first competing event with a window-length-matched placebo). **Stage 08 entry gate:** outcome-blind power re-run on the retained sample with real covariates, missingness, MSI at event dates, cluster-robust SEs by event month, residual variance from estimation-window/placebo residuals only; MDE by type recorded in the preregistration, which is then frozen. Test primary 3-session CAR; other windows secondary. Do not simultaneously include redundant fixed effects that make stress unidentified. Check sample size and statistical power before fitting.

**Before charts:** severity vs pre-event stress scatter, cohort balance, overlap/confounder frequencies, sample support across stress deciles. **After charts:** interaction marginal-effect curves with 95% CIs, predicted comparable shock under low/high stress, forest plot across benchmark/event windows, coefficient stability by leave-one-firm-out.

**Evaluation:** beta3 sign/magnitude/CI, clustered inference, placebo pseudo-events, matched-severity analysis, alternative stress indices, controls, leave-one-firm-out, influence diagnostics, time-split replication. If effect is imprecise, say inconclusive rather than no effect.

**Tests:** design-matrix rank, standardization within training period, fixed-effect encoding, clustered bootstrap, interaction marginal effect formula, no post-event covariates, sample-selection logging.

**v1.1:** Robustness specs add PUSI-F/PUSI-P as alternative moderators and add a power-exposure contrast (exposed firm list fixed before outcomes). The primary H1 moderator stays MSI, as preregistered.

**Gate:** sufficient effective events and variation, model diagnostics and sensitivity table published. If sample underpowered, label results exploratory and do not assert confirmation.

## 14. Stage 09: H2, stress interactions and nonlinear challengers

> **v1.9:** optional (H5 in v1.9 numbering).

**Notebook:** continue `10_H1_H2_interactions.ipynb` with separate outputs.

**Models:** additive resource+market stress model; two-way shock×resource and shock×market; resource×market×shock only if powered; spline interaction and XGBoost challenger for prediction. H2 is not automatically established by higher XGBoost accuracy: require interaction effect uncertainty and economic interpretation. Report whether supply constraint is positively or negatively associated with valuation; do not pre-assign direction.

**Before charts:** stress correlation and joint support heatmap, sparse-bin counts. **After charts:** marginal effect surfaces with confidence bands, additive-vs-interaction held-out error, SHAP/ALE as descriptive only, permutation importance with time-aware folds.

**Evaluation:** chronological held-out MAE/RMSE, nested model comparison, interaction CI, stability across definitions, permutation test and sample-support checks.

**Tests:** no feature leakage, cross-validation grouping, sparsity checks, reproducible hyperparameter search, XGBoost not used for causal claims.

**v1.1, power in H2 (primary power target):**
- Models: shock × PUSI-F, shock × PUSI-P and shock × MSI × PUSI (only if powered), each compared with the additive model. Run on the core-basket period (2005+) and on the full basket (2018-08+).
- Run all research plan 8.8 negative controls: market orthogonalization, AI-sentiment control, rates control, valuation control, XLP/XLV placebo sectors, physical-vs-financial divergence, timing placebos, block permutation, exposure contrast.
- Feasibility scan (2026-11-13): 1,083 panel events since 2018-08 (31 misconduct) and 229 since 2023 (6 misconduct). Run a power check before fitting. If underpowered, power-era interactions are labelled exploratory.
- *After charts:* marginal-effect curves by PUSI regime, with vs without power variables (walk-forward loss), coefficient stability across folds, negative-control forest plot.

**Gate:** only report synergy if interaction is robust and sample supports comparison; otherwise inconclusive.

## 15. Stage 10: H4, recovery time and dynamic response

**Notebook:** `11_H4_H5_long_horizon.ipynb`.

**Definition:** recovery event occurs when cumulative abnormal return returns to >=0 relative to a preregistered event baseline, sustained for e.g. 3 trading sessions; compare alternative thresholds and 1-day criterion. Follow up 20/60/120 trading days when observed. Right-censor events without recovery. Competing corporate events must be flagged; consider censoring sensitivity.

**Models:** Kaplan–Meier by pre-event stress quantile; Cox PH with severity and event controls; accelerated failure-time alternative if proportional hazards fail; local projections of abnormal returns over horizons, with overlap-aware uncertainty.

**Before charts:** event follow-up lengths, censoring patterns, competing event timeline. **After charts:** survival/recovery curves with confidence intervals, hazard ratios, local-projection impulse-response-style paths.

**Evaluation:** proportional hazards test, censoring sensitivity, bootstrap intervals, horizon sensitivity, event overlap, sample sufficiency.

**Tests:** censoring logic, recovery crossing, holiday calendars, no future stress variables, survival table integrity.

**v1.1:** Add the PUSI regime at the event as a covariate (Cox/AFT) in a sensitivity model. Report the change in the stress hazard ratio with vs without it.

**Gate:** enough post-event observations; for recent NVIDIA event report censored status, not fabricated long-run recovery.

## 16. Stage 11: H5, valuation equilibrium, mean reversion, and regime shifts

> **v1.9:** the NVIDIA part is N3 (valuation vs fundamentals, criteria in PLAN.md §2.8); the rest is deferred.

**Notebook:** continue `11_H4_H5_long_horizon.ipynb`.

**Measure:** log valuation relative to earnings or cash-flow fundamentals, plus peer-relative valuation spread. Explicitly separate nominal stock price from valuation ratio. Use point-in-time fundamentals and valuation timestamps; where forward earnings unavailable, use trailing measures and acknowledge lag. Test whether the proposed spread is stable before estimating reversion speed.

**Models:** ADF and KPSS, cointegration where theoretically justified, error-correction or OU/AR(1) on stationary spread, rolling half-life only if stationarity and stable coefficients hold, Bai–Perron/ruptures or Chow-style break tests with proper critical values. Compare stable mean-reversion, time-varying mean, and structural-break models out of sample.

**Before charts:** valuation numerator/denominator, data coverage, rolling spread, stationarity diagnostics. **After charts:** estimated equilibrium and spread, break dates with uncertainty, regime comparisons, out-of-sample model scores, half-life only if meaningful.

**Evaluation:** stationarity/break evidence, bootstrap sensitivity, forecast performance, revised-fundamental sensitivity, alternative peer groups. A single post-event decline is not mean reversion.

**Tests:** logarithm domain, corporate action handling, lagged fundamentals, ADF/KPSS wrapper fixtures, structural-break synthetic cases, half-life stability guard.

**v1.1:** Add a sensitivity spread measured relative to the power-equipment basket (VRT/ETN/PWR/GRID), so that a repricing of the whole AI-power trade is not mistaken for NVIDIA-specific reversion.

**Gate:** distinguish reversion, repricing, and insufficient evidence; no automatic assertion that stress produces reversion.

## 17. Stage 12: integrated evaluation, robustness, report, dashboard

**Notebook:** `12_report.ipynb`.

**v1.1:** The scorecard gains a column "power/utilities incremental value", giving the M0 vs M1–M3 loss difference with its CI, the negative-control outcome, and a verdict of `improves / no incremental value / inconclusive` per hypothesis.

**Combine:** a five-row hypothesis scorecard: estimand, sample, method, effect, 95% CI, p-value if appropriate, out-of-sample diagnostics, placebo performance, limitations, verdict `supported / not supported / inconclusive`. Include the actual first-disclosure chronology and separate ex-ante and conditional counterfactuals. Explain whether the same-shock 2025 vs 2026 comparison is inside observed support or extrapolation.

**Before charts:** validation completeness dashboard, sample attrition waterfall, robustness matrix. **After charts:** stress chronology, event-study CAR, H1 marginal-effect curves, H2 interaction surface, H3 forecast fan chart, H4 recovery curves, H5 regime/valuation plot, sensitivity forest plots. Dashboard may use Plotly + static HTML for Colab/Drive; Streamlit optional and not required.

**Validation:** run all tests, rerun on a clean Colab runtime from pinned requirements and Drive snapshots, regenerate hashes/tables/figures, verify no hardcoded private paths, generate a source license/access inventory. Distinguish missing data from zeros. Check no chart claims more precision than underlying data support.

**Publication (v1.1):**
- Render the final report and figures as a static site (`reports/site/`, built by the pipeline from frozen outputs; Plotly HTML + PNG).
- Deploy it with a GitHub Actions Pages workflow from the NVIDIA-fall repository to `https://moghbaie.github.io/NVIDIA-fall/`.
- Add a project card to the existing Jekyll user site (`moghbaie/moghbaie.github.io`, branch `site-v2`, `_projects/` collection) that links to it.
- Publication is a separate, user-approved step after the gate.
- Before publishing, review the page for source attribution of every allegation, synthetic-vs-empirical labels, and data licenses: no raw Yahoo/PJM files are redistributed, only derived figures and tables with citations.

**Gate:** all mandatory stages PASS or documented limitations; reproducibility script works; final claims trace to dated sources and test results.

## 18. End-to-end automated test plan

**Unit tests (fast, every change):** returns, split handling, OHLC invariants, calendar/event timestamp mapping, index weights, rolling z-scores, severity schema, point-in-time joins, AR/CAR math, recovery censoring, confidence interval formatting.

**Integration tests (per stage):** API schema and 429 handling, cache roundtrip, source provenance, DuckDB/Parquet schema, news-to-event merge, full synthetic pipeline, Drive checkpoint recovery.

**Statistical tests (on synthetic fixtures):** recover known beta and interaction in simulated panel; zero-effect simulation should not systematically yield significant interaction; regime-shift detector recognizes injected break within tolerance; AR(1) mean reversion half-life matches known parameter; synthetic control recovers known no-treatment path under valid assumptions; calibration backtest hits approximate nominal coverage across many simulations.

**Leakage tests (mandatory):** inject a future filing, future article, revised macro series, post-event price and future-fitted scaler. Assert each is rejected by feature builders at earlier cutoff. Verify train/test event-window embargo.

**Power/utilities data tests (v1.1, mandatory):**
- missing values preserved;
- duplicate dates/periods rejected;
- release-date timestamp alignment;
- monthly/annual → session frequency conversion via as-of only, with `max_age`;
- corporate actions on utility/infra tickers and listing-date guards;
- robust outlier flags without deletion;
- unit consistency and conversion round-trips;
- look-ahead perturbation (data after the cutoff changed → PUSI and forecasts unchanged);
- projections excluded from regressors;
- PUSI never contains NVDA;
- placebo-sector recipe identical to PUSI-F.

Statistical fixtures (SYNTHETIC):
- an injected power effect is recovered by the M3 vs M0 comparison;
- a market-only common factor shows no gain after orthogonalization;
- the placebo index yields no gain under the null;
- the DM test has nominal size under the null.

**Research integrity tests:** source URL and timestamp present for each included event, manual review flags for unverified allegations, outcome-blind severity labels, donor contamination flags, source coverage disclosure, no false historical values in plots.

**CI:** GitHub Actions optional for unit/synthetic tests (no secrets or heavy downloads). Colab smoke test on a clean runtime before final delivery. `pytest -q tests/unit tests/statistical`; `pytest -q tests/integration` when configured source credentials/access exist; `python -m src.pipeline --through 12 --offline-snapshot SNAPSHOT_ID` for full reproduction.

## 19. Evaluation matrix and preregistered decision policy

> **v1.9:** the N1 decision table in PLAN.md §2.7 is the primary decision policy; the rows below apply to secondary and optional analyses under their v1.0 IDs (crosswalk at the top).

| Hypothesis | Primary outcome | Primary method | Minimum evidence to consider support | Reasons to withhold conclusion |
|---|---|---|---|---|
| H1 | 3-session CAR | firm/time panel severity×pre-stress | negative interaction with meaningful CI and robustness | severity confounding, too few events, donor contamination |
| H2 | CAR and held-out prediction | resource×market×shock interactions | stable joint effect beyond additive model | sparse joint-stress states, weak physical proxies |
| H3 | forward returns and CAR gap | frozen ex-ante forecast + conditional counterfactual | calibrated forecast shows downside vulnerability before news | poor backtest calibration, future-factor leakage |
| H4 | days to sustained CAR recovery | Kaplan–Meier + Cox/AFT | materially lower recovery hazard under stress with robustness | censoring, competing shocks, insufficient follow-up |
| H5 | valuation spread and breaks | stationarity/ECM + break tests | stable reverting spread or documented break, clearly distinguished | nonstationary fundamentals, data revisions, short sample |
| H6 | rival/supplier group CARs; G1 − G3 difference; panel rival CARs vs substitutability and leader fragility | group-portfolio event study, SPY-only benchmark, rebound control; panel regression with clustered SEs | G1 − G3 > 0 and rising with substitutability / fragility | contagion masking, groups chosen after seeing returns, rival news on the same day, foreign-session timing |

**Power/utilities evaluation (v1.1), applied to every row:** compare models without power variables (M0) with M1 (+PUSI-F), M2 (+PUSI-P) and M3 (both), using rolling-origin walk-forward validation, predictive metrics (CRPS / pinball / RMSE / coverage), coefficient stability across folds, block-bootstrap uncertainty and the negative controls. Primary for H2 and H3; robustness for H1, H4 and H5.

Do not use a binary significance threshold as the only criterion. Report economic magnitude, uncertainty, model sensitivity, and sample support. If conducting many secondary tests, label exploratory and apply appropriate false-discovery or familywise corrections.

## 20. Explicit visual inspection protocol at every stage

For each stage, save a `stage_##_before.png`, `stage_##_after.png`, and `stage_##_validation.json` plus detailed plots.

**`stage_##_validation.json` schema (v1.3):** `{stage, run_id, git_commit, started_utc, finished_utc, runtime: {fresh: bool, platform, python, packages_lock_sha256}, inputs: [{dataset, source_url, retrieved_utc, sha256, vintage | current_vintage_only, rows}], tests: [{name, status: PASS|FAIL|WARN|SKIP, detail}], figures: [{path, sha256}], outputs: [{path, sha256, rows}], gate: {decision: PASS|FAIL|WARN, reasons: [..]}}`. A stage without this file has not passed its gate.

**Fresh-runtime rule (v1.3):** before each gate, run the stage end-to-end in a new runtime: on Colab, *Runtime → Disconnect and delete runtime*, then run all cells from the top; locally, a new venv and kernel via `nbclient`/`papermill`. Inputs come only from configs and checkpointed artifacts, never from earlier in-memory state; the JSON records `runtime.fresh = true`. CI (GitHub Actions) runs `pytest -W error -m "not data"` and each stage's `--smoke` mode on synthetic fixtures on every push. The **before** chart exposes source/raw-data assumptions. The **after** chart shows the transformed output or estimated effect. Include a side-by-side markdown summary with `what changed`, `why`, `possible artifact`, and `decision`. Use identical dates and axes when comparing before/after series. Use interactive Plotly for investigation and Matplotlib PNG for archived publication figures. Include source names, as-of date, sample N, uncertainty where appropriate. Do not interpret a smoothed line as evidence without corresponding raw points.

**Required power/utilities charts (v1.1), by stage:**

| Chart | Stage |
|---|---|
| Utility and infrastructure stock performance normalized to a common start | 01 |
| Utilities vs semiconductor-sector performance | 01 |
| Rolling NVDA correlations with utility/infrastructure series (raw and residualized, with placebo) | 01 |
| Electricity prices, demand and capacity over time | 03b |
| Release-lag and coverage diagnostics | 03b |
| PUSI-F / PUSI-P over time with regimes and disclosure stages | 03b / 05 |
| NVDA predicted returns with vs without power variables | 07 |
| Walk-forward loss differences and coefficient stability | 07 / 09 |
| Negative-control forest plot | 09 |

## 21. Execution ordering, dependencies, and stop rules

```text
00 setup/source audit
  -> 01 prices
  -> 02 macro/fundamentals
  -> 03 resources
  -> 03b power/utilities (04b_power_utilities.ipynb; needs 01 + 02)
  -> 04 news
  -> 05 stress (requires event chronology from 04)
  -> 06 event registry + baseline abnormal returns
  -> 07 H3 ex-ante/conditional counterfactual
  -> 08 H1 panel amplification
  -> 09 H2 interacting stresses
  -> 10 H4 recovery
  -> 11 H5 valuation regimes
  -> 12 integrated report
```

**Dependencies:** stages 01–04 may run independently after setup, but do not compute final pre-event stress until news cutoff is established. H3's 2025-vs-2026 *stress transport* uses H1 estimates and must run after stage 08, even though H3 ex-ante forecasting runs at stage 07. H4 and H5 are secondary and may be deferred when follow-up or fundamentals are insufficient.

**Stop rules:** stop if first disclosure cannot be verified, primary event sample has no usable low/high stress overlap, no viable ex-NVDA peer benchmark, source terms prohibit needed data use, or leakage checks fail. Record and redesign before proceeding. Never silently replace a failed dataset with synthetic observations in the main empirical analysis.

## 22. Suggested timeline and Colab resource budget

- Days 1–3: setup, source audit, preregistration.
- Days 4–7: prices, macro, filings, and validation.
- Days 8–12: resources and news chronology.
- Days 12–16 (v1.1, overlaps): power/utilities data, PUSI, data-quality report (Stage 03b). Overall timeline +4–6 days.
- Days 13–16: labels, event registry, stress indices.
- Days 17–20: baseline factor models and H3.
- Days 21–25: H1/H2 interactions and robustness.
- Days 26–30: H4/H5, contingent on adequate data.
- Days 31–35: clean-run reproducibility, dashboard, report.

This is an engineering estimate, not a guarantee. Historical leadership-event curation and point-in-time news timestamps are the biggest schedule risks. Colab CPU is adequate for tabular models; optional text inference may need a GPU session but must not block the core study.

## 23. First Claude Code prompt (copy verbatim)

> You are the implementation engineer for `nvidia_shock_amplification_colab_implementation_plan.md`. Read the entire plan and companion `state_dependent_shock_amplification_research_plan.md` before writing code. Implement Stage 00 only. Create the repository structure, configuration schemas, Colab setup notebook, pinned-dependency smoke test, source feasibility audit, provenance manifest, synthetic fixtures, and unit tests. Do not fetch full datasets yet and do not invent observations. Generate the required before/after feasibility visualizations, `reports/progress.md`, and stage gate PASS/FAIL report. Run the unit tests and report exact commands and results. Stop after Stage 00 and ask for review before proceeding. Keep all substantive logic in `src/`, and make notebooks thin executable wrappers. Never hardcode credentials or use future information in features.

## 24. Public source entry points to verify during Stage 00

These are starting points, not guarantees of particular API access, licensing, or historical coverage. Check live availability and source terms before use.

- Yahoo Finance: https://finance.yahoo.com/ ; `yfinance` project: https://github.com/ranaroussi/yfinance
- SEC EDGAR APIs: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- FRED API: https://fred.stlouisfed.org/docs/api/fred/
- CBOE volatility index history: https://www.cboe.com/tradable_products/vix/vix_historical_data/
- GDELT project: https://www.gdeltproject.org/ ; DOC API documentation: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
- Nasdaq historical market data landing page: https://www.nasdaq.com/market-activity
- X developer portal (optional): https://developer.x.com/
- (v1.1) Power and electricity sources: see research plan Sections 5.1 and 15. EIA API v2 (free key), FRED/ALFRED, PJM RPM results, LBNL Queued Up, NERC assessments, LBNL 2024 data-center report. IEA *Energy and AI* still needs manual license verification.

## 25. Definition of done

The project is complete when a fresh Colab runtime can execute the full pipeline against a frozen, provenance-logged dataset snapshot; each stage has validated inputs, before/after visualizations, tests, and a gate decision; H1–H6 each receive an evidence-based verdict or a documented inconclusive result; the NVIDIA first-disclosure timeline is independently audited; ex-ante forecasts are not confused with conditional counterfactuals; the report includes uncertainty, placebo results, and limitations; and no result depends on invented or forward-leaked data.

## 26. Change log

### v1.1 (2026-11-13): power, utilities and electricity infrastructure

**Modified sections**

| Section | Change |
|---|---|
| Header | version 1.1 |
| 2 Colab / persistence | `EIA_API_KEY`, `SEC_USER_AGENT` via Colab Secrets; EIA paging and caching; `pdfplumber` for human-verified PDF tables; behaviour when a key is missing |
| Repository contract | `configs/power_sources.yaml`, `configs/power_stress.yaml`; notebook `04b_power_utilities.ipynb`; modules `ingest/eia.py`, `ingest/power_reports.py`, `validate/power.py`, `features/power_stress.py`, `evaluation/incremental_value.py`, `evaluation/negative_controls.py`, `viz/power_utilities.py`; new test files |
| 3 Data inventory | utilities / power-equipment equities row; physical electricity row; schemas `power_physical`, `power_reports`, `power_stress` |
| 4 Quality standards | power/electricity rules: units, release-date joins, no interpolation, `max_age`, outliers, vintages, projections |
| 6 Stage 01 | power/utility tickers, basket versions, before/after charts, tests, gate |
| 7 Stage 02 | seven verified FRED energy series with release-date rules |
| **8b Stage 03b (new)** | power and utilities ingestion, PUSI-F / PUSI-P, data-quality report, charts, tests, PASS/FAIL gate |
| 10 Stage 05 | PUSI as separate RSI components |
| 12 Stage 07 (H3) | M0–M3 walk-forward comparison on the predictive distribution; with/without chart |
| 13 Stage 08 (H1) | PUSI as robustness moderator; exposure contrast |
| 14 Stage 09 (H2) | PUSI interactions, full negative-control battery, power-era feasibility numbers |
| 15–16 Stages 10–11 | PUSI covariate in recovery; AI-power-basket spread for H5 |
| 17 Stage 12 | scorecard column for power incremental value; GitHub Pages publication step |
| 18 Tests | power/utilities data tests; synthetic statistical fixtures |
| 19 Evaluation matrix | power/utilities evaluation applied to all hypotheses |
| 20 Visual protocol | required power charts by stage |
| 21–22 Order / timeline | Stage 03b inserted; +4–6 days |
| 24 Sources | power sources pointer |

**Newly required datasets (verified 2026-11-13):**
- equities: XLU, ^UTY, GRID, ETN, VRT, PWR; placebo XLP (XLV to verify);
- EIA API v2: retail-sales, electric-power-operational-data, rto (EIA-930), operating-generator-capacity;
- FRED: APU000072610, CUSR0000SEHF01, PCU22112211, WPU0543, IPG2211S, CAPUTLG2211S, DHHNGSP;
- PJM BRA clearing prices; LBNL Queued Up; NERC LTRA/SRA/WRA;
- context only: LBNL 2024 data-center report, IEA Energy and AI (pending license check).

**Unavailable (recorded, not replaced):**
- S&P 500 Utilities Index history (proxy XLU);
- an EIA data-center electricity series (does not exist);
- PJM Data Miner, ERCOT API and CAISO OASIS (terms or retention), FERC 714 (not verifiable).

**New tests:**
- missing values preserved;
- duplicate dates/periods;
- release-date alignment;
- frequency conversion via as-of with `max_age`;
- corporate actions and listing-date guards;
- outlier flags without deletion;
- unit conversions;
- look-ahead perturbation;
- projections excluded;
- NVDA excluded from PUSI;
- placebo recipe parity;
- synthetic recovery / null / orthogonalization / DM-size fixtures.

**New visualizations:**
- normalized utility/infrastructure performance;
- utilities vs semis;
- electricity prices, demand and capacity;
- rolling NVDA correlations (raw, residualized, placebo);
- PUSI-F/PUSI-P over time;
- F-vs-P divergence;
- NVDA predicted returns with vs without power variables;
- walk-forward loss differences;
- coefficient stability;
- negative-control forest plot.

### v1.2 (2026-11-13): alignment with the project `CLAUDE.md`

| Topic | Change | Where it lands |
|---|---|---|
| Event time | earliest verified public source; `time_known` flag | Stage 06 event panel; `calendar.map_event` inputs; new test: 8-K filed days after the press release keeps the press-release session |
| Event windows | 0-start windows only for `time_known` events | Stage 08; `configs/preregistration.yaml` |
| Session calendar | NYSE exchange calendar with early closes (new dependency, pinned) | Stage 01; new test: 14:00 ET news on an early-close day maps to the next session |
| Severity | announcement-day codability audit | Stage 06 gate; new table `severity_audit` |
| Point-in-time validity | `current_vintage_only` excluded from confirmatory M0–M3; FRED API key required (Colab Secret `FRED_API_KEY`) | §4, Stage 03b, Stages 07 and 09 (research plan 8.7) |

### v1.3 (2026-11-13): external review incorporated

| Topic | Change | Where it lands |
|---|---|---|
| Severity | categorical event type, separate Holm-adjusted performance and misconduct tests primary; pooled and ordinal secondary | Stage 08; `configs/preregistration.yaml`; power check `scripts/step0b_severity_power.py`, `shockamp.power.simulate_power_categorical` |
| Resilience outcomes | R1, R2 (additional damage, placebo-referenced), R3 | Stages 06, 08, 10 |
| Controls | founder, tenure, planned vs surprise, successor named, size, sector, prior return, as of T; new fields in `event_registry` | Stage 06 (8-K text pass, proxy-filing founder check), Stage 08 |
| Normal-return model | four candidates, placebo-based selection by stress tercile | Stage 06 |
| Validation reports | `stage_##_validation.json` schema; fresh-runtime rule; CI smoke runs | §20, §18 |
| Provisional numbers | Step 0 market numbers reproduced by Stage 01 or explained | Stage 01 gate |

### v1.4 (2026-11-13): second review

| Topic | Change | Where it lands |
|---|---|---|
| H1 interpretation | total slopes vs matched non-event dates; wording rule | Stage 06 (pseudo-event sampler), Stage 08; tests: pseudo dates respect exclusion windows and matching |
| R2 | full sample + `competing_event`, `competing_event_first_session` fields; two sensitivities | Stage 06 event registry, Stage 08 |
| Power | outcome-blind re-run on the real sample before H1 (`shockamp.power`, cluster-aware) | Stage 08 entry gate |
| Consistency | Stage 08 primary estimand restated; `primary_tests` block in the preregistration; `tests/test_prereg.py` | Stage 00 config schema |

### v1.5 (2026-11-13): H6 competitive spillover

| Topic | Change | Where it lands |
|---|---|---|
| H6 | new hypothesis; groups G1–G4 from the leader's 10-K (`configs/tickers.yaml: h6_groups`, with source and accession) | Stage 06 (NVIDIA groups, panel rivals), Stage 09 (H6 panel) |
| Benchmarks | H6 outcome firms never in a benchmark; NVIDIA primary benchmark = SPY + G3; mixed Step 0 basket = sensitivity | Stage 01 baskets, Stage 06 |
| Tests | benchmark-disjointness test (no outcome firm in any benchmark); group assignment loaded from config with source; foreign-listing session mapping | `tests/test_h6_groups.py` |
| Data | Hoberg-Phillips TNIC similarity (to verify: availability, license, coverage end) for the panel substitutability gradient | Stage 00 source audit |
| Visuals | daily AR heatmap by group; group CAR per disclosure; rebound scatter | Stage 06 / 09 |

### v1.6 (2026-11-13): scope tiers

| Topic | Change | Where it lands |
|---|---|---|
| Priority | stages for optional parts (03b, power parts of 07/09, 09 H2, 11 H5, H6 panel) run only after Stage 08 is reported | §21 ordering, per `PLAN.md` §2 |
| Stage 01 | starts with a dated news timeline for the 2026-11-04/05 chip selloff | Stage 01 / 04 |
| Stage 08 | leave-one-stress-episode-out robustness; interpretation rule in `configs/preregistration.yaml` | Stage 08 |

### v1.7 (2026-11-13): vulnerability families

| Topic | Change | Where it lands |
|---|---|---|
| H1 moderator | leadership vulnerability from DEF 14A / 10-K accepted before T−30 (founder, President/COO titles, chair); coverage gate; financial fallback | Stage 06 (extraction, coverage gate), Stage 08 |
| Fixed effects | event-month FE primary; quarter FE + MSI robustness | Stage 08 |
| NVIDIA profile | four families incl. resource/deployment (10-Q exposures, hyperscaler capex releases, dated deployment reports) | Stages 03, 07 |
| Step 1 additions | Nov 4–5 selloff cause; hyperscaler Q3 release times and capex changes; rule-built dated news list Aug 26 → Oct 28 | Stages 01, 04 |
| Consistency | spec card identical to the preregistration; `tests/test_plan_consistency.py`, `tests/test_prereg.py` | CI |

### v1.8 (2026-11-13): user revisions

| Topic | Change | Where it lands |
|---|---|---|
| Naming | LC = leadership concentration; naming rule in the preregistration | Stage 08 reporting |
| Gate | coverage-gate failure halts H1; no automatic fallback | Stage 06 gate |
| Counterfactual | pre-E0 counterfactual A and B required; inputs frozen at the 2026-10-28 close; snapshot hash in `validation.json`; leakage test perturbs everything after the cutoff | Stage 07 |
| Claims | H1a / H1b separate verdicts; labels fixed by term | Stage 08, report |

### v1.9 (2026-11-13): NVIDIA attribution primary (written after NVIDIA's November returns were seen)

| Topic | Change | Where it lands |
|---|---|---|
| Question | N1 primary: leadership-associated residual after non-leadership counterfactuals; exploratory, frozen rules | Stage 07 (steps N-a .. N-f) |
| Counterfactuals | A and B1–B4 required; validation on placebo blocks and rule-selected historical shocks; contamination checks on G3/G4 | Stage 07 |
| Attribution | mutually exclusive session categories from a frozen post-E0 inventory; mixed sessions unresolved | Stage 04 + Stage 07 |
| Inference | same-arrangement placebo; non-overlapping blocks primary (offset 2010-01-04); sensitivities; equivalence within δ for "negligible" | Stage 07, report |
| Families | five NVIDIA families incl. political/regulatory, separately; no thresholds on beta/volatility | Stage 05 |
| Panel | H1a/H1b secondary, unchanged | Stage 08 |
| Workflow | each model reported with data and figures before the next | all stages |
