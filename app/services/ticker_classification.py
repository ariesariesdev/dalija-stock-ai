"""Holding classification and snapshot resolution rules for Phase 1."""

from dataclasses import replace

from app.domain.portfolio_models import HoldingRecord, HoldingState
from app.services.interfaces import SnapshotPriceProvider


# AIDEV-NOTE: ManualSnapshotPrice is intentionally limited to summary fallback only in Phase 1.
def classify_holding(holding: HoldingRecord, provider: SnapshotPriceProvider) -> HoldingRecord:
    """Classify one holding and resolve the summary snapshot source."""

    ticker = holding.full_ticker.strip()
    if not ticker:
        return replace(
            holding,
            state=HoldingState.UNSUPPORTED_SYMBOL,
            state_reason="missing_ticker",
            snapshot_price=None,
            snapshot_source=None,
        )

    if not provider.is_supported_symbol(ticker):
        return replace(
            holding,
            state=HoldingState.UNSUPPORTED_SYMBOL,
            state_reason="provider_unsupported",
            snapshot_price=None,
            snapshot_source=None,
        )

    provider_snapshot = provider.get_snapshot_price(ticker)
    if provider_snapshot is not None and holding.shares_amount is not None:
        return replace(
            holding,
            state=HoldingState.SUPPORTED_US,
            state_reason="live_snapshot",
            snapshot_price=float(provider_snapshot),
            snapshot_source="live",
        )

    if holding.manual_snapshot_price is not None and holding.shares_amount is not None:
        return replace(
            holding,
            state=HoldingState.SUPPORTED_US,
            state_reason="manual_snapshot",
            snapshot_price=float(holding.manual_snapshot_price),
            snapshot_source="manual",
        )

    return replace(
        holding,
        state=HoldingState.UNAVAILABLE_PRICE,
        state_reason="missing_snapshot",
        snapshot_price=None,
        snapshot_source=None,
    )


def classify_holdings(
    holdings: list[HoldingRecord],
    provider: SnapshotPriceProvider,
) -> list[HoldingRecord]:
    """Classify the full holdings set using the configured provider."""

    return [classify_holding(holding, provider) for holding in holdings]
