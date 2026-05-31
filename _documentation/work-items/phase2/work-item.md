## Title

Phase 2 Implementation: Selection and Chart Experience

## Description

Extend the Phase 1 summary dashboard with a unified stock selection and interactive chart view so users can move from portfolio summary to a single-stock candlestick chart in one continuous flow, without page-level navigation. This work item delivers the interactive experience layer that builds directly on the stable data foundation established in Phase 1.

## Background Information

Phase 1 delivered a working portfolio ingestion, classification, and KPI summary shell. The Phase 2 work adds the next user-facing capability: the ability to pick any in-scope holding from a searchable selector and immediately view a 1-year interactive candlestick chart for that stock.

Key constraints carried forward from Phase 1 and the solution design:
- US-only ticker enforcement is already in place; unsupported symbols must be handled non-blockingly in the selector context.
- `YFinanceSnapshotProvider` exists and the `yfinance` integration is already functional for snapshot prices; Phase 2 extends this to full 1-year OHLCV history.
- The unified flow must remain on one page: summary always visible, selector and chart render below it.
- If live yfinance OHLCV fetch fails, the app must fall back to a static JSON file on disk before surfacing an error state.

**Decisions from implementation review:**
- Default chart type: candlestick (OHLC bars).
- Unsupported symbols in selector: hidden by default, with a toggle to show them.
- Selector widget: Streamlit `st.selectbox` with type-ahead text filtering.
- OHLCV caching: `@st.cache_data` decorator on the fetch function to meet NFR-01 (≤2s cached).
- Indicator library for future Phase 3: `pandas-ta` (no indicator controls are implemented in this phase).
- OHLCV fallback format: JSON file per ticker at `source-files/history/{TICKER}.json`.
- Chart failure behaviour: fall back to static JSON; show plain-language error in chart area if both sources fail.
- Test coverage: unit tests for new services + integration smoke.

## Plan Step Reference

Analysis Repository: ariesariesdev/dalija-stock-ai
Plan File: /initial_v1/plan.md
Plan Step: Phase 2: Selection and Chart Experience

## Work Item Details

Extend the existing Streamlit application to support the following capabilities:

### 1. OHLCV Historical Data Adapter Extension

Extend `app/adapters/yfinance_adapter.py` to add a `get_historical_ohlcv(ticker, period)` method that:
- Fetches 1-year daily OHLCV history using `yf.Ticker(ticker).history(period="1y")`.
- Returns a `pandas.DataFrame` with columns: `Date`, `Open`, `High`, `Low`, `Close`, `Volume`.
- Returns `None` (not an exception) on fetch failure to allow fallback handling.

Extend `app/services/interfaces.py` to define a `HistoricalDataProvider` protocol with:
```python
def get_historical_ohlcv(self, ticker: str, period: str = "1y") -> pd.DataFrame | None: ...
```

### 2. Historical Data Service with Fallback

Create `app/services/historical_data_service.py` that:
- Exposes a `@st.cache_data`-decorated function `fetch_ohlcv(ticker, period, provider)` (or a wrapper pattern compatible with testing) that:
  1. Calls `provider.get_historical_ohlcv(ticker, period)`.
  2. If the provider returns `None` or raises, attempts to load from `source-files/history/{TICKER}.json`.
  3. JSON fallback file format: array of records `[{"Date": "...", "Open": ..., "High": ..., "Low": ..., "Close": ..., "Volume": ...}]` (matching `DataFrame.to_json(orient="records")`).
  4. If both sources fail, returns `None` so the UI can surface an error state.
- The service must not raise uncaught exceptions; all failures return `None` with optional structured log output.

### 3. Stock Selector UI Component

Create `app/ui/selector_components.py` that:
- Provides `render_stock_selector(st_module, holdings, show_unsupported)` returning the selected `HoldingRecord | None`.
- Builds the selectable option list from `holdings` using `full_ticker` as the display and value.
- When `show_unsupported=False` (default): filters out holdings with `state == HoldingState.UNSUPPORTED_SYMBOL`.
- Renders a `st.selectbox` with a placeholder option so no ticker is selected on first load.
- Provides `render_unsupported_toggle(st_module, default=False)` returning the current boolean toggle value using `st.checkbox` or `st.toggle`.
- Renders a plain-language caption when unsupported symbols are hidden to inform the user how many are hidden.

### 4. Candlestick Chart UI Component

Create `app/ui/chart_components.py` that:
- Provides `render_stock_chart(st_module, ticker, ohlcv_df)` that renders an interactive Plotly candlestick chart using `plotly.graph_objects.Candlestick` wrapped in `st.plotly_chart`.
- Chart must support hover tooltips (date, O/H/L/C), zoom, and pan — these are native Plotly behaviours; confirm they are not suppressed.
- Chart title must display the selected ticker symbol.
- Provides `render_chart_error(st_module, ticker)` that displays a plain-language, non-blocking error message when OHLCV data is unavailable.
- No indicator controls are implemented in this phase.

### 5. Unified Flow Orchestration in `main.py`

Update `app/main.py` to implement the unified single-page flow:
- Fix the current `if __name__ == "__main__":` guard so `render_summary_shell()` is called unconditionally at module level (Streamlit runs scripts via `exec`, not as `__main__`, so the guard currently prevents any rendering).
- After the summary section renders, add a `st.divider()` and render the stock selector section.
- Manage `show_unsupported` toggle state and the selected ticker via `st.session_state`.
- On ticker selection, call `fetch_ohlcv` and render the chart or the error state.
- No page reload or multi-page navigation may occur during the summary → selection → chart flow.

### 6. Session State Keys

Document and use the following `st.session_state` keys in `main.py`:
- `selected_ticker`: `str | None` — currently selected ticker.
- `show_unsupported`: `bool` — whether unsupported symbols are shown in the selector.

### 7. Test Coverage

- `tests/unit/test_historical_data_service.py`: unit tests covering live fetch success, live fetch failure with JSON fallback success, both sources failing.
- `tests/unit/test_selector_components.py`: unit tests covering unsupported filtering, toggle default state, selectbox rendering with FakeStreamlit.
- `tests/unit/test_chart_components.py`: unit tests covering chart render call with valid data and error render call with None data using FakeStreamlit.
- `tests/integration/test_selection_chart_smoke.py`: integration smoke test that exercises the full `run_summary_pipeline` → selector render → `fetch_ohlcv` → chart render path using fixture data.
- Add fixture file: `tests/fixtures/history/AAPL.json` with minimal 5-row daily OHLCV data.

## Design Considerations

- Preserve the existing `SnapshotPriceProvider` interface and all Phase 1 service boundaries; Phase 2 adds alongside, not replacing.
- `YFinanceSnapshotProvider` already uses `yf.Ticker(...).history(period="1d")` for support checks; the OHLCV extension uses `period="1y"` — keep them as separate methods, not shared.
- `@st.cache_data` caches by argument value; the `provider` object must be hashable or the cache decorator applied to a thin wrapper function that accepts only serialisable arguments (ticker string + period string).
- Plotly chart must use `use_container_width=True` in `st.plotly_chart` to be responsive.
- The JSON fallback path must resolve relative to `PROJECT_ROOT`, not the current working directory, using the same `Path(__file__).resolve()` pattern as `app/config.py`.
- Do not implement FR-07, FR-08, or DR-03 (indicator controls) in this work item — those are Phase 3.
- The `render_summary_shell` unconditional call fix is a prerequisite for Phase 2 to render anything; it must be included in this work item.

## Acceptance Criteria

- ACC-01: Searchable Stock Selector Renders From Holdings

  **GIVEN** the app has loaded the portfolio
  **WHEN** the summary section renders
  **THEN** a searchable selectbox appears below the summary with all supported holdings listed
  **AND** unsupported symbols are hidden by default
  **AND** a toggle allows the user to show unsupported symbols

- ACC-02: Unsupported Symbol Toggle Behaviour

  **GIVEN** the unsupported toggle is off (default)
  **WHEN** the selector renders
  **THEN** only `supported_us` and `unavailable_price` holdings are selectable
  **AND** a plain-language caption shows how many unsupported holdings are hidden

  **GIVEN** the user enables the unsupported toggle
  **WHEN** the selector re-renders
  **THEN** unsupported symbols appear in the selector and a non-blocking state label is shown

- ACC-03: Single-Stock Candlestick Chart Loads On Selection

  **GIVEN** the user selects a valid US ticker from the selector
  **WHEN** selection is confirmed
  **THEN** a 1-year daily candlestick chart renders below the selector
  **AND** the chart title includes the selected ticker symbol
  **AND** no full page reload occurs

- ACC-04: Interactive Chart Behaviours

  **GIVEN** a candlestick chart is displayed
  **WHEN** the user hovers over a candle
  **THEN** a tooltip shows the date plus open, high, low, close values
  **AND** zoom and pan interactions update the chart viewport without triggering a full Streamlit rerun

- ACC-05: OHLCV Static Fallback

  **GIVEN** live yfinance fetch fails for a selected ticker
  **WHEN** a matching JSON file exists at `source-files/history/{TICKER}.json`
  **THEN** the chart renders using the static file data

  **GIVEN** both live fetch and static file are unavailable
  **WHEN** the user selects the ticker
  **THEN** a plain-language error message appears in the chart area
  **AND** the rest of the application remains usable

- ACC-06: Caching Meets Responsiveness Target

  **GIVEN** a ticker's OHLCV data has already been fetched once in the session
  **WHEN** the user selects the same ticker again
  **THEN** the chart renders without a new network call (served from `@st.cache_data` cache)

- ACC-07: Unified Flow — No Page Navigation

  **GIVEN** the main dashboard is open
  **WHEN** the user completes summary → selector → chart actions
  **THEN** all sections remain on one page without multi-page navigation or full app reload

- ACC-08: Summary Always Visible

  **GIVEN** the user has selected a stock and the chart is visible
  **WHEN** viewing the dashboard
  **THEN** the portfolio summary KPI cards remain visible above the selector and chart

- ACC-09: Test Coverage Baseline

  **GIVEN** Phase 2 implementation is complete
  **WHEN** the test suite is executed
  **THEN** unit tests for historical data service, selector components, and chart components all pass
  **AND** an integration smoke test validates the full selection-to-chart pipeline

## References

- Analysis repository: ariesariesdev/dalija-stock-ai
- Feature: /initial_v1/feature.md
- Solution design: /initial_v1/solution-design.md
- Acceptance criteria: /initial_v1/acceptance-criteria.md
- Requirements: /initial_v1/requirements.md
- Plan: /initial_v1/plan.md
