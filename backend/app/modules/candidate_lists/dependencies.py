from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.candidate_lists.repository import CandidateListRepository
from app.modules.candidate_lists.service import CandidateListService


def get_candidate_list_repository(
    db: AsyncSession = Depends(get_db),
) -> CandidateListRepository:
    return CandidateListRepository(db)


def get_candidate_list_service(
    repository: CandidateListRepository = Depends(get_candidate_list_repository),
) -> CandidateListService:
    return CandidateListService(repository=repository)
