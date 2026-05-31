# Requirements: Dynamic Portfolio and Technical Analysis Dashboard (v1)

## Scope and Inputs

- Source portfolio file: `../source-files/Porfelis20260221.csv`
- Portfolio scope rule: include all current rows in the CSV (dynamic as file updates)
- Market scope: US tickers only
- Default chart history window: 1 year
- Out of scope: authentication, account management, report/file export

## Assumptions

- CSV contains at least one unique ticker symbol per holding row.
- The application can access Yahoo Finance data during active sessions.
- Daily OHLCV granularity is sufficient for v1 analysis workflows.

## Functional Requirements

### FR-01 Portfolio Ingestion
The system shall ingest the portfolio CSV at startup and expose all valid holdings from the current file rows.

### FR-02 Portfolio Summary KPIs
The system shall display a portfolio summary area with, at minimum:
- total portfolio value computed as the sum of `(position_quantity * snapshot_price)` for holdings where snapshot price is available
- total holdings count from CSV rows
- unavailable-price holdings count

### FR-03 Missing Snapshot Price Handling
The system shall treat missing snapshot prices as unavailable, exclude those holdings from value totals, and surface unavailable counts in the summary.

### FR-04 Fast Stock Lookup and Selection
The system shall provide stock search and selection for all in-scope holdings and allow opening a selected stock in one interaction flow.

### FR-05 Single-Stock Chart View
The system shall render an interactive single-stock chart for the selected ticker using a default 1-year historical window.

### FR-06 Interactive Chart Behaviors
The stock chart shall support hover tooltips, zoom, and pan.

### FR-07 Technical Indicator Controls
The system shall provide indicator controls for:
- Simple/Exponential Moving Averages
- Bollinger Bands
- Fibonacci Retracement levels auto-calculated from the visible 1-year high/low range
- RSI

### FR-08 Indicator Default State
On first load, the system shall enable default indicators `SMA (20)` and `RSI (14)`, while other indicators remain off by default, and allow the user to toggle indicators on/off dynamically.

### FR-09 US-Only Ticker Enforcement
The system shall enforce US-only ticker support in v1 and represent unsupported symbols with a non-blocking unavailable/unsupported state.

### FR-10 Unified User Flow
The system shall support a single workflow where the user can move from portfolio summary to selected-stock analysis without page-level navigation complexity.

## Non-Functional Requirements

### NFR-01 Responsiveness with Full Portfolio
With the full CSV dataset loaded, stock selection-to-chart render time shall be within 2.0 seconds for cached data and within 5.0 seconds for first fetch under normal network conditions.

### NFR-02 UI Clarity for Unavailable Data
Unavailable and unsupported states shall use plain-language labels and remain non-blocking for all other interactions.

### NFR-03 Reliability of Core Flow
For valid US tickers with retrievable data, summary-to-chart flow success rate shall be at least 99% across 100 consecutive manual selections.

### NFR-04 Deterministic KPI Rules
KPI calculations shall produce identical results for the same input CSV and same available snapshot price values across repeated runs.

## Data and Integration Requirements

### DR-01 Data Provider
Historical OHLCV market data shall be retrieved from Yahoo Finance via `yfinance`.

### DR-02 Visualization Engine
Interactive chart rendering shall use Plotly-compatible components.

### DR-03 Indicator Engine
Indicator computations shall use `pandas-ta` or equivalent formulas that produce validated indicator outputs.

## Traceability Notes

- FR-01 to FR-04 map user goal: fast portfolio understanding and stock access.
- FR-05 to FR-08 map user goal: technical analysis on a selected stock.
- FR-03 and NFR-02 map missing-data transparency requirement.
- NFR-01 and NFR-03 map responsiveness and reliability success signals.
