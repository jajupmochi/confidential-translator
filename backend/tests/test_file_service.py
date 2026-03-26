"""Tests for the file processing service."""

import pytest

from app.services.file_service import file_service


def test_get_file_type_pdf():
    """Test PDF file type detection."""
    assert file_service.get_file_type("document.pdf") == ".pdf"


def test_get_file_type_xlsx():
    """Test XLSX file type detection."""
    assert file_service.get_file_type("data.xlsx") == ".xlsx"


def test_get_file_type_unsupported():
    """Test unsupported file type."""
    assert file_service.get_file_type("video.mp4") is None


def test_is_supported():
    """Test supported file detection."""
    assert file_service.is_supported("doc.pdf") is True
    assert file_service.is_supported("img.png") is True
    assert file_service.is_supported("data.csv") is True
    assert file_service.is_supported("text.md") is True
    assert file_service.is_supported("sheet.xlsx") is True
    assert file_service.is_supported("video.avi") is False


@pytest.mark.asyncio
async def test_extract_text_plain():
    """Test plain text extraction."""
    content = b"Hello, this is a test document."
    result = await file_service.extract_text(content, "test.txt")
    assert result == "Hello, this is a test document."


@pytest.mark.asyncio
async def test_extract_text_markdown():
    """Test markdown text extraction."""
    content = b"# Title\n\nThis is **bold** text."
    result = await file_service.extract_text(content, "readme.md")
    assert "# Title" in result
    assert "**bold**" in result


@pytest.mark.asyncio
async def test_extract_csv():
    """Test CSV text extraction."""
    content = b"name,age,city\nAlice,30,Berlin\nBob,25,Paris"
    result = await file_service.extract_text(content, "data.csv")
    assert "Alice" in result
    assert "Berlin" in result


@pytest.mark.asyncio
async def test_extract_unsupported():
    """Test that unsupported files raise ValueError."""
    with pytest.raises(ValueError, match="Unsupported file type"):
        await file_service.extract_text(b"data", "video.mp4")
