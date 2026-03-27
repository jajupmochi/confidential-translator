"""Export API endpoint."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.models import ExportRequest, ExportNativeRequest
from app.services.export_service import export_service
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.database import get_db
from app.services.history_service import history_service

router = APIRouter(prefix="/export", tags=["Export"])


@router.post("")
async def export_translation(request: ExportRequest) -> Response:
    """Export translated content to the specified file format.

    Returns the file as a download response.
    """
    try:
        file_bytes, content_type, filename = await export_service.export(
            translated_text=request.translated_text,
            file_type=request.original_file_type,
            file_name=request.file_name,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {e}") from e

    return Response(
        content=file_bytes,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

@router.post("/native")
async def export_translation_native(
    request: ExportNativeRequest,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Export natively to disk and optionally update translation history."""
    import logging
    logger = logging.getLogger(__name__)
    try:
        file_bytes, _, _ = await export_service.export(
            translated_text=request.translated_text,
            file_type=request.original_file_type,
            file_name=request.file_name,
        )
        with open(request.save_path, "wb") as f:
            f.write(file_bytes)
        logger.info(f"File exported to: {request.save_path}")
            
        if request.history_id is not None:
            await history_service.update_target_file(db, request.history_id, request.save_path)
            logger.info(f"History record {request.history_id} updated with target_file_name={request.save_path}")
        
        return {"status": "success", "file_path": request.save_path}
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {e}") from e
