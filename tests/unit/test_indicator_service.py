"""Unit tests for Phase 3 indicator calculations and payload shaping."""

import pandas as pd

from app.services.indicator_service import IndicatorSettings, build_indicator_payload


def _ohlcv_frame(row_count: int = 40) -> pd.DataFrame:
    """Return deterministic OHLCV data long enough for all Phase 3 indicators."""

    base_dates = pd.date_range("2026-01-01", periods=row_count, freq="D", tz="UTC")
    close_values = [100.0 + index for index in range(row_count)]
    return pd.DataFrame(
        {
            "Date": base_dates,
            "Open": [value - 1.0 for value in close_values],
            "High": [value + 2.0 for value in close_values],
            "Low": [value - 2.0 for value in close_values],
            "Close": close_values,
            "Volume": [1000 + index * 10 for index in range(row_count)],
        }
    )


def test_build_indicator_payload_returns_selected_series() -> None:
    """Payload should include enabled overlay series, RSI, and Fibonacci levels."""

    payload = build_indicator_payload(
        _ohlcv_frame(),
        IndicatorSettings(
            sma20=True,
            ema20=True,
            bollinger_20_2=True,
            fibonacci=True,
            rsi14=True,
        ),
    )

    overlay_names = {series.name for series in payload.overlay_series}
    assert "SMA (20)" in overlay_names
    assert "EMA (20)" in overlay_names
    assert "Bollinger Upper" in overlay_names
    assert "Bollinger Middle" in overlay_names
    assert "Bollinger Lower" in overlay_names
    assert payload.rsi_series is not None
    assert payload.rsi_series.name == "RSI (14)"
    assert len(payload.fibonacci_levels) == 5
    assert payload.notices == ()


def test_build_indicator_payload_short_history_returns_notice_without_failure() -> None:
    """Short history should keep the chart viable and report missing indicator context."""

    payload = build_indicator_payload(
        _ohlcv_frame(row_count=10),
        IndicatorSettings(
            sma20=True,
            ema20=False,
            bollinger_20_2=True,
            fibonacci=True,
            rsi14=True,
        ),
    )

    overlay_names = {series.name for series in payload.overlay_series}
    assert "SMA (20)" not in overlay_names
    assert "Bollinger Upper" not in overlay_names
    assert payload.rsi_series is None
    assert len(payload.fibonacci_levels) == 5
    assert any("insufficient history" in notice.lower() for notice in payload.notices)
