import logging
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Support Ticket Classification API"
    app_version: str = "1.0.0"
    environment: str = "development"
    log_level: str = "INFO"

    api_prefix: str = "/"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    backend_root: Path = Path(__file__).resolve().parents[2]
    artifacts_dir: Path = backend_root / "artifacts"
    metrics_dir: Path = backend_root / "metrics"

    model_extensions: tuple[str, ...] = (".joblib", ".pkl", ".pickle")
    health_check_interval_seconds: int = 10

    # traditional | qwen
    response_mode: str = "qwen"
    local_models_dir: Path = backend_root / "artifacts" / "models"
    embed_model_name: str = "BAAI/bge-base-en-v1.5"
    gen_model_name: str = "Qwen/Qwen2.5-1.5B-Instruct"
    local_embed_dirname: str = "bge-base-en-v1.5"
    local_gen_dirname: str = "qwen2.5-1.5b-instruct"
    embed_device: str = "auto"
    generation_device: str = "auto"
    top_k: int = 5
    faiss_weight: float = 0.55
    bm25_weight: float = 0.45
    rag_candidate_pool: int = 50
    max_new_tokens: int = 120
    faiss_use_mmap: bool = True
    preload_qwen: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def use_qwen_generation(self) -> bool:
        return self.response_mode.strip().lower() == "qwen"

    @property
    def embed_model_path(self) -> str:
        local = self.local_models_dir / self.local_embed_dirname
        if (local / "config.json").exists():
            return str(local)
        return self.embed_model_name

    @property
    def gen_model_path(self) -> str:
        local = self.local_models_dir / self.local_gen_dirname
        if (local / "config.json").exists():
            return str(local)
        return self.gen_model_name

    def _resolve_device(self, preference: str) -> str:
        normalized = preference.strip().lower()
        if normalized in {"cuda", "gpu"}:
            return "cuda"
        if normalized in {"cpu", "mps"}:
            return normalized
        if normalized not in {"", "auto"}:
            logging.getLogger(__name__).warning(
                "Unknown device preference '%s'; falling back to automatic detection.",
                preference,
            )
        try:
            import torch

            return "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            return "cpu"

    @property
    def resolved_embed_device(self) -> str:
        return self._resolve_device(self.embed_device)

    @property
    def resolved_generation_device(self) -> str:
        return self._resolve_device(self.generation_device)


@lru_cache
def get_settings() -> Settings:
    return Settings()
