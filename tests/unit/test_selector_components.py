"""Unit tests for stock selector rendering helpers."""

from app.domain.portfolio_models import HoldingRecord, HoldingState
from app.ui.selector_components import render_stock_selector, render_unsupported_toggle


class FakeStreamlit:
    """Minimal streamlit facade to capture selector interactions for tests."""

    def __init__(self, toggle_value: bool = False, selected_index: int = 0) -> None:
        """Store deterministic widget outputs and capture rendered options."""

        self.toggle_value = toggle_value
        self.selected_index = selected_index
        self.selectbox_options: list[str | None] = []
        self.captions: list[str] = []

    def toggle(self, label: str, value: bool = False) -> bool:
        """Return a deterministic toggle state for test assertions."""

        return self.toggle_value

    def selectbox(
        self,
        label: str,
        options: list[str | None],
        index: int = 0,
        placeholder: str | None = None,
    ) -> str | None:
        """Capture selectbox options and return the selected test option."""

        self.selectbox_options = options
        return options[self.selected_index]

    def caption(self, value: str) -> None:
        """Capture caption messages emitted by selector helpers."""

        self.captions.append(value)


def _holding(ticker: str, state: HoldingState) -> HoldingRecord:
    """Create a simple holding model for selector behavior tests."""

    return HoldingRecord(
        full_ticker=ticker,
        shares_amount=1.0,
        purchase_price=100.0,
        closing_price_31_12_2025=120.0,
        manual_snapshot_price=None,
        invalid_numeric_fields=(),
        state=state,
    )


def test_render_toggle_defaults_to_hidden_unsupported() -> None:
    """Unsupported toggle should default to False when not user-overridden."""

    fake = FakeStreamlit(toggle_value=False)

    value = render_unsupported_toggle(fake, default=False)

    assert value is False


def test_selector_hides_unsupported_by_default() -> None:
    """Unsupported symbols should not appear in selectbox options by default."""

    fake = FakeStreamlit(selected_index=1)
    holdings = [
        _holding("AAPL", HoldingState.SUPPORTED_US),
        _holding("NVDA", HoldingState.UNAVAILABLE_PRICE),
        _holding("BALTIC.LT", HoldingState.UNSUPPORTED_SYMBOL),
    ]

    selected = render_stock_selector(fake, holdings, show_unsupported=False)

    assert selected.full_ticker == "AAPL"
    assert fake.selectbox_options == [None, "AAPL", "NVDA"]
    assert any("hidden" in caption.lower() for caption in fake.captions)


def test_selector_groups_unsupported_at_bottom_when_shown() -> None:
    """Unsupported symbols should be listed after supported options when shown."""

    fake = FakeStreamlit(selected_index=3)
    holdings = [
        _holding("BALTIC.LT", HoldingState.UNSUPPORTED_SYMBOL),
        _holding("AAPL", HoldingState.SUPPORTED_US),
        _holding("NVDA", HoldingState.UNAVAILABLE_PRICE),
    ]

    selected = render_stock_selector(fake, holdings, show_unsupported=True)

    assert fake.selectbox_options == [None, "AAPL", "NVDA", "BALTIC.LT"]
    assert selected.full_ticker == "BALTIC.LT"
