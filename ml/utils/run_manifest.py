# ml/utils/run_manifest.py

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np


# Project root: .../ml/utils/run_manifest.py -> parents[2] = repo root
PROJECT_ROOT = Path(__file__).resolve().parents[2]


# Convert numpy types → Python native types
def _json_safe(obj: Any) -> Any:
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    return obj


# Calculate SHA256 hash of a file
def _file_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


# Get Git commit SHA
def _git_sha(project_root: Path) -> Optional[str]:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(project_root),
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return out or None
    except Exception:
        return None


# Generate pipeline run id
def new_run_id(prefix: str = "run") -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{ts}"


@dataclass
class RunManifest:
    run_id: str
    created_utc: str
    git_sha: Optional[str]
    stage: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    metrics: Dict[str, Any]


# Write manifest.json
def write_manifest(manifest: RunManifest, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_dict = _json_safe(asdict(manifest))

    path = out_dir / "manifest.json"
    path.write_text(json.dumps(manifest_dict, indent=2, sort_keys=True))

    return path


# Build training manifest
def build_training_manifest(
    project_root: Path,
    run_id: str,
    stage: str,
    train_parquet: Path,
    model_path: Path,
    metrics: Dict[str, Any],
    extra_outputs: Optional[Dict[str, Any]] = None,
) -> RunManifest:

    created = datetime.now(timezone.utc).isoformat()
    git_sha = _git_sha(project_root)

    inputs = {
        "train_parquet": str(train_parquet),
        "train_parquet_sha256": _file_sha256(train_parquet)
        if train_parquet.exists()
        else None,
    }

    outputs = {
        "model_path": str(model_path),
        "model_exists": model_path.exists(),
    }

    if extra_outputs:
        outputs.update(extra_outputs)

    return RunManifest(
        run_id=run_id,
        created_utc=created,
        git_sha=git_sha,
        stage=stage,
        inputs=inputs,
        outputs=outputs,
        metrics=metrics,
    )


# Build batch inference manifest
def build_batch_manifest(
    project_root: Path,
    run_id: str,
    stage: str,
    curated_parquet: Path,
    predictions_parquet: Path,
    model_path: Path,
    extra_inputs: Optional[Dict[str, Any]] = None,
) -> RunManifest:

    created = datetime.now(timezone.utc).isoformat()
    git_sha = _git_sha(project_root)

    inputs = {
        "curated_parquet": str(curated_parquet),
        "curated_parquet_sha256": _file_sha256(curated_parquet)
        if curated_parquet.exists()
        else None,
    }

    if extra_inputs:
        inputs.update(extra_inputs)

    outputs = {
        "predictions_parquet": str(predictions_parquet),
        "predictions_exists": predictions_parquet.exists(),
        "model_path": str(model_path),
        "model_exists": model_path.exists(),
    }

    return RunManifest(
        run_id=run_id,
        created_utc=created,
        git_sha=git_sha,
        stage=stage,
        inputs=inputs,
        outputs=outputs,
        metrics={},
    )