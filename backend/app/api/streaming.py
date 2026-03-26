"""Streaming translation API endpoint using Server-Sent Events."""

import asyncio
import json
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models import TranslationRequest
from app.services.translation_service import translation_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/translate", tags=["Translation Streaming"])


@router.post("/stream")
async def stream_translate(request: TranslationRequest):
    """Stream translation tokens via Server-Sent Events.

    Event types sent:
    - meta: Model info, languages, chunk count
    - thinking: Content from model's <think> block (for display only)
    - token: Translated text token
    - chunk_done: A chunk finished translating
    - done: Translation complete with full report
    - error: An error occurred
    """

    async def event_generator():
        try:
            async for event in translation_service.translate_stream(
                text=request.text,
                target_language=request.target_language,
                source_language=request.source_language,
                model=request.model,
            ):
                yield f"data: {json.dumps(event)}\n\n"

        except asyncio.CancelledError:
            # Client disconnected (abort)
            logger.info("Client disconnected, aborting translation stream.")
            return
        except Exception as e:
            logger.error(f"Streaming translation error: {e}")
            error_event = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
