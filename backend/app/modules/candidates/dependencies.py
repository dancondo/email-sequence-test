from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.candidates.repository import CandidateRepository
from app.modules.candidates.service import CandidateService


def get_candidate_repository(
    db: AsyncSession = Depends(get_db),
) -> CandidateRepository:
    return CandidateRepository(db)


def get_candidate_service(
    repository: CandidateRepository = Depends(get_candidate_repository),
) -> CandidateService:
    return CandidateService(repository=repository)
