# src/data/build_curated_dataset.py

from pathlib import Path
import pandas as pd
import logging


# -------------------------------------------------
# Logging Setup
# -------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# -------------------------------------------------
# Paths
# -------------------------------------------------
PROJECT_ROOT = Path("D:/Dev/enterprise-aws-data-lakehouse-ml-system")
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_CURATED = PROJECT_ROOT / "data" / "curated"

DATA_CURATED.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------
# Load Datasets
# -------------------------------------------------
def load_datasets():
    logger.info("Loading foundation dataset...")
    foundation = pd.read_parquet(DATA_PROCESSED / "train_foundation.parquet")

    logger.info("Loading behavioral dataset...")
    behavioral = pd.read_parquet(DATA_PROCESSED / "train_behavioral.parquet")

    logger.info(f"Foundation shape: {foundation.shape}")
    logger.info(f"Behavioral shape: {behavioral.shape}")

    return foundation, behavioral


# -------------------------------------------------
# Clean Merge Logic
# -------------------------------------------------
def merge_datasets(foundation: pd.DataFrame, behavioral: pd.DataFrame) -> pd.DataFrame:

    logger.info("Starting clean merge process...")

    # Ensure merge key exists
    if "TransactionID" not in foundation.columns:
        raise ValueError("TransactionID missing in foundation dataset")

    if "TransactionID" not in behavioral.columns:
        raise ValueError("TransactionID missing in behavioral dataset")

    # Drop duplicate columns from behavioral
    duplicate_cols = set(foundation.columns).intersection(set(behavioral.columns))
    duplicate_cols.remove("TransactionID")

    if duplicate_cols:
        logger.info(f"Dropping duplicate columns from behavioral: {duplicate_cols}")
        behavioral = behavioral.drop(columns=list(duplicate_cols))

    # Left merge (foundation is truth)
    curated = foundation.merge(
        behavioral,
        on="TransactionID",
        how="left",
        validate="one_to_one"
    )

    logger.info(f"Curated dataset shape: {curated.shape}")

    return curated


# -------------------------------------------------
# Save
# -------------------------------------------------
def save_dataset(df: pd.DataFrame):
    output_path = DATA_CURATED / "train_curated.parquet"
    df.to_parquet(output_path, index=False)
    logger.info(f"Curated dataset saved to {output_path}")


# -------------------------------------------------
# Main
# -------------------------------------------------
if __name__ == "__main__":

    foundation_df, behavioral_df = load_datasets()
    curated_df = merge_datasets(foundation_df, behavioral_df)
    save_dataset(curated_df)

    logger.info("Curated dataset build completed successfully.")