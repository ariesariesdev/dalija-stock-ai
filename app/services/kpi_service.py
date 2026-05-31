"""Deterministic KPI aggregation for the Phase 1 summary dashboard."""

from datetime import UTC, datetime
from decimal import Decimal, ROUND_HALF_UP

from app.domain.portfolio_models import HoldingRecord, HoldingState, SummaryKPI
from app.services.interfaces import SnapshotPriceProvider
from app.services.ticker_classification import classify_holdings


def format_kpi_value(value: float) -> str:
    """Format KPI values using deterministic HALF_UP rounding to two decimals."""

    quantized = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{quantized:.2f}"


def compute_summary_kpis(
    holdings: list[HoldingRecord],
    provider: SnapshotPriceProvider,
    snapshot_timestamp: datetime | None = None,
) -> SummaryKPI:
    """Compute summary KPIs from classified holdings and snapshot metadata."""

    classified = classify_holdings(holdings, provider)
    timestamp = snapshot_timestamp or datetime.now(UTC)

    unavailable_count = sum(
        1 for holding in classified if holding.state is HoldingState.UNAVAILABLE_PRICE
    )
    unsupported_count = sum(
        1 for holding in classified if holding.state is HoldingState.UNSUPPORTED_SYMBOL
    )

    total_value = 0.0
    for holding in classified:
        if (
            holding.state is HoldingState.SUPPORTED_US
            and holding.snapshot_price is not None
            and holding.shares_amount is not None
        ):
            total_value += holding.snapshot_price * holding.shares_amount

    rounded_total = float(format_kpi_value(total_value))
    return SummaryKPI(
        total_holdings_count=len(classified),
        unavailable_price_holdings_count=unavailable_count,
        unsupported_holdings_count=unsupported_count,
        total_portfolio_value=rounded_total,
        total_portfolio_value_formatted=format_kpi_value(total_value),
        snapshot_timestamp=timestamp,
    )
