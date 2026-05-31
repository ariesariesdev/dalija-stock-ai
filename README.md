# dalija-stock-ai

Phase 1 baseline for the Dalija stock tracker and analysis app.

## Phase 1 scope

- Portfolio CSV ingestion from `source-files/Porfelis20260221.csv`
- Summary KPI computation with deterministic timestamp metadata
- `ManualSnapshotPrice` fallback support for summary KPI calculation only
- US-only classification with clear unavailable and unsupported state messaging
- Streamlit summary shell with automated pytest coverage

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run tests:

```bash
pytest -q
```

3. Start the summary application:

```bash
streamlit run app/main.py
```

## Notes

- `ManualSnapshotPrice` is part of the Phase 1 CSV contract, but the app still tolerates older CSV files where the column is missing.
- Summary snapshot resolution order is: live snapshot, `ManualSnapshotPrice`, then unavailable state.
- Phase 1 does not include stock selection, charting, or technical indicators.
