"""Provider interface contracts used by the Phase 1 services."""

from typing import Protocol

import pandas as pd


class SnapshotPriceProvider(Protocol):
    """Protocol for symbol support checks and snapshot price retrieval."""

    def is_supported_symbol(self, ticker: str) -> bool:
        """Return True when the provider can serve the given ticker symbol."""

    def get_snapshot_price(self, ticker: str) -> float | None:
        """Return the latest snapshot price for the ticker when available."""


class HistoricalDataProvider(Protocol):
    """Protocol for historical OHLCV retrieval used by charting services."""

    def get_historical_ohlcv(self, ticker: str, period: str = "1y") -> pd.DataFrame | None:
        """Return historical OHLCV rows for a ticker when data is available."""
