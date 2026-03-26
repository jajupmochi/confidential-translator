"""Export API endpoint."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.models import ExportRequest
from app.services.export_service import export_service

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
