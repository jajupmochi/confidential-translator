"""Pydantic schemas for API request/response models."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class TranslationType(StrEnum):
    """Type of translation."""

    TEXT = "text"
    FILE = "file"


class TranslationRequest(BaseModel):
    """Request body for text translation."""

    text: str = Field(..., min_length=1, max_length=50000, description="Text to translate")
    source_language: str = Field(default="auto", description="Source language code or 'auto'")
    target_language: str = Field(..., description="Target language code (zh, en, de, fr)")
    model: str | None = Field(default=None, description="Ollama model to use")


class TranslationReport(BaseModel):
    """Statistics report for a translation."""

    source_language: str
    target_language: str
    model_used: str
    characters_input: int
    characters_output: int
    tokens_input: int = 0
    tokens_output: int = 0
    time_taken_ms: int
    tokens_per_second: float = 0.0


class TranslationResponse(BaseModel):
    """Response body for text translation."""

    translated_text: str
    report: TranslationReport


class FileTranslationRequest(BaseModel):
    """Metadata for file translation (file sent as form data)."""

    source_language: str = "auto"
    target_language: str = "en"
    model: str | None = None


class FileTranslationResponse(BaseModel):
    """Response body for file translation."""

    translated_text: str
    original_text: str
    file_name: str
    file_type: str
    report: TranslationReport
    export_available: bool = False


class LanguageDetectionResponse(BaseModel):
    """Response for language detection."""

    language: str
    confidence: float
    language_name: str


class ModelInfo(BaseModel):
    """Information about an Ollama model."""

    name: str
    size: int = 0
    parameter_size: str = ""
    quantization: str = ""
    modified_at: str = ""
    digest: str = ""


class ModelListResponse(BaseModel):
    """Response for listing models."""

    models: list[ModelInfo]


class ModelPullRequest(BaseModel):
    """Request to pull a new model."""

    name: str = Field(..., description="Model name to pull (e.g. qwen2.5:7b)")


class ModelPullProgress(BaseModel):
    """Progress update for model pulling."""

    status: str
    completed: int = 0
    total: int = 0
    percent: float = 0.0


class ModelRecommendation(BaseModel):
    """Model recommendation based on system specs."""

    recommended_model: str
    reason: str
    gpu_vram_mb: int = 0
    ram_mb: int = 0
    alternatives: list[str] = []


class OllamaInstallRequest(BaseModel):
    """Request to install Ollama."""

    accept_terms: bool = True


class OllamaInstallProgress(BaseModel):
    """Progress update for Ollama installation."""

    status: str
    percent: float = 0.0
    message: str = ""


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    ollama_connected: bool
    ollama_installed: bool
    ollama_url: str
    version: str
    available_models: list[str] = []


class ExportRequest(BaseModel):
    """Request to export translated content."""

    translated_text: str
    original_file_type: str
    file_name: str = "translation"

class ExportNativeRequest(BaseModel):
    """Request to natively export and link translated content."""

    history_id: int | None = None
    save_path: str
    translated_text: str
    original_file_type: str
    file_name: str = "translation"


class HistoryRecord(BaseModel):
    """A single translation history record."""

    id: int
    created_at: datetime
    source_language: str
    target_language: str
    translation_type: str
    file_name: str | None = None
    target_file_name: str | None = None
    file_type: str | None = None
    source_text: str
    translated_text: str
    model_used: str
    characters_input: int
    characters_output: int
    tokens_input: int = 0
    tokens_output: int = 0
    time_taken_ms: int
    tokens_per_second: float = 0.0


class HistoryListResponse(BaseModel):
    """Paginated history list response."""

    records: list[HistoryRecord]
    total: int
    page: int
    page_size: int


class StatisticsResponse(BaseModel):
    """Dashboard statistics response."""

    total_translations: int
    total_characters_translated: int
    total_files_translated: int
    average_time_ms: float
    most_used_language_pair: str
    most_used_model: str
    translations_by_day: list[dict]
    language_pair_distribution: list[dict]
    recent_translations: list[HistoryRecord]


class AppSettings(BaseModel):
    """Application settings that can be customized via GUI."""

    ollama_models_path: str = ""


# --- Glossary Schemas ---


class GlossaryEntryCreate(BaseModel):
    """Request body to create a glossary entry."""

    source_term: str = Field(..., min_length=1, max_length=500)
    target_term: str = Field(..., min_length=1, max_length=500)


class GlossaryEntryResponse(BaseModel):
    """Response for a single glossary entry."""

    id: int
    source_term: str
    target_term: str


class GlossaryCreate(BaseModel):
    """Request body to create a new glossary."""

    name: str = Field(..., min_length=1, max_length=255)
    source_language: str = Field(..., description="Source language code")
    target_language: str = Field(..., description="Target language code")


class GlossaryResponse(BaseModel):
    """Response for a single glossary."""

    id: int
    name: str
    source_language: str
    target_language: str
    created_at: datetime
    entry_count: int = 0


class GlossaryListResponse(BaseModel):
    """Response for listing all glossaries."""

    glossaries: list[GlossaryResponse]

