import json
import logging
import pickle
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class ModelCandidate:
    path: Path
    metrics: dict[str, Any]
    score: float

    @property
    def model_name(self) -> str:
        return self.path.stem


def _extract_numeric_metrics(metrics: dict[str, Any], flat: dict[str, float], prefix: str = "") -> None:
    for key, value in metrics.items():
        composed = f"{prefix}.{key}" if prefix else key
        if isinstance(value, (int, float)):
            flat[composed.lower()] = float(value)
        elif isinstance(value, dict):
            _extract_numeric_metrics(value, flat, composed)


def _candidate_score(metrics: dict[str, Any]) -> float:
    flat: dict[str, float] = {}
    _extract_numeric_metrics(metrics, flat)

    weighted_f1 = max([v for k, v in flat.items() if "weighted_f1" in k or k.endswith(".f1")] or [0.0])
    accuracy = max([v for k, v in flat.items() if "accuracy" in k] or [0.0])
    precision = max([v for k, v in flat.items() if "precision" in k] or [0.0])
    recall = max([v for k, v in flat.items() if "recall" in k] or [0.0])

    return (weighted_f1 * 0.5) + (accuracy * 0.3) + (precision * 0.1) + (recall * 0.1)


def _tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.lower()))


def _parse_metrics_files(metrics_dir: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    if not metrics_dir.exists():
        return entries

    for path in metrics_dir.rglob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            entries.append({"path": path, "data": data})
        except Exception as exc:
            logger.warning("Skipping unreadable metrics file %s: %s", path, exc)
    return entries


def _match_metrics_to_model(model_path: Path, metrics_entries: list[dict[str, Any]]) -> dict[str, Any]:
    model_tokens = _tokens(model_path.stem)
    best_match: dict[str, Any] = {}
    best_overlap = -1

    for entry in metrics_entries:
        data = entry["data"]
        candidate_tokens = _tokens(entry["path"].stem)
        if isinstance(data, dict) and isinstance(data.get("model"), str):
            candidate_tokens |= _tokens(data["model"])

        overlap = len(model_tokens & candidate_tokens)
        if overlap > best_overlap:
            best_overlap = overlap
            best_match = data if isinstance(data, dict) else {}

    return best_match


def discover_model_files() -> list[Path]:
    settings = get_settings()
    if not settings.artifacts_dir.exists():
        logger.warning("Artifacts directory does not exist: %s", settings.artifacts_dir)
        return []

    models: list[Path] = []
    for extension in settings.model_extensions:
        models.extend(settings.artifacts_dir.rglob(f"*{extension}"))

    return sorted(set(models), key=lambda p: p.stat().st_mtime, reverse=True)


def select_best_model() -> ModelCandidate:
    settings = get_settings()
    model_paths = discover_model_files()
    if not model_paths:
        raise RuntimeError("No model files found in artifacts directory.")

    metrics_entries = _parse_metrics_files(settings.metrics_dir)
    candidates: list[ModelCandidate] = []

    for model_path in model_paths:
        metrics = _match_metrics_to_model(model_path, metrics_entries)
        score = _candidate_score(metrics)

        if score == 0:
            # Prefer newer models when metrics are missing.
            score = model_path.stat().st_mtime / 1e10

        candidates.append(ModelCandidate(path=model_path, metrics=metrics, score=score))

    best_candidate = sorted(candidates, key=lambda c: c.score, reverse=True)[0]
    logger.info(
        "Selected model: %s | score=%.6f | path=%s",
        best_candidate.model_name,
        best_candidate.score,
        best_candidate.path,
    )
    return best_candidate


def load_model(path: Path) -> Any:
    suffix = path.suffix.lower()
    if suffix == ".joblib":
        return joblib.load(path)

    if suffix in {".pkl", ".pickle"}:
        with path.open("rb") as file:
            return pickle.load(file)

    raise ValueError(f"Unsupported model extension: {suffix}")
