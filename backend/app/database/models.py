from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class SessionModel(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    student_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    scholarship_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    rule_config: Mapped[str] = mapped_column(Text)
    readiness: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    documents = relationship(
        "DocumentModel",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    extracted_fields = relationship(
        "ExtractedFieldModel",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    discrepancies = relationship(
        "DiscrepancyModel",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doc_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    session_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("sessions.session_id"),
        index=True,
    )
    file_name: Mapped[str] = mapped_column(String(255))
    detected_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    session = relationship("SessionModel", back_populates="documents")


class ExtractedFieldModel(Base):
    __tablename__ = "extracted_fields"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("sessions.session_id"),
        index=True,
    )
    field_name: Mapped[str] = mapped_column(String(100))
    value: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    source_doc_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    session = relationship("SessionModel", back_populates="extracted_fields")


class DiscrepancyModel(Base):
    __tablename__ = "discrepancies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("sessions.session_id"),
        index=True,
    )
    discrepancy_id: Mapped[str] = mapped_column(String(100))
    field_name: Mapped[str] = mapped_column(String(100))
    doc_a_type: Mapped[str] = mapped_column(String(100))
    doc_b_type: Mapped[str] = mapped_column(String(100))
    value_a: Mapped[str] = mapped_column(Text)
    value_b: Mapped[str] = mapped_column(Text)
    similarity_score: Mapped[float] = mapped_column(Float)
    explanation: Mapped[str] = mapped_column(Text)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    session = relationship("SessionModel", back_populates="discrepancies")
