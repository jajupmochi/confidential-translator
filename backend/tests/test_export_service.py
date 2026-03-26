"""Tests for the export service."""

import pytest

from app.services.export_service import export_service


@pytest.mark.asyncio
async def test_export_text():
    """Test text export."""
    content, ctype, fname = await export_service.export("Hello world", ".txt", "test")
    assert content == b"Hello world"
    assert ctype == "text/plain"
    assert fname == "test.txt"


@pytest.mark.asyncio
async def test_export_markdown():
    """Test markdown export."""
    content, ctype, fname = await export_service.export("# Title\n\nBody", ".md", "doc")
    assert b"# Title" in content
    assert ctype == "text/markdown"
    assert fname == "doc.md"


@pytest.mark.asyncio
async def test_export_csv():
    """Test CSV export."""
    content, ctype, fname = await export_service.export(
        "name | age | city\nAlice | 30 | Berlin", ".csv", "data"
    )
    assert ctype == "text/csv"
    assert fname == "data.csv"
    text = content.decode("utf-8")
    assert "Alice" in text
    assert "Berlin" in text


@pytest.mark.asyncio
async def test_export_xlsx():
    """Test XLSX export."""
    content, ctype, fname = await export_service.export(
        "name | age\nAlice | 30", ".xlsx", "sheet"
    )
    assert fname == "sheet.xlsx"
    assert len(content) > 0  # XLSX should produce non-empty bytes
    # Verify it starts with XLSX magic bytes (PK zip header)
    assert content[:2] == b"PK"
