import csv
import json
import logging
import pickle
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from app.core.config import get_settings
from app.services.rag_retriever import RagRuntime, load_rag_runtime

logger = logging.getLogger(__name__)


@dataclass
class LoadedArtifact:
    name: str
    path: str
    object: Any
    metrics: dict[str, Any]


@dataclass
class RuntimeModels:
    classifier: LoadedArtifact
    vectorizer: LoadedArtifact
    response_model: LoadedArtifact
    response_corpus: list[dict[str, str]]
    rag_runtime: RagRuntime | None = None
    response_mode: str = "traditional"


def _tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.lower()))


def _load_serialized(path: Path) -> Any:
    if path.suffix.lower() == ".joblib":
        return joblib.load(path)
    with path.open("rb") as handle:
        return pickle.load(handle)


def _parse_metrics(metrics_dir: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    if not metrics_dir.exists():
        return results
    for path in metrics_dir.rglob("*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            results.append({"path": path, "data": payload})
        except Exception as exc:
            logger.warning("Skipping invalid metrics file %s: %s", path, exc)
    return results


def _score_from_metrics(payload: dict[str, Any]) -> float:
    numbers: list[float] = []

    def walk(data: Any) -> None:
        if isinstance(data, dict):
            for value in data.values():
                walk(value)
        elif isinstance(data, (int, float)):
            numbers.append(float(data))

    walk(payload)
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)


def _metrics_for_file(path: Path, metrics_entries: list[dict[str, Any]]) -> dict[str, Any]:
    model_tokens = _tokens(path.stem)
    best_overlap = -1
    best_payload: dict[str, Any] = {}

    for entry in metrics_entries:
        payload = entry["data"]
        candidate_tokens = _tokens(entry["path"].stem)
        if isinstance(payload, dict) and isinstance(payload.get("model"), str):
            candidate_tokens |= _tokens(payload["model"])
        overlap = len(model_tokens & candidate_tokens)
        if overlap > best_overlap:
            best_overlap = overlap
            best_payload = payload if isinstance(payload, dict) else {}
    return best_payload


def _discover_serialized_files(artifacts_dir: Path, extensions: tuple[str, ...]) -> list[Path]:
    files: list[Path] = []
    for ext in extensions:
        files.extend(artifacts_dir.rglob(f"*{ext}"))
    return sorted(set(files), key=lambda item: item.stat().st_mtime, reverse=True)


def _is_vectorizer(obj: Any, path: Path) -> bool:
    cls_name = obj.__class__.__name__.lower()
    return (
        ("vectorizer" in cls_name or "tfidf" in cls_name or "countvectorizer" in cls_name)
        and hasattr(obj, "transform")
    ) or ("vectorizer" in path.stem.lower())


def _is_classifier(obj: Any, path: Path) -> bool:
    if hasattr(obj, "predict") and hasattr(obj, "predict_proba") and not _is_vectorizer(obj, path):
        return True
    if isinstance(obj, dict) and any(key in obj for key in ["classifier", "model"]):
        return True
    return "classif" in path.stem.lower() or "logreg" in path.stem.lower()


def _is_response_model(obj: Any, path: Path) -> bool:
    stem = path.stem.lower()
    if any(token in stem for token in ["response", "reply", "generation", "rag", "retrieval"]):
        return True
    if hasattr(obj, "generate") or callable(obj):
        return True
    return False


def _discover_response_corpus(artifacts_dir: Path) -> tuple[str, list[dict[str, str]]]:
    best_path = ""
    best_rows: list[dict[str, str]] = []
    best_score = -1

    for csv_path in artifacts_dir.rglob("*.csv"):
        try:
            with csv_path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                fields = [field.lower() for field in (reader.fieldnames or [])]
                if not fields:
                    continue
                score = 0
                if "input" in fields or "input_clean" in fields:
                    score += 2
                if "output" in fields or "output_clean" in fields or "rag_response" in fields:
                    score += 3
                if "category" in fields or "true_category" in fields:
                    score += 1

                if score <= 0:
                    continue

                rows: list[dict[str, str]] = []
                for index, row in enumerate(reader):
                    if index >= 1500:
                        break
                    rows.append({(k or "").lower(): (v or "") for k, v in row.items()})

                if score > best_score and rows:
                    best_score = score
                    best_path = str(csv_path)
                    best_rows = rows
        except Exception as exc:
            logger.warning("Skipping response corpus candidate %s: %s", csv_path, exc)

    return best_path, best_rows


def _select_classifier_and_vectorizer(model_files: list[Path], metrics_entries: list[dict[str, Any]]) -> tuple[LoadedArtifact, LoadedArtifact]:
    classifier_candidates: list[LoadedArtifact] = []
    vectorizer_candidates: list[LoadedArtifact] = []

    for file_path in model_files:
        try:
            obj = _load_serialized(file_path)
        except Exception as exc:
            logger.warning("Skipping model file %s: %s", file_path, exc)
            continue

        metrics = _metrics_for_file(file_path, metrics_entries)
        if _is_vectorizer(obj, file_path):
            vectorizer_candidates.append(
                LoadedArtifact(file_path.stem, str(file_path), obj, metrics)
            )
        if _is_classifier(obj, file_path):
            classifier_candidates.append(
                LoadedArtifact(file_path.stem, str(file_path), obj, metrics)
            )

        if isinstance(obj, dict):
            if "vectorizer" in obj and hasattr(obj["vectorizer"], "transform"):
                vectorizer_candidates.append(
                    LoadedArtifact(f"{file_path.stem}_vectorizer", str(file_path), obj["vectorizer"], metrics)
                )
            model_key = obj.get("classifier") or obj.get("model")
            if model_key is not None and hasattr(model_key, "predict"):
                classifier_candidates.append(
                    LoadedArtifact(f"{file_path.stem}_classifier", str(file_path), model_key, metrics)
                )

    if not classifier_candidates:
        fallback = _build_fallback_classifier_from_dataset(get_settings().artifacts_dir)
        if fallback is None:
            raise RuntimeError("Could not discover a compatible classification model in artifacts.")
        classifier_candidates.append(fallback[0])
        vectorizer_candidates.append(fallback[1])

    classifier = sorted(
        classifier_candidates,
        key=lambda candidate: (_score_from_metrics(candidate.metrics), Path(candidate.path).stat().st_mtime),
        reverse=True,
    )[0]

    if vectorizer_candidates:
        vectorizer = sorted(
            vectorizer_candidates,
            key=lambda candidate: (
                int(_tokens(classifier.name) == _tokens(candidate.name)),
                _score_from_metrics(candidate.metrics),
                Path(candidate.path).stat().st_mtime,
            ),
            reverse=True,
        )[0]
    elif hasattr(classifier.object, "named_steps"):
        vectorizer_obj = None
        for step_name, step_obj in classifier.object.named_steps.items():
            if hasattr(step_obj, "transform"):
                vectorizer_obj = step_obj
                break
        if vectorizer_obj is not None:
            vectorizer = LoadedArtifact(
                name=f"{classifier.name}_embedded_vectorizer",
                path=classifier.path,
                object=vectorizer_obj,
                metrics=classifier.metrics,
            )
        else:
            raise RuntimeError("No compatible vectorizer discovered for selected classifier.")
    else:
        raise RuntimeError("No compatible vectorizer discovered for selected classifier.")

    return classifier, vectorizer


def _select_response_model(model_files: list[Path], metrics_entries: list[dict[str, Any]]) -> LoadedArtifact:
    preferred_name = "tfidf_nearest_response_model.joblib"
    for file_path in model_files:
        if file_path.name.lower() == preferred_name:
            try:
                logger.info("Preferred response model found: %s", file_path)
                obj = _load_serialized(file_path)
                return LoadedArtifact(
                    name=file_path.stem,
                    path=str(file_path),
                    object=obj,
                    metrics=_metrics_for_file(file_path, metrics_entries),
                )
            except Exception as exc:
                logger.warning("Failed to load preferred response model %s: %s", file_path, exc)

    candidates: list[LoadedArtifact] = []
    for file_path in model_files:
        try:
            obj = _load_serialized(file_path)
        except Exception:
            continue
        if _is_response_model(obj, file_path):
            candidates.append(
                LoadedArtifact(
                    name=file_path.stem,
                    path=str(file_path),
                    object=obj,
                    metrics=_metrics_for_file(file_path, metrics_entries),
                )
            )

    if not candidates:
        return LoadedArtifact(name="retrieval_response_engine", path="", object=None, metrics={})

    return sorted(
        candidates,
        key=lambda candidate: (_score_from_metrics(candidate.metrics), Path(candidate.path).stat().st_mtime),
        reverse=True,
    )[0]


@lru_cache(maxsize=1)
def load_runtime_models() -> RuntimeModels:
    settings = get_settings()
    if not settings.artifacts_dir.exists():
        raise RuntimeError(f"Artifacts directory not found: {settings.artifacts_dir}")

    metrics_entries = _parse_metrics(settings.metrics_dir)
    model_files = _discover_serialized_files(settings.artifacts_dir, settings.model_extensions)

    classifier, vectorizer = _select_classifier_and_vectorizer(model_files, metrics_entries)
    response_model = _select_response_model(model_files, metrics_entries)
    corpus_path, response_corpus = _discover_response_corpus(settings.artifacts_dir)

    if response_model.object is None and not response_corpus:
        raise RuntimeError("No response model or response corpus artifacts were discovered.")

    if response_model.object is None:
        response_model.path = corpus_path

    rag_runtime = None
    if settings.use_qwen_generation:
        rag_runtime = load_rag_runtime(
            artifacts_dir=settings.artifacts_dir,
            embed_model_path=settings.embed_model_path,
            top_k=settings.top_k,
            faiss_weight=settings.faiss_weight,
            bm25_weight=settings.bm25_weight,
            candidate_pool=settings.rag_candidate_pool,
            device=settings.resolved_embed_device,
            faiss_use_mmap=settings.faiss_use_mmap,
        )

    logger.info("Loaded classifier: %s (%s)", classifier.name, classifier.path)
    logger.info("Loaded vectorizer: %s (%s)", vectorizer.name, vectorizer.path)
    logger.info("Loaded response model: %s (%s)", response_model.name, response_model.path)
    if rag_runtime is not None:
        logger.info("Loaded RAG runtime for Qwen generation")

    return RuntimeModels(
        classifier=classifier,
        vectorizer=vectorizer,
        response_model=response_model,
        response_corpus=response_corpus,
        rag_runtime=rag_runtime,
        response_mode=settings.response_mode,
    )


def _build_fallback_classifier_from_dataset(artifacts_dir: Path) -> tuple[LoadedArtifact, LoadedArtifact] | None:
    dataset_candidates = [artifacts_dir / "train_split.csv", artifacts_dir / "cleaned_labeled_dataset.csv"]
    for dataset in dataset_candidates:
        if not dataset.exists():
            continue
        try:
            texts: list[str] = []
            labels: list[str] = []
            with dataset.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                for idx, row in enumerate(reader):
                    if idx >= 25000:
                        break
                    normalized = {str(k).lower(): (v or "") for k, v in row.items()}
                    text = (
                        normalized.get("input_clean")
                        or normalized.get("input")
                        or f"{normalized.get('title', '')} {normalized.get('description', '')}".strip()
                    )
                    label = normalized.get("category") or normalized.get("label")
                    if text and label:
                        texts.append(text)
                        labels.append(label)

            if len(texts) < 100:
                continue

            vectorizer = TfidfVectorizer(max_features=30000, ngram_range=(1, 2))
            x_train = vectorizer.fit_transform(texts)
            classifier = LogisticRegression(max_iter=1200, multi_class="auto")
            classifier.fit(x_train, labels)
            logger.warning(
                "Using fallback trained classifier/vectorizer from dataset artifact %s",
                dataset,
            )
            return (
                LoadedArtifact(
                    name="fallback_tfidf_logreg_classifier",
                    path=str(dataset),
                    object=classifier,
                    metrics={"source": "runtime_dataset_training"},
                ),
                LoadedArtifact(
                    name="fallback_tfidf_vectorizer",
                    path=str(dataset),
                    object=vectorizer,
                    metrics={"source": "runtime_dataset_training"},
                ),
            )
        except Exception as exc:
            logger.warning("Failed fallback classifier build from %s: %s", dataset, exc)
    return None
