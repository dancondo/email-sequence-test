from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.health.service import check_db_health

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    return await check_db_health(db)
