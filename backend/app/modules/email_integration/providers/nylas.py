import json
import logging

import requests
from nylas import Client as NylasClient

from app.core.config import settings
from app.modules.email_integration.providers.base import (
    EmailProvider,
    OAuthResult,
    SendResult,
)


logger = logging.getLogger(__name__)


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
        reply_to_message_id: str | None = None,
    ) -> SendResult:
        request_body = {
            "to": [{"email": to_email}],
            "subject": subject,
            "body": body,
        }
        if send_at is not None:
            request_body["send_at"] = send_at
        if reply_to_message_id is not None:
            request_body["reply_to_message_id"] = reply_to_message_id

        # Bypass the SDK's Message deserialization which drops schedule_id.
        # Hit the Nylas API directly to get the raw JSON response.
        http = self._client.messages._http_client
        resp = requests.post(
            f"{http.api_server}/v3/grants/{grant_id}/messages/send",
            headers={
                "Authorization": f"Bearer {http.api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps(request_body, ensure_ascii=False).encode("utf-8"),
            timeout=http.timeout,
        )
        resp.raise_for_status()
        logger.info("Nylas send raw response: %s", resp.json())
        data = resp.json().get("data", {})

        return SendResult(
            message_id=data.get("id", ""),
            schedule_id=data.get("schedule_id"),
            thread_id=data.get("thread_id"),
        )

    def cancel_scheduled_message(self, grant_id: str, schedule_id: str) -> bool:
        self._client.messages.stop_scheduled_message(grant_id, schedule_id)
        return True
