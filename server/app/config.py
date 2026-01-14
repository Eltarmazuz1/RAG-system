from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    # LLM Configuration
    LLM_PROVIDER: Literal["openai", "anthropic", "gemini"] = "openai"
    LLM_MODEL: str = "gpt-4o-mini"
    EMBEDDINGS_MODEL: str = "text-embedding-3-small"
    
    # API Keys
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None

    # Vector DB
    VECTOR_DB_URL: str | None = None # Set to None for local mode
    VECTOR_DB_PATH: str = "qdrant_local_storage"
    VECTOR_DB_COLLECTION: str = "rag_docs"

    # API Token for simple auth
    API_TOKEN: str = "my-dev-token"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
