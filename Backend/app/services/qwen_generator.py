import logging
from functools import lru_cache
from threading import Lock

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class QwenGenerator:
    def __init__(self, model_path: str, max_new_tokens: int, device: str):
        self.model_path = model_path
        self.max_new_tokens = max_new_tokens
        self.device = device
        self._generator = None
        self._lock = Lock()
        self._ready = False

    @property
    def is_ready(self) -> bool:
        return self._ready

    def preload(self) -> None:
        self._ensure_loaded()

    def _ensure_loaded(self) -> None:
        if self._generator is not None:
            return

        with self._lock:
            if self._generator is not None:
                return

            logger.info("Loading Qwen generator from %s on %s", self.model_path, self.device)
            tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)

            if self.device == "cuda":
                model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    device_map="auto",
                    dtype=torch.float16,
                    trust_remote_code=True,
                )
            else:
                model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    trust_remote_code=True,
                    low_cpu_mem_usage=True,
                ).to(self.device)

            self._generator = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                return_full_text=False,
            )
            self._ready = True
            logger.info("Qwen generator ready: %s", self.model_path)

    def generate(self, prompt: str) -> str:
        self._ensure_loaded()
        assert self._generator is not None
        with self._lock:
            result = self._generator(prompt)[0]["generated_text"].strip()
        return result


def build_rag_prompt(query: str, predicted_category: str, retrieved_examples: list[dict]) -> str:
    context_blocks = []
    for index, example in enumerate(retrieved_examples, start=1):
        context_blocks.append(
            f"Example {index}\n"
            f"Ticket: {example['input']}\n"
            f"Category: {example['category']}\n"
            f"Support response: {example['output']}"
        )
    context = "\n\n".join(context_blocks)

    return f"""
You are a professional customer support assistant.

Task:
Generate a concise, helpful, and context-aware support response.

Predicted ticket category:
{predicted_category}

Customer ticket:
{query}

Relevant historical support examples:
{context}

Rules:
- Do not copy the examples exactly.
- Be polite and practical.
- Answer directly.
- If information is missing, ask for the needed detail.
- Keep the answer short.

Final support response:
""".strip()


def build_chat_prompt(message: str, retrieved_examples: list[dict]) -> str:
    context_blocks = []
    for index, example in enumerate(retrieved_examples, start=1):
        context_blocks.append(
            f"Example {index}\n"
            f"Customer: {example['input']}\n"
            f"Agent: {example['output']}"
        )
    context = "\n\n".join(context_blocks)

    return f"""
You are a helpful customer support operations assistant.

The user is asking for help drafting support replies or triage guidance.

User message:
{message}

Relevant historical support examples:
{context}

Rules:
- Be practical and concise.
- Provide actionable steps when useful.
- If the user wants a customer reply draft, write one.
- Do not copy examples exactly.

Assistant response:
""".strip()


@lru_cache(maxsize=1)
def get_qwen_generator() -> QwenGenerator:
    settings = get_settings()
    return QwenGenerator(
        model_path=settings.gen_model_path,
        max_new_tokens=settings.max_new_tokens,
        device=settings.resolved_generation_device,
    )
