"""Unit tests for holding classification rules."""

from dataclasses import replace

from app.domain.portfolio_models import HoldingRecord, HoldingState
from app.services.ticker_classification import classify_holding


class FakeProvider:
    """Provider fake used to control support and snapshot lookup outcomes."""

    def __init__(self, supported: dict[str, bool], snapshot: dict[str, float | None]) -> None:
        self.supported = supported
        self.snapshot = snapshot

    def is_supported_symbol(self, ticker: str) -> bool:
        """Return whether a symbol is supported."""
        return self.supported.get(ticker, False)

    def get_snapshot_price(self, ticker: str) -> float | None:
        """Return a snapshot price when available."""
        return self.snapshot.get(ticker)


def _holding(**kwargs: object) -> HoldingRecord:
    base = HoldingRecord(
        full_ticker="AAPL",
        shares_amount=2.0,
        purchase_price=100.0,
        closing_price_31_12_2025=150.0,
        manual_snapshot_price=None,
        invalid_numeric_fields=(),
    )
    return replace(base, **kwargs)


def test_classify_marks_unsupported_when_provider_rejects_symbol() -> None:
    """Provider rejection should mark the holding as unsupported."""
    provider = FakeProvider(supported={"BALTIC.LT": False}, snapshot={})

    classified = classify_holding(_holding(full_ticker="BALTIC.LT"), provider)

    assert classified.state is HoldingState.UNSUPPORTED_SYMBOL


def test_classify_uses_manual_snapshot_fallback_for_summary() -> None:
    """ManualSnapshotPrice should be used when live snapshot is unavailable."""
    provider = FakeProvider(supported={"NVDA": True}, snapshot={"NVDA": None})

    classified = classify_holding(
        _holding(full_ticker="NVDA", closing_price_31_12_2025=None, manual_snapshot_price=455.5),
        provider,
    )

    assert classified.state is HoldingState.SUPPORTED_US
    assert classified.snapshot_price == 455.5
    assert classified.snapshot_source == "manual"


def test_classify_marks_unavailable_when_all_snapshot_sources_missing() -> None:
    """Holdings remain unavailable when live and manual snapshots are both absent."""
    provider = FakeProvider(supported={"NVDA": True}, snapshot={"NVDA": None})

    classified = classify_holding(
        _holding(full_ticker="NVDA", closing_price_31_12_2025=None, manual_snapshot_price=None),
        provider,
    )

    assert classified.state is HoldingState.UNAVAILABLE_PRICE


def test_classify_blank_ticker_as_unsupported() -> None:
    """Blank ticker rows should remain in the model but be unsupported."""
    provider = FakeProvider(supported={}, snapshot={})

    classified = classify_holding(_holding(full_ticker=""), provider)

    assert classified.state is HoldingState.UNSUPPORTED_SYMBOL
