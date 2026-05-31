## Title

Phase 1 Implementation: Portfolio Data and Summary Foundation

## Description

Build the first implementation-ready slice of the dashboard so the application can ingest the portfolio CSV, classify holdings, compute deterministic summary KPIs, and expose clear unavailable or unsupported states that later chart-analysis phases can safely build on.

## Background Information

The current repository contains analysis artifacts for a local-first Streamlit dashboard but no active application source code. The reviewed feature plan places Phase 1 first because downstream selection, charting, and indicator features depend on a stable portfolio data model and predictable KPI rules. The solution design also introduces `ManualSnapshotPrice` as a Phase 1 CSV contract addition so KPI calculations remain deterministic and user-controllable when live snapshot data is unavailable.

Phase 1 is therefore bootstrap-oriented and must establish both the application structure and the core data-handling behavior. The work item must preserve the agreed v1 scope: US-only support, non-blocking unavailable and unsupported states, session-local usage, and deterministic summary output including snapshot timestamp metadata.

## Plan Step Reference

Analysis Repository: ariesariesdev/dalija-stock-ai
Plan File: /initial_v1/plan.md
Plan Step: Phase 1: Portfolio Data and Summary Foundation

## Work Item Details

Create a Python Streamlit Phase 1 baseline that implements portfolio ingestion and summary logic only.

Implementation scope:

1. Project bootstrap
- Establish the initial Python application structure for a Streamlit-based dashboard.
- Add dependency management and local run or test commands.
- Create initial module boundaries for ingestion, classification, KPI computation, UI presentation, and external market-data access.

2. Portfolio CSV ingestion and normalization
- Load `/source-files/Porfelis20260221.csv` at startup.
- Parse and normalize the existing portfolio fields and support a new optional `ManualSnapshotPrice` column.
- Ignore trailing empty or unnamed columns.
- Treat `ManualSnapshotPrice` as part of the supported Phase 1 CSV contract.
- Validate numeric fields and preserve invalid or missing values as explicit unavailable states rather than hard failures.

3. Holding classification and state handling
- Apply US-only support rules for v1.
- Represent each holding with one of the domain states:
  - `supported_us`
  - `unsupported_symbol`
  - `unavailable_price`
- Keep unsupported holdings visible in counts and state summaries.
- Exclude unsupported and unavailable holdings from total portfolio value.

4. Summary KPI computation
- Compute deterministic summary KPIs:
  - total holdings count
  - unavailable price holdings count
  - unsupported holdings count
  - total portfolio value
  - snapshot timestamp metadata for KPI run context
- Resolve summary snapshot values in this order:
  1. live snapshot provider
  2. `ManualSnapshotPrice`
  3. unavailable state
- Keep `ManualSnapshotPrice` limited to summary KPI fallback only.

5. Summary UI shell
- Build a Streamlit summary view that shows KPI cards and plain-language data-state messaging.
- Keep the UI resilient when unsupported or unavailable holdings exist.
- Do not implement stock charting or indicator controls in this work item.

6. Validation baseline
- Add automated tests for ingestion, fallback handling, classification, deterministic KPI rules, and startup summary flow.
- Add lightweight developer documentation for local run and test commands.

## Design Considerations

- Preserve clear service boundaries between ingestion, classification, KPI logic, UI, and provider integrations.
- Keep calculation rules outside UI code so downstream phases can reuse them safely.
- Treat `ManualSnapshotPrice` as optional for backward compatibility but include it in the expected CSV contract for Phase 1.
- Capture snapshot timestamp metadata with KPI output to support deterministic-run traceability.
- Keep unsupported-symbol visibility transparent without introducing chart-selection behavior in this phase.
- Avoid implementation of Phase 2 and Phase 3 features in this work item.

## Acceptance Criteria

- ACC-01: Portfolio CSV Ingestion And Contract Support

  **GIVEN** the source CSV is present at `/source-files/Porfelis20260221.csv`
  **WHEN** the application starts
  **THEN** valid holdings are loaded into the in-memory portfolio model
  **AND** trailing empty columns do not affect ingestion results
  **AND** the optional `ManualSnapshotPrice` column is supported as part of the Phase 1 contract

- ACC-02: Deterministic Summary KPI Rules

  **GIVEN** loaded holdings with mixed available, unavailable, and unsupported entries
  **WHEN** summary KPIs are computed
  **THEN** total portfolio value includes only supported holdings with available snapshot values
  **AND** unsupported and unavailable holdings are excluded from total portfolio value
  **AND** KPI output includes snapshot timestamp metadata

- ACC-03: Manual Snapshot Fallback Behavior

  **GIVEN** a holding has no live snapshot value but has `ManualSnapshotPrice`
  **WHEN** the summary KPI pipeline runs
  **THEN** `ManualSnapshotPrice` is used as the fallback snapshot value for summary KPI computation
  **AND** if neither source is available the holding remains `unavailable_price`

- ACC-04: Unsupported And Unavailable Transparency

  **GIVEN** one or more holdings are unsupported or unavailable
  **WHEN** the summary UI renders
  **THEN** plain-language state messaging is visible
  **AND** holdings counts remain accurate
  **AND** the application remains usable without crash or blocked flow

- ACC-05: Validation Baseline

  **GIVEN** the Phase 1 implementation is complete
  **WHEN** automated tests are executed
  **THEN** ingestion, fallback, classification, and KPI logic are covered by unit tests
  **AND** at least one integration smoke test validates startup and summary rendering flow

## References

- Analysis repository: ariesariesdev/dalija-stock-ai
- Feature: /initial_v1/feature.md
- Solution design: /initial_v1/solution-design.md
- Acceptance criteria: /initial_v1/acceptance-criteria.md
- Requirements: /initial_v1/requirements.md
- Plan: /initial_v1/plan.md