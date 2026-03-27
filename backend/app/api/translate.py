"""Translation API endpoints."""

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models import (
    FileTranslationResponse,
    LanguageDetectionResponse,
    TranslationRequest,
    TranslationResponse,
)
from app.services.file_service import file_service
from app.services.history_service import history_service
from app.services.translation_service import translation_service

router = APIRouter(prefix="/translate", tags=["Translation"])


@router.post("", response_model=TranslationResponse)
async def translate_text(
    request: TranslationRequest,
    db: AsyncSession = Depends(get_db),
) -> TranslationResponse:
    """Translate text using a local LLM.

    - Automatically detects source language if set to 'auto'
    - Returns translation with detailed performance report
    - Saves to translation history
    """
    try:
        translated_text, report = await translation_service.translate(
            text=request.text,
            target_language=request.target_language,
            source_language=request.source_language,
            model=request.model,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {e}") from e

    # Save to history
    await history_service.save_translation(
        db=db,
        report=report,
        source_text=request.text,
        translated_text=translated_text,
        translation_type="text",
    )

    return TranslationResponse(translated_text=translated_text, report=report)


@router.post("/file", response_model=FileTranslationResponse)
async def translate_file(
    file: UploadFile,
    source_language: str = Form(default="auto"),
    target_language: str = Form(default="en"),
    model: str = Form(default=None),
    db: AsyncSession = Depends(get_db),
) -> FileTranslationResponse:
    """Upload and translate a file.

    Supported formats: PDF, PNG/JPG (OCR), XLSX, CSV, MD, TXT, DOCX
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    if not file_service.is_supported(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported: {', '.join(file_service.SUPPORTED_EXTENSIONS) if hasattr(file_service, 'SUPPORTED_EXTENSIONS') else 'PDF, images, XLSX, CSV, MD, TXT, DOCX'}",
        )

    # Read file content
    content = await file.read()
    max_size = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_upload_size_mb}MB",
        )

    # Extract text
    try:
        original_text = await file_service.extract_text(content, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text: {e}") from e

    if not original_text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted from the file")

    # Translate
    try:
        translated_text, report = await translation_service.translate(
            text=original_text,
            target_language=target_language,
            source_language=source_language,
            model=model,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {e}") from e

    file_type = file_service.get_file_type(file.filename) or ""

    # Save to history
    await history_service.save_translation(
        db=db,
        report=report,
        source_text=original_text,
        translated_text=translated_text,
        translation_type="file",
        file_name=file.filename,
        file_type=file_type,
    )

    return FileTranslationResponse(
        translated_text=translated_text,
        original_text=original_text,
        file_name=file.filename,
        file_type=file_type,
        report=report,
        export_available=file_type in (".txt", ".md", ".csv", ".xlsx"),
    )


@router.post("/file/native", response_model=FileTranslationResponse)
async def translate_file_native(
    file_path: str = Form(...),
    source_language: str = Form(default="auto"),
    target_language: str = Form(default="en"),
    model: str = Form(default=None),
    db: AsyncSession = Depends(get_db),
) -> FileTranslationResponse:
    import os
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found at the specified path.")
        
    filename = os.path.basename(file_path)
    if not file_service.is_supported(filename):
        raise HTTPException(status_code=400, detail="Unsupported file type.")
        
    # Read the local file directly
    try:
        with open(file_path, "rb") as f:
            content = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {e}")
        
    # Extract text
    try:
        original_text = await file_service.extract_text(content, filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text: {e}") from e

    if not original_text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted from the file")

    # Translate
    try:
        translated_text, report = await translation_service.translate(
            text=original_text,
            target_language=target_language,
            source_language=source_language,
            model=model,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {e}") from e

    file_type = file_service.get_file_type(filename) or ""

    # Save to history USING INJECTED ABSOLUTE PATH AS FILE_NAME
    await history_service.save_translation(
        db=db,
        report=report,
        source_text=original_text,
        translated_text=translated_text,
        translation_type="file",
        file_name=file_path, # STORE ABSOLUTE PATH
        file_type=file_type,
    )

    return FileTranslationResponse(
        translated_text=translated_text,
        original_text=original_text,
        file_name=file_path,
        file_type=file_type,
        report=report,
        export_available=file_type in (".txt", ".md", ".csv", ".xlsx"),
    )


@router.get("/detect-language", response_model=LanguageDetectionResponse)
async def detect_language(text: str) -> LanguageDetectionResponse:
    """Detect the language of the given text."""
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    lang, confidence = translation_service.detect_language(text)
    return LanguageDetectionResponse(
        language=lang,
        confidence=round(confidence, 3),
        language_name=translation_service.get_language_name(lang),
    )
