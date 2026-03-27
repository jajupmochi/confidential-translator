import asyncio
import sqlalchemy as sa
from app.core.database import engine

async def alter_db():
    async with engine.begin() as conn:
        try:
            await conn.execute(sa.text("ALTER TABLE translation_history ADD COLUMN target_file_name VARCHAR(255);"))
            print("Successfully added target_file_name to translation_history.")
        except Exception as e:
            print(f"Error (may already exist): {e}")

if __name__ == "__main__":
    asyncio.run(alter_db())
