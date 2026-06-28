"""Runtime configuration for the SafeBasket backend.

All settings are environment-driven so the service runs out-of-the-box in a
development environment with no secrets, while still being able to light up
the optional LLM / web-search / LangSmith integrations when keys are present.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    """Application settings resolved from environment variables."""

    def __init__(self) -> None:
        self.app_name: str = "SafeBasket"
        self.data_dir: Path = Path(__file__).resolve().parent / "data"

        # Optional LLM layer. When absent, the agent falls back to a fully
        # deterministic rule-based analyzer so the product works offline.
        self.openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
        self.llm_model: str = os.getenv("SAFEBASKET_LLM_MODEL", "gpt-4o-mini")

        # Conditional web search tool. Enabled only when explicitly configured.
        self.enable_web_search: bool = _as_bool(os.getenv("SAFEBASKET_ENABLE_WEB_SEARCH"))
        self.tavily_api_key: str | None = os.getenv("TAVILY_API_KEY")

        # LangSmith tracing (LangChain observability). No-op without a key.
        self.langsmith_api_key: str | None = os.getenv("LANGSMITH_API_KEY") or os.getenv(
            "LANGCHAIN_API_KEY"
        )
        self.langsmith_project: str = os.getenv("LANGCHAIN_PROJECT", "safebasket")

        # API "modes": a free public tier and a metered commercial tier.
        # Commercial keys can be supplied as a comma separated list.
        self.commercial_api_keys: set[str] = {
            key.strip()
            for key in os.getenv("SAFEBASKET_API_KEYS", "").split(",")
            if key.strip()
        }
        self.free_rate_limit: int = int(os.getenv("SAFEBASKET_FREE_RATE_LIMIT", "60"))

        # Embedding model for the FAISS RAG layer; falls back automatically.
        self.embedding_model: str = os.getenv(
            "SAFEBASKET_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )

        self.cors_origins: list[str] = [
            origin.strip()
            for origin in os.getenv("SAFEBASKET_CORS_ORIGINS", "*").split(",")
            if origin.strip()
        ]

    @property
    def llm_enabled(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def langsmith_enabled(self) -> bool:
        return bool(self.langsmith_api_key)

    def configure_langsmith(self) -> None:
        """Wire up LangSmith env vars so LangChain auto-traces when enabled."""
        if not self.langsmith_enabled:
            return
        os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
        os.environ.setdefault("LANGCHAIN_API_KEY", self.langsmith_api_key or "")
        os.environ.setdefault("LANGCHAIN_PROJECT", self.langsmith_project)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
