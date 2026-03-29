from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CandidateList(Base):
    __tablename__ = "candidate_list"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    candidates: Mapped[list["CandidateListCandidate"]] = relationship(
        "CandidateListCandidate",
        back_populates="candidate_list",
        lazy="noload",
    )


class CandidateListCandidate(Base):
    __tablename__ = "candidate_list_candidate"

    __table_args__ = (
        UniqueConstraint(
            "candidate_list_id", "candidate_id", name="uq_candidate_list_candidate"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    candidate_list_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("candidate_list.id", ondelete="CASCADE"), nullable=False
    )
    candidate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("candidate.id", ondelete="CASCADE"), nullable=False
    )

    candidate_list: Mapped["CandidateList"] = relationship(
        "CandidateList",
        back_populates="candidates",
        lazy="noload",
    )
