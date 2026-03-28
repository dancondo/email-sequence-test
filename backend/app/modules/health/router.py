from fastapi import APIRouter, Depends

from app.modules.health.dependencies import get_health_service
from app.modules.health.service import HealthService

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check(service: HealthService = Depends(get_health_service)):
    return await service.check()
