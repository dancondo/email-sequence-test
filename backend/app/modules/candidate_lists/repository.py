from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.candidate_lists.models import CandidateList, CandidateListCandidate


class CandidateListRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, list_id: int) -> CandidateList | None:
        stmt = select(CandidateList).where(CandidateList.id == list_id)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> CandidateList | None:
        stmt = select(CandidateList).where(CandidateList.name == name)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> list[CandidateList]:
        stmt = select(CandidateList).order_by(CandidateList.name)
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, name: str) -> CandidateList:
        candidate_list = CandidateList(name=name)
        self._db.add(candidate_list)
        await self._db.flush()
        await self._db.refresh(candidate_list)
        return candidate_list

    async def add_candidates(
        self, list_id: int, candidate_ids: list[int]
    ) -> None:
        existing_stmt = select(CandidateListCandidate.candidate_id).where(
            CandidateListCandidate.candidate_list_id == list_id,
            CandidateListCandidate.candidate_id.in_(candidate_ids),
        )
        result = await self._db.execute(existing_stmt)
        existing_ids = {row[0] for row in result.all()}

        new_ids = [cid for cid in candidate_ids if cid not in existing_ids]
        for candidate_id in new_ids:
            self._db.add(
                CandidateListCandidate(
                    candidate_list_id=list_id,
                    candidate_id=candidate_id,
                )
            )

        if new_ids:
            await self._db.flush()

        await self._db.commit()
