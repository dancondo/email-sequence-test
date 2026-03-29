from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Candidate(Base):
    __tablename__ = "candidate"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    referred_by_candidate_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("candidate.id", ondelete="SET NULL"), nullable=True
    )

    referred_by: Mapped["Candidate | None"] = relationship(
        "Candidate",
        remote_side="Candidate.id",
        foreign_keys=[referred_by_candidate_id],
        lazy="selectin",
    )

    sequence_run_candidates: Mapped[list["SequenceRunCandidate"]] = relationship(
        "SequenceRunCandidate",
        back_populates="candidate",
        lazy="noload",
    )
