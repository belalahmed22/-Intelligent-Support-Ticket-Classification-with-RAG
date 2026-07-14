import logging
from dataclasses import dataclass
from typing import Any

import numpy as np

from app.schemas.ticket import PredictionRequest, PredictionResponse
from app.utils.text import preprocess_text

logger = logging.getLogger(__name__)


@dataclass
class LoadedModelState:
    model_name: str
    model_path: str
    model: Any
    metrics: dict[str, Any]


def _infer_priority(category: str, confidence: float) -> str:
    category_normalized = category.lower()
    if any(token in category_normalized for token in ["billing", "refund", "payment"]):
        return "high"
    if any(token in category_normalized for token in ["technical", "login", "account"]):
        return "medium"
    if confidence < 0.55:
        return "medium"
    return "low"


def _predict_with_model(model: Any, text: str) -> tuple[str, float]:
    if hasattr(model, "predict_proba") and hasattr(model, "predict"):
        probabilities = model.predict_proba([text])[0]
        prediction = model.predict([text])[0]
        confidence = float(np.max(probabilities))
        return str(prediction), confidence

    if isinstance(model, dict):
        vectorizer = model.get("vectorizer")
        classifier = model.get("classifier")
        label_encoder = model.get("label_encoder")
        if vectorizer is not None and classifier is not None:
            features = vectorizer.transform([text])
            probabilities = classifier.predict_proba(features)[0]
            predicted_idx = int(np.argmax(probabilities))
            confidence = float(probabilities[predicted_idx])
            category = (
                label_encoder.inverse_transform([predicted_idx])[0]
                if label_encoder is not None
                else str(predicted_idx)
            )
            return str(category), confidence

    if callable(model):
        prediction = model(text)
        if isinstance(prediction, dict):
            return str(prediction.get("category", "unknown")), float(prediction.get("confidence", 0.5))

    raise RuntimeError("Loaded model format is not supported for prediction.")


def predict_ticket(state: LoadedModelState, payload: PredictionRequest) -> PredictionResponse:
    combined = f"{payload.title.strip()} {payload.description.strip()}"
    normalized_text = preprocess_text(combined)

    category, confidence = _predict_with_model(state.model, normalized_text)
    priority = _infer_priority(category, confidence)

    logger.info("Prediction success | category=%s | confidence=%.4f", category, confidence)

    return PredictionResponse(
        category=category,
        priority=priority,
        confidence=round(confidence, 4),
        model_used=state.model_name,
    )
