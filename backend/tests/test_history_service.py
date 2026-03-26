"""Tests for the history service."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TranslationReport
from app.services.history_service import history_service


def _make_report(**kwargs) -> TranslationReport:
    """Create a test TranslationReport with defaults."""
    defaults = {
        "source_language": "en",
        "target_language": "zh",
        "model_used": "qwen3:14b-q4_K_M",
        "characters_input": 100,
        "characters_output": 80,
        "tokens_input": 50,
        "tokens_output": 40,
        "time_taken_ms": 1500,
        "tokens_per_second": 60.0,
    }
    defaults.update(kwargs)
    return TranslationReport(**defaults)


@pytest.mark.asyncio
async def test_save_and_retrieve(db_session: AsyncSession):
    """Test saving and retrieving a translation record."""
    report = _make_report()
    record_id = await history_service.save_translation(
        db=db_session,
        report=report,
        source_text="Hello world",
        translated_text="你好世界",
    )
    assert record_id > 0

    record = await history_service.get_record(db_session, record_id)
    assert record is not None
    assert record.source_text == "Hello world"
    assert record.translated_text == "你好世界"
    assert record.model_used == "qwen3:14b-q4_K_M"


@pytest.mark.asyncio
async def test_list_history(db_session: AsyncSession):
    """Test listing history with pagination."""
    for i in range(5):
        await history_service.save_translation(
            db=db_session,
            report=_make_report(),
            source_text=f"Text {i}",
            translated_text=f"翻译 {i}",
        )

    result = await history_service.get_history(db_session, page=1, page_size=3)
    assert result.total == 5
    assert len(result.records) == 3
    assert result.page == 1


@pytest.mark.asyncio
async def test_delete_record(db_session: AsyncSession):
    """Test deleting a history record."""
    report = _make_report()
    record_id = await history_service.save_translation(
        db=db_session,
        report=report,
        source_text="Delete me",
        translated_text="删除我",
    )

    success = await history_service.delete_record(db_session, record_id)
    assert success is True

    record = await history_service.get_record(db_session, record_id)
    assert record is None


@pytest.mark.asyncio
async def test_statistics_empty(db_session: AsyncSession):
    """Test statistics on empty database."""
    stats = await history_service.get_statistics(db_session)
    assert stats.total_translations == 0
    assert stats.total_characters_translated == 0
    assert stats.most_used_language_pair == "N/A"


@pytest.mark.asyncio
async def test_statistics_with_data(db_session: AsyncSession):
    """Test statistics with some translation records."""
    for i in range(3):
        await history_service.save_translation(
            db=db_session,
            report=_make_report(characters_input=100),
            source_text=f"Text {i}",
            translated_text=f"翻译 {i}",
        )

    stats = await history_service.get_statistics(db_session)
    assert stats.total_translations == 3
    assert stats.total_characters_translated == 300
    assert stats.most_used_language_pair == "en->zh"
