"""Unit tests for candlestick chart rendering helpers."""

import pandas as pd

from app.services.indicator_service import IndicatorPayload, IndicatorSeries, FibonacciLevel
from app.ui.chart_components import render_chart_error, render_stock_chart


class FakeStreamlit:
    """Small streamlit facade that records chart and warning calls."""

    def __init__(self) -> None:
        """Initialize capture lists for chart and warning assertions."""

        self.plots: list[object] = []
        self.warnings: list[str] = []
        self.captions: list[str] = []

    def plotly_chart(self, figure: object, use_container_width: bool = False) -> None:
        """Capture chart rendering calls from chart helper functions."""

        self.plots.append((figure, use_container_width))

    def warning(self, value: str) -> None:
        """Capture warning messages emitted for unavailable chart data."""

        self.warnings.append(value)

    def caption(self, value: str) -> None:
        """Capture informational captions emitted for partial indicator availability."""

        self.captions.append(value)


def _ohlcv_frame() -> pd.DataFrame:
    """Return deterministic OHLCV data used for chart helper tests."""

    return pd.DataFrame(
        {
            "Date": [pd.Timestamp("2026-01-01T00:00:00Z"), pd.Timestamp("2026-01-02T00:00:00Z")],
            "Open": [100.0, 101.0],
            "High": [102.0, 103.0],
            "Low": [99.0, 100.0],
            "Close": [101.0, 102.5],
            "Volume": [1000, 1100],
        }
    )


def _indicator_payload(include_rsi: bool = True) -> IndicatorPayload:
    """Return a simple indicator payload for chart rendering assertions."""

    dates = list(_ohlcv_frame()["Date"])
    overlay_series = (
        IndicatorSeries(name="SMA (20)", x=dates, y=[100.5, 101.5]),
        IndicatorSeries(name="EMA (20)", x=dates, y=[100.8, 101.8]),
    )
    rsi_series = IndicatorSeries(name="RSI (14)", x=dates, y=[55.0, 58.0]) if include_rsi else None
    fibonacci_levels = (
        FibonacciLevel(label="23.6%", value=101.8),
        FibonacciLevel(label="38.2%", value=101.2),
    )
    return IndicatorPayload(
        overlay_series=overlay_series,
        rsi_series=rsi_series,
        fibonacci_levels=fibonacci_levels,
        notices=("RSI omitted for shorter history.",) if not include_rsi else (),
    )


def test_render_stock_chart_plots_candlestick_figure() -> None:
    """Chart helper should emit a Plotly figure for valid OHLCV data."""

    fake = FakeStreamlit()

    render_stock_chart(fake, "AAPL", _ohlcv_frame())

    assert len(fake.plots) == 1
    assert fake.plots[0][1] is True


def test_render_stock_chart_adds_overlay_and_rsi_traces() -> None:
    """Indicator payload should extend the chart with overlays and an RSI subplot."""

    fake = FakeStreamlit()

    render_stock_chart(fake, "AAPL", _ohlcv_frame(), indicator_payload=_indicator_payload())

    figure = fake.plots[0][0]
    trace_names = {trace.name for trace in figure.data}
    assert "AAPL" in trace_names
    assert "SMA (20)" in trace_names
    assert "EMA (20)" in trace_names
    assert "RSI (14)" in trace_names
    assert hasattr(figure.layout, "yaxis2")


def test_render_stock_chart_surfaces_indicator_notices_as_captions() -> None:
    """Short-history notices should be shown as non-blocking captions."""

    fake = FakeStreamlit()

    render_stock_chart(fake, "AAPL", _ohlcv_frame(), indicator_payload=_indicator_payload(include_rsi=False))

    assert fake.captions == ["RSI omitted for shorter history."]


def test_render_chart_error_shows_user_guidance() -> None:
    """Error helper should show plain-language warning with next action hint."""

    fake = FakeStreamlit()

    render_chart_error(fake, "AAPL")

    assert len(fake.warnings) == 1
    assert "Try another ticker" in fake.warnings[0]
