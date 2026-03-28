from app.modules.health.repository import HealthRepository


class HealthService:
    def __init__(self, repository: HealthRepository):
        self.repository = repository

    async def check(self) -> dict:
        try:
            await self.repository.check_connection()
            return {"status": "healthy", "database": "connected"}
        except Exception as e:
            return {"status": "unhealthy", "database": str(e)}
