from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Sequence(Base):
    __tablename__ = "sequence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    steps: Mapped[list["SequenceStep"]] = relationship(
        "SequenceStep",
        back_populates="sequence",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="SequenceStep.step_order",
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
