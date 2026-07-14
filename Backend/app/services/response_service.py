import logging
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class RetrievalResponseEngine:
    def __init__(self, rows: list[dict[str, str]]):
        if not rows:
            raise RuntimeError("Response corpus is empty.")
        self.rows = rows
        self.vectorizer = TfidfVectorizer(max_features=12000, ngram_range=(1, 2))
        self.inputs = [self._input_value(row) for row in rows]
        self.matrix = self.vectorizer.fit_transform(self.inputs)

    @staticmethod
    def _input_value(row: dict[str, str]) -> str:
        return (
            row.get("input_clean")
            or row.get("input")
            or row.get("title")
            or row.get("description")
            or ""
        )

    @staticmethod
    def _output_value(row: dict[str, str]) -> str:
        return (
            row.get("output_clean")
            or row.get("output")
            or row.get("rag_response")
            or row.get("reference_output")
            or ""
        )

    def generate(self, text: str, category: str) -> tuple[str, str]:
        query = self.vectorizer.transform([text])
        sims = cosine_similarity(query, self.matrix)[0]
        top_idx = int(np.argmax(sims))
        best_row = self.rows[top_idx]
        suggestion = self._output_value(best_row).strip()
        if not suggestion:
            suggestion = f"We are looking into your {category} issue and will follow up shortly."

        solution = (
            f"Check account details, verify recent actions, and apply the response playbook for '{category}'."
        )
        return solution, suggestion


def generate_response(
    response_model: Any,
    response_corpus: list[dict[str, str]],
    text: str,
    category: str,
    confidence: float,
) -> tuple[str, str]:
    logger.info("Response generation step started")

    if response_model is not None:
        if isinstance(response_model, dict):
            model = response_model.get("model") or response_model.get("response_model")
            vectorizer = response_model.get("vectorizer")
            responses = response_model.get("responses") or response_model.get("reply_templates")
            if model is not None and vectorizer is not None and responses is not None:
                try:
                    query = vectorizer.transform([text])
                    if hasattr(model, "kneighbors"):
                        _, indices = model.kneighbors(query, n_neighbors=1)
                        idx = int(indices[0][0])
                    elif hasattr(model, "predict"):
                        idx = int(model.predict(query)[0])
                    else:
                        idx = 0
                    chosen = responses[idx] if isinstance(responses, (list, tuple)) and responses else ""
                    if isinstance(chosen, dict):
                        chosen = chosen.get("customer_reply") or chosen.get("suggested_response") or ""
                    chosen_text = str(chosen).strip()
                    if chosen_text:
                        solution = (
                            f"Use nearest historical resolution and adapt to category '{category}' with customer context."
                        )
                        return solution, chosen_text
                except Exception as exc:
                    logger.warning("Dict response model inference failed, using fallback retrieval: %s", exc)

        if hasattr(response_model, "generate"):
            result = response_model.generate(text=text, category=category, confidence=confidence)
            if isinstance(result, dict):
                return str(result.get("agent_solution") or result.get("solution", "")), str(
                    result.get("customer_reply") or result.get("suggested_response", "")
                )
            if isinstance(result, tuple) and len(result) == 2:
                return str(result[0]), str(result[1])
        if hasattr(response_model, "predict"):
            try:
                prediction = response_model.predict([text])
                if prediction is not None and len(prediction) > 0:
                    predicted = str(prediction[0]).strip()
                    if predicted:
                        solution = (
                            f"Use response model prediction and validate details for '{category}' before sending."
                        )
                        return solution, predicted
            except Exception as exc:
                logger.warning("Predict-style response model failed, using retrieval fallback: %s", exc)
        if callable(response_model):
            result = response_model(text)
            if isinstance(result, dict):
                return str(result.get("agent_solution") or result.get("solution", "")), str(
                    result.get("customer_reply") or result.get("suggested_response", "")
                )

    retrieval = RetrievalResponseEngine(response_corpus)
    solution, suggested = retrieval.generate(text=text, category=category)
    logger.info("Response generation complete")
    return solution, suggested
