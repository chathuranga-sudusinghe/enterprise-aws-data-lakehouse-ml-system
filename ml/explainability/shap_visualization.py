# ml/explainability/shap_visualization.py

import os
import shap
import matplotlib.pyplot as plt
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
PLOT_DIR = BASE_DIR / "model_artifacts" / "shap_plots"


def _ensure_plot_dir():
    os.makedirs(PLOT_DIR, exist_ok=True)


def plot_beeswarm(shap_values, save: bool = True, filename: str = "beeswarm.png"):
    """
    Generate SHAP beeswarm plot.
    """

    _ensure_plot_dir()

    shap.plots.beeswarm(shap_values, show=False)

    if save:
        path = os.path.join(PLOT_DIR, filename)
        plt.savefig(path, bbox_inches="tight")

    plt.close()


def plot_summary(shap_values, X, save: bool = True, filename: str = "summary.png"):
    """
    Generate SHAP summary plot.
    """

    _ensure_plot_dir()

    shap.summary_plot(shap_values, X, show=False)

    if save:
        path = os.path.join(PLOT_DIR, filename)
        plt.savefig(path, bbox_inches="tight")

    plt.close()


def plot_bar(shap_values, X, save: bool = True, filename: str = "bar.png"):
    """
    Generate SHAP bar importance plot.
    """

    _ensure_plot_dir()

    shap.summary_plot(shap_values, X, plot_type="bar", show=False)

    if save:
        path = os.path.join(PLOT_DIR, filename)
        plt.savefig(path, bbox_inches="tight")

    plt.close()