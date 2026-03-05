# ml/monitoring/data_drift.py

import numpy as np
import pandas as pd


def calculate_psi(expected, actual, bins=10):
    """
    Calculate Population Stability Index (PSI)
    """

    expected = np.array(expected)
    actual = np.array(actual)

    breakpoints = np.linspace(0, 100, bins + 1)
    breakpoints = np.percentile(expected, breakpoints)

    expected_counts = np.histogram(expected, breakpoints)[0] / len(expected)
    actual_counts = np.histogram(actual, breakpoints)[0] / len(actual)

    psi = np.sum(
        (actual_counts - expected_counts)
        * np.log((actual_counts + 1e-6) / (expected_counts + 1e-6))
    )

    return psi


def detect_drift(train_df: pd.DataFrame, prod_df: pd.DataFrame):

    drift_report = {}

    for col in train_df.columns:

        psi = calculate_psi(train_df[col], prod_df[col])

        if psi < 0.1:
            status = "stable"
        elif psi < 0.25:
            status = "warning"
        else:
            status = "drift_detected"

        drift_report[col] = {
            "psi": float(psi),
            "status": status,
        }

    return drift_report