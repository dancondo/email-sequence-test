from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.candidates.models import Candidate


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
