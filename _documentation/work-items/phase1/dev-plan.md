# Phase 1 Implementation: Portfolio Data and Summary Foundation

**Description:** Establish the initial Python Streamlit codebase that ingests the portfolio CSV, supports ManualSnapshotPrice fallback, computes deterministic summary KPIs, and renders a resilient Phase 1 summary shell with automated validation.

## Goal

Create the production-ready foundation that later stock-selection, charting, and indicator phases can build on safely. This work item matters because it defines the canonical portfolio data model, snapshot resolution rules, and non-blocking state handling that the rest of the dashboard depends on.

## Implementation Steps

- [x] Step 1: Bootstrap the Phase 1 application skeleton
  - **Files:**
    - `app/main.py` - add the Streamlit entrypoint and summary shell orchestration
    - `app/config.py` - centralize default file paths and app constants
    - `app/domain/portfolio_models.py` - define holding, KPI, and state contracts
    - `app/services/interfaces.py` - define provider-facing boundaries
    - `requirements.txt` - confirm runtime and test dependencies
    - `README.md` - add local run and test instructions for the new baseline
  - **Code Changes:**
    - Create the initial `app` package structure and typed domain models
    - Define a snapshot provider protocol and shared configuration constants
    - Establish the top-level summary pipeline entrypoint in `main.py`
  - **What:**
    Build the minimum application skeleton required to support a clean bootstrap implementation. The code should separate domain contracts, service logic, UI orchestration, and external-provider boundaries from the start so later phases do not have to unwind tightly coupled Phase 1 code.
  - **Testing:**
    - Verify imports and package structure load without side effects.
    - Confirm `pytest` test discovery works in the new repository layout.
    - Validates ACC-05 (validation baseline).

- [x] Step 2: Implement ingestion and CSV contract support
  - **Files:**
    - `app/services/portfolio_ingestion.py` - add CSV load, normalization, and numeric coercion behavior
    - `tests/unit/test_ingestion.py` - cover ingestion edge cases and schema handling
    - `tests/fixtures/portfolio_edge_cases.csv` - fixture data for malformed and optional-column scenarios
    - `source-files/Porfelis20260221.csv` - add the optional `ManualSnapshotPrice` column to the Phase 1 source contract if needed
  - **Code Changes:**
    - `load_portfolio_csv(path)`
    - `normalize_columns(dataframe)`
    - `coerce_numeric_fields(dataframe)`
    - `to_holding_records(dataframe)`
  - **What:**
    Implement CSV ingestion that supports the existing portfolio fields plus the optional `ManualSnapshotPrice` column, ignores trailing empty columns, and converts invalid numeric values into explicit unavailable metadata instead of crashing. The ingestion layer must preserve backward compatibility when the new column is absent while treating it as a supported Phase 1 contract.
  - **Testing:**
    - Add a test for trailing empty columns being ignored while required columns remain intact.
    - Add a test for missing `ManualSnapshotPrice` column remaining non-fatal.
    - Add a test for invalid numeric coercion across summary-relevant fields.
    - Validates ACC-01 and ACC-05.

- [x] Step 3: Implement classification and deterministic KPI services
  - **Files:**
    - `app/services/ticker_classification.py` - add US-only holding state rules
    - `app/services/kpi_service.py` - add KPI aggregation, fallback precedence, and timestamp metadata
    - `app/adapters/yfinance_adapter.py` - add snapshot provider adapter boundary
    - `tests/unit/test_ticker_classification.py` - cover supported, unsupported, and unavailable states
    - `tests/unit/test_kpi_service.py` - cover exclusion logic, fallback precedence, and deterministic metadata
  - **Code Changes:**
    - `classify_holding(holding, provider)`
    - `classify_holdings(holdings, provider)`
    - `compute_summary_kpis(holdings, provider)`
    - `format_kpi_value(value)` and timestamp metadata construction
    - Snapshot resolution precedence: live provider -> `ManualSnapshotPrice` -> unavailable
  - **What:**
    Implement the core summary business rules: US-only support, unsupported and unavailable state assignment, exclusion from total value, and deterministic KPI output. `ManualSnapshotPrice` must be limited to summary KPI fallback only, and KPI output must include snapshot timestamp metadata for run traceability.
  - **Testing:**
    - Add a test that unsupported holdings remain counted but excluded from total portfolio value.
    - Add a test that `ManualSnapshotPrice` is used when live snapshot is missing.
    - Add a test that missing both sources results in `unavailable_price`.
    - Add a test that repeated runs with unchanged inputs produce identical KPI outputs and timestamp shape.
    - Validates ACC-02, ACC-03, ACC-04, and ACC-05.

- [x] Step 4: Build the Phase 1 summary UI shell and state messaging
  - **Files:**
    - `app/ui/summary_components.py` - add KPI and state-message presentation helpers
    - `app/main.py` - wire ingestion, classification, KPI, and render flow together
    - `tests/integration/test_startup_smoke.py` - validate startup and summary render pipeline
  - **Code Changes:**
    - `run_summary_pipeline()`
    - `render_summary_shell()`
    - KPI card rendering and plain-language unsupported/unavailable messaging
  - **What:**
    Build a summary-only Streamlit experience that presents KPI cards, snapshot timestamp context, and clear data-state messaging without introducing Phase 2 chart-selection behavior. The UI must stay usable when unsupported or unavailable holdings exist and should remain explicitly scoped to summary concerns only.
  - **Testing:**
    - Add an integration smoke test for startup with the repository CSV.
    - Add a render-flow test confirming KPI values and state messages appear in one pass.
    - Add a regression test that unsupported or unavailable entries do not crash the summary shell.
    - Validates ACC-04 and ACC-05.

- [x] Step 5: Finalize developer readiness and validation baseline
  - **Files:**
    - `README.md` - add final run, test, and Phase 1 limitation guidance
    - `tests/` - refine assertions and shared fixtures as needed
  - **Code Changes:**
    - Document local commands for `streamlit run` and `pytest`
    - Document the Phase 1 scope boundary and ManualSnapshotPrice fallback behavior
    - Execute and stabilize the Phase 1 test suite
  - **What:**
    Finish the developer-facing baseline so implementation can be run, tested, and handed off cleanly. The end state should be a validated local-first summary application with automated coverage over the highest-risk data and KPI rules.
  - **Testing:**
    - Run the full `pytest` suite and confirm all Phase 1 tests pass.
    - Perform one manual local summary run to confirm the app starts and renders without charting features.
    - Validate the README commands against the finished repository layout.
    - Validates ACC-05.
