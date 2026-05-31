"""Streamlit entrypoint and pipeline orchestration for Phase 1 to Phase 3 flows."""

from datetime import UTC, datetime
from pathlib import Path
import sys
from typing import MutableMapping

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    # Ensure absolute imports like `from app...` work when Streamlit runs this file directly.
    sys.path.insert(0, str(PROJECT_ROOT))

from app.adapters.yfinance_adapter import YFinanceSnapshotProvider
from app.config import DEFAULT_SOURCE_CSV
from app.domain.portfolio_models import HoldingRecord, PipelineResult, StateSummary
from app.services.indicator_service import IndicatorSettings, build_indicator_payload
from app.services.kpi_service import compute_summary_kpis
from app.services.historical_data_service import _load_ohlcv, fetch_ohlcv
from app.services.portfolio_ingestion import read_portfolio
from app.services.ticker_classification import classify_holdings
from app.ui.chart_components import render_chart_error, render_stock_chart
from app.ui.indicator_controls import render_indicator_controls
from app.ui.selector_components import render_stock_selector, render_unsupported_toggle
from app.ui.summary_components import render_data_state_section, render_kpi_cards


def run_summary_pipeline(
    csv_path: str | Path = DEFAULT_SOURCE_CSV,
    provider: object | None = None,
    snapshot_timestamp: datetime | None = None,
) -> PipelineResult:
    """Run ingestion, classification, and KPI aggregation for the summary shell."""

    provider_instance = provider if provider is not None else YFinanceSnapshotProvider()
    effective_timestamp = snapshot_timestamp or datetime.now(UTC)
    ingestion = read_portfolio(csv_path)
    classified = classify_holdings(ingestion.holdings, provider_instance)
    summary = compute_summary_kpis(
        ingestion.holdings,
        provider_instance,
        snapshot_timestamp=effective_timestamp,
    )
    state_summary = StateSummary(
        unavailable_count=summary.unavailable_price_holdings_count,
        unsupported_count=summary.unsupported_holdings_count,
        warning_count=len(ingestion.warnings),
    )
    return PipelineResult(
        holdings=classified,
        summary=summary,
        state_summary=state_summary,
        warnings=ingestion.warnings,
    )


def render_summary_shell(
    st_module: object = st,
    csv_path: str | Path = DEFAULT_SOURCE_CSV,
    provider: object | None = None,
    snapshot_timestamp: datetime | None = None,
    historical_fallback_dir: Path | None = None,
) -> PipelineResult:
    """Render the Streamlit dashboard shell and return pipeline output."""

    st_module.title("Dalija Stock AI Dashboard")
    result = run_summary_pipeline(
        csv_path=csv_path,
        provider=provider,
        snapshot_timestamp=snapshot_timestamp,
    )
    render_kpi_cards(st_module, result.summary)
    render_data_state_section(st_module, result.state_summary, result.warnings)
    render_selection_shell(
        st_module=st_module,
        holdings=result.holdings,
        provider=provider,
        historical_fallback_dir=historical_fallback_dir,
    )
    return result


def _get_session_state(st_module: object) -> MutableMapping[str, object]:
    """Return a mutable session-state mapping for streamlit and test doubles."""

    state = getattr(st_module, "session_state", None)
    if state is not None:
        return state
    if not hasattr(st_module, "_session_state"):
        setattr(st_module, "_session_state", {})
    return getattr(st_module, "_session_state")


def render_selection_shell(
    st_module: object,
    holdings: list[HoldingRecord],
    provider: object | None,
    historical_fallback_dir: Path | None,
) -> None:
    """Render Phase 2 and Phase 3 selection, controls, and chart sections."""

    st_module.divider()
    st_module.subheader("Stock Selection and Technical Analysis")

    session_state = _get_session_state(st_module)
    show_unsupported = bool(session_state.get("phase2_show_unsupported", False))
    updated_toggle = render_unsupported_toggle(st_module, default=show_unsupported)
    session_state["phase2_show_unsupported"] = updated_toggle

    selected_holding = render_stock_selector(
        st_module=st_module,
        holdings=holdings,
        show_unsupported=updated_toggle,
    )
    if selected_holding is None:
        st_module.write("Select a stock to view a 1-year candlestick chart.")
        return

    selected_ticker = selected_holding.full_ticker.strip()
    session_state["phase2_selected_ticker"] = selected_ticker

    if provider is not None and hasattr(provider, "get_historical_ohlcv"):
        ohlcv_frame = _load_ohlcv(
            ticker=selected_ticker,
            provider=provider,
            period="1y",
            fallback_dir=historical_fallback_dir,
        )
    else:
        ohlcv_frame = fetch_ohlcv(ticker=selected_ticker)

    if ohlcv_frame is None:
        render_chart_error(st_module, selected_ticker)
        return

    indicator_defaults = _get_indicator_state(session_state)
    indicator_settings = render_indicator_controls(st_module, defaults=indicator_defaults)
    _persist_indicator_state(session_state, indicator_settings)
    indicator_payload = build_indicator_payload(ohlcv_frame, indicator_settings)
    render_stock_chart(
        st_module,
        selected_ticker,
        ohlcv_frame,
        indicator_payload=indicator_payload,
    )


def _auto_render_streamlit_entrypoint() -> None:
    """Render app automatically when executed by Streamlit runtime."""

    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        if get_script_run_ctx() is not None:
            render_summary_shell()
    except Exception:
        return


def _get_indicator_state(session_state: MutableMapping[str, object]) -> IndicatorSettings:
    """Return Phase 3 indicator state with session-safe defaults applied."""

    return IndicatorSettings(
        sma20=bool(session_state.setdefault("phase3_indicator_sma20", True)),
        ema20=bool(session_state.setdefault("phase3_indicator_ema20", False)),
        bollinger_20_2=bool(session_state.setdefault("phase3_indicator_bollinger_20_2", False)),
        fibonacci=bool(session_state.setdefault("phase3_indicator_fibonacci", False)),
        rsi14=bool(session_state.setdefault("phase3_indicator_rsi14", True)),
    )


def _persist_indicator_state(session_state: MutableMapping[str, object], settings: IndicatorSettings) -> None:
    """Persist Phase 3 indicator choices into session state."""

    session_state["phase3_indicator_sma20"] = settings.sma20
    session_state["phase3_indicator_ema20"] = settings.ema20
    session_state["phase3_indicator_bollinger_20_2"] = settings.bollinger_20_2
    session_state["phase3_indicator_fibonacci"] = settings.fibonacci
    session_state["phase3_indicator_rsi14"] = settings.rsi14


_auto_render_streamlit_entrypoint()
