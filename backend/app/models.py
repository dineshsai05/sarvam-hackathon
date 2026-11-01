import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(20), index=True)  # E.164
    preferred_language: Mapped[str | None] = mapped_column(String(32), nullable=True)
    consent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    calls: Mapped[list["CallAttempt"]] = relationship(back_populates="lead", order_by="CallAttempt.created_at")


class CallAttempt(Base):
    """One row per Sarvam instant-outbound attempt. Updated in place when the webhook arrives."""

    __tablename__ = "call_attempts"

    attempt_id: Mapped[str] = mapped_column(String(64), primary_key=True)  # from Sarvam
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    # Filled by webhook
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending|connected|no_answer|busy|failed
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    interaction_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    channel_provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    agent_phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    final_agent_variables: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    transcript: Mapped[list | None] = mapped_column(JSON, nullable=True)
    raw_webhook: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    lead: Mapped[Lead] = relationship(back_populates="calls")
