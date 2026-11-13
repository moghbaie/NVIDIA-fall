# NVIDIA-fall: state-dependent shock amplification

Research code testing whether pre-existing market, firm and power/utilities stress amplifies the
stock-market response to adverse leadership news, with NVIDIA's November 2026 leadership
transition as the motivating case and a cross-firm CEO-turnover panel as the primary identification.

- `PLAN.md`: the working execution plan (steps, deviations, feasibility findings)
- `state_dependent_shock_amplification_research_plan.md`: research design (v1.1)
- `nvidia_shock_amplification_colab_implementation_plan.md`: build spec (v1.1)
- `configs/`: preregistration draft, NVIDIA disclosure chronology, tickers, power sources
- `src/shockamp/`: session calendar, point-in-time joins, abnormal returns, power simulation
- `reports/step0/`: Step 0 outputs (source audit, exploratory NVIDIA chart, panel feasibility, H1 power)

## Setup

```bash
uv venv -p 3.12 .venv && uv pip install -e ".[dev]"
.venv/Scripts/python -m pytest -W error          # synthetic tests
.venv/Scripts/python scripts/step0_feasibility.py # needs network + data/raw/ceo_dismissal (see below)
```

Colab: `pip install git+https://github.com/moghbaie/NVIDIA-fall.git`, then run the scripts. Set
`EIA_API_KEY`, `FRED_API_KEY` and `SEC_USER_AGENT` through Colab Secrets.

## Data

Raw data is not committed (`data/` is gitignored). The CEO turnover panel uses Gentry, Harrison,
Quigley & Boivie, *Open Sourced Database for CEO Dismissal* (Zenodo record 23328926, CC-BY-4.0).
Price data come from Yahoo Finance (research prototype; not redistributed).

## Caveats

Allegations reported in the press are attributed to their sources and are not treated as established
facts. Outputs labelled EXPLORATORY or SYNTHETIC are not confirmatory results.
