# CLAUDE.md — State-Dependent Shock Amplification (NVIDIA fall)

Research code: does a firm-specific governance shock (CEO misconduct / dismissal) move the stock
more when market, sector and power-sector stress are already high? Applied to NVIDIA's Oct–Nov 2026
disclosure sequence, tested on a cross-firm panel of CEO departures.

Plans: `PLAN.md` (execution plan, steps and gates), `state_dependent_shock_amplification_research_plan.md`
(research design, hypotheses H1–H5), `nvidia_shock_amplification_colab_implementation_plan.md`
(stages, schemas, tests). Progress and decisions: `reports/progress.md`, `reports/decision_log.md`.

## Non-negotiable rules

### Rule 1: Evaluate with rolling-origin backtesting, without leakage

- The time unit is the **NYSE trading session** (daily). Horizons, embargoes, estimation windows and
  origin steps are counted in sessions on the exchange calendar, never in calendar days. Do not
  hardcode a session count outside `src/shockamp` constants or `configs/`.
- Day boundaries are fixed in **America/New_York**. A session is complete only after its 16:00 ET
  close. Known gap: early closes (13:00) are not modelled yet, so news between 13:00 and 16:00 on
  an early-close day would map to the wrong session; check such events by hand. Intraday data is
  not used.
- At each origin T (end of session T):
  - Training: use only examples whose full target window ends at or before T. An example at session
    t with target window (t + L, t + L + H] is included only if t ≤ T − L − H.
  - Prediction: compute features as of T and predict (T + L, T + L + H].
- Data after T must never be used in training, feature fitting, scaling, imputation, index
  construction (PCA loadings, z-score means/SDs, weights), or hyperparameter tuning for that fold.
  Tune only with a nested time split inside the training window.
- Walk-forward with an expanding training window unless a config says sliding. Report metrics per
  fold and aggregated across folds.

### Rule 2: Build features using only past data (point-in-time correctness)

- Every feature is computed as of origin T. "Lag k" means k sessions before T.
- Rolling and lag features look backward only (shift before rolling; no centered windows, no
  backfill, no forward-fill across a release that had not happened yet).
- Statistics fitted on data are fitted only on each fold's training window.
- **Join external data on its availability timestamp, not its reference period** (`pit.asof_join`).
- Do not interpolate unavailable historical observations. Missing stays missing, with a reason.

Before changing the pipeline: check it against both rules. If it breaks them, explain where, update
the plans, rewrite only the affected code, and keep `tests/test_no_leakage.py` passing.

## How the rules are applied in this project

- **Event timing.** For an event first public at `public_at` (UTC): before 16:00 ET on a session →
  event session = that session; after the close or on a non-session day → next session. Origin
  T = the last complete session before `public_at` (`calendar.map_event`). Events known only by date
  (`time_known=False`) map to the first session on/after that date, and their windows must start
  at −1 to absorb the timing ambiguity.
- **Abnormal returns.** Market model fitted on sessions [−252, −31] relative to the event session,
  min 120 obs (`returns.fit_market_model`); nothing at or after −30 enters the fit. Stress features
  are measured as of T, i.e. before the event window.
- **Availability timestamps** (when a value may first be used):

  | Source | Reference time | Available at |
  |---|---|---|
  | Prices / returns (Yahoo adjusted closes) | session d | close of d (16:00 ET) |
  | 8-K filings | event | EDGAR acceptance timestamp |
  | News reports | event | first verifiable publication timestamp |
  | FRED / ALFRED series | observation period | vintage `realtime_start`; if no vintage, official release date |
  | EIA API v2 | month/week | publication date of that release (no vintages: latest revised values, documented limitation) |
  | PJM BRA, LBNL, NERC reports | report | publication date of the report |
  | Gentry et al. departure coding | event | event characteristic; must be codable from announcement-day information |
  | Exchange calendar | any | always (deterministic) |

- **Locked confirmatory test.** `configs/preregistration.yaml` is frozen (after user sign-off) before
  any H1 estimate is computed. Later changes go in `reports/decision_log.md` and mark affected
  results exploratory. The NVIDIA sequence is an application of the frozen model, not a tuning set.
- **Power and Utilities Stress Index (PUSI).** Financial (PUSI-F) and physical (PUSI-P) families
  stay separate; PUSI-X (projections) is context only, never a model input. Rising utility prices are
  not assumed to mean stress. Incremental value is judged only by walk-forward M0–M3 comparisons and
  the negative controls in research plan §8.7–8.8.
- **Code.** `shockamp.calendar` (sessions, event mapping), `shockamp.pit` (as-of joins,
  `assert_available`), `shockamp.returns` (market model, AR/CAR), `shockamp.power` (simulated H1
  power). `tests/test_no_leakage.py` perturbs all data after T and requires fits and features to be
  unchanged.

## Other conventions

- Raw data, runs and model outputs stay out of git (`data/`, `runs/`). Figures and small summary
  tables go in `reports/<step>/`.
- Show results with figures after each step and agree on the next step with the user before starting
  it. Do not publish to GitHub Pages until the user approves.
- Before finishing: `ruff format`, `ruff check`, `mypy src`, `pytest -W error` (plus `-m data`).
- Commit and push to `origin/main` only when the user asks.
- Secrets (`EIA_API_KEY`, `FRED_API_KEY`, `SEC_USER_AGENT`) come from env vars / Colab Secrets,
  never from files in git.
- Wording: label simulated outcomes as synthetic; label exploratory results as exploratory;
  attribute allegations to their source ("reported by", "alleged"), never state them as fact;
  never call a proxy (e.g. XLU for S&P 500 Utilities) the original series.

## Commands

```bash
uv pip install -e ".[dev]"
.venv/Scripts/python -m pytest -W error -m "not data"   # synthetic tests
.venv/Scripts/python -m pytest -m data                  # network / real-data tests
.venv/Scripts/python scripts/step0_feasibility.py       # Step 0 audit + figures -> reports/step0/
```
