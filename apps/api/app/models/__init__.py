"""SQLAlchemy ORM modelleri"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Profil - eşleştirme/üretim ajanlarının hafıza katmanı için gerekli
    target_position: Mapped[str] = mapped_column(String(255), nullable=True)
    seniority: Mapped[str] = mapped_column(String(50), nullable=True)  # junior/mid/senior
    experience_years: Mapped[float] = mapped_column(Float, nullable=True)
    skills: Mapped[str] = mapped_column(Text, nullable=True)  # JSON array (string)
    experience_summary: Mapped[str] = mapped_column(Text, nullable=True)
    tone_preference: Mapped[str] = mapped_column(
        String(50), nullable=True, default="professional"
    )  # professional/casual/confident

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class JobListing(Base):
    __tablename__ = "job_listings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True, index=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=True)
    company: Mapped[str] = mapped_column(String(255), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Analiz Ajanı çıktısı (JSON string)
    required_skills: Mapped[str] = mapped_column(Text, nullable=True)
    nice_to_have_skills: Mapped[str] = mapped_column(Text, nullable=True)
    seniority: Mapped[str] = mapped_column(String(50), nullable=True)
    parsed_json: Mapped[str] = mapped_column(Text, nullable=True)
    analysis_status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending/completed/failed

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    listing_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("job_listings.id"), nullable=False, index=True
    )

    score: Mapped[float] = mapped_column(Float, nullable=False)
    matched_skills: Mapped[str] = mapped_column(Text, nullable=True)  # JSON array
    missing_skills: Mapped[str] = mapped_column(Text, nullable=True)  # JSON array

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    listing_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("job_listings.id"), nullable=True, index=True
    )

    doc_type: Mapped[str] = mapped_column(String(20), nullable=False)  # cv / cover_letter
    cv_url: Mapped[str] = mapped_column(String(1000), nullable=True)
    cover_letter_text: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# Import agent models for future integration
