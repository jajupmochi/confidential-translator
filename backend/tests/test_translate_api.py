"""Tests for the translation API endpoints."""

import pytest
import respx
from httpx import AsyncClient, Response


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test the health check endpoint."""
    with respx.mock:
        # Mock Ollama being unreachable
        respx.get("http://localhost:11434/api/tags").mock(return_value=Response(500))
        respx.get("http://127.0.0.1:11434/api/tags").mock(return_value=Response(500))
        response = await client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"
    assert "ollama_connected" in data


@pytest.mark.asyncio
async def test_translate_text_requires_body(client: AsyncClient):
    """Test that translation requires a request body."""
    response = await client.post("/api/translate")
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_translate_text_validates_target(client: AsyncClient):
    """Test that translation requires target_language."""
    response = await client.post("/api/translate", json={"text": "hello"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_translate_text_success(client: AsyncClient):
    """Test successful text translation with mocked Ollama."""
    with respx.mock:
        respx.get("http://127.0.0.1:11434/api/tags").mock(return_value=Response(200, json={"models": []}))
        respx.post("http://127.0.0.1:11434/api/generate").mock(
            return_value=Response(
                200,
                json={
                    "response": "你好世界",
                    "prompt_eval_count": 10,
                    "eval_count": 8,
                },
            )
        )
        response = await client.post(
            "/api/translate",
            json={
                "text": "Hello world",
                "source_language": "en",
                "target_language": "zh",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["translated_text"] == "你好世界"
    assert data["report"]["source_language"] == "en"
    assert data["report"]["target_language"] == "zh"
    assert data["report"]["characters_input"] == 11
    assert data["report"]["time_taken_ms"] >= 0


@pytest.mark.asyncio
async def test_detect_language(client: AsyncClient):
    """Test language detection endpoint."""
    response = await client.get(
        "/api/translate/detect-language",
        params={"text": "This is a longer English sentence to ensure reliable detection."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "en"
    assert data["language_name"] == "English"
    assert 0 <= data["confidence"] <= 1.0


@pytest.mark.asyncio
async def test_detect_language_chinese(client: AsyncClient):
    """Test Chinese language detection."""
    response = await client.get(
        "/api/translate/detect-language", params={"text": "你好世界，这是一个测试"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "zh"


@pytest.mark.asyncio
async def test_detect_language_empty(client: AsyncClient):
    """Test language detection with empty text."""
    response = await client.get("/api/translate/detect-language", params={"text": ""})
    assert response.status_code == 400
