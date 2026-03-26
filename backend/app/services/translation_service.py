"""Translation service — core translation logic with language detection and chunking."""

import logging
import re
import time

from langdetect import detect_langs

from app.core.config import settings
from app.models import TranslationReport
from app.services.ollama_service import ollama_service

logger = logging.getLogger(__name__)

# Language code to name mapping
LANGUAGE_NAMES = {
    "zh": "Chinese",
    "zh-cn": "Chinese (Simplified)",
    "zh-tw": "Chinese (Traditional)",
    "en": "English",
    "de": "German",
    "fr": "French",
    "ja": "Japanese",
    "ko": "Korean",
    "es": "Spanish",
    "pt": "Portuguese",
    "ru": "Russian",
    "ar": "Arabic",
    "it": "Italian",
}

# Improved, highly directive translation system prompts (suppress overthinking)
TRANSLATION_PROMPTS = {
    "zh": (
        "You are a translation engine. You receive text and output ONLY the Chinese (Simplified) translation.\n"
        "Rules:\n"
        "1. Output ONLY the translation. No explanations, notes, comments, or alternatives.\n"
        "2. Preserve all formatting: newlines, bullet points, markdown, code blocks.\n"
        "3. Preserve proper nouns and brand names unless a glossary mapping is provided.\n"
        "4. Translate naturally and idiomatically, not word-by-word.\n"
        "5. Do not add any prefix like 'Translation:' or 'Here is the translation:'.\n"
        "6. If the input is already in Chinese, output it unchanged."
    ),
    "en": (
        "You are a translation engine. You receive text and output ONLY the English translation.\n"
        "Rules:\n"
        "1. Output ONLY the translation. No explanations, notes, comments, or alternatives.\n"
        "2. Preserve all formatting: newlines, bullet points, markdown, code blocks.\n"
        "3. Preserve proper nouns and brand names unless a glossary mapping is provided.\n"
        "4. Translate naturally and idiomatically, not word-by-word.\n"
        "5. Do not add any prefix like 'Translation:' or 'Here is the translation:'.\n"
        "6. If the input is already in English, output it unchanged."
    ),
    "de": (
        "You are a translation engine. You receive text and output ONLY the German translation.\n"
        "Rules:\n"
        "1. Output ONLY the translation. No explanations, notes, comments, or alternatives.\n"
        "2. Preserve all formatting: newlines, bullet points, markdown, code blocks.\n"
        "3. Preserve proper nouns and brand names unless a glossary mapping is provided.\n"
        "4. Translate naturally and idiomatically, not word-by-word.\n"
        "5. Do not add any prefix like 'Translation:' or 'Here is the translation:'.\n"
        "6. If the input is already in German, output it unchanged."
    ),
    "fr": (
        "You are a translation engine. You receive text and output ONLY the French translation.\n"
        "Rules:\n"
        "1. Output ONLY the translation. No explanations, notes, comments, or alternatives.\n"
        "2. Preserve all formatting: newlines, bullet points, markdown, code blocks.\n"
        "3. Preserve proper nouns and brand names unless a glossary mapping is provided.\n"
        "4. Translate naturally and idiomatically, not word-by-word.\n"
        "5. Do not add any prefix like 'Translation:' or 'Here is the translation:'.\n"
        "6. If the input is already in French, output it unchanged."
    ),
}

# Regex to strip <think>...</think> blocks from output
THINK_BLOCK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


class TranslationService:
    """Service for translating text using local LLMs."""

    def detect_language(self, text: str) -> tuple[str, float]:
        """Detect the language of the given text."""
        try:
            langs = detect_langs(text)
            if langs:
                lang = langs[0]
                code = str(lang.lang)
                if code in ("zh-cn", "zh-tw"):
                    code = "zh"
                return code, lang.prob
            return "en", 0.0
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return "en", 0.0

    def get_language_name(self, code: str) -> str:
        """Get human-readable language name from code."""
        return LANGUAGE_NAMES.get(code, code.upper())

    def _chunk_text(self, text: str, max_size: int | None = None) -> list[str]:
        # todo: is this necessary? Is it possible to get the max_size from the model?
        """Split text into chunks that fit within model context."""
        max_size = max_size or settings.max_chunk_size
        if len(text) <= max_size:
            return [text]

        chunks = []
        paragraphs = text.split("\n\n")
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 > max_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                if len(para) > max_size:
                    sentences = para.replace(". ", ".\n").split("\n")
                    current_chunk = ""
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) + 1 > max_size:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = sentence
                        else:
                            current_chunk += " " + sentence if current_chunk else sentence
                else:
                    current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def _get_system_prompt(
        self,
        source_lang: str,
        target_lang: str,
        glossary_entries: list[dict] | None = None,
    ) -> str:
        """Get the translation system prompt for the target language."""
        base_prompt = TRANSLATION_PROMPTS.get(
            target_lang,
            f"You are a translation engine. You receive text and output ONLY the "
            f"{self.get_language_name(target_lang)} translation.\n"
            f"Rules:\n"
            f"1. Output ONLY the translation. No explanations, notes, or alternatives.\n"
            f"2. Preserve all formatting.\n"
            f"3. Translate naturally and idiomatically.\n"
            f"4. Do not add any prefix.",
        )

        if source_lang != "auto":
            base_prompt += (
                f"\n\nThe source text is in {self.get_language_name(source_lang)}."
            )

        # Inject glossary terms if provided
        # todo: this is very straightforward, can we do better with other techs such as RAG to save tokens?
        if glossary_entries:
            glossary_section = "\n\nTERMINOLOGY (use these exact translations):\n"
            glossary_section += "| Source | Target |\n|--------|--------|\n"
            for entry in glossary_entries:
                glossary_section += f"| {entry['source_term']} | {entry['target_term']} |\n"
            base_prompt += glossary_section

        return base_prompt

    def _build_user_prompt(self, text: str, model: str) -> str:
        """Build the user prompt, appending /no_think for thinking models."""
        return text

    @staticmethod
    def _strip_think_blocks(text: str) -> str:
        """Remove any <think>...</think> blocks from the response."""
        cleaned = THINK_BLOCK_RE.sub("", text)
        return cleaned.strip()

    async def translate(
        self,
        text: str,
        target_language: str,
        source_language: str = "auto",
        model: str | None = None,
        glossary_entries: list[dict] | None = None,
    ) -> tuple[str, TranslationReport]:
        """Translate text and return (translated_text, report)."""
        model = model or settings.default_model
        start_time = time.monotonic()

        # Auto-detect source language
        if source_language == "auto":
            source_language, _ = self.detect_language(text)

        # If source == target, return as-is
        if source_language == target_language:
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            report = TranslationReport(
                source_language=source_language,
                target_language=target_language,
                model_used=model,
                characters_input=len(text),
                characters_output=len(text),
                time_taken_ms=elapsed_ms,
            )
            return text, report

        # Chunk text if needed
        chunks = self._chunk_text(text)
        translated_chunks = []
        total_tokens_in = 0
        total_tokens_out = 0

        system_prompt = self._get_system_prompt(
            source_language, target_language, glossary_entries
        )

        for chunk in chunks:
            user_prompt = self._build_user_prompt(chunk, model)
            response = await ollama_service.generate(
                model=model,
                prompt=user_prompt,
                system=system_prompt,
                temperature=0.7,
            )
            raw_response = response.get("response", "")
            cleaned = self._strip_think_blocks(raw_response)
            translated_chunks.append(cleaned)
            total_tokens_in += response.get("prompt_eval_count", 0)
            total_tokens_out += response.get("eval_count", 0)

        translated_text = "\n\n".join(translated_chunks)
        elapsed_ms = int((time.monotonic() - start_time) * 1000)
        total_tokens = total_tokens_in + total_tokens_out
        tokens_per_second = (total_tokens / (elapsed_ms / 1000)) if elapsed_ms > 0 else 0

        report = TranslationReport(
            source_language=source_language,
            target_language=target_language,
            model_used=model,
            characters_input=len(text),
            characters_output=len(translated_text),
            tokens_input=total_tokens_in,
            tokens_output=total_tokens_out,
            time_taken_ms=elapsed_ms,
            tokens_per_second=round(tokens_per_second, 1),
        )

        return translated_text, report

    async def translate_stream(
        self,
        text: str,
        target_language: str,
        source_language: str = "auto",
        model: str | None = None,
        glossary_entries: list[dict] | None = None,
    ):
        """Stream translation tokens. Yields SSE-formatted event dicts.

        Event types:
          {"type": "meta", "model": ..., "source_lang": ..., "target_lang": ...}
          {"type": "thinking", "content": ...}
          {"type": "token", "content": ...}
          {"type": "chunk_done", "chunk_index": ..., "total_chunks": ...}
          {"type": "done", "report": {...}}
        """
        logger.debug(
            f"Starting stream | model='{model}' source='{source_language}' "
            f"target='{target_language}' text_len={len(text)} "
            f"glossary_count={len(glossary_entries) if glossary_entries else 0}"
        )

        model = model or settings.default_model
        start_time = time.monotonic()

        if source_language == "auto":
            source_language, _ = self.detect_language(text)

        if source_language == target_language:
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            yield {
                "type": "meta",
                "model": model,
                "source_lang": source_language,
                "target_lang": target_language,
            }
            yield {"type": "token", "content": text}
            yield {
                "type": "done",
                "report": {
                    "source_language": source_language,
                    "target_language": target_language,
                    "model_used": model,
                    "characters_input": len(text),
                    "characters_output": len(text),
                    "tokens_input": 0,
                    "tokens_output": 0,
                    "time_taken_ms": elapsed_ms,
                    "tokens_per_second": 0.0,
                },
            }
            return

        chunks = self._chunk_text(text)
        system_prompt = self._get_system_prompt(
            source_language, target_language, glossary_entries
        )

        yield {
            "type": "meta",
            "model": model,
            "source_lang": source_language,
            "target_lang": target_language,
            "total_chunks": len(chunks),
        }

        total_tokens_in = 0
        total_tokens_out = 0
        full_output = ""

        # Track think block state for streaming
        in_think_block = False
        think_buffer = ""

        for chunk_idx, chunk in enumerate(chunks):
            user_prompt = self._build_user_prompt(chunk, model)

            logger.debug(
                f"Chunk {chunk_idx+1}/{len(chunks)} | model='{model}' "
                f"user_prompt_len={len(user_prompt)} "
                f"system_prompt_len={len(system_prompt)}"
            )

            logger.debug(f"----- User prompt: {user_prompt}")  # fixme
            logger.debug(f"----- System prompt: {system_prompt}")  # fixme

            async for token_data in ollama_service.generate_stream(
                model=model,
                prompt=user_prompt,
                system=system_prompt,
                temperature=0.7,
            ):
                if "error_type" in token_data:
                    yield {
                        "type": "error",
                        "error_type": token_data["error_type"],
                        "message": token_data.get("message", "Unknown error"),
                        "model": model,
                    }
                    return

                logger.debug(f"----- Token data: {token_data}")  # fixme

                token = token_data.get("response", "")

                if token_data.get("done", False):
                    # Final chunk metadata
                    total_tokens_in += token_data.get("prompt_eval_count", 0)
                    total_tokens_out += token_data.get("eval_count", 0)

                    # If we were in a think block that wasn't closed, clear it
                    if in_think_block:
                        in_think_block = False
                        think_buffer = ""

                    yield {
                        "type": "chunk_done",
                        "chunk_index": chunk_idx,
                        "total_chunks": len(chunks),
                    }
                    continue

                # Detect <think> blocks in the stream
                think_buffer += token
                if not in_think_block and "<think>" in think_buffer:
                    in_think_block = True
                    # Emit any content before <think>
                    before = think_buffer.split("<think>")[0]
                    if before:
                        full_output += before
                        yield {"type": "token", "content": before}
                    think_buffer = think_buffer.split("<think>", 1)[1]
                    continue

                if in_think_block:
                    if "</think>" in think_buffer:
                        # End of think block
                        thinking_content = think_buffer.split("</think>")[0]
                        yield {"type": "thinking", "content": thinking_content}
                        after = think_buffer.split("</think>", 1)[1]
                        think_buffer = ""
                        in_think_block = False
                        if after:
                            full_output += after
                            yield {"type": "token", "content": after}
                    else:
                        # Still inside think block, just buffer quietly
                        # Periodically emit thinking content for UI feedback
                        if len(think_buffer) > 50:
                            yield {"type": "thinking", "content": think_buffer}
                            think_buffer = ""
                    continue

                # Normal token
                think_buffer = ""
                full_output += token
                yield {"type": "token", "content": token}

        elapsed_ms = int((time.monotonic() - start_time) * 1000)
        total_tokens = total_tokens_in + total_tokens_out
        tokens_per_second = (
            (total_tokens / (elapsed_ms / 1000)) if elapsed_ms > 0 else 0
        )

        yield {
            "type": "done",
            "report": {
                "source_language": source_language,
                "target_language": target_language,
                "model_used": model,
                "characters_input": len(text),
                "characters_output": len(full_output),
                "tokens_input": total_tokens_in,
                "tokens_output": total_tokens_out,
                "time_taken_ms": elapsed_ms,
                "tokens_per_second": round(tokens_per_second, 1),
            },
        }


# Singleton instance
translation_service = TranslationService()
