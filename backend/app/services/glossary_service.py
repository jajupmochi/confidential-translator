"""Glossary service — CRUD and term matching for translation glossaries."""

import csv
import io
import logging

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.database import Glossary, GlossaryEntry

logger = logging.getLogger(__name__)


class GlossaryService:
    """Service for managing glossaries and matching terms in source text."""

    async def list_glossaries(self, db: AsyncSession) -> list[dict]:
        """List all glossaries with entry counts."""
        stmt = (
            select(
                Glossary.id,
                Glossary.name,
                Glossary.source_language,
                Glossary.target_language,
                Glossary.created_at,
                func.count(GlossaryEntry.id).label("entry_count"),
            )
            .outerjoin(GlossaryEntry, Glossary.id == GlossaryEntry.glossary_id)
            .group_by(Glossary.id)
            .order_by(Glossary.created_at.desc())
        )
        result = await db.execute(stmt)
        rows = result.all()
        return [
            {
                "id": r.id,
                "name": r.name,
                "source_language": r.source_language,
                "target_language": r.target_language,
                "created_at": r.created_at,
                "entry_count": r.entry_count,
            }
            for r in rows
        ]

    async def create_glossary(
        self, db: AsyncSession, name: str, source_language: str, target_language: str
    ) -> Glossary:
        """Create a new glossary."""
        glossary = Glossary(
            name=name,
            source_language=source_language,
            target_language=target_language,
        )
        db.add(glossary)
        await db.commit()
        await db.refresh(glossary)
        return glossary

    async def delete_glossary(self, db: AsyncSession, glossary_id: int) -> bool:
        """Delete a glossary and all its entries."""
        result = await db.execute(
            delete(Glossary).where(Glossary.id == glossary_id)
        )
        await db.commit()
        return result.rowcount > 0  # type: ignore[union-attr]

    async def list_entries(self, db: AsyncSession, glossary_id: int) -> list[dict]:
        """List all entries in a glossary."""
        stmt = (
            select(GlossaryEntry)
            .where(GlossaryEntry.glossary_id == glossary_id)
            .order_by(GlossaryEntry.source_term)
        )
        result = await db.execute(stmt)
        entries = result.scalars().all()
        return [
            {
                "id": e.id,
                "source_term": e.source_term,
                "target_term": e.target_term,
            }
            for e in entries
        ]

    async def add_entry(
        self,
        db: AsyncSession,
        glossary_id: int,
        source_term: str,
        target_term: str,
    ) -> GlossaryEntry:
        """Add a single entry to a glossary."""
        entry = GlossaryEntry(
            glossary_id=glossary_id,
            source_term=source_term.strip(),
            target_term=target_term.strip(),
        )
        db.add(entry)
        await db.commit()
        await db.refresh(entry)
        return entry

    async def delete_entry(self, db: AsyncSession, entry_id: int) -> bool:
        """Delete a single glossary entry."""
        result = await db.execute(
            delete(GlossaryEntry).where(GlossaryEntry.id == entry_id)
        )
        await db.commit()
        return result.rowcount > 0  # type: ignore[union-attr]

    async def upload_entries(
        self, db: AsyncSession, glossary_id: int, file_content: bytes, filename: str
    ) -> int:
        """Upload entries from CSV/TSV file. Returns number of entries added."""
        text = file_content.decode("utf-8-sig")
        delimiter = "\t" if filename.endswith(".tsv") else ","
        reader = csv.reader(io.StringIO(text), delimiter=delimiter)

        count = 0
        for row in reader:
            if len(row) >= 2:
                source_term = row[0].strip()
                target_term = row[1].strip()
                if source_term and target_term:
                    entry = GlossaryEntry(
                        glossary_id=glossary_id,
                        source_term=source_term,
                        target_term=target_term,
                    )
                    db.add(entry)
                    count += 1

        await db.commit()
        return count

    async def find_matching_entries(
        self,
        db: AsyncSession,
        source_text: str,
        source_lang: str,
        target_lang: str,
    ) -> list[dict]:
        """Find all glossary entries matching terms in the source text.

        Returns entries from ALL glossaries matching the language pair.
        Uses case-insensitive substring matching.
        """
        # Get all entries for the language pair
        stmt = (
            select(GlossaryEntry)
            .join(Glossary)
            .where(
                Glossary.source_language == source_lang,
                Glossary.target_language == target_lang,
            )
        )
        result = await db.execute(stmt)
        all_entries = result.scalars().all()

        # Filter to entries whose source term appears in the text
        text_lower = source_text.lower()
        matched = []
        for entry in all_entries:
            if entry.source_term.lower() in text_lower:
                matched.append(
                    {
                        "source_term": entry.source_term,
                        "target_term": entry.target_term,
                    }
                )

        return matched


glossary_service = GlossaryService()
