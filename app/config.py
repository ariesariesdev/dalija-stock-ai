"""Central configuration values for the Phase 1 summary application."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_CSV = PROJECT_ROOT / "source-files" / "Porfelis20260221.csv"
CORE_COLUMNS = [
    "FullTicker",
    "SharesAmount",
    "PurchasePrice",
    "ClosingPrice31_12_2025",
    "ManualSnapshotPrice",
]
