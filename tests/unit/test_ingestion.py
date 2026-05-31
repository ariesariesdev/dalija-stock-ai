"""Unit tests for portfolio CSV ingestion and normalization."""

from pathlib import Path

from app.services.portfolio_ingestion import (
    coerce_numeric_fields,
    load_portfolio_csv,
    normalize_columns,
    read_portfolio,
)


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures"


def test_normalize_columns_ignores_trailing_empty_columns() -> None:
    """Only Phase 1 contract columns should remain after normalization."""
    dataframe = load_portfolio_csv(FIXTURE_DIR / "portfolio_edge_cases.csv")

    normalized = normalize_columns(dataframe)

    assert normalized.columns.tolist() == [
        "FullTicker",
        "SharesAmount",
        "PurchasePrice",
        "ClosingPrice31_12_2025",
        "ManualSnapshotPrice",
    ]


def test_missing_manual_snapshot_column_is_non_fatal() -> None:
    """Older CSV files without ManualSnapshotPrice should still ingest successfully."""
    dataframe = load_portfolio_csv(FIXTURE_DIR / "portfolio_without_manual.csv")

    normalized = normalize_columns(dataframe)

    assert "ManualSnapshotPrice" in normalized.columns
    assert normalized["ManualSnapshotPrice"].isna().all()


def test_coerce_numeric_fields_marks_invalid_values() -> None:
    """Invalid numeric values should be converted to missing with invalid flags."""
    dataframe = load_portfolio_csv(FIXTURE_DIR / "portfolio_edge_cases.csv")
    normalized = normalize_columns(dataframe)

    converted = coerce_numeric_fields(normalized)

    assert converted.loc[1, "SharesAmount"] != converted.loc[1, "SharesAmount"]
    assert bool(converted.loc[1, "_invalid_SharesAmount"]) is True
    assert bool(converted.loc[3, "_invalid_PurchasePrice"]) is True


def test_read_portfolio_preserves_missing_ticker_warning() -> None:
    """Rows without ticker should remain available for unsupported classification with warnings."""
    result = read_portfolio(FIXTURE_DIR / "portfolio_edge_cases.csv")

    assert len(result.holdings) == 4
    assert any("missing FullTicker" in warning for warning in result.warnings)
