"""Language validation API endpoint using LLM."""

import json
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ollama_service import ollama_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Language Validation"])


class ValidateLanguageRequest(BaseModel):
    language_name: str
    model: str


class ValidateLanguageResponse(BaseModel):
    valid: bool
    canonical_name: str | None = None
    suggestions: list[str] = []


@router.post("/validate-language", response_model=ValidateLanguageResponse)
async def validate_language(request: ValidateLanguageRequest):
    """Validate if a string is a valid language name using LLM."""
    prompt = (
        f'Is "{request.language_name}" a valid human language name? '
        'Reply ONLY with a JSON object (no markdown, no explanation): '
        '{"valid": true/false, "canonical_name": "the standard English name of the language or null", '
        '"suggestions": ["list", "of", "similar", "language", "names", "if invalid"]}. '
        'Examples of valid: English, Spanish, 中文, Deutsch, العربية, 日本語, हिन्दी. '
        'If it is valid, canonical_name should be the standard name. '
        'If invalid, suggestions should list 1-3 real languages that are most similar to the input.'
    )

    try:
        result = await ollama_service.generate(
            model=request.model,
            prompt=prompt,
            system="You are a language identification assistant. Output only valid JSON. No markdown formatting.",
            thinking=False,
        )

        # Try to parse JSON from the response
        response_text = result.get("response", "").strip()
        # Strip markdown code fences if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        data = json.loads(response_text)
        return ValidateLanguageResponse(
            valid=data.get("valid", False),
            canonical_name=data.get("canonical_name"),
            suggestions=data.get("suggestions", []),
        )
    except json.JSONDecodeError:
        logger.warning(f"LLM returned non-JSON for language validation: {result.get('response', '')}")
        # Fallback: treat as invalid
        return ValidateLanguageResponse(
            valid=False,
            canonical_name=None,
            suggestions=["English", "中文", "Deutsch", "Français", "Español"],
        )
    except Exception as e:
        logger.error(f"Language validation error: {e}")
        raise HTTPException(status_code=500, detail=f"Language validation failed: {e}")
