"""Domain models for holdings, ingestion, and summary KPI results."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class HoldingState(StrEnum):
    """Canonical state values assigned during Phase 1 classification."""

    SUPPORTED_US = "supported_us"
    UNSUPPORTED_SYMBOL = "unsupported_symbol"
    UNAVAILABLE_PRICE = "unavailable_price"


@dataclass(frozen=True)
class HoldingRecord:
    """Normalized portfolio holding record used across the summary pipeline."""

    full_ticker: str
    shares_amount: float | None
    purchase_price: float | None
    closing_price_31_12_2025: float | None
    manual_snapshot_price: float | None
    invalid_numeric_fields: tuple[str, ...]
    state: HoldingState | None = None
    state_reason: str | None = None
    snapshot_price: float | None = None
    snapshot_source: str | None = None


@dataclass(frozen=True)
class IngestionResult:
    """Result of CSV ingestion with parsed holdings and non-fatal warnings."""

    holdings: list[HoldingRecord]
    warnings: list[str]


@dataclass(frozen=True)
class SummaryKPI:
    """Deterministic summary KPI output for the Phase 1 dashboard."""

    total_holdings_count: int
    unavailable_price_holdings_count: int
    unsupported_holdings_count: int
    total_portfolio_value: float
    total_portfolio_value_formatted: str
    snapshot_timestamp: datetime


@dataclass(frozen=True)
class StateSummary:
    """Aggregated state counts shown in plain-language UI sections."""

    unavailable_count: int
    unsupported_count: int
    warning_count: int


@dataclass(frozen=True)
class PipelineResult:
    """Complete pipeline output used by the summary UI shell."""

    holdings: list[HoldingRecord]
    summary: SummaryKPI
    state_summary: StateSummary
    warnings: list[str]
