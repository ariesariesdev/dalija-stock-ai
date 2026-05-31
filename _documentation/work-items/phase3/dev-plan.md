# Phase 3 Implementation: Indicator Controls and End-to-End Validation

**Description:** Add fixed-parameter technical indicator controls, extend the chart to render overlays and RSI analysis, and complete deterministic end-to-end validation for the local v1 dashboard.

## Goal

Implement the final Phase 3 slice on top of the existing Phase 2 flow so users can move from summary to ticker selection to technical analysis in one Streamlit page. The plan keeps calculation logic isolated in a dedicated service, limits UI scope to fixed toggles, and validates the final release path with deterministic unit and integration tests.

## Implementation Steps

- [x] Step 1: Add Indicator Data Contracts and Computation Service
  - **Files:**
    - `app/services/indicator_service.py` - create indicator settings or payload types and the computation entrypoint.
    - `app/domain/portfolio_models.py` (optional) - add shared dataclasses only if the indicator contract needs to be reused outside the service module.
    - `requirements.txt` - confirm `pandas-ta` remains declared for the preferred implementation path.
  - **Code Changes:**
    - `build_indicator_payload` - create the main service entrypoint for SMA, EMA, Bollinger Bands, Fibonacci, and RSI.
    - `IndicatorSettings` - represent the fixed on or off indicator choices for Phase 3.
    - `IndicatorPayload` - return overlay series, RSI series, and Fibonacci level definitions in a chart-ready structure.
    - Internal helper methods for `SMA (20)`, `EMA (20)`, `Bollinger Bands (20, 2)`, `RSI (14)`, and Fibonacci level calculation from the loaded 1-year range.
  - **What:**
    - Add a dedicated indicator service so financial calculations stay out of `main.py` and Plotly rendering code. Keep one stable contract that can use `pandas-ta` when available, while containing any formula-equivalent fallback inside the same service to avoid leaking dependency risk across the app.
    - Ensure empty or too-short OHLCV inputs remain non-fatal and return a deterministic empty or partial payload rather than raising.
  - **Testing:**
    - Unit: deterministic OHLCV fixture produces expected payload sections for SMA, EMA, Bollinger, RSI, and Fibonacci (ACC-03: Overlay Indicators Render Correctly, ACC-04: RSI Renders As Separate Analysis Panel, ACC-05: Fibonacci Levels Use The Loaded 1-Year Dataset Range).
    - Unit: short OHLCV input returns non-fatal empty or partial outputs without exceptions (ACC-07: Validation Baseline Supports Local v1 Release).
    - Unit: service contract remains stable whether the implementation path uses `pandas-ta` or internal formulas (ACC-07).

- [x] Step 2: Build Indicator Controls UI and Session-State Wiring
  - **Files:**
    - `app/ui/indicator_controls.py` - create the Phase 3 control renderer.
    - `app/main.py` - initialize default indicator state and pass settings into the chart flow.
  - **Code Changes:**
    - `render_indicator_controls` - render fixed-parameter toggles for `SMA (20)`, `EMA (20)`, `Bollinger Bands (20, 2)`, `Fibonacci Retracement`, and `RSI (14)`.
    - `_get_session_state` usage in `main.py` - add `phase3_indicator_*` keys without changing Phase 2 keys.
    - Selection flow orchestration - render controls only when OHLCV data exists and build settings from session state before chart rendering.
  - **What:**
    - Add a small, explicit control surface above the chart that follows the clarified Phase 3 scope: `SMA (20)` and `RSI (14)` enabled by default, all other indicators off by default, and no parameter editors in v1.
    - Keep the unified one-page flow intact and preserve existing fallback behavior when historical data cannot be loaded.
  - **Testing:**
    - Unit: control renderer returns default state with `SMA (20)` and `RSI (14)` enabled on first load (ACC-01: Indicator Controls Render For Selected Ticker, ACC-02: Default Indicator State On First Load).
    - Unit: toggling each indicator updates returned settings and preserves the existing session-only behavior (ACC-01, ACC-02).
    - Integration: selected ticker with available OHLCV renders the controls before the chart path executes (ACC-01, ACC-06: Unified Flow And Error Resilience Remain Intact).

- [x] Step 3: Extend Chart Rendering for Overlays and RSI Subplot
  - **Files:**
    - `app/ui/chart_components.py` - extend candlestick rendering to accept indicator payloads and optionally build a two-row subplot layout.
    - `app/main.py` - pass indicator payloads into the chart renderer.
  - **Code Changes:**
    - `render_stock_chart` - accept an indicator payload argument and add traces for SMA, EMA, Bollinger, and Fibonacci.
    - Plotly subplot construction - use `make_subplots` when RSI is enabled and keep price data in row 1 and RSI in row 2.
    - Layout updates - preserve responsive width, hover, zoom, pan, and disabled range slider behavior.
  - **What:**
    - Extend the existing chart helper rather than replacing it, so the candlestick chart remains the base series and indicator traces layer on top in a predictable way. Keep Fibonacci anchored to the loaded 1-year high and low range instead of introducing viewport event logic.
    - When RSI is disabled, keep the simpler single-panel chart path; when RSI is enabled, switch to a two-row layout that keeps the candlestick view readable.
  - **Testing:**
    - Unit: base candlestick rendering still emits a Plotly chart when no indicators are enabled (ACC-06).
    - Unit: enabled SMA, EMA, Bollinger, and Fibonacci add overlay traces or shapes to the price chart (ACC-03).
    - Unit: enabled RSI renders a lower subplot trace while preserving the main chart trace set (ACC-04).
    - Unit: chart title and interactivity-related layout settings remain intact after Phase 3 extension (ACC-03, ACC-04, ACC-06).

- [x] Step 4: Extend Deterministic Test Coverage and Unified Smoke Validation
  - **Files:**
    - `tests/unit/test_indicator_service.py` - add direct service tests for indicator payload generation.
    - `tests/unit/test_indicator_controls.py` - add control default and toggle tests with a fake Streamlit facade.
    - `tests/unit/test_chart_components.py` - extend chart assertions for overlays and RSI subplot behavior.
    - `tests/integration/test_selection_chart_smoke.py` - extend the existing offline smoke test to validate default indicators in the unified flow.
  - **Code Changes:**
    - Add deterministic OHLCV fixtures or inline frames suitable for overlay and oscillator assertions.
    - Extend the fake Streamlit facade to capture Phase 3 toggle calls and chart outputs.
    - Update the integration smoke path to assert the one-page summary -> selector -> indicator controls -> chart flow in one run.
  - **What:**
    - Keep test coverage focused on the critical acceptance paths rather than broad finance-library parity tests. Reuse the existing fake-based testing style so the Phase 3 suite stays offline, deterministic, and fast.
    - Extend the current smoke test instead of creating a separate Phase 3 flow, because the plan’s core goal is to validate the final unified dashboard behavior.
  - **Testing:**
    - Unit: service, controls, and chart helpers each validate their own core behavior and edge cases (ACC-01 through ACC-05, ACC-07).
    - Integration: existing smoke test proves summary, selection, default indicators, and chart rendering remain unified and offline (ACC-06, ACC-07).

- [x] Step 5: Final Validation and Release-Readiness Polish
  - **Files:**
    - `app/main.py` - optional title or label polish to reflect final dashboard scope.
    - `app/ui/chart_components.py` - minor legend, naming, or layout polish if needed.
    - `_documentation/work-items/phase3/dev-notes.md` - confirm or refine the manual release checklist if implementation reveals a needed adjustment.
  - **Code Changes:**
    - Align UI labels with the final Phase 3 experience if any Phase 1 or Phase 2-specific wording remains.
    - Confirm chart trace names and legend text are clear enough for user-facing analysis.
    - Keep any polish tightly scoped to Phase 3 behavior only.
  - **What:**
    - Perform a final pass that checks acceptance-fit, readability, and release readiness without expanding scope. The focus is to verify that the final local v1 experience works end to end and that the existing non-blocking error behavior still holds.
  - **Testing:**
    - Run the focused unit and integration suite for the touched Phase 3 files (ACC-07).
    - Manual verification checklist:
      - Select supported ticker -> candlestick plus default `SMA (20)` and `RSI (14)` render.
      - Toggle `EMA (20)`, `Bollinger Bands`, and `Fibonacci Retracement` on and off -> chart updates without losing the base candlestick trace.
      - Switch between multiple supported tickers -> indicator outputs refresh for the new symbol.
      - Force fallback or unavailable OHLCV path -> plain-language warning still appears and the page remains usable.
      - Re-select the same ticker in the same session -> cached path remains responsive.
    - ACC coverage confirmation:
      - ACC-01/02 indicator controls and default state.
      - ACC-03 overlay rendering.
      - ACC-04 RSI subplot behavior.
      - ACC-05 Fibonacci range source.
      - ACC-06 unified flow and resilient error handling.
      - ACC-07 deterministic validation baseline.
