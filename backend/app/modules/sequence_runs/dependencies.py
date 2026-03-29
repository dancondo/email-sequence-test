from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.candidate_lists.dependencies import get_candidate_list_service
from app.modules.candidate_lists.service import CandidateListService
from app.modules.candidates.dependencies import get_candidate_service
from app.modules.candidates.service import CandidateService
from app.modules.email_integration.dependencies import get_email_service
from app.modules.email_integration.service import EmailIntegrationService
from app.modules.sequence_runs.repository import SequenceRunRepository
from app.modules.sequence_runs.service import SequenceRunService
from app.modules.sequences.dependencies import get_sequence_service
from app.modules.sequences.service import SequenceService


def get_sequence_run_repository(
    db: AsyncSession = Depends(get_db),
) -> SequenceRunRepository:
    return SequenceRunRepository(db)


def get_sequence_run_service(
    run_repository: SequenceRunRepository = Depends(get_sequence_run_repository),
    sequence_service: SequenceService = Depends(get_sequence_service),
    candidate_service: CandidateService = Depends(get_candidate_service),
    email_service: EmailIntegrationService = Depends(get_email_service),
    candidate_list_service: CandidateListService = Depends(get_candidate_list_service),
) -> SequenceRunService:
    return SequenceRunService(
        run_repository=run_repository,
        sequence_service=sequence_service,
        candidate_service=candidate_service,
        email_service=email_service,
        candidate_list_service=candidate_list_service,
    )
