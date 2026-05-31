"""UI helpers for the Phase 3 technical indicator control surface."""

from app.services.indicator_service import IndicatorSettings


def render_indicator_controls(
    st_module: object,
    defaults: IndicatorSettings | None = None,
) -> IndicatorSettings:
    """Render the fixed-parameter Phase 3 toggles and return the chosen settings."""

    resolved_defaults = defaults or IndicatorSettings()
    st_module.caption("Technical indicators update the chart in place for the selected ticker.")
    return IndicatorSettings(
        sma20=bool(st_module.toggle("SMA (20)", value=resolved_defaults.sma20)),
        ema20=bool(st_module.toggle("EMA (20)", value=resolved_defaults.ema20)),
        bollinger_20_2=bool(
            st_module.toggle("Bollinger Bands (20, 2)", value=resolved_defaults.bollinger_20_2)
        ),
        fibonacci=bool(st_module.toggle("Fibonacci Retracement", value=resolved_defaults.fibonacci)),
        rsi14=bool(st_module.toggle("RSI (14)", value=resolved_defaults.rsi14)),
    )