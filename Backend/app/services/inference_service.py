import logging
from dataclasses import dataclass
from typing import Any

import numpy as np

from app.schemas.ticket import PredictionRequest, PredictionResponse
from app.services.model_loader import RuntimeModels
from app.services.qwen_generator import build_rag_prompt, get_qwen_generator
from app.services.rag_retriever import build_agent_solution, hybrid_retrieve
from app.services.response_service import generate_response
from app.services.vectorizer_service import vectorize_text
from app.utils.text import preprocess_text

logger = logging.getLogger(__name__)


@dataclass
class InferenceState:
    runtime: RuntimeModels


def _infer_priority(category: str, confidence: float) -> str:
    category_normalized = category.lower()
    if any(token in category_normalized for token in ["billing", "refund", "payment"]):
        return "high"
    if any(token in category_normalized for token in ["technical", "account", "login"]):
        return "medium"
    if confidence < 0.55:
        return "medium"
    return "low"


def _predict_category(classifier: Any, vectorized_text: Any, raw_text: str) -> tuple[str, float]:
    logger.info("Classification step started")
    if hasattr(classifier, "predict_proba") and hasattr(classifier, "predict"):
        try:
            probabilities = classifier.predict_proba(vectorized_text)[0]
            category = str(classifier.predict(vectorized_text)[0])
            confidence = float(np.max(probabilities))
            logger.info("Classification complete | category=%s | confidence=%.4f", category, confidence)
            return category, confidence
        except Exception:
            probabilities = classifier.predict_proba([raw_text])[0]
            category = str(classifier.predict([raw_text])[0])
            confidence = float(np.max(probabilities))
            logger.info(
                "Classification complete via raw-text fallback | category=%s | confidence=%.4f",
                category,
                confidence,
            )
            return category, confidence

    if hasattr(classifier, "predict"):
        try:
            category = str(classifier.predict(vectorized_text)[0])
            logger.info("Classification complete | category=%s", category)
            return category, 0.5
        except Exception:
            category = str(classifier.predict([raw_text])[0])
            logger.info("Classification complete via raw-text fallback | category=%s", category)
            return category, 0.5

    raise RuntimeError("Classification model does not expose a compatible predict API.")


def _generate_qwen_response(
    state: InferenceState,
    normalized_text: str,
    category: str,
) -> tuple[str, str]:
    if state.runtime.rag_runtime is None:
        raise RuntimeError("Qwen response mode is enabled but RAG runtime is not loaded.")

    retrieved_examples = hybrid_retrieve(state.runtime.rag_runtime, normalized_text)
    agent_solution = build_agent_solution(category, retrieved_examples)
    prompt = build_rag_prompt(normalized_text, category, retrieved_examples)
    customer_reply = get_qwen_generator().generate(prompt)
    logger.info("Qwen response generation complete | examples=%s", len(retrieved_examples))
    return agent_solution, customer_reply


def _generate_fallback_response(
    state: InferenceState,
    normalized_text: str,
    category: str,
    confidence: float,
) -> tuple[str, str]:
    logger.info("Falling back to traditional response generation")
    return generate_response(
        response_model=state.runtime.response_model.object,
        response_corpus=state.runtime.response_corpus,
        text=normalized_text,
        category=category,
        confidence=confidence,
    )


def run_inference(state: InferenceState, payload: PredictionRequest) -> PredictionResponse:
    combined_text = f"{payload.title.strip()} {payload.description.strip()}"
    normalized_text = preprocess_text(combined_text)

    vectorized = vectorize_text(state.runtime.vectorizer.object, normalized_text)
    category, confidence = _predict_category(state.runtime.classifier.object, vectorized, normalized_text)
    priority = _infer_priority(category, confidence)

    if state.runtime.response_mode.strip().lower() == "qwen":
        try:
            solution, suggested_response = _generate_qwen_response(state, normalized_text, category)
            model_used = f"{state.runtime.classifier.name} + Hybrid_RAG_Qwen_Generator"
            vectorizer_used = (
                f"Hybrid weights: FAISS [{state.runtime.rag_runtime.faiss_weight:.2f}] / "
                f"BM25 [{state.runtime.rag_runtime.bm25_weight:.2f}]"
                if state.runtime.rag_runtime
                else state.runtime.vectorizer.name
            )
        except Exception as exc:
            logger.exception("Qwen response generation failed, using fallback response model: %s", exc)
            solution, suggested_response = _generate_fallback_response(
                state=state,
                normalized_text=normalized_text,
                category=category,
                confidence=confidence,
            )
            model_used = f"{state.runtime.classifier.name} + Fallback_Response_Model"
            vectorizer_used = state.runtime.vectorizer.name
    else:
        solution, suggested_response = _generate_fallback_response(
            state=state,
            normalized_text=normalized_text,
            category=category,
            confidence=confidence,
        )
        model_used = state.runtime.classifier.name
        vectorizer_used = state.runtime.vectorizer.name

    return PredictionResponse(
        category=category,
        priority=priority,
        confidence=round(confidence, 4),
        agent_solution=solution,
        customer_reply=suggested_response,
        model_used=model_used,
        vectorizer_used=vectorizer_used,
    )
