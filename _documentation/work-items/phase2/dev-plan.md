# Phase 2 Implementation: Selection and Chart Experience

**Description:** Add a unified stock selection and single-stock candlestick chart experience on top of the existing Phase 1 summary flow, including JSON fallback and deterministic tests.

## Goal

Implement the full Phase 2 user flow in one Streamlit page: summary remains visible, user selects a stock quickly, and an interactive 1-year chart renders with resilient fallback behavior. The plan prioritizes clean service boundaries, low-risk integration with existing Phase 1 modules, and test coverage for key acceptance criteria.

## Implementation Steps

- [x] Step 1: Extend Data Contracts and Historical Data Retrieval
  - **Files:**
    - `app/services/interfaces.py` - add `HistoricalDataProvider` protocol.
    - `app/adapters/yfinance_adapter.py` - add `get_historical_ohlcv(ticker, period="1y")`.
    - `app/services/historical_data_service.py` - add historical fetch logic with JSON fallback from `source-files/history/{TICKER}.json`.
  - **Code Changes:**
    - `HistoricalDataProvider.get_historical_ohlcv` - new protocol method.
    - `YFinanceSnapshotProvider.get_historical_ohlcv` - return normalized DataFrame with Date column, or `None` on failure.
    - `historical_data_service.fetch_ohlcv` - `@st.cache_data` wrapper.
    - `historical_data_service._load_ohlcv` - uncached provider + fallback loader for testability.
  - **What:**
    - Add a dedicated historical data boundary that complements, but does not alter, existing Phase 1 snapshot logic.
    - Implement precedence: live yfinance first, then per-ticker JSON fallback, then unavailable state (`None`).
    - Standardize fallback date format handling as ISO-8601 UTC strings and parse robustly with pandas.
  - **Testing:**
    - Unit: live provider success path returns chartable DataFrame (ACC-03: Single-Stock Chart Loads On Selection).
    - Unit: live failure + JSON exists returns fallback DataFrame (ACC-05: OHLCV Static Fallback).
    - Unit: live failure + missing/invalid JSON returns `None` (ACC-05: non-blocking failure behavior).
    - Unit: repeated same ticker fetch uses cache wrapper path (ACC-06: Caching Meets Responsiveness Target).

- [x] Step 2: Build Selector and Chart UI Components
  - **Files:**
    - `app/ui/selector_components.py` - selector/toggle rendering and filtering.
    - `app/ui/chart_components.py` - candlestick rendering and chart error messaging.
  - **Code Changes:**
    - `render_unsupported_toggle` - default `False` (hidden by default).
    - `render_stock_selector` - searchable selectbox, unsupported grouped at bottom when shown.
    - `render_stock_chart` - Plotly candlestick with responsive layout.
    - `render_chart_error` - plain-language warning with next-action hint.
  - **What:**
    - Implement explicit selector behavior aligned to grill-me outcomes: unsupported hidden by default, toggle to show, and unsupported options grouped below supported entries.
    - Render candlestick chart with hover/zoom/pan native behavior and clear no-data messaging.
  - **Testing:**
    - Unit: selector hides unsupported by default and shows them when toggled (ACC-01, ACC-02).
    - Unit: selector ordering places unsupported entries at bottom when visible (ACC-02).
    - Unit: chart render function emits Plotly chart call for valid OHLCV input (ACC-03, ACC-04).
    - Unit: chart error path displays plain-language warning + next action hint when OHLCV is unavailable (ACC-05).

- [x] Step 3: Integrate Unified Flow in Main Entrypoint
  - **Files:**
    - `app/main.py` - orchestrate summary -> selector -> chart.
    - `app/config.py` (optional) - session-state key constants if preferred.
  - **Code Changes:**
    - Fix Streamlit execution behavior by calling `render_summary_shell()` at module level (remove reliance on `__main__` guard).
    - Add Phase 2 section below summary with `st.divider()`.
    - Add `st.session_state` keys for selected ticker and unsupported toggle (session-only persistence).
    - Wire selector output to `fetch_ohlcv` and chart/error rendering.
  - **What:**
    - Keep summary always visible while adding stock exploration below it in the same page and same run flow.
    - Ensure no page-level navigation and non-blocking behavior when data for a chosen ticker is unavailable.
  - **Testing:**
    - Integration smoke: summary renders, selection is possible, and chart or error area renders in one unified view (ACC-07, ACC-08).
    - Integration smoke: state remains session-only and resets on restart (grill-me decision + ACC-07 intent).

- [x] Step 4: Add Fixtures, Dependencies, and Automated Coverage
  - **Files:**
    - `tests/fixtures/history/AAPL.json` - ISO-8601 UTC OHLCV fixture.
    - `tests/unit/test_historical_data_service.py` - service unit tests.
    - `tests/unit/test_selector_components.py` - selector unit tests.
    - `tests/unit/test_chart_components.py` - chart component tests.
    - `tests/integration/test_selection_chart_smoke.py` - fully offline end-to-end smoke.
    - `requirements.txt` - ensure `plotly` present; keep `pandas-ta` available for Phase 3.
  - **Code Changes:**
    - Add fake providers and fake streamlit facade extensions for deterministic tests.
    - Keep integration smoke fully offline using fake provider + local fixture JSON.
  - **What:**
    - Validate critical behavior using deterministic tests to avoid network flakiness.
    - Ensure coverage aligns with acceptance criteria rather than broad unbounded testing.
  - **Testing:**
    - Full unit + integration suite for ACC-01 through ACC-09 with emphasis on fallback, caching, unified flow, and resilient messaging.

- [x] Step 5: Validate End-to-End Behavior and Polish
  - **Files:**
    - `app/main.py` - minor UX polish text/labels.
    - `app/ui/*.py` - message tuning and chart titles.
  - **Code Changes:**
    - Confirm selector placeholder behavior and user guidance text.
    - Confirm fallback warning language and next-action guidance are clear.
    - Confirm chart interactions (hover/zoom/pan) remain enabled and not overridden.
  - **What:**
    - Perform final pass to ensure user flow quality and acceptance-fit before handoff to implementation completion.
  - **Testing:**
    - Manual verification checklist:
      - Select supported ticker -> candlestick chart renders.
      - Force provider failure -> JSON fallback renders.
      - Remove fallback file -> plain-language warning appears, app remains usable.
      - Toggle unsupported visibility -> selector updates correctly.
      - Summary remains visible throughout interactions.
    - ACC coverage confirmation:
      - ACC-01/02 selector behavior.
      - ACC-03/04 chart rendering and interactions.
      - ACC-05 fallback/error behavior.
      - ACC-06 cache path.
      - ACC-07/08 unified flow and summary persistence.
      - ACC-09 automated test baseline.
