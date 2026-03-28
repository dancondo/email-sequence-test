from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.health.repository import HealthRepository
from app.modules.health.service import HealthService


def get_health_repository(db: AsyncSession = Depends(get_db)) -> HealthRepository:
    return HealthRepository(db)


def get_health_service(
    repository: HealthRepository = Depends(get_health_repository),
) -> HealthService:
    return HealthService(repository)
