"""Streaming translation API endpoint using Server-Sent Events."""

import asyncio
import json
import logging

from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile
from fastapi.responses import StreamingResponse

from app.models import TranslationRequest
from app.services.translation_service import translation_service
from app.services.file_service import file_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/translate", tags=["Translation Streaming"])


def _build_event_generator(
    text: str,
    target_language: str,
    source_language: str,
    model: str,
    translation_type: str = "text",
    file_name: str = None,
    file_type: str = None,
    initial_events: list = None,
):
    async def event_generator():
        translated_chunks = []
        final_report = None
        
        if initial_events:
            for ev in initial_events:
                yield f"data: {json.dumps(ev)}\n\n"
                
        try:
            async for event in translation_service.translate_stream(
                text=text,
                target_language=target_language,
                source_language=source_language,
                model=model,
            ):
                if event.get("type") == "token":
                    translated_chunks.append(event.get("content", ""))
                elif event.get("type") == "done":
                    final_report = event.get("report")
                
                yield f"data: {json.dumps(event)}\n\n"

        except asyncio.CancelledError:
            logger.info("Client disconnected, aborting translation stream.")
            return
        except Exception as e:
            logger.error(f"Streaming translation error: {e}")
            error_event = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(error_event)}\n\n"
            
        # Stream finished successfully, perform DB commit before closing HTTP socket
        if final_report:
            full_text = "".join(translated_chunks)
            
            from app.core.database import async_session
            from app.services.history_service import history_service
            from app.models import TranslationReport
            
            try:
                report_obj = TranslationReport(**final_report)
                async with async_session() as db:
                    record = await history_service.save_translation(
                        db=db,
                        report=report_obj,
                        source_text=text,
                        translated_text=full_text,
                        translation_type=translation_type,
                        file_name=file_name,
                        file_type=file_type,
                        target_file_name=None,
                    )
                    # Notify client of the newly created History ID
                    yield f"data: {json.dumps({'type': 'history', 'id': record.id})}\n\n"
            except Exception as db_e:
                logger.error(f"Failed to save translation to history after stream: {db_e}")

    return event_generator()


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
    generator = _build_event_generator(
        text=request.text,
        target_language=request.target_language,
        source_language=request.source_language,
        model=request.model,
    )
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

@router.post("/stream/file")
async def stream_translate_file(
    file: UploadFile,
    source_language: str = Form(default="auto"),
    target_language: str = Form(default="en"),
    model: str = Form(default=None),
):
    """Upload and stream translation of a file via SSE."""
    from app.core.config import settings
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    if not file_service.is_supported(file.filename):
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    content = await file.read()
    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large.")

    try:
        original_text = await file_service.extract_text(content, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text: {e}")

    if not original_text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted from the file")

    ftype = file_service.get_file_type(file.filename) or ""
    
    generator = _build_event_generator(
        text=original_text,
        target_language=target_language,
        source_language=source_language,
        model=model,
        translation_type="file",
        file_name=file.filename,
        file_type=ftype,
        initial_events=[{"type": "extracted_text", "content": original_text, "file_name": file.filename}]
    )
    return StreamingResponse(generator, media_type="text/event-stream")


@router.post("/stream/file/native")
async def stream_translate_file_native(
    file_path: str = Form(...),
    source_language: str = Form(default="auto"),
    target_language: str = Form(default="en"),
    model: str = Form(default=None),
):
    import os
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found at the specified path.")
        
    filename = os.path.basename(file_path)
    if not file_service.is_supported(filename):
        raise HTTPException(status_code=400, detail="Unsupported file type.")
        
    try:
        with open(file_path, "rb") as f:
            content = f.read()
        original_text = await file_service.extract_text(content, filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {e}")

    if not original_text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted from the file")

    ftype = file_service.get_file_type(filename) or ""
    
    generator = _build_event_generator(
        text=original_text,
        target_language=target_language,
        source_language=source_language,
        model=model,
        translation_type="file",
        file_name=file_path,
        file_type=ftype,
        initial_events=[{"type": "extracted_text", "content": original_text, "file_name": filename}]
    )
    return StreamingResponse(generator, media_type="text/event-stream")
