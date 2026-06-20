from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置，所有 Provider 均由配置驱动。"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "smart-customer-service"
    app_env: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/customer_service"
    redis_url: str = "redis://redis:6379/0"

    tracker_store: Literal["memory", "redis"] = "memory"
    vector_store: Literal["memory", "pgvector"] = "memory"

    llm_provider: str = "mock"
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = ""
    llm_temperature: float = 0.1
    llm_timeout: int = 60
    llm_max_retries: int = 2

    embedding_provider: str = "mock"
    embedding_model: str = ""
    embedding_base_url: str = ""
    embedding_api_key: str = ""
    embedding_dimension: int = 1024

    rerank_provider: str = "mock"
    rerank_model: str = ""
    rerank_base_url: str = ""
    rerank_api_key: str = ""

    business_provider: str = "mock"
    business_api_base_url: str = ""
    business_api_key: str = ""
    business_api_timeout: int = 15

    handoff_provider: str = "mock"
    handoff_webhook_url: str = ""
    handoff_api_key: str = ""

    nlg_rephrase_enabled: bool = False
    nlg_rephrase_style: str = "professional"

    chunk_size: int = 600
    chunk_overlap: int = 100
    retrieval_top_k: int = 10
    rerank_top_n: int = 5
    retrieval_score_threshold: float = 0.35

    max_actions_per_turn: int = 10
    max_history_messages: int = 20
    session_ttl_seconds: int = 86400
    flow_dir: str = Field(default="flows")
    external_interfaces_config: str = "config/external_interfaces.yaml"

    @field_validator("llm_provider", "embedding_provider", "rerank_provider", "business_provider")
    @classmethod
    def normalize_provider(cls, value: str) -> str:
        return value.strip().lower() or "mock"


@lru_cache
def get_settings() -> Settings:
    return Settings()
