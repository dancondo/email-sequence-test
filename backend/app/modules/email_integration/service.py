from app.modules.email_integration.models import EmailAccount
from app.modules.email_integration.providers.base import EmailProvider
from app.modules.email_integration.repository import EmailAccountRepository


class EmailIntegrationService:
    def __init__(
        self,
        repository: EmailAccountRepository,
        provider: EmailProvider,
    ) -> None:
        self._repository = repository
        self._provider = provider

    def get_auth_url(self) -> str:
        return self._provider.generate_auth_url()

    async def handle_callback(self, code: str) -> EmailAccount:
        result = self._provider.exchange_code(code)
        return await self._repository.save(
            grant_id=result.grant_id,
            email=result.email,
        )

    async def get_status(self) -> EmailAccount | None:
        return await self._repository.get_active()

    async def disconnect(self) -> bool:
        return await self._repository.disconnect()
