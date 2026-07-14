import logging

from app.services.inference_service import InferenceState
from app.services.qwen_generator import build_chat_prompt, get_qwen_generator
from app.services.rag_retriever import hybrid_retrieve
from app.utils.text import preprocess_text

logger = logging.getLogger(__name__)


def run_chat(state: InferenceState, message: str) -> tuple[str, int]:
    if state.runtime.response_mode.strip().lower() != "qwen":
        return (
            "Qwen chat is disabled. Set RESPONSE_MODE=qwen in the backend environment.",
            0,
        )

    if state.runtime.rag_runtime is None:
        return ("RAG runtime is not loaded. Check backend logs for startup errors.", 0)

    normalized = preprocess_text(message)
    retrieved_examples = hybrid_retrieve(state.runtime.rag_runtime, normalized)
    prompt = build_chat_prompt(message.strip(), retrieved_examples)
    reply = get_qwen_generator().generate(prompt)
    logger.info("Chat response generated | examples=%s", len(retrieved_examples))
    return reply, len(retrieved_examples)
