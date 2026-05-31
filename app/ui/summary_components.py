"""Presentation helpers for the Phase 1 summary shell."""

from app.domain.portfolio_models import StateSummary, SummaryKPI


def render_kpi_cards(st_module: object, summary: SummaryKPI) -> None:
    """Render KPI cards using a Streamlit-compatible module interface."""

    st_module.subheader("Portfolio Summary KPIs")
    columns = st_module.columns(5)
    columns[0].metric("Total Holdings", str(summary.total_holdings_count))
    columns[1].metric("Unavailable Price", str(summary.unavailable_price_holdings_count))
    columns[2].metric("Unsupported Symbols", str(summary.unsupported_holdings_count))
    columns[3].metric("Total Portfolio Value", summary.total_portfolio_value_formatted)
    columns[4].metric("Snapshot Timestamp", summary.snapshot_timestamp.isoformat())


def render_data_state_section(
    st_module: object,
    state_summary: StateSummary,
    warnings: list[str],
) -> None:
    """Render plain-language explanations for unsupported and unavailable states."""

    st_module.subheader("Data Availability State")
    st_module.write(
        "The summary remains usable even when some holdings are unsupported or unavailable."
    )
    st_module.write(
        f"Unavailable price holdings: {state_summary.unavailable_count}. "
        f"Unsupported holdings: {state_summary.unsupported_count}."
    )
    if warnings:
        st_module.write(f"Data-quality warnings: {state_summary.warning_count}")
        for warning in warnings:
            st_module.write(f"- {warning}")
