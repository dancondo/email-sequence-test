from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class HealthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_connection(self) -> bool:
        result = await self.db.execute(text("SELECT 1"))
        result.scalar_one()
        return True
