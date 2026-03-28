from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Candidate(Base):
    __tablename__ = "candidate"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)

    sequence_run_candidates: Mapped[list["SequenceRunCandidate"]] = relationship(
        "SequenceRunCandidate",
        back_populates="candidate",
        lazy="noload",
    )
