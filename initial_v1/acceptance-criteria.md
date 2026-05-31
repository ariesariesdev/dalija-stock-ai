# Acceptance Criteria: Dynamic Portfolio and Technical Analysis Dashboard (v1)

## Requirement-to-Criteria Mapping

### FR-01 Portfolio Ingestion
1. Given a valid portfolio CSV, when the app starts, then all valid holding rows from the current file are loaded into the in-memory portfolio model.
2. Given the CSV row count changes, when the app restarts, then the loaded holdings count reflects the new row count.

### FR-02 Portfolio Summary KPIs
1. Given loaded holdings with available snapshot prices and quantities, when the summary renders, then total portfolio value equals `sum(position_quantity * snapshot_price)` for holdings with available snapshot prices.
2. Given loaded holdings, when the summary renders, then total holdings count is shown.
3. Given one or more missing snapshot prices, when the summary renders, then unavailable-price holdings count is shown.

### FR-03 Missing Snapshot Price Handling
1. Given holdings with missing snapshot prices, when total value is computed, then those holdings are excluded from total value calculation.
2. Given missing snapshot prices, when summary renders, then user-visible unavailable state is shown for affected holdings.

### FR-04 Fast Stock Lookup and Selection
1. Given the full in-scope portfolio, when a user searches by ticker, then matching holdings appear in the selector results.
2. Given a selected ticker, when user confirms selection, then selected-stock analysis view opens in the same interaction flow.

### FR-05 Single-Stock Chart View
1. Given a selected valid US ticker, when chart loads, then a 1-year historical chart is displayed by default.
2. Given a chart is visible, when user changes ticker, then chart updates to the newly selected ticker.

### FR-06 Interactive Chart Behaviors
1. Given a displayed chart, when user hovers over a candle/point, then tooltip shows date/time and price values.
2. Given a displayed chart, when user zooms or pans, then the viewport updates accordingly without full app reset.

### FR-07 Technical Indicator Controls
1. Given a displayed chart, when user enables SMA/EMA, then selected moving average overlays appear.
2. Given a displayed chart, when user enables Bollinger Bands, then upper/mid/lower bands appear.
3. Given a displayed chart, when user enables Fibonacci retracement, then retracement levels are auto-calculated from the visible 1-year high/low range.
4. Given a displayed chart, when user enables RSI, then RSI panel/series appears.

### FR-08 Indicator Default State
1. Given first app load, when no prior session settings exist, then `SMA (20)` and `RSI (14)` are enabled and all other indicators are disabled.
2. Given any indicator is enabled or disabled, when user toggles it, then chart updates within 1 second.

### FR-09 US-Only Ticker Enforcement
1. Given a non-US ticker in source data, when ticker is selected, then system shows unsupported state and does not crash.
2. Given a valid US ticker, when selected, then system proceeds to fetch and render data normally.

### FR-10 Unified User Flow
1. Given the main dashboard view, when user completes summary-to-selection-to-chart actions, then no page reload or multi-page navigation is required.

## Non-Functional Acceptance Criteria

### NFR-01 Responsiveness with Full Portfolio
1. Given full portfolio loaded and cached ticker data, when selecting any ticker, then chart renders within 2.0 seconds.
2. Given full portfolio loaded and first-time ticker fetch, when selecting any ticker, then chart renders within 5.0 seconds under normal network conditions.

### NFR-02 UI Clarity for Unavailable Data
1. Given unavailable snapshot price or unsupported ticker, when state is displayed, then a plain-language reason is visible to the user.
2. Given unavailable items exist, when user continues workflow, then unaffected tickers remain fully usable.

### NFR-03 Reliability of Core Flow
1. Given 100 consecutive manual selections of valid US tickers with retrievable data, when executed, then at least 99 selections complete summary-to-chart successfully.

### NFR-04 Deterministic KPI Rules
1. Given unchanged CSV and unchanged available snapshot values, when app is restarted, then KPI values remain identical.

## Data and Integration Acceptance Criteria

### DR-01 Data Provider
1. Given valid US ticker and available Yahoo data, when history is requested, then OHLCV data is retrieved through `yfinance`.

### DR-02 Visualization Engine
1. Given historical data, when chart renders, then an interactive Plotly-based chart is displayed.

### DR-03 Indicator Engine
1. Given indicator toggles are enabled, when indicator calculations run, then outputs match library/formula expectations for the selected period parameters.

## Validation Notes

- Terminology is normalized across artifacts: holdings, unavailable snapshot price, selected ticker, indicator overlays.
- Each requirement in `requirements.md` has at least one explicit acceptance criterion in this file.
