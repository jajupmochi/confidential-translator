"""Health check endpoint."""

from fastapi import APIRouter

from app.core.config import settings
from app.models import HealthResponse
from app.services.ollama_service import ollama_service

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check system health and Ollama connection status."""
    connected = await ollama_service.is_connected()
    installed = ollama_service.is_installed()
    models = []
    if connected:
        model_list = await ollama_service.list_models()
        models = [m.get("name", "") for m in model_list]

    return HealthResponse(
        status="healthy",
        ollama_connected=connected,
        ollama_installed=installed,
        ollama_url=settings.ollama_base_url,
        version=settings.app_version,
        available_models=models,
    )
