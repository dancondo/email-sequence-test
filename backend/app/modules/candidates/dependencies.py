from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.candidate_lists.dependencies import get_candidate_list_service
from app.modules.candidate_lists.service import CandidateListService
from app.modules.candidates.repository import CandidateRepository
from app.modules.candidates.service import CandidateService


def get_candidate_repository(
    db: AsyncSession = Depends(get_db),
) -> CandidateRepository:
    return CandidateRepository(db)


def get_candidate_service(
    repository: CandidateRepository = Depends(get_candidate_repository),
    candidate_list_service: CandidateListService = Depends(get_candidate_list_service),
) -> CandidateService:
    return CandidateService(
        repository=repository,
        candidate_list_service=candidate_list_service,
    )
