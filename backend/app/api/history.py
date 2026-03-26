"""Translation history and statistics API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import HistoryListResponse, HistoryRecord, StatisticsResponse
from app.services.history_service import history_service

router = APIRouter(tags=["History"])


@router.get("/history", response_model=HistoryListResponse)
async def list_history(
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    language_pair: str | None = None,
    translation_type: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> HistoryListResponse:
    """Get paginated translation history with optional filters."""
    return await history_service.get_history(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        language_pair=language_pair,
        translation_type=translation_type,
    )


@router.get("/history/{record_id}", response_model=HistoryRecord)
async def get_history_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
) -> HistoryRecord:
    """Get a single translation history record."""
    record = await history_service.get_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.delete("/history/{record_id}")
async def delete_history_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Delete a translation history record."""
    success = await history_service.delete_record(db, record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"status": "deleted", "id": record_id}


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(
    db: AsyncSession = Depends(get_db),
) -> StatisticsResponse:
    """Get dashboard statistics for translation history."""
    return await history_service.get_statistics(db)
