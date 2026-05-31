"""Phase 2 and Phase 3 chart rendering helpers for selected stock analysis."""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app.services.indicator_service import IndicatorPayload


def render_stock_chart(
    st_module: object,
    ticker: str,
    ohlcv_df: pd.DataFrame,
    indicator_payload: IndicatorPayload | None = None,
) -> None:
    """Render an interactive candlestick chart with optional Phase 3 overlays."""

    payload = indicator_payload or IndicatorPayload()
    has_rsi_panel = payload.rsi_series is not None
    figure = make_subplots(
        rows=2 if has_rsi_panel else 1,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.72, 0.28] if has_rsi_panel else None,
    )
    figure.add_trace(
        go.Candlestick(
            x=ohlcv_df["Date"],
            open=ohlcv_df["Open"],
            high=ohlcv_df["High"],
            low=ohlcv_df["Low"],
            close=ohlcv_df["Close"],
            name=ticker,
        ),
        row=1,
        col=1,
    )

    for overlay in payload.overlay_series:
        figure.add_trace(
            go.Scatter(x=list(overlay.x), y=list(overlay.y), mode="lines", name=overlay.name),
            row=1,
            col=1,
        )

    if payload.fibonacci_levels:
        start_date = ohlcv_df["Date"].iloc[0]
        end_date = ohlcv_df["Date"].iloc[-1]
        for level in payload.fibonacci_levels:
            figure.add_trace(
                go.Scatter(
                    x=[start_date, end_date],
                    y=[level.value, level.value],
                    mode="lines",
                    name=f"Fib {level.label}",
                    line={"dash": "dot"},
                ),
                row=1,
                col=1,
            )

    if payload.rsi_series is not None:
        # AIDEV-NOTE: Keep RSI in a dedicated subplot so overlay density does not obscure price action.
        figure.add_trace(
            go.Scatter(
                x=list(payload.rsi_series.x),
                y=list(payload.rsi_series.y),
                mode="lines",
                name=payload.rsi_series.name,
            ),
            row=2,
            col=1,
        )
        figure.update_yaxes(title_text="RSI", row=2, col=1)

    figure.update_layout(
        title=f"{ticker} - 1Y Technical Analysis",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
    )

    for notice in payload.notices:
        st_module.caption(notice)

    st_module.plotly_chart(figure, use_container_width=True)


def render_chart_error(st_module: object, ticker: str) -> None:
    """Render a plain-language warning when chart data cannot be resolved."""

    # AIDEV-NOTE: Include clear next action hints to keep failure states non-blocking.
    st_module.warning(
        f"Historical data is unavailable for {ticker}. Try another ticker or add a fallback JSON file in source-files/history/."
    )
