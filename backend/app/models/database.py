"""SQLAlchemy database models for translation history and glossaries."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TranslationHistory(Base):
    """Model for storing translation history records."""

    __tablename__ = "translation_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    source_language: Mapped[str] = mapped_column(String(10), nullable=False)
    target_language: Mapped[str] = mapped_column(String(10), nullable=False)
    translation_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'text' or 'file'
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    translated_text: Mapped[str] = mapped_column(Text, nullable=False)
    model_used: Mapped[str] = mapped_column(String(100), nullable=False)
    characters_input: Mapped[int] = mapped_column(Integer, nullable=False)
    characters_output: Mapped[int] = mapped_column(Integer, nullable=False)
    tokens_input: Mapped[int] = mapped_column(Integer, default=0)
    tokens_output: Mapped[int] = mapped_column(Integer, default=0)
    time_taken_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    tokens_per_second: Mapped[float] = mapped_column(Float, default=0.0)


class Glossary(Base):
    """A named glossary for a specific language pair."""

    __tablename__ = "glossaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_language: Mapped[str] = mapped_column(String(10), nullable=False)
    target_language: Mapped[str] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    entries: Mapped[list["GlossaryEntry"]] = relationship(
        "GlossaryEntry", back_populates="glossary", cascade="all, delete-orphan"
    )


class GlossaryEntry(Base):
    """A single source→target term pair within a glossary."""

    __tablename__ = "glossary_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    glossary_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("glossaries.id", ondelete="CASCADE"), nullable=False
    )
    source_term: Mapped[str] = mapped_column(String(500), nullable=False)
    target_term: Mapped[str] = mapped_column(String(500), nullable=False)

    glossary: Mapped["Glossary"] = relationship("Glossary", back_populates="entries")

