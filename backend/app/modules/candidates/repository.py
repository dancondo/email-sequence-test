from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.candidate_lists.models import CandidateListCandidate
from app.modules.candidates.models import Candidate
from app.modules.sequence_runs.models import SequenceRun, SequenceRunCandidate


class CandidateRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, candidate_id: int) -> Candidate | None:
        stmt = select(Candidate).where(Candidate.id == candidate_id)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Candidate | None:
        stmt = select(Candidate).where(Candidate.email == email)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def bulk_create_or_get(
        self, entries: list[dict[str, str | None]]
    ) -> tuple[list[Candidate], list[Candidate]]:
        """Create candidates from a list of {email, name} dicts.

        Returns (created, existing) tuple of candidate lists.
        """
        emails = [e["email"] for e in entries]

        stmt = select(Candidate).where(Candidate.email.in_(emails))
        result = await self._db.execute(stmt)
        existing = list(result.scalars().all())
        existing_emails = {c.email for c in existing}

        created: list[Candidate] = []
        for entry in entries:
            if entry["email"] not in existing_emails:
                candidate = Candidate(
                    email=entry["email"],
                    name=entry.get("name"),
                )
                self._db.add(candidate)
                created.append(candidate)

        if created:
            await self._db.flush()

        await self._db.commit()

        for candidate in created:
            await self._db.refresh(candidate)

        return created, existing

    async def list_all(
        self, list_ids: list[int] | None = None
    ) -> list[tuple[Candidate, int]]:
        run_count = func.count(SequenceRunCandidate.id).label("run_count")
        stmt = (
            select(Candidate, run_count)
            .outerjoin(
                SequenceRunCandidate,
                SequenceRunCandidate.candidate_id == Candidate.id,
            )
        )

        if list_ids:
            stmt = stmt.join(
                CandidateListCandidate,
                CandidateListCandidate.candidate_id == Candidate.id,
            ).where(CandidateListCandidate.candidate_list_id.in_(list_ids))

        stmt = stmt.group_by(Candidate.id).order_by(Candidate.created_at.desc())
        result = await self._db.execute(stmt)
        return list(result.tuples().all())

    async def get_with_runs(self, candidate_id: int) -> Candidate | None:
        stmt = (
            select(Candidate)
            .where(Candidate.id == candidate_id)
            .options(
                selectinload(Candidate.sequence_run_candidates)
                .selectinload(SequenceRunCandidate.sequence_run)
                .selectinload(SequenceRun.sequence),
                selectinload(Candidate.referred_by),
            )
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()
