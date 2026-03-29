from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Sequence(Base):
    __tablename__ = "sequence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    referral_list_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("candidate_list.id", ondelete="SET NULL"), nullable=True
    )

    referral_list: Mapped["CandidateList | None"] = relationship(
        "CandidateList", lazy="selectin"
    )

    @property
    def referral_list_name(self) -> str | None:
        return self.referral_list.name if self.referral_list else None

    steps: Mapped[list["SequenceStep"]] = relationship(
        "SequenceStep",
        back_populates="sequence",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="SequenceStep.step_order",
    )

    runs: Mapped[list["SequenceRun"]] = relationship(
        "SequenceRun",
        back_populates="sequence",
        cascade="all, delete-orphan",
        lazy="noload",
    )


class SequenceStep(Base):
    __tablename__ = "sequence_step"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sequence_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sequence.id", ondelete="CASCADE"), nullable=False
    )
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    subject: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    delay_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    sequence: Mapped["Sequence"] = relationship(
        "Sequence", back_populates="steps"
    )
