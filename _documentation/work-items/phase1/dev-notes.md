## Technical Notes

### Source-Code Baseline Observation
- The current repository has analysis artifacts and dependency declarations but no active application source tree under the workspace root.
- Phase 1 must therefore establish the initial project layout as part of the work item rather than extending existing modules.

### Suggested Initial Module Layout
- `app/main.py` - Streamlit entrypoint for the summary shell.
- `app/config.py` - central file paths and application constants.
- `app/domain/portfolio_models.py` - holding, KPI, and state models.
- `app/services/portfolio_ingestion.py` - CSV parsing, normalization, and numeric validation.
- `app/services/ticker_classification.py` - v1 US-only classification rules.
- `app/services/kpi_service.py` - deterministic KPI aggregation and snapshot timestamp metadata.
- `app/services/interfaces.py` - provider protocol boundaries.
- `app/adapters/yfinance_adapter.py` - snapshot provider adapter.
- `app/ui/summary_components.py` - KPI and state rendering helpers.
- `tests/unit/` and `tests/integration/` - automated validation locations.

### Data-Contract Notes
- `ManualSnapshotPrice` should be treated as optional but first-class in the Phase 1 schema.
- Backward compatibility rule: missing `ManualSnapshotPrice` column must not break startup.
- Numeric coercion should be explicit for `SharesAmount`, `PurchasePrice`, `ClosingPrice31_12_2025`, and `ManualSnapshotPrice`.
- The CSV may still contain trailing empty columns that must be ignored safely.

### State Model Guidance
- `supported_us`: holding is in-scope and has a usable summary snapshot price.
- `unsupported_symbol`: holding is outside the supported v1 symbol policy.
- `unavailable_price`: holding is supported but no usable summary snapshot source is available.

### Snapshot Resolution Rule
1. live snapshot provider
2. `ManualSnapshotPrice`
3. unavailable state

### Determinism Guidance
- Centralize rounding and formatting rules in one service-level function.
- Include snapshot timestamp metadata in the KPI output object rather than scattered UI state.
- Use provider fakes in tests to avoid network dependence.

### Test Guidance
- Add unit coverage for missing optional column, invalid numeric values, and fallback precedence.
- Add regression coverage that unsupported holdings remain counted but excluded from value totals.
- Add one integration smoke test for startup-to-summary render flow with no network calls.

### Non-Goals For This Work Item
- No stock-selection UX.
- No chart rendering.
- No technical indicators.
- No persistence beyond local runtime.