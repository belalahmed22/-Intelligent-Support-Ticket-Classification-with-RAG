import logging
from typing import Any

logger = logging.getLogger(__name__)


def vectorize_text(vectorizer: Any, text: str) -> Any:
    if not hasattr(vectorizer, "transform"):
        raise RuntimeError("Loaded vectorizer does not implement transform().")
    logger.info("Vectorization step started")
    features = vectorizer.transform([text])
    logger.info("Vectorization complete | shape=%s", getattr(features, "shape", "unknown"))
    return features
