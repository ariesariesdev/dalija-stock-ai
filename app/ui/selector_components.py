"""Stock selector and unsupported-toggle UI helpers for Phase 2 flow."""

from app.domain.portfolio_models import HoldingRecord, HoldingState


def render_unsupported_toggle(st_module: object, default: bool = False) -> bool:
    """Render a toggle for showing unsupported symbols in the stock selector."""

    return bool(
        st_module.toggle(
            "Show unsupported symbols",
            value=default,
        )
    )


def render_stock_selector(
    st_module: object,
    holdings: list[HoldingRecord],
    show_unsupported: bool,
) -> HoldingRecord | None:
    """Render a searchable selector and return the selected holding when chosen."""

    supported_like = [
        holding
        for holding in holdings
        if holding.state is not HoldingState.UNSUPPORTED_SYMBOL
    ]
    unsupported = [
        holding
        for holding in holdings
        if holding.state is HoldingState.UNSUPPORTED_SYMBOL
    ]
    visible_holdings = supported_like + (unsupported if show_unsupported else [])

    if not show_unsupported and unsupported:
        st_module.caption(
            f"{len(unsupported)} unsupported symbol(s) hidden. Enable toggle to show."
        )

    # AIDEV-NOTE: Keep placeholder as first option to avoid accidental default chart fetches.
    options: list[str | None] = [None] + [holding.full_ticker for holding in visible_holdings]
    selected_ticker = st_module.selectbox(
        "Select stock",
        options=options,
        index=0,
        placeholder="Select a stock...",
    )
    if selected_ticker is None:
        return None

    holdings_by_ticker = {holding.full_ticker: holding for holding in visible_holdings}
    return holdings_by_ticker.get(selected_ticker)
