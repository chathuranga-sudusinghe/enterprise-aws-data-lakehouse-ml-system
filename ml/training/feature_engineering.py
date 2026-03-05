from __future__ import annotations

import logging
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ============================================================
# Custom Exceptions
# ============================================================

class FeatureEngineeringError(Exception):
    """Base exception for feature engineering errors."""


class SchemaMismatchError(FeatureEngineeringError):
    """Raised when required columns are missing."""


# ============================================================
# Fraud Feature Engineering Engine (Production v2)
# ============================================================

class FraudFeatureEngineeringEngine:
    """
    Enterprise-grade leakage-safe feature engineering engine.

    Fit phase (TRAIN ONLY):
        - Learn categorical levels
        - Learn frequency maps
        - Learn UID aggregation statistics
        - Store final feature schema

    Transform phase (Train / Val / Test / API):
        - Create deterministic features
        - Apply frozen statistics
        - Align schema
    """

    REQUIRED_COLUMNS = [
        "TransactionDT",
        "TransactionAmt",
        "card1",
        "card2",
        "card3",
        "card4",
        "addr1",
    ]

    TARGET_COLUMN = "isFraud"

    def __init__(self) -> None:

        # Schema
        self.feature_schema: List[str] = []
        self.categorical_cols: List[str] = []
        self.category_levels: Dict[str, List[str]] = {}

        # Frequency Encoding
        self.freq_cols = ["card1", "card2", "card3", "card4"]
        self.freq_maps: Dict[str, Dict] = {}

        # UID Aggregations
        self.uid_txn_count_map: Dict[str, int] = {}
        self.uid_amt_mean_map: Dict[str, float] = {}
        self.uid_amt_std_map: Dict[str, float] = {}
        self.uid_amt_median_map: Dict[str, float] = {}

        self.global_amt_mean: float = 0.0
        self.global_amt_std: float = 1.0

        logger.info("FraudFeatureEngineeringEngine initialized.")

    # ============================================================
    # Validation
    # ============================================================

    def _validate_input(self, X: pd.DataFrame) -> None:
        missing_cols = [
            col for col in self.REQUIRED_COLUMNS if col not in X.columns
        ]
        if missing_cols:
            raise SchemaMismatchError(
                f"Missing required columns: {missing_cols}"
            )

    # ============================================================
    # FIT (TRAIN ONLY)
    # ============================================================

    def fit(self, X: pd.DataFrame) -> None:
        """
        Learn statistical mappings from TRAIN data only.
        """

        try:
            logger.info("Starting fit phase.")
            self._validate_input(X)

            X = X.copy()

            # ----------------------------------------------------
            # Time Features
            # ----------------------------------------------------
            X["day"] = X["TransactionDT"] // 86400
            X["hour"] = (X["TransactionDT"] // 3600) % 24

            # ----------------------------------------------------
            # UID
            # ----------------------------------------------------
            X["uid"] = (
                X["card1"].astype(str) + "_" + X["addr1"].astype(str)
            )

            # ----------------------------------------------------
            # Frequency Encoding (TRAIN ONLY)
            # ----------------------------------------------------
            for col in self.freq_cols:
                freq = X[col].value_counts(dropna=False)
                self.freq_maps[col] = freq.to_dict()

            # IMPORTANT:
            # Create frequency columns during FIT so they are included
            # in frozen feature schema
            for col in self.freq_cols:
                X[f"{col}_freq"] = (
                    X[col]
                    .map(self.freq_maps[col])
                    .fillna(0)
                )

            # ----------------------------------------------------
            # UID Aggregations (TRAIN ONLY)
            # ----------------------------------------------------
            uid_group = X.groupby("uid")

            self.uid_txn_count_map = (
                 uid_group.size().to_dict()
            )

            self.uid_amt_mean_map = (
                uid_group["TransactionAmt"].mean().to_dict()
            )

            std_series = (
                uid_group["TransactionAmt"].std().fillna(0)
            )
            self.uid_amt_std_map = std_series.to_dict()

            self.uid_amt_median_map = (
                uid_group["TransactionAmt"].median().to_dict()
            )

            self.global_amt_mean = float(X["TransactionAmt"].mean())
            self.global_amt_std = float(
                X["TransactionAmt"].std() or 1.0
            )

            # ----------------------------------------------------
            # Drop helper columns before freezing schema
            # ----------------------------------------------------
            drop_cols = ["TransactionID", "uid"]
            if self.TARGET_COLUMN in X.columns:
                drop_cols.append(self.TARGET_COLUMN)

            X = X.drop(columns=drop_cols, errors="ignore")

            # ----------------------------------------------------
            # Store categorical schema
            # ----------------------------------------------------
            # Reset to prevent duplicate accumulation if fit() is called twice
            self.categorical_cols = []
            self.category_levels = {}

            for col in X.columns:
                if pd.api.types.is_object_dtype(X[col]):
                    self.categorical_cols.append(col)
                    self.category_levels[col] = (
                        X[col]
                        .astype("category")
                        .cat.categories
                        .tolist()
                    )

            self.feature_schema = X.columns.tolist()

            logger.info("Fit phase completed successfully.")

        except Exception as e:
            logger.exception("Error during fit.")
            raise FeatureEngineeringError(str(e)) from e

    # ============================================================
    # TRANSFORM
    # ============================================================

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Apply frozen mappings safely.
        """

        try:
            logger.info("Starting transform phase.")
            self._validate_input(X)

            X = X.copy()

            # Time
            X["day"] = X["TransactionDT"] // 86400
            X["hour"] = (X["TransactionDT"] // 3600) % 24

            # UID
            X["uid"] = (
                X["card1"].astype(str) + "_" + X["addr1"].astype(str)
            )

            # Frequency Encoding
            for col in self.freq_cols:
                X[f"{col}_freq"] = (
                    X[col]
                    .map(self.freq_maps.get(col, {}))
                    .fillna(0)
                )

            # UID Aggregations
            X["uid_txn_count"] = (
                X["uid"]
                .map(self.uid_txn_count_map)
                .fillna(1)
            )

            X["uid_amt_mean"] = (
                X["uid"]
                .map(self.uid_amt_mean_map)
                .fillna(self.global_amt_mean)
            )

            X["uid_amt_std"] = (
                X["uid"]
                .map(self.uid_amt_std_map)
                .fillna(self.global_amt_std)
            )

            X["uid_amt_median"] = (
                X["uid"]
                .map(self.uid_amt_median_map)
                .fillna(self.global_amt_mean)
            )

            X["uid_amt_deviation"] = (
                (X["TransactionAmt"] - X["uid_amt_mean"])
                / (X["uid_amt_std"] + 1e-6)
            )

            # Drop helper columns
            drop_cols = ["TransactionID", "uid"]
            if self.TARGET_COLUMN in X.columns:
                drop_cols.append(self.TARGET_COLUMN)

            X = X.drop(columns=drop_cols, errors="ignore")

            # Align schema
            for col in self.feature_schema:
                if col not in X.columns:
                    X[col] = 0

            X = X[self.feature_schema]

            # Freeze categorical
            for col in self.categorical_cols:
                if col in X.columns:
                    X[col] = pd.Categorical(
                        X[col],
                        categories=self.category_levels[col],
                    )

            logger.info("Transform phase completed.")
            return X

        except Exception as e:
            logger.exception("Error during transform.")
            raise FeatureEngineeringError(str(e)) from e

    # ============================================================
    # FIT + TRANSFORM
    # ============================================================

    def fit_transform(
        self,
        X_train: pd.DataFrame,
        X_val: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:

        self.fit(X_train)
        return self.transform(X_train), self.transform(X_val)