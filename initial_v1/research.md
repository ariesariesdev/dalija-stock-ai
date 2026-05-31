# Research: Dynamic Portfolio and Technical Analysis Dashboard

## Summary

The repository already contains enough evidence to proceed with v1 planning. The source portfolio file matches the feature scope at 116 holdings, and the proposed Python dashboard stack is technically aligned with the user flow described in the feature.

## Findings

1. Portfolio scope is 116 holdings.
   - The feature definition states the release covers all 116 rows in the source portfolio.
   - The CSV confirms a header row followed by data through the final visible row, which makes the in-scope baseline 116 holdings.
   - The technical notes mention 100 stocks, but that appears to be stale and should not be used as the current scope baseline.

2. Streamlit is a reasonable fit for the UI flow.
   - The dashboard needs a fast selector for tickers and responsive controls for overlays.
   - Streamlit supports select widgets and interactive chart components, which matches the required portfolio-to-stock drilldown path.

3. Plotly supports the charting shape required for the MVP.
   - The feature needs a single-stock interactive chart with OHLC candles and overlay indicators.
   - Plotly documents candlestick chart support and interactive plotting, which fits the price history and technical analysis use case.

4. yfinance fits the on-demand market data requirement.
   - The technical notes specify yfinance as the market data source.
   - yfinance is designed to download market data from Yahoo Finance, which matches the need for historical OHLCV retrieval.

5. pandas-ta is a plausible indicator engine, but implementation details still need verification.
   - The technical notes call for moving averages, Bollinger Bands, Fibonacci retracement, and RSI.
   - pandas-ta is the intended quantitative library in the notes, but the exact indicator formulas and presentation rules should be confirmed during implementation so chart behavior stays consistent.

## Constraints

- The feature is intentionally narrow for v1: US-only ticker support, no authentication, and no export flow.
- Missing snapshot prices should remain explicit unavailable states rather than being auto-filled.
- The data source is a user-provided portfolio snapshot, so any live market data fetch should preserve the source portfolio as the baseline of record.

## Risks

- yfinance depends on Yahoo Finance public APIs and is intended for research and educational use, so data availability and rate behavior may vary.
- The repository does not yet define exact KPI formulas or overlay defaults, so those rules still need to be specified before implementation.

## Open Questions

- Should v1 treat the CSV as a fixed snapshot of 116 holdings, or should it support future rows as the source file changes?
- Should all indicator toggles be on by default or off by default?
- What is the exact rule for unavailable snapshot prices in the summary KPI calculations?

## References

- [feature.md](feature.md)
- [techincal-notes.md](techincal-notes.md)
- [Porfelis20260221.csv](../source-files/Porfelis20260221.csv)
- Streamlit select widgets and chart API documentation
- Plotly candlestick chart documentation
- yfinance repository documentation