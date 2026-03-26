"""Tests for the translation service."""


from app.services.translation_service import translation_service


def test_detect_language_english():
    """Test English language detection."""
    lang, conf = translation_service.detect_language(
        "Hello, how are you today? Here is a longer sequence of English text."
    )
    assert lang == "en"
    assert conf > 0.5


def test_detect_language_chinese():
    """Test Chinese language detection."""
    lang, conf = translation_service.detect_language("你好，今天天气怎么样？")
    assert lang == "zh"
    assert conf > 0.5


def test_detect_language_german():
    """Test German language detection."""
    lang, conf = translation_service.detect_language(
        "Guten Tag, wie geht es Ihnen heute?"
    )
    assert lang == "de"
    assert conf > 0.3


def test_detect_language_french():
    """Test French language detection."""
    lang, conf = translation_service.detect_language(
        "Bonjour, comment allez-vous aujourd'hui?"
    )
    assert lang == "fr"
    assert conf > 0.3


def test_get_language_name():
    """Test language name lookup."""
    assert translation_service.get_language_name("en") == "English"
    assert translation_service.get_language_name("zh") == "Chinese"
    assert translation_service.get_language_name("de") == "German"
    assert translation_service.get_language_name("fr") == "French"


def test_chunk_text_short():
    """Test that short text is not chunked."""
    chunks = translation_service._chunk_text("Short text", max_size=100)
    assert len(chunks) == 1
    assert chunks[0] == "Short text"


def test_chunk_text_long():
    """Test that long text is chunked on paragraph boundaries."""
    text = "Paragraph one.\n\n" * 20 + "Paragraph two.\n\n" * 20
    chunks = translation_service._chunk_text(text, max_size=200)
    assert len(chunks) > 1
    # All original text should be preserved across chunks
    rejoined = "\n\n".join(chunks)
    assert "Paragraph one." in rejoined
    assert "Paragraph two." in rejoined


def test_system_prompt_contains_language():
    """Test that system prompt mentions the target language."""
    prompt = translation_service._get_system_prompt("en", "zh")
    assert "Chinese" in prompt
    prompt = translation_service._get_system_prompt("en", "de")
    assert "German" in prompt
