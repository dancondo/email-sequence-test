from app.modules.email_integration.models import EmailAccount
from app.modules.email_integration.providers.base import EmailProvider, SendResult
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

    def send_message(
        self,
        grant_id: str,
        to_email: str,
        subject: str,
        body: str,
        send_at: int | None = None,
        reply_to_message_id: str | None = None,
    ) -> SendResult:
        return self._provider.send_message(
            grant_id=grant_id,
            to_email=to_email,
            subject=subject,
            body=body,
            send_at=send_at,
            reply_to_message_id=reply_to_message_id,
        )

    def cancel_scheduled_message(self, grant_id: str, schedule_id: str) -> bool:
        return self._provider.cancel_scheduled_message(
            grant_id=grant_id,
            schedule_id=schedule_id,
        )
