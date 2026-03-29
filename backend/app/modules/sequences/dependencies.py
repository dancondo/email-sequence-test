from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.candidate_lists.dependencies import get_candidate_list_service
from app.modules.candidate_lists.service import CandidateListService
from app.modules.sequences.repository import SequenceRepository
from app.modules.sequences.service import SequenceService


def get_sequence_repository(
    db: AsyncSession = Depends(get_db),
) -> SequenceRepository:
    return SequenceRepository(db)


def get_sequence_service(
    repository: SequenceRepository = Depends(get_sequence_repository),
    candidate_list_service: CandidateListService = Depends(get_candidate_list_service),
) -> SequenceService:
    return SequenceService(
        repository=repository,
        candidate_list_service=candidate_list_service,
    )
