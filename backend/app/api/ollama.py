"""Ollama installation API endpoints."""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models import OllamaInstallRequest
from app.services.ollama_service import ollama_service

router = APIRouter(prefix="/ollama", tags=["Ollama"])


@router.post("/install")
async def install_ollama(request: OllamaInstallRequest):
    """Install Ollama on the system. Streams progress updates."""

    async def stream_progress():
        import json

        async for progress in ollama_service.install_ollama():
            yield json.dumps(progress) + "\n"

    return StreamingResponse(stream_progress(), media_type="application/x-ndjson")
