"""Unit tests for Phase 3 indicator control rendering."""

from app.services.indicator_service import IndicatorSettings
from app.ui.indicator_controls import render_indicator_controls


class FakeStreamlit:
    """Minimal streamlit facade for indicator toggle tests."""

    def __init__(self, toggle_values: dict[str, bool] | None = None) -> None:
        """Capture toggle labels and return configured values."""

        self.toggle_values = toggle_values or {}
        self.toggle_calls: list[tuple[str, bool]] = []
        self.captions: list[str] = []

    def toggle(self, label: str, value: bool = False) -> bool:
        """Return the configured toggle choice or the provided default."""

        self.toggle_calls.append((label, value))
        return self.toggle_values.get(label, value)

    def caption(self, value: str) -> None:
        """Capture descriptive UI text for assertions."""

        self.captions.append(value)


def test_render_indicator_controls_uses_phase3_defaults() -> None:
    """First render should enable only SMA and RSI by default."""

    fake = FakeStreamlit()

    settings = render_indicator_controls(fake)

    assert settings == IndicatorSettings(
        sma20=True,
        ema20=False,
        bollinger_20_2=False,
        fibonacci=False,
        rsi14=True,
    )
    assert len(fake.toggle_calls) == 5


def test_render_indicator_controls_returns_user_toggle_choices() -> None:
    """User overrides should be reflected in the returned settings object."""

    fake = FakeStreamlit(
        toggle_values={
            "SMA (20)": False,
            "EMA (20)": True,
            "Bollinger Bands (20, 2)": True,
            "Fibonacci Retracement": True,
            "RSI (14)": False,
        }
    )

    settings = render_indicator_controls(fake)

    assert settings == IndicatorSettings(
        sma20=False,
        ema20=True,
        bollinger_20_2=True,
        fibonacci=True,
        rsi14=False,
    )
