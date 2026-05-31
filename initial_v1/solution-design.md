# Solution Design

## Overview

This design defines an architecture-level solution for a single-flow Streamlit dashboard that moves from portfolio summary to selected-stock analysis. The key decisions are deterministic ingestion, explicit unavailable/unsupported handling, US-only enforcement, and modular service boundaries for data acquisition, indicator computation, and visualization. A manually maintained fallback column, `ManualSnapshotPrice`, is used for summary KPI fallback only when live snapshot data is unavailable.

## Context

The feature, requirements, and acceptance criteria establish a v1 scope centered on portfolio-level KPIs, stock selection, charting, and technical indicators for US tickers only. Existing analysis documents define:

- Source portfolio baseline in [initial_v1/feature.md](initial_v1/feature.md)
- Functional and non-functional requirements in [initial_v1/requirements.md](initial_v1/requirements.md)
- Validation rules in [initial_v1/acceptance-criteria.md](initial_v1/acceptance-criteria.md)
- Prior technical direction in [initial_v1/techincal-notes.md](initial_v1/techincal-notes.md)

No product-overview, product-architecture, or product-glossary artifacts were found for this feature scope, so this design is anchored to the available feature artifacts and clarified review decisions.

## Architectural Flow

1. Ingestion and normalization
- Load portfolio CSV at startup.
- Normalize required columns and domain states.
- Include `ManualSnapshotPrice` as a controllable fallback source.

2. Classification and summary pipeline
- Apply US-only symbol support policy.
- Keep unsupported symbols visible in UX with plain-language reason and provide a user toggle to hide/show unsupported entries in selector views.
- Resolve snapshot source in order: live snapshot provider, then `ManualSnapshotPrice`, then unavailable state.
- Compute deterministic KPIs from eligible holdings only.
- Persist snapshot timestamp metadata with KPI output for deterministic run traceability.

3. Selection and chart analysis pipeline
- Provide fast ticker search/selection over in-scope holdings.
- Fetch 1-year OHLCV for valid selected symbols.
- Render interactive chart with overlays and indicator controls.
- Apply default indicators (`SMA 20`, `RSI 14`) on first load.

4. UX resilience and observability
- Keep unavailable/unsupported states non-blocking.
- Present explicit state messaging in summary and selection contexts.
- Emit structured diagnostic logging around data fetch, classification, KPI generation, and chart rendering.

## Detailed Design

The solution is organized into five architecture layers:

1. Presentation layer
- Streamlit UI shell for summary cards, selector, and chart region.
- State messaging components for unavailable/unsupported conditions.
- Indicator control surface for overlays and default state application.

2. Application orchestration layer
- Coordinated flow for startup ingestion, classification, KPI aggregation, selection updates, and chart refresh.
- Central session-state model to preserve selected ticker, indicator toggles, hide-unsupported toggle, and chart window defaults.

3. Domain services layer
- Ingestion service for schema normalization and value coercion.
- Classification service for US-only policy and unsupported-state assignment.
- KPI service for deterministic aggregate values and exclusion logic.
- KPI metadata service for snapshot timestamp capture.
- Indicator service for SMA/EMA, Bollinger Bands, Fibonacci, and RSI generation.

4. Integration layer
- Market data adapter to Yahoo Finance for snapshot and historical OHLCV retrieval.
- Resilience strategy for partial data conditions and transient provider failures.

5. Data contract layer
- CSV schema contract including existing fields plus `ManualSnapshotPrice`.
- Domain status contract for `supported_us`, `unsupported_symbol`, and `unavailable_price`.
- KPI metadata contract including deterministic snapshot timestamp.

Traceability intent:
- FR-01 to FR-04: ingestion, KPI, and selection architecture.
- FR-05 to FR-08: chart and indicator architecture.
- FR-09 and NFR-02: unsupported/unavailable visibility and non-blocking UX.
- NFR-01, NFR-03, NFR-04: responsiveness, reliability, and deterministic computation boundaries.

## Affected Components

| Component | Repository | Change Type | Requirements |
|-----------|-----------|-------------|--------------|
| Portfolio CSV contract | ariesariesdev/dalija-stock-ai | Extended | FR-01, FR-02, FR-03, NFR-04 |
| Summary pipeline (ingest/classify/KPI) | ariesariesdev/dalija-stock-ai | Modified | FR-01, FR-02, FR-03, FR-09 |
| Stock selector workflow | ariesariesdev/dalija-stock-ai | Modified | FR-04, FR-09, FR-10, NFR-02 |
| Chart rendering workflow | ariesariesdev/dalija-stock-ai | Extended | FR-05, FR-06, DR-02 |
| Indicator orchestration | ariesariesdev/dalija-stock-ai | New | FR-07, FR-08, DR-03 |
| Market data integration boundary | ariesariesdev/dalija-stock-ai | Modified | DR-01, NFR-01, NFR-03 |
| Runtime logging/diagnostics | ariesariesdev/dalija-stock-ai | New | NFR-02, NFR-03 |
| KPI metadata output | ariesariesdev/dalija-stock-ai | New | NFR-04 |

## New Components

1. Manual fallback price contract
- Purpose: provide controlled continuity for KPI computations when live snapshot retrieval is unavailable.
- Integration: adds `ManualSnapshotPrice` column to ingestion schema and summary computation precedence rules.
- Interface: nullable numeric field per holding row.
- Behavior: used only for summary KPI fallback when live snapshot is unavailable; if absent, holding remains unavailable for value calculation.

2. Indicator orchestration service
- Purpose: centralize indicator generation and default-state behavior.
- Integration: consumes historical price series and publishes overlay-ready datasets to chart rendering.
- Interface: indicator request contract (enabled flags, windows/parameters, visible range).
- Behavior: supports SMA/EMA, Bollinger Bands, Fibonacci retracement from visible high/low, and RSI.

3. State messaging subsystem
- Purpose: unify unavailable/unsupported explanations across summary and stock-selection views.
- Integration: receives domain status outputs from classification and chart availability checks.
- Interface: message model with reason code and user-facing label.
- Behavior: keeps interaction flow non-blocking while preserving transparency.

4. Unsupported visibility toggle component
- Purpose: allow users to hide/show unsupported symbols while preserving transparent default visibility.
- Integration: consumes classification output and applies client-side filtering in selector views.
- Interface: boolean toggle state in session model.
- Behavior: default is visible; when enabled, unsupported rows are hidden from selectors but still counted in summary state metrics.

5. KPI snapshot metadata component
- Purpose: preserve deterministic-run context by exposing snapshot timestamp with KPI payload.
- Integration: attached to KPI response model and displayed in summary metadata area.
- Interface: timestamp field populated during snapshot resolution pass.
- Behavior: reflects the effective snapshot evaluation moment used by KPI computation.

## Data Changes

- Extend CSV domain contract to include `ManualSnapshotPrice`.
- Preserve existing required fields (`FullTicker`, `SharesAmount`, `PurchasePrice`, `ClosingPrice31_12_2025`).
- Introduce snapshot resolution precedence for summary use cases:
  1. live provider snapshot
  2. `ManualSnapshotPrice`
  3. unavailable state
- Add KPI metadata output field for `snapshot_timestamp` to support deterministic-run traceability.
- No relational database changes are proposed in v1.
- Backward compatibility note: if `ManualSnapshotPrice` is absent, ingestion should treat it as optional and continue with unavailable handling.

## Integration Points

- Yahoo Finance (`yfinance`) for snapshot and 1-year historical OHLCV retrieval.
- Plotly rendering surface embedded in Streamlit for interactive chart behavior.
- Indicator computation library (`pandas-ta` or formula-equivalent implementation) for overlays and RSI.

## Security Considerations

- Per user clarification, CIM integration is not required for this local v1 scope.
- Scope remains single-user local usage without authentication/authorization features.
- Sensitive data handling is limited to local portfolio file content.
- Future hardening should include auth integration and stricter external-call controls if scope expands beyond local use.

## Deployment Considerations

- Primary target is local execution for v1 validation.
- No feature-toggle or licensing gate is proposed for the current local scope.
- Deployment automation beyond local run commands is out of scope in this phase.
- If later moved to shared hosting, introduce feature gating and release controls before multi-user rollout.

## Risks & Open Questions

- **RISK-001**: Manual fallback values can drift from market reality, affecting decision confidence if not maintained regularly.
- **RISK-002**: External market data availability/rate limits can impact responsiveness and reliability targets.
- **RISK-003**: Indicator calculation consistency can vary if mixed formula sources are introduced.
- **OPEN-001**: Should the unsupported visibility toggle preference persist across app restarts or remain session-only in v1?

## GIT Repositories Referred To

- github : ariesariesdev/dalija-stock-ai
- azuredevops : none identified for this scope

## Glossary Terms Used

| Term | Glossary | Status | Description |
|------|----------|--------|-------------|
| ManualSnapshotPrice | product | new | Manually maintained per-row fallback value used when live snapshot retrieval is unavailable. |
| unsupported_symbol | product | existing | Domain state for symbols outside supported US-only scope or provider support. |
| unavailable_price | product | existing | Domain state where no usable snapshot is available after fallback evaluation. |
| unified user flow | product | existing | Single dashboard interaction path from summary to selected-stock analysis without page-level navigation. |

## Related Documents / Further Reading

- [initial_v1/feature.md](initial_v1/feature.md)
- [initial_v1/requirements.md](initial_v1/requirements.md)
- [initial_v1/acceptance-criteria.md](initial_v1/acceptance-criteria.md)
- [initial_v1/research.md](initial_v1/research.md)
- [initial_v1/techincal-notes.md](initial_v1/techincal-notes.md)
