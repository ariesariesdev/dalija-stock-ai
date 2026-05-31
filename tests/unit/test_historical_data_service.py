"""Unit tests for historical OHLCV loading and fallback behavior."""

from pathlib import Path

import pandas as pd

from app.services.historical_data_service import _load_ohlcv, fetch_ohlcv


class FakeHistoricalProvider:
    """Fake provider used to simulate live historical data responses."""

    def __init__(self, frame: pd.DataFrame | None) -> None:
        """Store the frame that should be returned for all ticker requests."""

        self._frame = frame

    def get_historical_ohlcv(self, ticker: str, period: str = "1y") -> pd.DataFrame | None:
        """Return deterministic data to avoid network calls in tests."""

        return self._frame


def _build_live_frame() -> pd.DataFrame:
    """Return a minimal OHLCV frame used as a predictable live response."""

    return pd.DataFrame(
        {
            "Date": [pd.Timestamp("2026-01-01T00:00:00Z")],
            "Open": [100.0],
            "High": [102.0],
            "Low": [99.0],
            "Close": [101.5],
            "Volume": [1000],
        }
    )


def test_load_ohlcv_uses_live_provider_first(tmp_path: Path) -> None:
    """Live provider data should be used when available and non-empty."""

    provider = FakeHistoricalProvider(_build_live_frame())

    frame = _load_ohlcv("AAPL", provider, fallback_dir=tmp_path)

    assert frame is not None
    assert list(frame.columns) == ["Date", "Open", "High", "Low", "Close", "Volume"]
    assert float(frame.iloc[0]["Close"]) == 101.5


def test_load_ohlcv_falls_back_to_json_when_live_missing() -> None:
    """Fallback JSON should load when live provider returns no data."""

    provider = FakeHistoricalProvider(None)
    fallback_dir = Path(__file__).resolve().parents[1] / "fixtures" / "history"

    frame = _load_ohlcv("AAPL", provider, fallback_dir=fallback_dir)

    assert frame is not None
    assert len(frame) == 5
    assert "Close" in frame.columns


def test_load_ohlcv_returns_none_when_live_and_fallback_unavailable(tmp_path: Path) -> None:
    """The loader should return None when no source can provide OHLCV data."""

    provider = FakeHistoricalProvider(None)

    frame = _load_ohlcv("MSFT", provider, fallback_dir=tmp_path)

    assert frame is None


def test_fetch_ohlcv_returns_none_without_any_source(monkeypatch: object) -> None:
    """Cached wrapper should return None cleanly when loader cannot resolve data."""

    from app.services import historical_data_service as module

    def _fake_loader(
        ticker: str,
        provider: object,
        period: str = "1y",
        fallback_dir: Path | None = None,
    ) -> pd.DataFrame | None:
        return None

    monkeypatch.setattr(module, "_load_ohlcv", _fake_loader)
    module.fetch_ohlcv.clear()

    frame = fetch_ohlcv("UNKNOWN", period="1y")

    assert frame is None
