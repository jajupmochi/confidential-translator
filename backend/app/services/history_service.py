"""Translation history service — CRUD operations for history records."""

import logging
from datetime import datetime, timedelta

from sqlalchemy import delete, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    HistoryListResponse,
    HistoryRecord,
    StatisticsResponse,
    TranslationReport,
)
from app.models.database import TranslationHistory

logger = logging.getLogger(__name__)


class HistoryService:
    """Service for managing translation history in the database."""

    async def save_translation(
        self,
        db: AsyncSession,
        report: TranslationReport,
        source_text: str,
        translated_text: str,
        translation_type: str = "text",
        file_name: str | None = None,
        file_type: str | None = None,
        target_file_name: str | None = None,
    ) -> int:
        """Save a translation record to the database. Returns the record ID."""
        record = TranslationHistory(
            source_language=report.source_language,
            target_language=report.target_language,
            translation_type=translation_type,
            file_name=file_name,
            file_type=file_type,
            target_file_name=target_file_name,
            source_text=source_text[:10000],  # Limit stored text
            translated_text=translated_text[:10000],
            model_used=report.model_used,
            characters_input=report.characters_input,
            characters_output=report.characters_output,
            tokens_input=report.tokens_input,
            tokens_output=report.tokens_output,
            time_taken_ms=report.time_taken_ms,
            tokens_per_second=report.tokens_per_second,
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record.id

    async def get_history(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        language_pair: str | None = None,
        translation_type: str | None = None,
    ) -> HistoryListResponse:
        """Get paginated translation history."""
        query = select(TranslationHistory).order_by(desc(TranslationHistory.created_at))

        # Apply filters
        if search:
            query = query.where(
                TranslationHistory.source_text.contains(search)
                | TranslationHistory.translated_text.contains(search)
            )
        if language_pair:
            parts = language_pair.split("->")
            if len(parts) == 2:
                query = query.where(
                    TranslationHistory.source_language == parts[0].strip(),
                    TranslationHistory.target_language == parts[1].strip(),
                )
        if translation_type:
            query = query.where(TranslationHistory.translation_type == translation_type)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await db.execute(query)
        records = result.scalars().all()

        return HistoryListResponse(
            records=[self._to_record(r) for r in records],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_record(self, db: AsyncSession, record_id: int) -> HistoryRecord | None:
        """Get a single history record by ID."""
        result = await db.execute(
            select(TranslationHistory).where(TranslationHistory.id == record_id)
        )
        record = result.scalar_one_or_none()
        return self._to_record(record) if record else None

    async def delete_record(self, db: AsyncSession, record_id: int) -> bool:
        """Delete a history record by ID."""
        result = await db.execute(
            delete(TranslationHistory).where(TranslationHistory.id == record_id)
        )
        await db.commit()
        return result.rowcount > 0

    async def update_target_file(self, db: AsyncSession, record_id: int, target_file_name: str) -> bool:
        """Update the target_file_name for a given history record."""
        result = await db.execute(
            select(TranslationHistory).where(TranslationHistory.id == record_id)
        )
        record = result.scalar_one_or_none()
        if record:
            record.target_file_name = target_file_name
            await db.commit()
            return True
        return False

    async def get_statistics(self, db: AsyncSession) -> StatisticsResponse:
        """Get dashboard statistics."""
        # Total translations
        total_result = await db.execute(select(func.count(TranslationHistory.id)))
        total_translations = total_result.scalar() or 0

        # Total characters
        chars_result = await db.execute(
            select(func.sum(TranslationHistory.characters_input))
        )
        total_characters = chars_result.scalar() or 0

        # Total files
        files_result = await db.execute(
            select(func.count(TranslationHistory.id)).where(
                TranslationHistory.translation_type == "file"
            )
        )
        total_files = files_result.scalar() or 0

        # Average time
        avg_result = await db.execute(
            select(func.avg(TranslationHistory.time_taken_ms))
        )
        avg_time = avg_result.scalar() or 0.0

        # Most used language pair
        lang_pair_result = await db.execute(
            select(
                TranslationHistory.source_language,
                TranslationHistory.target_language,
                func.count().label("cnt"),
            )
            .group_by(TranslationHistory.source_language, TranslationHistory.target_language)
            .order_by(desc("cnt"))
            .limit(1)
        )
        lang_pair_row = lang_pair_result.first()
        most_used_pair = (
            f"{lang_pair_row[0]}->{lang_pair_row[1]}" if lang_pair_row else "N/A"
        )

        # Most used model
        model_result = await db.execute(
            select(TranslationHistory.model_used, func.count().label("cnt"))
            .group_by(TranslationHistory.model_used)
            .order_by(desc("cnt"))
            .limit(1)
        )
        model_row = model_result.first()
        most_used_model = model_row[0] if model_row else "N/A"

        # Translations by day (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        by_day_result = await db.execute(
            select(
                func.date(TranslationHistory.created_at).label("day"),
                func.count().label("count"),
            )
            .where(TranslationHistory.created_at >= thirty_days_ago)
            .group_by("day")
            .order_by("day")
        )
        translations_by_day = [
            {"date": str(row[0]), "count": row[1]} for row in by_day_result.all()
        ]

        # Language pair distribution
        lang_dist_result = await db.execute(
            select(
                TranslationHistory.source_language,
                TranslationHistory.target_language,
                func.count().label("count"),
            )
            .group_by(TranslationHistory.source_language, TranslationHistory.target_language)
            .order_by(desc("count"))
            .limit(10)
        )
        language_pair_distribution = [
            {"pair": f"{row[0]}→{row[1]}", "count": row[2]}
            for row in lang_dist_result.all()
        ]

        # Recent translations
        recent_result = await db.execute(
            select(TranslationHistory)
            .order_by(desc(TranslationHistory.created_at))
            .limit(10)
        )
        recent = [self._to_record(r) for r in recent_result.scalars().all()]

        return StatisticsResponse(
            total_translations=total_translations,
            total_characters_translated=total_characters,
            total_files_translated=total_files,
            average_time_ms=round(avg_time, 1),
            most_used_language_pair=most_used_pair,
            most_used_model=most_used_model,
            translations_by_day=translations_by_day,
            language_pair_distribution=language_pair_distribution,
            recent_translations=recent,
        )

    def _to_record(self, db_record: TranslationHistory) -> HistoryRecord:
        """Convert a database record to a Pydantic model."""
        return HistoryRecord(
            id=db_record.id,
            created_at=db_record.created_at,
            source_language=db_record.source_language,
            target_language=db_record.target_language,
            translation_type=db_record.translation_type,
            file_name=db_record.file_name,
            target_file_name=getattr(db_record, "target_file_name", None),
            file_type=db_record.file_type,
            source_text=db_record.source_text,
            translated_text=db_record.translated_text,
            model_used=db_record.model_used,
            characters_input=db_record.characters_input,
            characters_output=db_record.characters_output,
            tokens_input=db_record.tokens_input,
            tokens_output=db_record.tokens_output,
            time_taken_ms=db_record.time_taken_ms,
            tokens_per_second=db_record.tokens_per_second,
        )


# Singleton instance
history_service = HistoryService()
