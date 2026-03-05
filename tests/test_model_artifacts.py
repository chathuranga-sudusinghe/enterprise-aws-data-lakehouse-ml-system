import json
import joblib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = PROJECT_ROOT / "model_artifacts"


def test_model_file_exists():
    model_path = ARTIFACT_DIR / "fraud_lgbm_v1.pkl"
    assert model_path.exists()


def test_threshold_file_exists():
    threshold_path = ARTIFACT_DIR / "threshold_v1.json"
    assert threshold_path.exists()


def test_feature_columns_file_exists():
    feature_path = ARTIFACT_DIR / "feature_columns_v1.json"
    assert feature_path.exists()


def test_model_can_load():
    model_path = ARTIFACT_DIR / "fraud_lgbm_v1.pkl"
    model = joblib.load(model_path)
    assert model is not None


def test_threshold_valid():
    threshold_path = ARTIFACT_DIR / "threshold_v1.json"
    with open(threshold_path) as f:
        threshold = json.load(f)["threshold"]

    assert 0 <= threshold <= 1


def test_feature_columns_valid():
    feature_path = ARTIFACT_DIR / "feature_columns_v1.json"
    with open(feature_path) as f:
        features = json.load(f)

    assert isinstance(features, list)
    assert len(features) > 0