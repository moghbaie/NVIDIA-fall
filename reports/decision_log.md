# Decision log

- 2026-11-13: Deviations D1–D10 from the source plans recorded in PLAN.md §1.
- 2026-11-13: NVIDIA outcome inspected (exploratory AR table) before preregistration; the
  preregistration binds the panel only (D9).
- 2026-11-13: The disclosure sequence starts with the NYT report on 2026-10-29 (E0), not the
  resignation; the 8-K acceptance time for E2 is 2026-11-12 13:52:41 UTC (pre-market).
- 2026-11-13 (user decision): Power and utilities stress (PUSI-F / PUSI-P) added as a separate RSI
  component; overrides PLAN.md D5 for power.
- 2026-11-13: S&P 500 Utilities Index history is unavailable from free sources; XLU is the proxy.
- 2026-11-13 (user request): Final results to be published on GitHub Pages after user approval.
- 2026-11-13 (user request): `CLAUDE.md` rewritten for this project; plans aligned as v1.2
  (PLAN.md D11–D15): earliest-public event time; 0-start windows only for time-known events;
  severity codability audit; `current_vintage_only` series excluded from the confirmatory
  incremental-value test (FRED API key now required); NYSE calendar with early closes.
- 2026-11-13 (external review): plans v1.3. Primary H1 uses categorical event type with separate
  Holm-adjusted performance x stress and misconduct x stress tests (pooled contrast and ordinal
  score secondary; Step 0b synthetic power check showed both fail if only misconduct amplifies). Resilience
  outcomes R1-R3, controls as of T, per-step validation.json + fresh-runtime rule, normal-return
  model comparison on placebo events. Step 0 market numbers provisional. Preregistration still draft.

- 2026-11-13 (second review): plans v1.4. Total stress slopes per type vs matched non-event dates
  with a wording rule (relative vs absolute amplification); R2 on the full sample with a
  competing-event indicator and sensitivities; outcome-blind power re-run on the real sample
  (Step 4b) before freezing the preregistration. Stale "ordinal is primary" text corrected.

- 2026-11-13 (user request): H6 competitive spillover added (plans v1.5). Groups fixed from NVIDIA's
  FY2026 10-K; no H6 outcome firm in any benchmark; NVIDIA primary benchmark = SPY + G3 (Step 0
  mixed basket demoted to sensitivity; it inflated the E1 CAR by about 1.5 pp). NVIDIA-sequence H6
  results are hypothesis-generating because the Nov 12 rival moves were seen first.

- 2026-11-13 (user decision): plan v1.6, simplified around H1 (PLAN.md D25). H1 is the only
  confirmatory hypothesis; secondary = H3 description, H6 NVIDIA description, H4, R2; optional =
  power/utilities index, H2, H5, H6 panel, H6b, NVIDIA counterfactuals A/B. Two primary tests kept,
  with the "more negative or less positive" reading for performance dismissals. Step 1 starts with
  the cause of the 2026-11-04/05 chip selloff, since NVIDIA E1 stress (VIX 82nd pct) follows it and
  E0 stress was low (VIX 43rd pct).
- 2026-11-13 (user decision): plans v1.7 (PLAN.md D26). H1 primary moderator = leadership
  vulnerability (founder CEO, no designated successor, CEO-chair duality; filings before T-30),
  event-month FE, coverage gate (80% overall / 70% misconduct) with financial vulnerability as the
  declared fallback. Reservation recorded: founder status also measures shock size, so the claim
  "pre-existing vulnerability amplifies" requires the LV-without-founder result to agree. Financial
  vulnerability and MSI secondary; volatility a control. NVIDIA: four families incl.
  resource/deployment, never combined. Price-based NVIDIA measures at E0 were inspected before this
  decision (VIX 43rd pct; 12-month return and idiosyncratic volatility ~31st pct of own history).
  Push only after spec-card consistency tests pass (user condition).
- 2026-11-13 (user revisions): plans v1.8 (PLAN.md D27). Primary moderator renamed "leadership
  concentration" (LC) until validated as vulnerability (naming rule in the preregistration).
  Automatic financial fallback removed: a failed coverage gate halts H1 for an outcome-blind joint
  decision. Frozen pre-E0 counterfactual (cutoff 2026-10-28 close; A unconditional bootstrap /
  EWMA-t, B factor model on realized SPY and G3) required; specified after NVIDIA's path was seen,
  so labelled exploratory. H1a (misconduct x LC, adverse-news amplification) separated from H1b
  (performance x LC, attenuated replacement benefit); labels fixed by term.
