import asyncio
import sys

from app.core.database import async_session
from app.services.history_service import history_service
from app.models import TranslationReport

async def main():
    report = TranslationReport(
        source_language="en",
        target_language="de",
        model_used="qwen",
        characters_input=10,
        characters_output=10,
        tokens_input=0,
        tokens_output=0,
        time_taken_ms=1000,
        tokens_per_second=0
    )
    
    saved_path = "/media/linlin/New Volume/projects/2026.03.16_local_translator/app_data/uploads/test.txt"
    try:
        async with async_session() as db:
            await history_service.save_translation(
                db=db,
                report=report,
                source_text="hello",
                translated_text="hallo",
                translation_type="file",
                file_name=saved_path,
                file_type="txt",
            )
        print("SUCCESS")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(main())
