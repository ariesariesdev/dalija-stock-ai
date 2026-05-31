## Title

Phase 3 Implementation: Indicator Controls and End-to-End Validation

## Description

Complete the local v1 dashboard by adding technical indicator controls on top of the existing Phase 2 selector and candlestick chart flow, then lock in release-readiness validation for the full summary-to-chart experience.

## Background Information

Phase 2 already delivers the single-page summary, ticker selection, historical OHLCV retrieval, JSON fallback handling, and candlestick chart rendering. What remains from the plan is the analysis layer itself: indicator controls, default indicator behavior, and a validation baseline that gives confidence in the final local release.

The analysis artifacts define Phase 3 scope narrowly:
- add indicator controls for SMA, EMA, Bollinger Bands, Fibonacci retracement, and RSI
- enable `SMA (20)` and `RSI (14)` by default on first load
- preserve the existing unified one-page Streamlit flow and responsiveness targets
- validate the full dashboard behavior without turning this phase into a broad refactor

Decisions confirmed during the required grill-me step:
- control model: explicit per-indicator toggles with fixed default parameters
- chart layout: overlays remain on the main candlestick chart, RSI renders in a lower subplot
- Fibonacci source range: compute from the loaded 1-year dataset, not from dynamic viewport events
- release validation baseline: deterministic automated tests plus a concise manual release checklist

## Plan Step Reference

Analysis Repository: ariesariesdev/dalija-stock-ai
Plan File: /initial_v1/plan.md
Plan Step: Phase 3: Indicator Controls and End-to-End Validation

## Work Item Details

Extend the existing Streamlit application to support the following Phase 3 capabilities:

### 1. Indicator Computation Service

Create `app/services/indicator_service.py` that accepts normalized OHLCV data and returns indicator-ready series for the Phase 3 charting flow.

Implementation scope:
- Compute `SMA (20)` from `Close` values.
- Compute `EMA (20)` from `Close` values.
- Compute Bollinger Bands using period `20` and standard deviation multiplier `2`.
- Compute `RSI (14)` as a dedicated oscillator series.
- Compute Fibonacci retracement levels from the full loaded 1-year high/low range of the selected ticker dataset.
- Return results in a deterministic structure that chart rendering code can consume without embedding financial math inside UI helpers.
- Treat empty or too-short OHLCV input as a non-fatal condition by returning only the indicators that can be computed, or an empty indicator payload when nothing valid can be produced.

Library rule:
- Use `pandas-ta` if it imports cleanly in the project environment.
- If library compatibility becomes an issue, implement formula-equivalent calculations inside the service without changing the public service contract.

### 2. Indicator Control UI

Create `app/ui/indicator_controls.py` that renders the Phase 3 control surface for a selected ticker.

Required controls:
- `SMA (20)` toggle
- `EMA (20)` toggle
- `Bollinger Bands (20, 2)` toggle
- `Fibonacci Retracement` toggle
- `RSI (14)` toggle

Behavior rules:
- On first app load, `SMA (20)` and `RSI (14)` are enabled by default.
- `EMA`, `Bollinger Bands`, and `Fibonacci Retracement` are disabled by default.
- Controls use fixed parameters in the UI for v1; no user-editable period or multiplier inputs are included in this work item.
- Toggle changes update the chart in the same single-page flow.

Use explicit session-state keys to avoid collisions with Phase 2 state. Recommended keys:
- `phase3_indicator_sma20`
- `phase3_indicator_ema20`
- `phase3_indicator_bollinger_20_2`
- `phase3_indicator_fibonacci`
- `phase3_indicator_rsi14`

### 3. Chart Rendering Extension

Update `app/ui/chart_components.py` so the chart layer can render indicator overlays and an RSI subplot while preserving existing candlestick behavior.

Required changes:
- Keep candlestick rendering as the base series.
- Add SMA, EMA, and Bollinger Band traces as overlays on the main chart.
- Add Fibonacci retracement lines or shapes to the main chart using levels derived from the 1-year dataset range.
- Render RSI in a lower subplot using Plotly subplots when RSI is enabled.
- Preserve existing interactivity expectations: hover, zoom, pan, and responsive container width.
- Keep the unavailable-data path non-blocking and compatible with the existing `render_chart_error` behavior.

Implementation note:
- When RSI is disabled, the chart may render as a single panel.
- When RSI is enabled, use a two-row Plotly figure so the price chart remains readable.

### 4. Unified Flow Orchestration in `main.py`

Update `app/main.py` so indicator controls participate in the existing Phase 2 selection flow without introducing page navigation or a separate screen.

Required orchestration:
- After a ticker is selected and OHLCV data is available, render the Phase 3 indicator controls above the chart region.
- Apply default indicator state on first use of the session.
- Build the indicator payload from control state and pass it through the new indicator service before chart rendering.
- Keep summary KPIs visible above the selector and chart.
- Preserve existing Phase 2 fallback behavior when OHLCV data is unavailable.

Optional cleanup allowed within this work item:
- Update outdated Phase 1/Phase 2-only page labels if needed so the UI reflects the final dashboard scope.

### 5. Deterministic Validation and Release Readiness

Add automated coverage for indicator calculations, indicator control defaults, and the final chart orchestration path.

Required test additions:
- `tests/unit/test_indicator_service.py`
  - validates SMA, EMA, Bollinger, RSI, and Fibonacci output presence for deterministic fixture data
  - validates short or empty OHLCV input remains non-fatal
- `tests/unit/test_indicator_controls.py`
  - validates default toggle state and session-state behavior using a fake Streamlit facade
- update `tests/unit/test_chart_components.py`
  - validates indicator overlays and RSI subplot traces are added when enabled
  - validates base candlestick rendering still works when indicators are disabled
- update `tests/integration/test_selection_chart_smoke.py` or add a dedicated Phase 3 smoke test
  - validates summary -> selector -> indicator controls -> chart flow works in one offline run
  - validates default indicators are applied on first load

Manual release checklist to document in `dev-notes.md`:
- select supported ticker -> candlestick + default SMA/RSI render
- toggle EMA, Bollinger, Fibonacci on/off -> chart updates without breaking base chart
- switch between multiple supported tickers -> chart and indicators refresh for the new symbol
- unavailable historical data path still shows warning and keeps summary usable
- repeated same-ticker selection remains responsive in cached path

## Design Considerations

- Keep financial calculations in a service module, not inside `main.py` or Plotly helper code.
- Preserve Phase 2 session-state keys and add Phase 3 keys alongside them rather than replacing them.
- Keep the fixed-parameter control model for v1 to reduce UI and testing complexity.
- Do not add viewport-driven recalculation logic for Fibonacci in this work item.
- Do not broaden the data provider boundary or rewrite the existing historical data service unless directly required for indicator inputs.
- If `pandas-ta` import behavior is unstable on the target Python version, contain the workaround inside the indicator service rather than spreading conditional logic across the app.

## Acceptance Criteria

- ACC-01: Indicator Controls Render For Selected Ticker

  **GIVEN** a supported ticker is selected and historical OHLCV data is available
  **WHEN** the analysis section renders
  **THEN** indicator toggles for `SMA (20)`, `EMA (20)`, `Bollinger Bands`, `Fibonacci Retracement`, and `RSI (14)` are visible
  **AND** the user can toggle them on or off in the same page flow

- ACC-02: Default Indicator State On First Load

  **GIVEN** the user has not changed indicator settings in the current session
  **WHEN** a chart first renders for a selected ticker
  **THEN** `SMA (20)` and `RSI (14)` are enabled by default
  **AND** all other indicators are disabled by default

- ACC-03: Overlay Indicators Render Correctly

  **GIVEN** indicator toggles are enabled for SMA, EMA, Bollinger Bands, or Fibonacci Retracement
  **WHEN** the chart renders
  **THEN** the selected overlays appear on the main candlestick chart
  **AND** the base price chart remains readable and interactive

- ACC-04: RSI Renders As Separate Analysis Panel

  **GIVEN** `RSI (14)` is enabled
  **WHEN** the chart renders
  **THEN** RSI appears in a lower subplot beneath the main candlestick chart
  **AND** the main chart remains visible above it

- ACC-05: Fibonacci Levels Use The Loaded 1-Year Dataset Range

  **GIVEN** Fibonacci Retracement is enabled
  **WHEN** indicator data is computed
  **THEN** retracement levels are derived from the selected ticker's loaded 1-year high and low values
  **AND** they do not depend on viewport event handling

- ACC-06: Unified Flow And Error Resilience Remain Intact

  **GIVEN** the summary dashboard is open
  **WHEN** the user moves from summary to selection to indicator analysis
  **THEN** the experience remains on one page without multi-page navigation
  **AND** if historical data is unavailable the existing plain-language error flow still applies without breaking the app

- ACC-07: Validation Baseline Supports Local v1 Release

  **GIVEN** Phase 3 implementation is complete
  **WHEN** automated tests are executed
  **THEN** indicator calculations, control defaults, and end-to-end chart orchestration are covered by deterministic unit and integration tests
  **AND** a manual release checklist exists for responsiveness and repeated-selection validation

## References

- Analysis repository: ariesariesdev/dalija-stock-ai
- Feature: /initial_v1/feature.md
- Solution design: /initial_v1/solution-design.md
- Acceptance criteria: /initial_v1/acceptance-criteria.md
- Requirements: /initial_v1/requirements.md
- Plan: /initial_v1/plan.md