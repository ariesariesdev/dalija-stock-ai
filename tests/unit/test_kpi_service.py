"""Unit tests for deterministic KPI aggregation."""

from dataclasses import replace
from datetime import UTC, datetime

from app.domain.portfolio_models import HoldingRecord
from app.services.kpi_service import compute_summary_kpis, format_kpi_value


class FakeProvider:
    """Provider fake used by KPI tests."""

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
        shares_amount=1.0,
        purchase_price=100.0,
        closing_price_31_12_2025=120.0,
        manual_snapshot_price=None,
        invalid_numeric_fields=(),
    )
    return replace(base, **kwargs)


def test_compute_summary_kpis_excludes_unavailable_and_unsupported_from_total() -> None:
    """Only supported holdings with resolved snapshots should contribute to total value."""
    holdings = [
        _holding(full_ticker="AAPL", shares_amount=2.0),
        _holding(full_ticker="NVDA", shares_amount=1.0, closing_price_31_12_2025=None, manual_snapshot_price=455.5),
        _holding(full_ticker="BALTIC.LT", shares_amount=3.0),
    ]
    provider = FakeProvider(
        supported={"AAPL": True, "NVDA": True, "BALTIC.LT": False},
        snapshot={"AAPL": 140.0, "NVDA": None, "BALTIC.LT": None},
    )
    timestamp = datetime(2026, 5, 30, 12, 0, tzinfo=UTC)

    summary = compute_summary_kpis(holdings, provider, snapshot_timestamp=timestamp)

    assert summary.total_holdings_count == 3
    assert summary.unavailable_price_holdings_count == 0
    assert summary.unsupported_holdings_count == 1
    assert summary.total_portfolio_value == 735.5
    assert summary.snapshot_timestamp == timestamp


def test_compute_summary_kpis_is_deterministic_for_same_inputs() -> None:
    """Repeated runs with the same inputs and timestamp should produce identical output."""
    holdings = [_holding(full_ticker="AAPL", shares_amount=2.0)]
    provider = FakeProvider(supported={"AAPL": True}, snapshot={"AAPL": 140.0})
    timestamp = datetime(2026, 5, 30, 12, 0, tzinfo=UTC)

    first = compute_summary_kpis(holdings, provider, snapshot_timestamp=timestamp)
    second = compute_summary_kpis(holdings, provider, snapshot_timestamp=timestamp)

    assert first == second


def test_format_kpi_value_uses_half_up_two_decimal_rounding() -> None:
    """KPI formatting should centralize deterministic two-decimal HALF_UP rounding."""
    assert format_kpi_value(1.005) == "1.01"
    assert format_kpi_value(99.994) == "99.99"
