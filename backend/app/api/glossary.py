"""Glossary management API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import (
    GlossaryCreate,
    GlossaryEntryCreate,
    GlossaryEntryResponse,
    GlossaryListResponse,
    GlossaryResponse,
)
from app.services.glossary_service import glossary_service

router = APIRouter(prefix="/glossaries", tags=["Glossaries"])


@router.get("", response_model=GlossaryListResponse)
async def list_glossaries(db: AsyncSession = Depends(get_db)):
    """List all glossaries with entry counts."""
    glossaries = await glossary_service.list_glossaries(db)
    return GlossaryListResponse(glossaries=glossaries)


@router.post("", response_model=GlossaryResponse)
async def create_glossary(
    request: GlossaryCreate, db: AsyncSession = Depends(get_db)
):
    """Create a new glossary for a language pair."""
    glossary = await glossary_service.create_glossary(
        db, request.name, request.source_language, request.target_language
    )
    return GlossaryResponse(
        id=glossary.id,
        name=glossary.name,
        source_language=glossary.source_language,
        target_language=glossary.target_language,
        created_at=glossary.created_at,
        entry_count=0,
    )


@router.delete("/{glossary_id}")
async def delete_glossary(
    glossary_id: int, db: AsyncSession = Depends(get_db)
):
    """Delete a glossary and all its entries."""
    deleted = await glossary_service.delete_glossary(db, glossary_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Glossary not found")
    return {"status": "deleted"}


@router.get("/{glossary_id}/entries", response_model=list[GlossaryEntryResponse])
async def list_entries(
    glossary_id: int, db: AsyncSession = Depends(get_db)
):
    """List all entries in a glossary."""
    return await glossary_service.list_entries(db, glossary_id)


@router.post(
    "/{glossary_id}/entries", response_model=GlossaryEntryResponse
)
async def add_entry(
    glossary_id: int,
    entry: GlossaryEntryCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a term pair to a glossary."""
    result = await glossary_service.add_entry(
        db, glossary_id, entry.source_term, entry.target_term
    )
    return GlossaryEntryResponse(
        id=result.id,
        source_term=result.source_term,
        target_term=result.target_term,
    )


@router.delete("/{glossary_id}/entries/{entry_id}")
async def delete_entry(
    glossary_id: int, entry_id: int, db: AsyncSession = Depends(get_db)
):
    """Remove a term pair from a glossary."""
    deleted = await glossary_service.delete_entry(db, entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"status": "deleted"}


@router.post("/{glossary_id}/upload")
async def upload_entries(
    glossary_id: int,
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
):
    """Upload a CSV or TSV file of term pairs (source,target per row)."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    if not file.filename.endswith((".csv", ".tsv")):
        raise HTTPException(
            status_code=400, detail="Only CSV and TSV files are supported"
        )

    content = await file.read()
    count = await glossary_service.upload_entries(
        db, glossary_id, content, file.filename
    )
    return {"status": "uploaded", "entries_added": count}
