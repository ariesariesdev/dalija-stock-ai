"""Integration smoke tests for the Phase 1 summary pipeline."""

from datetime import UTC, datetime
from pathlib import Path

from app.main import render_summary_shell, run_summary_pipeline


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures"


class FakeProvider:
    """Provider fake for smoke testing the summary pipeline."""

    def __init__(self) -> None:
        self.supported = {"AAPL": True, "NVDA": True, "BALTIC.LT": False}
        self.snapshot = {"AAPL": 155.0, "NVDA": None, "BALTIC.LT": None}

    def is_supported_symbol(self, ticker: str) -> bool:
        """Return whether a symbol is supported."""
        return self.supported.get(ticker, False)

    def get_snapshot_price(self, ticker: str) -> float | None:
        """Return a snapshot price when available."""
        return self.snapshot.get(ticker)


class FakeStreamlit:
    """Minimal Streamlit facade used to capture summary rendering output."""

    def __init__(self) -> None:
        self.metrics: list[tuple[str, str]] = []
        self.messages: list[str] = []
        self._session_state: dict[str, object] = {}

    def title(self, value: str) -> None:
        """Capture title output."""
        self.messages.append(value)

    def subheader(self, value: str) -> None:
        """Capture subheader output."""
        self.messages.append(value)

    def write(self, value: str) -> None:
        """Capture general text output."""
        self.messages.append(str(value))

    def metric(self, label: str, value: str) -> None:
        """Capture KPI metric output."""
        self.metrics.append((label, value))

    def columns(self, count: int) -> list["FakeStreamlit"]:
        """Return stand-in column objects for metric rendering."""
        return [self for _ in range(count)]

    def divider(self) -> None:
        """Capture divider output."""

        self.messages.append("divider")

    def toggle(self, label: str, value: bool = False) -> bool:
        """Return deterministic toggle state for non-interactive smoke tests."""

        return value

    def selectbox(
        self,
        label: str,
        options: list[str | None],
        index: int = 0,
        placeholder: str | None = None,
    ) -> str | None:
        """Return placeholder option so chart selection remains opt-in in Phase 1 smoke."""

        return options[0]

    def caption(self, value: str) -> None:
        """Capture caption output."""

        self.messages.append(value)

    def warning(self, value: str) -> None:
        """Capture warning output."""

        self.messages.append(value)

    def plotly_chart(self, figure: object, use_container_width: bool = False) -> None:
        """Capture chart rendering calls without requiring plotly rendering backend."""

        self.messages.append("plot")


def test_startup_pipeline_runs_without_crash() -> None:
    """The startup summary pipeline should complete and return KPI state."""
    result = run_summary_pipeline(
        csv_path=FIXTURE_DIR / "portfolio_smoke.csv",
        provider=FakeProvider(),
        snapshot_timestamp=datetime(2026, 5, 30, 12, 0, tzinfo=UTC),
    )

    assert result.summary.total_holdings_count == 3
    assert result.summary.unsupported_holdings_count == 1


def test_render_summary_shell_outputs_kpis_and_state_messages() -> None:
    """The summary shell should render KPI cards and state explanations."""
    fake_st = FakeStreamlit()

    render_summary_shell(
        st_module=fake_st,
        csv_path=FIXTURE_DIR / "portfolio_smoke.csv",
        provider=FakeProvider(),
        snapshot_timestamp=datetime(2026, 5, 30, 12, 0, tzinfo=UTC),
    )

    assert len(fake_st.metrics) >= 4
    assert any("unsupported" in message.lower() for message in fake_st.messages)
