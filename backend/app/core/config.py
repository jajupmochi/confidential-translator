"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "Confidential Translator"
    app_version: str = "0.1.0"
    debug: bool = False

    # Ollama configuration
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_models_path: str = ""
    default_model: str = "qwen3.5:9b"
    fallback_models: list[str] = [
        "qwen3.5:7b",
        "qwen3.5:3b",
        "qwen2.5:7b",
    ]
    thinking_enabled: bool = False  # ollama support thinking mode True, False, or "high", "medium", "low" for supported models
    max_generation_tokens: int = 4096
    translation_timeout_seconds: int = 120

    # Translation settings
    supported_languages: list[str] = ["zh", "en", "de", "fr"]
    max_chunk_size: int = 50000
    default_source_lang: str = "auto"
    default_target_lang: str = "en"

    # File processing
    max_upload_size_mb: int = 50
    temp_dir: str = "/tmp/confidential_translator"

    # Database
    database_url: str = "sqlite+aiosqlite:///./translation_history.db"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = {"env_prefix": "CT_", "env_file": ".env", "extra": "ignore"}


settings = Settings()
