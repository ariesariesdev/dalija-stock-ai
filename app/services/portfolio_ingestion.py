"""CSV ingestion and normalization for the Phase 1 summary application."""

from pathlib import Path

import pandas as pd

from app.config import CORE_COLUMNS
from app.domain.portfolio_models import HoldingRecord, IngestionResult


NUMERIC_COLUMNS = (
    "SharesAmount",
    "PurchasePrice",
    "ClosingPrice31_12_2025",
    "ManualSnapshotPrice",
)


def load_portfolio_csv(csv_path: str | Path) -> pd.DataFrame:
    """Load the portfolio CSV using string types to preserve raw values."""

    return pd.read_csv(csv_path, dtype=str)


def normalize_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Reduce the CSV to the supported Phase 1 contract columns only."""

    normalized = pd.DataFrame()
    for column in CORE_COLUMNS:
        normalized[column] = dataframe[column] if column in dataframe.columns else pd.NA
    return normalized


def _coerce_column(dataframe: pd.DataFrame, column: str) -> None:
    """Convert one numeric column while keeping invalid-value metadata."""

    raw_values = dataframe[column]
    stripped = raw_values.fillna("").astype(str).str.strip()
    numeric = pd.to_numeric(stripped.replace("", pd.NA), errors="coerce")
    dataframe[column] = numeric
    dataframe[f"_invalid_{column}"] = stripped.ne("") & numeric.isna()


def coerce_numeric_fields(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Coerce all summary-relevant numeric fields and annotate invalid values."""

    converted = dataframe.copy()
    for column in NUMERIC_COLUMNS:
        _coerce_column(converted, column)
    return converted


def to_holding_records(dataframe: pd.DataFrame) -> tuple[list[HoldingRecord], list[str]]:
    """Translate normalized rows into typed holding records and warnings."""

    holdings: list[HoldingRecord] = []
    warnings: list[str] = []

    for index, row in dataframe.iterrows():
        ticker = str(row["FullTicker"]).strip() if not pd.isna(row["FullTicker"]) else ""
        invalid_fields = tuple(
            column for column in NUMERIC_COLUMNS if bool(row[f"_invalid_{column}"])
        )
        if not ticker:
            warnings.append(
                f"Row {index + 2} has missing FullTicker and will be classified as unsupported."
            )

        holdings.append(
            HoldingRecord(
                full_ticker=ticker,
                shares_amount=None if pd.isna(row["SharesAmount"]) else float(row["SharesAmount"]),
                purchase_price=None if pd.isna(row["PurchasePrice"]) else float(row["PurchasePrice"]),
                closing_price_31_12_2025=(
                    None
                    if pd.isna(row["ClosingPrice31_12_2025"])
                    else float(row["ClosingPrice31_12_2025"])
                ),
                manual_snapshot_price=(
                    None
                    if pd.isna(row["ManualSnapshotPrice"])
                    else float(row["ManualSnapshotPrice"])
                ),
                invalid_numeric_fields=invalid_fields,
            )
        )

    return holdings, warnings


def read_portfolio(csv_path: str | Path) -> IngestionResult:
    """Run the full ingestion flow from CSV file to typed portfolio model."""

    dataframe = load_portfolio_csv(csv_path)
    normalized = normalize_columns(dataframe)
    converted = coerce_numeric_fields(normalized)
    holdings, warnings = to_holding_records(converted)
    return IngestionResult(holdings=holdings, warnings=warnings)
