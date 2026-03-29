import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.modules.email_integration.models import IntegrationProvider


class SequenceRunStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"


class SequenceRunCandidateStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    REPLIED = "replied"
    INTERESTED = "interested"
    NOT_INTERESTED = "not_interested"
    UNSUBSCRIBED = "unsubscribed"


class EventType(str, enum.Enum):
    ENROLLED = "enrolled"
    EMAIL_SCHEDULED = "email_scheduled"
    EMAIL_SENT = "email_sent"
    EMAIL_FAILED = "email_failed"
    EMAIL_CANCELED = "email_canceled"
    REPLY_RECEIVED = "reply_received"
    REPLY_CLASSIFIED = "reply_classified"
    REPLY_SENT = "reply_sent"
    COMPLETED = "completed"
    UNSUBSCRIBED = "unsubscribed"
    REFERRAL_DETECTED = "referral_detected"
    REFERRAL_HANDOFF_SENT = "referral_handoff_sent"


class SequenceRun(Base):
    __tablename__ = "sequence_run"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sequence_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sequence.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[SequenceRunStatus] = mapped_column(
        Enum(SequenceRunStatus), nullable=False, default=SequenceRunStatus.DRAFT
    )
    snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    sequence: Mapped["Sequence"] = relationship(
        "Sequence", back_populates="runs"
    )
    candidates: Mapped[list["SequenceRunCandidate"]] = relationship(
        "SequenceRunCandidate",
        back_populates="sequence_run",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class SequenceRunCandidate(Base):
    __tablename__ = "sequence_run_candidate"
    __table_args__ = (
        UniqueConstraint(
            "candidate_id", "sequence_run_id",
            name="uq_sequence_run_candidate",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("candidate.id", ondelete="CASCADE"), nullable=False
    )
    sequence_run_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sequence_run.id", ondelete="CASCADE"), nullable=False
    )
    current_step_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[SequenceRunCandidateStatus] = mapped_column(
        Enum(SequenceRunCandidateStatus),
        nullable=False,
        default=SequenceRunCandidateStatus.ACTIVE,
    )

    sequence_run: Mapped["SequenceRun"] = relationship(
        "SequenceRun", back_populates="candidates"
    )
    candidate: Mapped["Candidate"] = relationship(
        "Candidate", back_populates="sequence_run_candidates", lazy="selectin"
    )
    events: Mapped[list["SequenceRunCandidateEvent"]] = relationship(
        "SequenceRunCandidateEvent",
        back_populates="sequence_run_candidate",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="SequenceRunCandidateEvent.occurred_at",
    )


class SequenceRunCandidateEvent(Base):
    __tablename__ = "sequence_run_candidate_event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sequence_run_candidate_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sequence_run_candidate.id", ondelete="CASCADE"),
        nullable=False,
    )
    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType), nullable=False
    )
    step_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    external_message_id: Mapped[str | None] = mapped_column(
        String, nullable=True, index=True
    )
    external_schedule_id: Mapped[str | None] = mapped_column(
        String, nullable=True
    )
    external_thread_id: Mapped[str | None] = mapped_column(
        String, nullable=True, index=True
    )
    external_provider: Mapped[IntegrationProvider | None] = mapped_column(
        Enum(IntegrationProvider), nullable=True
    )
    extra: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    sequence_run_candidate: Mapped["SequenceRunCandidate"] = relationship(
        "SequenceRunCandidate", back_populates="events"
    )
