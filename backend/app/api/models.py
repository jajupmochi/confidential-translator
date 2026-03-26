"""Model management API endpoints."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models import ModelInfo, ModelListResponse, ModelPullRequest, ModelRecommendation
from app.services.ollama_service import ollama_service

router = APIRouter(prefix="/models", tags=["Models"])


@router.get("", response_model=ModelListResponse)
async def list_models() -> ModelListResponse:
    """List all locally installed Ollama models."""
    raw_models = await ollama_service.list_models()
    models = []
    for m in raw_models:
        details = m.get("details", {})
        models.append(
            ModelInfo(
                name=m.get("name", ""),
                size=m.get("size", 0),
                parameter_size=details.get("parameter_size", ""),
                quantization=details.get("quantization_level", ""),
                modified_at=m.get("modified_at", ""),
                digest=m.get("digest", ""),
            )
        )
    return ModelListResponse(models=models)


@router.post("/pull")
async def pull_model(request: ModelPullRequest):
    """Pull a model from the Ollama registry. Streams progress updates."""

    async def stream_progress():
        import json

        async for progress in ollama_service.pull_model(request.name):
            yield json.dumps(progress) + "\n"

    return StreamingResponse(stream_progress(), media_type="application/x-ndjson")


@router.delete("/{model_name:path}")
async def delete_model(model_name: str) -> dict:
    """Delete a locally installed model."""
    success = await ollama_service.delete_model(model_name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found or delete failed")
    return {"status": "deleted", "model": model_name}


@router.get("/recommend", response_model=ModelRecommendation)
async def recommend_model() -> ModelRecommendation:
    """Get the recommended model based on system hardware specs."""
    rec = ollama_service.recommend_model()
    return ModelRecommendation(**rec)
