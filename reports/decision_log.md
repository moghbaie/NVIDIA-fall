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
