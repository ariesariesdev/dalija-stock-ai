"""Integration smoke tests for the Phase 2 summary-to-chart flow."""

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from app.main import render_summary_shell


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures"


class FakeProvider:
    """Fake provider for deterministic Phase 2 integration behavior."""

    def __init__(self, historical_frame: pd.DataFrame | None) -> None:
        """Store deterministic responses for summary and chart pipelines."""

        self.supported = {"AAPL": True, "NVDA": True, "BALTIC.LT": False}
        self.snapshot = {"AAPL": 155.0, "NVDA": None, "BALTIC.LT": None}
        self.historical_frame = historical_frame

    def is_supported_symbol(self, ticker: str) -> bool:
        """Return support status for integration smoke fixtures."""

        return self.supported.get(ticker, False)

    def get_snapshot_price(self, ticker: str) -> float | None:
        """Return snapshot data for deterministic summary calculations."""

        return self.snapshot.get(ticker)

    def get_historical_ohlcv(self, ticker: str, period: str = "1y") -> pd.DataFrame | None:
        """Return pre-seeded historical data for selected symbols."""

        return self.historical_frame


class FakeStreamlit:
    """Integration facade that captures summary metrics and chart operations."""

    def __init__(self) -> None:
        """Initialize captured calls and deterministic widget defaults."""

        self.metrics: list[tuple[str, str]] = []
        self.messages: list[str] = []
        self.plots: list[object] = []
        self.toggle_labels: list[tuple[str, bool]] = []

    def title(self, value: str) -> None:
        """Capture title output."""

        self.messages.append(value)

    def subheader(self, value: str) -> None:
        """Capture subheader output."""

        self.messages.append(value)

    def write(self, value: str) -> None:
        """Capture generic text output."""

        self.messages.append(str(value))

    def metric(self, label: str, value: str) -> None:
        """Capture KPI metric output."""

        self.metrics.append((label, value))

    def columns(self, count: int) -> list["FakeStreamlit"]:
        """Return stand-in column objects for KPI rendering."""

        return [self for _ in range(count)]

    def divider(self) -> None:
        """Capture divider calls in the flow."""

        self.messages.append("divider")

    def toggle(self, label: str, value: bool = False) -> bool:
        """Keep unsupported symbols hidden by default in this smoke test."""

        self.toggle_labels.append((label, value))
        return value

    def selectbox(
        self,
        label: str,
        options: list[str | None],
        index: int = 0,
        placeholder: str | None = None,
    ) -> str:
        """Always choose first non-placeholder symbol to exercise chart rendering path."""

        for option in options:
            if option is not None:
                return option
        raise AssertionError("No selectable options were provided")

    def caption(self, value: str) -> None:
        """Capture selector captions."""

        self.messages.append(value)

    def plotly_chart(self, figure: object, use_container_width: bool = False) -> None:
        """Capture chart rendering calls."""

        self.plots.append((figure, use_container_width))

    def warning(self, value: str) -> None:
        """Capture warning output for negative-path assertions."""

        self.messages.append(value)


def _historical_frame() -> pd.DataFrame:
    """Return historical data for chart rendering smoke flow."""

    dates = pd.date_range("2026-01-01", periods=40, freq="D", tz="UTC")
    close_values = [100.0 + index for index in range(40)]
    return pd.DataFrame(
        {
            "Date": list(dates),
            "Open": [value - 1.0 for value in close_values],
            "High": [value + 2.0 for value in close_values],
            "Low": [value - 2.0 for value in close_values],
            "Close": close_values,
            "Volume": [1000 + index * 5 for index in range(40)],
        }
    )


def test_phase3_summary_to_chart_smoke_offline() -> None:
    """Summary, selector, indicator controls, and chart should render together offline."""

    fake_st = FakeStreamlit()
    provider = FakeProvider(historical_frame=_historical_frame())

    render_summary_shell(
        st_module=fake_st,
        csv_path=FIXTURE_DIR / "portfolio_smoke.csv",
        provider=provider,
        snapshot_timestamp=datetime(2026, 5, 30, 12, 0, tzinfo=UTC),
        historical_fallback_dir=FIXTURE_DIR / "history",
    )

    assert len(fake_st.metrics) >= 4
    assert len(fake_st.plots) == 1
    assert any(message == "divider" for message in fake_st.messages)
    assert any(label == "SMA (20)" and default is True for label, default in fake_st.toggle_labels)
    assert any(label == "RSI (14)" and default is True for label, default in fake_st.toggle_labels)

    figure = fake_st.plots[0][0]
    trace_names = {trace.name for trace in figure.data}
    assert "SMA (20)" in trace_names
    assert "RSI (14)" in trace_names
