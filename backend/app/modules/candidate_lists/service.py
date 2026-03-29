from fastapi import HTTPException

from app.modules.candidate_lists.models import CandidateList
from app.modules.candidate_lists.repository import CandidateListRepository


class CandidateListService:
    def __init__(self, repository: CandidateListRepository) -> None:
        self._repository = repository

    async def get_all_lists(self) -> list[CandidateList]:
        return await self._repository.get_all()

    async def get_or_create_list(
        self,
        list_id: int | None = None,
        list_name: str | None = None,
    ) -> CandidateList:
        if list_id:
            candidate_list = await self._repository.get_by_id(list_id)
            if not candidate_list:
                raise HTTPException(
                    status_code=404, detail="Candidate list not found"
                )
            return candidate_list

        if list_name:
            candidate_list = await self._repository.get_by_name(list_name)
            if candidate_list:
                return candidate_list
            return await self._repository.create(list_name)

        raise HTTPException(
            status_code=400,
            detail="Either list_id or list_name must be provided",
        )

    async def add_candidates_to_list(
        self, list_id: int, candidate_ids: list[int]
    ) -> None:
        await self._repository.add_candidates(list_id, candidate_ids)
