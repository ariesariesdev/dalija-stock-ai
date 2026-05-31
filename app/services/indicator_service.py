"""Indicator computation helpers for the Phase 3 chart-analysis experience."""

from dataclasses import dataclass

import pandas as pd

try:
    import pandas_ta as pandas_ta
except Exception:  # pragma: no cover - exercised indirectly through fallback behavior.
    pandas_ta = None


@dataclass(frozen=True)
class IndicatorSettings:
    """Fixed-parameter toggle state for the Phase 3 indicator controls."""

    sma20: bool = True
    ema20: bool = False
    bollinger_20_2: bool = False
    fibonacci: bool = False
    rsi14: bool = True


@dataclass(frozen=True)
class IndicatorSeries:
    """Chart-ready line series generated from OHLCV data."""

    name: str
    x: tuple[pd.Timestamp, ...]
    y: tuple[float, ...]


@dataclass(frozen=True)
class FibonacciLevel:
    """A named horizontal retracement level derived from the loaded 1-year range."""

    label: str
    value: float


@dataclass(frozen=True)
class IndicatorPayload:
    """Collection of overlay series, oscillator data, and non-blocking notices."""

    overlay_series: tuple[IndicatorSeries, ...] = ()
    rsi_series: IndicatorSeries | None = None
    fibonacci_levels: tuple[FibonacciLevel, ...] = ()
    notices: tuple[str, ...] = ()


def _series_from_values(name: str, dates: pd.Series, values: pd.Series) -> IndicatorSeries | None:
    """Return a chart-ready series when at least one non-null value exists."""

    cleaned = pd.DataFrame({"Date": dates, "Value": values}).dropna(subset=["Value"])
    if cleaned.empty:
        return None
    return IndicatorSeries(
        name=name,
        x=tuple(pd.Timestamp(value) for value in cleaned["Date"]),
        y=tuple(float(value) for value in cleaned["Value"]),
    )


def _sma(close_values: pd.Series, length: int) -> pd.Series:
    """Return a simple moving average using pandas-ta when available."""

    if pandas_ta is not None:
        return pandas_ta.sma(close_values, length=length)
    return close_values.rolling(window=length, min_periods=length).mean()


def _ema(close_values: pd.Series, length: int) -> pd.Series:
    """Return an exponential moving average using a safe fallback formula."""

    if pandas_ta is not None:
        return pandas_ta.ema(close_values, length=length)
    return close_values.ewm(span=length, adjust=False).mean()


def _bollinger(close_values: pd.Series, length: int, std_multiplier: float) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Return upper, middle, and lower Bollinger Band series."""

    if pandas_ta is not None:
        bands = pandas_ta.bbands(close_values, length=length, std=std_multiplier)
        if bands is not None:
            upper_name = next((name for name in bands.columns if "BBU" in name.upper()), None)
            middle_name = next((name for name in bands.columns if "BBM" in name.upper()), None)
            lower_name = next((name for name in bands.columns if "BBL" in name.upper()), None)
            if upper_name and middle_name and lower_name:
                return bands[upper_name], bands[middle_name], bands[lower_name]
            if len(bands.columns) >= 3:
                return bands.iloc[:, 2], bands.iloc[:, 1], bands.iloc[:, 0]

    middle = close_values.rolling(window=length, min_periods=length).mean()
    deviation = close_values.rolling(window=length, min_periods=length).std(ddof=0)
    upper = middle + (deviation * std_multiplier)
    lower = middle - (deviation * std_multiplier)
    return upper, middle, lower


def _rsi(close_values: pd.Series, length: int) -> pd.Series:
    """Return an RSI series using pandas-ta or an equivalent formula."""

    if pandas_ta is not None:
        return pandas_ta.rsi(close_values, length=length)

    deltas = close_values.diff()
    gains = deltas.clip(lower=0.0)
    losses = -deltas.clip(upper=0.0)
    average_gain = gains.rolling(window=length, min_periods=length).mean()
    average_loss = losses.rolling(window=length, min_periods=length).mean()
    relative_strength = average_gain / average_loss.replace(0.0, pd.NA)
    return 100 - (100 / (1 + relative_strength))


def _fibonacci_levels(ohlcv_df: pd.DataFrame) -> tuple[FibonacciLevel, ...]:
    """Return standard retracement levels from the loaded 1-year high and low range."""

    high_value = float(ohlcv_df["High"].max())
    low_value = float(ohlcv_df["Low"].min())
    price_range = high_value - low_value
    percentages = (("23.6%", 0.236), ("38.2%", 0.382), ("50.0%", 0.5), ("61.8%", 0.618), ("78.6%", 0.786))
    return tuple(
        FibonacciLevel(label=label, value=high_value - (price_range * ratio))
        for label, ratio in percentages
    )


def build_indicator_payload(ohlcv_df: pd.DataFrame, settings: IndicatorSettings) -> IndicatorPayload:
    """Build overlay, oscillator, and Fibonacci data for the Phase 3 chart flow."""

    if ohlcv_df.empty:
        return IndicatorPayload(notices=("Indicator data is unavailable because the price history is empty.",))

    overlay_series: list[IndicatorSeries] = []
    notices: list[str] = []
    dates = ohlcv_df["Date"]
    close_values = ohlcv_df["Close"]
    row_count = len(ohlcv_df)

    if settings.sma20:
        sma_series = _series_from_values("SMA (20)", dates, _sma(close_values, length=20))
        if sma_series is not None:
            overlay_series.append(sma_series)
        else:
            notices.append("SMA (20) omitted because the selected ticker has insufficient history.")

    if settings.ema20:
        ema_series = _series_from_values("EMA (20)", dates, _ema(close_values, length=20))
        if ema_series is not None:
            overlay_series.append(ema_series)

    if settings.bollinger_20_2:
        upper, middle, lower = _bollinger(close_values, length=20, std_multiplier=2.0)
        upper_series = _series_from_values("Bollinger Upper", dates, upper)
        middle_series = _series_from_values("Bollinger Middle", dates, middle)
        lower_series = _series_from_values("Bollinger Lower", dates, lower)
        if upper_series and middle_series and lower_series:
            overlay_series.extend((upper_series, middle_series, lower_series))
        else:
            notices.append("Bollinger Bands omitted because the selected ticker has insufficient history.")

    rsi_series: IndicatorSeries | None = None
    if settings.rsi14:
        rsi_series = _series_from_values("RSI (14)", dates, _rsi(close_values, length=14))
        if rsi_series is None:
            notices.append("RSI omitted because the selected ticker has insufficient history.")

    fibonacci_levels: tuple[FibonacciLevel, ...] = ()
    if settings.fibonacci and row_count > 0:
        fibonacci_levels = _fibonacci_levels(ohlcv_df)

    # AIDEV-NOTE: Keep indicator failures partial and visible so the base chart remains usable.
    deduped_notices = tuple(dict.fromkeys(notices))
    return IndicatorPayload(
        overlay_series=tuple(overlay_series),
        rsi_series=rsi_series,
        fibonacci_levels=fibonacci_levels,
        notices=deduped_notices,
    )