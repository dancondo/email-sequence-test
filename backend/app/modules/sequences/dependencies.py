from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.sequences.repository import SequenceRepository
from app.modules.sequences.service import SequenceService


def get_sequence_repository(
    db: AsyncSession = Depends(get_db),
) -> SequenceRepository:
    return SequenceRepository(db)


def get_sequence_service(
    repository: SequenceRepository = Depends(get_sequence_repository),
) -> SequenceService:
    return SequenceService(repository=repository)
