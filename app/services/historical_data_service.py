"""Historical OHLCV retrieval with live-provider and JSON fallback support."""

from pathlib import Path

import pandas as pd
import streamlit as st

from app.adapters.yfinance_adapter import YFinanceSnapshotProvider
from app.config import PROJECT_ROOT
from app.services.interfaces import HistoricalDataProvider


# AIDEV-NOTE: Keep fallback loading non-fatal so chart failures remain non-blocking in UI flows.
def _normalize_ohlcv_frame(frame: pd.DataFrame) -> pd.DataFrame | None:
    """Return a normalized OHLCV frame with required columns or None if invalid."""

    required_columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
    if frame.empty:
        return None
    if "Date" not in frame.columns:
        first_column = frame.columns[0]
        frame = frame.rename(columns={first_column: "Date"})
    if any(column not in frame.columns for column in required_columns):
        return None
    normalized = frame[required_columns].copy()
    normalized["Date"] = pd.to_datetime(normalized["Date"], utc=True, errors="coerce")
    normalized = normalized.dropna(subset=["Date"])
    if normalized.empty:
        return None
    return normalized


def _load_fallback_json(ticker: str, fallback_dir: Path) -> pd.DataFrame | None:
    """Load fallback OHLCV data from a per-ticker JSON file when it exists."""

    fallback_file = fallback_dir / f"{ticker.upper()}.json"
    if not fallback_file.exists():
        return None
    try:
        frame = pd.read_json(fallback_file)
        return _normalize_ohlcv_frame(frame)
    except Exception:
        return None


def _load_ohlcv(
    ticker: str,
    provider: HistoricalDataProvider,
    period: str = "1y",
    fallback_dir: Path | None = None,
) -> pd.DataFrame | None:
    """Resolve OHLCV with precedence: live provider first, JSON fallback second."""

    resolved_fallback_dir = fallback_dir or (PROJECT_ROOT / "source-files" / "history")
    live_frame = provider.get_historical_ohlcv(ticker=ticker, period=period)
    if live_frame is not None:
        normalized_live = _normalize_ohlcv_frame(live_frame)
        if normalized_live is not None:
            return normalized_live
    return _load_fallback_json(ticker=ticker, fallback_dir=resolved_fallback_dir)


@st.cache_data(show_spinner=False)
def fetch_ohlcv(ticker: str, period: str = "1y") -> pd.DataFrame | None:
    """Fetch OHLCV data with caching for repeated ticker selections in one session."""

    provider = YFinanceSnapshotProvider()
    # AIDEV-NOTE: Keep loader uncached for direct unit testing while caching this public wrapper.
    return _load_ohlcv(ticker=ticker, provider=provider, period=period)
