from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def check_db_health(db: AsyncSession) -> dict:
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar_one()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
