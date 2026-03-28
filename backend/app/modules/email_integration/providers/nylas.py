from nylas import Client as NylasClient

from app.core.config import settings
from app.modules.email_integration.providers.base import (
    EmailProvider,
    OAuthResult,
    SendResult,
)


class NylasEmailProvider(EmailProvider):
    def __init__(self, client: NylasClient) -> None:
        self._client = client

    def generate_auth_url(self) -> str:
        auth_url = self._client.auth.url_for_oauth2({
            "client_id": settings.NYLAS_CLIENT_ID,
            "redirect_uri": settings.NYLAS_REDIRECT_URI,
            "provider": "google",
        })
        return auth_url

    def exchange_code(self, code: str) -> OAuthResult:
        response = self._client.auth.exchange_code_for_token({
            "client_id": settings.NYLAS_CLIENT_ID,
            "redirect_uri": settings.NYLAS_REDIRECT_URI,
            "code": code,
        })
        return OAuthResult(
            grant_id=response.grant_id,
            email=response.email,
        )

    def send_message(
        self,
        grant_id: str,
        to_email: str,
        subject: str,
        body: str,
        send_at: int | None = None,
    ) -> SendResult:
        request_body = {
            "to": [{"email": to_email}],
            "subject": subject,
            "body": body,
        }
        if send_at is not None:
            request_body["send_at"] = send_at

        message, _ = self._client.messages.send(grant_id, request_body)

        schedule_id = getattr(message, "schedule_id", None)
        thread_id = getattr(message, "thread_id", None)

        return SendResult(
            message_id=message.id,
            schedule_id=schedule_id,
            thread_id=thread_id,
        )

    def cancel_scheduled_message(self, grant_id: str, schedule_id: str) -> bool:
        self._client.messages.scheduled_messages.destroy(grant_id, schedule_id)
        return True
