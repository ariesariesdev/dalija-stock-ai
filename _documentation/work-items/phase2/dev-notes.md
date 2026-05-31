## Technical Notes — Phase 2: Selection and Chart Experience

### Source-Code Baseline

Phase 1 is fully implemented. The following modules exist and must not be modified except where explicitly called out:
- `app/main.py` — Streamlit entrypoint (requires fix — see below)
- `app/adapters/yfinance_adapter.py` — requires extension for OHLCV history
- `app/services/interfaces.py` — requires extension for `HistoricalDataProvider`
- `app/domain/portfolio_models.py` — no changes required for Phase 2
- `app/services/kpi_service.py`, `portfolio_ingestion.py`, `ticker_classification.py` — no changes required
- `app/ui/summary_components.py` — no changes required
- `app/config.py` — no changes required

### Critical Bug: `main.py` Rendering Guard

The current `app/main.py` wraps `render_summary_shell()` inside `if __name__ == "__main__":`. Streamlit executes scripts via `exec()`, not as `__main__`, so the guard prevents all rendering. The fix is to call `render_summary_shell()` unconditionally at module level. This must be the first change in Phase 2 — without it the app renders nothing.

### `YFinanceSnapshotProvider` Extension Pattern

The existing adapter (`app/adapters/yfinance_adapter.py`) uses `yf.Ticker(ticker).history(period="1d")` for support checks. Add `get_historical_ohlcv` as a separate method using `period="1y"`. Do not reuse or modify the existing `is_supported_symbol` or `get_snapshot_price` methods. The method must:
- Return a `pd.DataFrame` with the index reset so `Date` is a plain column (call `.reset_index()` on the yfinance output).
- Return `None` on any exception, consistent with the non-fatal pattern already used across the adapter.

### `HistoricalDataProvider` Protocol

Add to `app/services/interfaces.py`:
```python
class HistoricalDataProvider(Protocol):
	def get_historical_ohlcv(self, ticker: str, period: str = "1y") -> pd.DataFrame | None: ...
```
`YFinanceSnapshotProvider` satisfies both `SnapshotPriceProvider` and `HistoricalDataProvider` via structural subtyping — no `implements` declaration needed.

### `@st.cache_data` and Provider Hashability

`@st.cache_data` hashes all arguments. Provider objects are not natively hashable by Streamlit's hash mechanism. Two implementation options:
1. **Preferred**: Make the cached function accept only `ticker: str` and `period: str`, and instantiate/call the provider inside the function body. This is the simplest pattern for `@st.cache_data`.
2. **Alternative**: Use `@st.cache_data(hash_funcs={YFinanceSnapshotProvider: lambda _: 0})` — but this breaks cache isolation if multiple providers are used in tests.

For testability, separate the pure fetch logic (provider call + JSON fallback) into an uncached `_load_ohlcv(ticker, period, provider)` function, and wrap it in a thin `@st.cache_data`-decorated `fetch_ohlcv(ticker, period)` that constructs the live provider. Tests call `_load_ohlcv` directly with a fake provider.

### JSON Fallback File Convention

- Location: `source-files/history/{TICKER}.json`
- Format (matches `pd.DataFrame.to_json(orient="records")`):
```json
[
  {"Date": "2025-05-30T00:00:00.000Z", "Open": 189.5, "High": 191.2, "Low": 188.1, "Close": 190.4, "Volume": 52000000},
  ...
]
```
- Date values from yfinance are timezone-aware; when writing test fixtures use ISO 8601 strings or epoch milliseconds (both parse correctly with `pd.to_datetime`).
- The service must resolve the path relative to `PROJECT_ROOT` from `app/config.py`, not `os.getcwd()`.

### Plotly Candlestick Chart

Minimal implementation pattern:
```python
import plotly.graph_objects as go

fig = go.Figure(data=[go.Candlestick(
	x=df["Date"],
	open=df["Open"],
	high=df["High"],
	low=df["Low"],
	close=df["Close"],
)])
fig.update_layout(title=ticker, xaxis_rangeslider_visible=False)
st_module.plotly_chart(fig, use_container_width=True)
```
- `xaxis_rangeslider_visible=False` removes the default range slider that can obscure the chart on smaller screens.
- Hover tooltips, zoom, and pan are native to Plotly and enabled by default — do not suppress them with `config={"staticPlot": True}`.

### Selector Component — Filtering Logic

`HoldingState` values relevant to the selector:
- `SUPPORTED_US` — always included.
- `UNAVAILABLE_PRICE` — included (user can attempt to select, chart may fail gracefully).
- `UNSUPPORTED_SYMBOL` — excluded when `show_unsupported=False`.

Caption when unsupported are hidden: `f"{n} unsupported symbol(s) hidden. Enable toggle to show."` where `n` is the count of hidden holdings.

`st.selectbox` with a `None` placeholder option pattern:
```python
options = [None] + [h.full_ticker for h in visible_holdings]
format_func = lambda x: "Select a stock..." if x is None else x
selected = st_module.selectbox("Stock", options, format_func=format_func)
```

### Session State Keys

Use these exact keys for consistency and to avoid Streamlit re-render collisions:
- `"phase2_selected_ticker"`: `str | None`
- `"phase2_show_unsupported"`: `bool`

Prefix with `phase2_` to avoid future key collisions with Phase 3 session state.

### Testing Patterns

All existing tests use a `FakeProvider` class (not a mock library) and a `FakeStreamlit` facade. Phase 2 tests must follow the same pattern:

**FakeOHLCVProvider** for historical data service tests:
```python
class FakeOHLCVProvider:
	def __init__(self, data: pd.DataFrame | None):
		self._data = data
	def get_historical_ohlcv(self, ticker: str, period: str = "1y") -> pd.DataFrame | None:
		return self._data
```

**FakeStreamlit** extension for chart and selector tests — extend the existing fake with:
- `plotly_chart(fig, use_container_width)` → append to messages
- `selectbox(label, options, format_func)` → return `options[0]`
- `checkbox(label, value)` / `toggle(label, value)` → return `value`
- `caption(text)` → append to messages

### Edge Cases

1. **Empty OHLCV DataFrame from provider** — treat the same as `None`; do not render a blank chart.
2. **Ticker with spaces or special characters** — `full_ticker.strip()` is already applied in Phase 1 classification; use the same stripped value for the JSON filename lookup (`ticker.upper() + ".json"`).
3. **JSON file with malformed content** — wrap `pd.read_json` in try/except and return `None` on parse failure.
4. **`unavailable_price` holdings in selector** — they appear in the list but may return `None` OHLCV; the chart error path handles this gracefully.
5. **Phase 1 pipeline is slow on first load** (live snapshot calls for 116 tickers) — this is a known Phase 1 constraint and out of scope for Phase 2. Do not add caching to the summary pipeline in this work item.

### NFR-01 Responsiveness Notes

- `@st.cache_data` on `fetch_ohlcv` addresses the ≤2s cached target.
- The ≤5s first-fetch target is a network-dependent target; no additional optimisation is required in Phase 2 beyond the `@st.cache_data` decorator.
- If profiling shows the summary pipeline is blocking the initial render, investigate moving `run_summary_pipeline` inside a `@st.cache_data` call in a follow-up ticket, not in this work item.

### Dependency Requirements

Add to `requirements.txt` if not already present:
- `plotly` — for candlestick chart rendering
- `pandas-ta` — reserved for Phase 3 indicator engine; confirm it is listed for forward compatibility

### Files to Create

| File | Type |
|------|------|
| `app/ui/chart_components.py` | New |
| `app/ui/selector_components.py` | New |
| `app/services/historical_data_service.py` | New |
| `tests/unit/test_historical_data_service.py` | New |
| `tests/unit/test_selector_components.py` | New |
| `tests/unit/test_chart_components.py` | New |
| `tests/integration/test_selection_chart_smoke.py` | New |
| `tests/fixtures/history/AAPL.json` | New |

### Files to Modify

| File | Change |
|------|--------|
| `app/main.py` | Fix `__main__` guard; add selector + chart orchestration |
| `app/adapters/yfinance_adapter.py` | Add `get_historical_ohlcv` method |
| `app/services/interfaces.py` | Add `HistoricalDataProvider` protocol |
| `requirements.txt` | Add `plotly`; confirm `pandas-ta` present |
