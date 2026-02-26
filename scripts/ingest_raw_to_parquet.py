"""
ingest_raw_to_parquet.py

Purpose:
    Convert RAW CSV files into Parquet format (no normalization).
    This script performs format conversion only.

Layer:
    RAW → RAW (format conversion only)
"""

import sys
import logging
from pathlib import Path
import pandas as pd


# ---------------------------------------------------
# Logging Configuration
# ---------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------
# Paths
# ---------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"


# ---------------------------------------------------
# Conversion Function
# ---------------------------------------------------

def convert_csv_to_parquet(csv_path: Path) -> None:
    """
    Convert a single CSV file to Parquet format.
    Output file will be saved in RAW directory.
    """

    try:
        logger.info(f"Reading CSV: {csv_path.name}")

        df = pd.read_csv(csv_path)

        output_path = csv_path.with_suffix(".parquet")

        logger.info(f"Saving Parquet: {output_path.name}")

        df.to_parquet(
            output_path,
            engine="pyarrow",
            compression="snappy",
            index=False
        )

        logger.info(f"Successfully converted: {csv_path.name}")

    except Exception as e:
        logger.exception(f"Failed to convert {csv_path.name}")
        sys.exit(1)


# ---------------------------------------------------
# Main Pipeline
# ---------------------------------------------------

def main() -> None:

    if not RAW_DIR.exists():
        logger.error("RAW directory does not exist.")
        sys.exit(1)

    csv_files = list(RAW_DIR.glob("*.csv"))

    if not csv_files:
        logger.warning("No CSV files found in RAW directory.")
        return

    logger.info(f"Found {len(csv_files)} CSV files.")

    for csv_file in csv_files:
        parquet_file = csv_file.with_suffix(".parquet")

        if parquet_file.exists():
            logger.info(f"Skipping (already exists): {parquet_file.name}")
            continue

        convert_csv_to_parquet(csv_file)

    logger.info("All CSV files processed successfully.")


if __name__ == "__main__":
    main()