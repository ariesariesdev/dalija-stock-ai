"""Yahoo Finance adapter for snapshot support checks and price lookup."""

import pandas as pd
import yfinance as yf

from app.services.interfaces import SnapshotPriceProvider


class YFinanceSnapshotProvider(SnapshotPriceProvider):
    """Provider adapter that queries Yahoo Finance for symbol support and prices."""

    # AIDEV-NOTE: Provider failures must remain non-fatal so unsupported and unavailable states stay transparent.
    def is_supported_symbol(self, ticker: str) -> bool:
        """Return True when the ticker appears retrievable from Yahoo Finance."""

        if not ticker:
            return False
        try:
            history = yf.Ticker(ticker).history(period="1d")
            return not history.empty
        except Exception:
            return False

    def get_snapshot_price(self, ticker: str) -> float | None:
        """Return a latest close or fast-info price when available."""

        if not ticker:
            return None
        try:
            ticker_obj = yf.Ticker(ticker)
            fast_info = getattr(ticker_obj, "fast_info", {})
            if isinstance(fast_info, dict):
                last_price = fast_info.get("lastPrice")
                if last_price is not None:
                    return float(last_price)
            history = ticker_obj.history(period="1d")
            if history.empty:
                return None
            return float(history["Close"].iloc[-1])
        except Exception:
            return None

    def get_historical_ohlcv(self, ticker: str, period: str = "1y") -> pd.DataFrame | None:
        """Return historical OHLCV rows with a normalized Date column when available."""

        if not ticker:
            return None
        try:
            history = yf.Ticker(ticker).history(period=period)
            if history.empty:
                return None
            frame = history.reset_index()
            first_column = frame.columns[0]
            if first_column != "Date":
                frame = frame.rename(columns={first_column: "Date"})
            return frame[["Date", "Open", "High", "Low", "Close", "Volume"]]
        except Exception:
            return None
