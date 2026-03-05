# lakehouse/transformations/process_test_batch.py
# ------------------------------------------------------------
# This script processes the TEST dataset for the fraud system.
#
# Pipeline steps:
# 1. Load external parquet datasets
# 2. Merge transaction + identity data
# 3. Apply basic cleaning
# 4. Save processed dataset
#
# Output dataset is saved to:
# lakehouse/processed/test_merged.parquet
# ------------------------------------------------------------

from pathlib import Path
import pandas as pd


# ------------------------------------------------------------
# Directory definitions
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

EXTERNAL_DIR = PROJECT_ROOT / "lakehouse" / "external"

PROCESSED_DIR = PROJECT_ROOT / "lakehouse" / "processed"

# ------------------------------------------------------------
# Load parquet file from external dataset
# ------------------------------------------------------------
def load_external_data(filename: str) -> pd.DataFrame:
    """
    Load a parquet file from the external data directory.

    Parameters
    ----------
    filename : str
        Name of the parquet file

    Returns
    -------
    pd.DataFrame
        Loaded dataset
    """

    file_path = EXTERNAL_DIR / filename    # build path using pathlib

     # pathlib uses the "/" operator to join paths cleanly
    # instead of os.path.join() :contentReference[oaicite:0]{index=0}

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # pandas automatically reads parquet into a DataFrame :contentReference[oaicite:1]{index=1}
    return pd.read_parquet(file_path)

# ------------------------------------------------------------
# Merge test datasets
# ------------------------------------------------------------
def merge_test_data() -> pd.DataFrame:
    """
    Merge transaction and identity test datasets
    using TransactionID as the key.
    """

    print("Loading test_transaction...")
    df_txn = load_external_data("test_transaction.parquet")

    print("Loading test_identity...")
    df_id = load_external_data("test_identity.parquet")

    print("Merging on TransactionID...")

    # left join keeps all transactions
    df_merged = df_txn.merge(df_id, on="TransactionID", how="left")

    return df_merged

# ------------------------------------------------------------
# Basic data cleaning
# ------------------------------------------------------------
def basic_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    # Drop completely empty columns
    df = df.dropna(axis=1, how="all")

    # Optional: drop duplicate rows
    df = df.drop_duplicates()

    return df

# ------------------------------------------------------------
# Save processed dataset
# ------------------------------------------------------------
def save_processed(df: pd.DataFrame) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    output_path = PROCESSED_DIR / "test_merged.parquet"
    df.to_parquet(output_path, index=False)

    print(f"Processed test batch saved to: {output_path}")

# ------------------------------------------------------------
# Main pipeline execution
# ------------------------------------------------------------
def main():
    # Step 1 — merge datasets
    df = merge_test_data()

    # Step 2 — clean dataset
    df_clean = basic_cleaning(df)

    # Step 3 — save processed output
    save_processed(df_clean)

# ------------------------------------------------------------
# Script entry point
# ------------------------------------------------------------
if __name__ == "__main__":
    main()