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
- 2026-11-13 (Step 1a/b): Nov 4-5 chip selloff attributed (secondary sources, SEC timestamps) to
  AMD/Qualcomm results, memory shortage, AI-capex doubts and post-midterm worries; no link to the
  Oct 29 NVIDIA report found, so stress at E1 is treated as pre-existing (provisional). E0 sessions
  coincide with Alphabet/Microsoft (Oct 29) and Amazon/Intel (Oct 30) results; NVDA AR ~0 on both.
  Bug fixed: YAML parsed ticker ON as boolean; quoted and tested. env.secrets added to .gitignore.
- 2026-11-13 (Step 1c-1f): pre-E0 news inventory (31 items) labelled and frozen (sha256 a1ab73d3...,
  18:45 UTC) before reactions; labels for items dated 2026-10-20 onward are not blind (fig6 seen).
  Only the two post-earnings sessions fall outside +-1.96 sigma. Overlap bug (same-day SEC releases)
  fixed after freezing; labels untouched. Step 1(f): AMD and INTC contaminated by own news on
  2026-11-12, AVGO unclear, MRVL clean; G1 - G3 recomputed (exploratory). Removal reports public by
  06:40 ET on 2026-11-12; event session unchanged.
- 2026-11-13 (user decision, AFTER NVIDIA's Oct-Nov returns were seen): plans v1.9 (PLAN.md D28).
  Primary question becomes NVIDIA attribution (N1): how much of the 2026-10-29 .. 2026-11-16 decline
  is consistent with independently observable non-leadership factors, and whether a material
  additional leadership-associated return remains. Exploratory with frozen rules; no causal
  percentages. Counterfactuals A and B1-B4 required with historical validation and contamination
  checks; mutually exclusive session categories, mixed leadership/other sessions unresolved;
  leadership-only and leadership-inclusive overlap scenarios; empirical placebo inference with the
  same session arrangement (non-overlapping 13-session blocks from 2010-01-04 primary; all-origin,
  regime-matched, earnings/extraordinary-excluded and peer-firm sensitivities); model-dependent
  uncertainty intervals; delta = median absolute placebo sum (ordinary unexplained variation, not an
  economic threshold); equivalence required for "negligible". N2 assesses five families separately
  (political/regulatory added), no beta/volatility thresholds. Panel H1a/H1b kept as secondary
  statistical study, unchanged. Numbering N1-N4 / H1a, H1b, H4-H6 with a crosswalk. Prereg keys
  primary_* renamed panel_*. Completed Step 0-1 work and results unchanged.
- 2026-11-13 (user instruction): report data, figures and results after each step or model before
  starting the next; do not build ahead.
