## Technical Notes — Phase 3: Indicator Controls and End-to-End Validation

### Source-Code Baseline

Phase 2 is implemented and provides the correct anchor for this work item:
- `app/main.py` already orchestrates summary -> selector -> chart in one page.
- `app/services/historical_data_service.py` already returns normalized OHLCV data with cache and JSON fallback.
- `app/ui/chart_components.py` currently renders a candlestick chart only.
- `tests/integration/test_selection_chart_smoke.py` already validates the offline Phase 2 flow.

This means Phase 3 should extend the existing chart path rather than introduce a second analysis flow.

### Recommended Module Additions And Touch Points

Create:
- `app/services/indicator_service.py`
- `app/ui/indicator_controls.py`
- `tests/unit/test_indicator_service.py`
- `tests/unit/test_indicator_controls.py`

Modify:
- `app/main.py`
- `app/ui/chart_components.py`
- `tests/unit/test_chart_components.py`
- `tests/integration/test_selection_chart_smoke.py` or a new dedicated Phase 3 smoke test

### Indicator Service Contract

Keep the service API explicit and UI-independent. A practical contract is:

```python
def build_indicator_payload(ohlcv_df: pd.DataFrame, settings: IndicatorSettings) -> IndicatorPayload:
    ...
```

Suggested supporting dataclasses:
- `IndicatorSettings` for enabled or disabled fixed-parameter toggles
- `IndicatorPayload` for overlay series, RSI series, and Fibonacci line definitions

This avoids passing raw toggle booleans throughout chart code and makes tests much simpler.

### Calculation Guidance

- `SMA (20)`: 20-period moving average over `Close`
- `EMA (20)`: 20-period exponential moving average over `Close`
- `Bollinger Bands`: 20-period middle band with upper and lower bands at `2` standard deviations
- `RSI (14)`: standard 14-period RSI oscillator
- `Fibonacci Retracement`: derive from the loaded dataset high and low; keep the logic stable for the full current 1-year frame

If `pandas-ta` is used:
- import name is typically `pandas_ta`
- isolate the dependency inside the service so import failure can be handled in one place

If equivalent formulas are implemented directly:
- keep column naming deterministic
- centralize all rolling-window constants in one place

### Chart Composition Guidance

Current `render_stock_chart` builds a single `go.Figure`. Phase 3 will likely need a split approach:
- use `plotly.subplots.make_subplots` when RSI is enabled
- keep candlestick and overlay traces in row 1
- place RSI in row 2 with its own y-axis title

Recommended behavior:
- `RSI` disabled: single chart panel
- `RSI` enabled: two-row figure with a smaller lower panel
- `use_container_width=True` remains enabled
- keep `xaxis_rangeslider_visible=False`

### Control Rendering Guidance

The grill-me decisions narrowed the control surface to fixed-parameter toggles only. Avoid adding number inputs or advanced settings in this phase.

Recommended labels:
- `SMA (20)`
- `EMA (20)`
- `Bollinger Bands (20, 2)`
- `Fibonacci Retracement`
- `RSI (14)`

Recommended default session-state values:
- `phase3_indicator_sma20 = True`
- `phase3_indicator_rsi14 = True`
- `phase3_indicator_ema20 = False`
- `phase3_indicator_bollinger_20_2 = False`
- `phase3_indicator_fibonacci = False`

### Main Flow Integration Notes

In `app/main.py`, the clean sequence after ticker selection is:
1. fetch OHLCV
2. short-circuit to `render_chart_error` if unavailable
3. render indicator controls
4. compute indicator payload from current settings
5. render chart with candlestick + selected indicators

Keep the existing Phase 2 state keys unchanged:
- `phase2_show_unsupported`
- `phase2_selected_ticker`

Phase 3 should only add adjacent state, not rename prior keys.

### Testing Guidance

Follow the existing fake-based testing style already used in the repository.

Unit tests should cover:
- default indicator settings
- toggling behavior captured through fake Streamlit widgets
- indicator payload creation for deterministic OHLCV frames
- empty or short datasets remaining non-fatal
- chart trace composition with and without RSI

Integration coverage should remain offline and deterministic:
- use a fake provider with seeded OHLCV data
- avoid live Yahoo calls
- assert default indicators appear on the first render path

### Manual Release Checklist

- Select `AAPL` or another supported ticker and confirm the chart shows candlestick plus default `SMA (20)` and `RSI (14)`.
- Toggle `EMA (20)`, `Bollinger Bands`, and `Fibonacci Retracement` on and off and confirm the chart updates without removing the base candlestick trace.
- Switch between two supported tickers and confirm overlays recalculate for the newly selected symbol.
- Force OHLCV fallback or failure and confirm the plain-language warning still renders and the rest of the page remains usable.
- Re-select the same ticker in the same session and confirm the cached path remains responsive.

### Inferred Considerations

- Standard Fibonacci levels can use the common retracement set `23.6%`, `38.2%`, `50.0%`, `61.8%`, and `78.6%`, with optional high/low anchor lines if the implementation stays readable.
- If subplot layout makes test assertions brittle, validate trace names and row allocation rather than exact serialized Plotly JSON.
- If the current page title still references only Phase 1 or Phase 2, update it as part of this work item so the final UI is internally consistent.