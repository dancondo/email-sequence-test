import hashlib
import hmac

from nylas import Client as NylasClient

from app.core.config import settings
from app.modules.webhooks.providers.base import (
    ParsedReply,
    WebhookDelta,
    WebhookProvider,
)


class NylasWebhookProvider(WebhookProvider):
    def __init__(self, client: NylasClient) -> None:
        self._client = client

    def verify_signature(self, raw_body: bytes, signature: str) -> bool:
        expected = hmac.new(
            settings.NYLAS_WEBHOOK_SECRET.encode(),
            raw_body,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    def parse_notification(self, payload: dict) -> list[WebhookDelta]:
        deltas = []
        for delta in payload.get("deltas", []):
            if delta.get("type") != "message.created":
                continue
            object_data = delta.get("object_data", {})
            grant_id = object_data.get("grant_id", "")
            message_id = object_data.get("id", "")
            if grant_id and message_id:
                deltas.append(WebhookDelta(grant_id=grant_id, message_id=message_id))
        return deltas

    def fetch_message(self, grant_id: str, message_id: str) -> ParsedReply:
        message, _ = self._client.messages.find(grant_id, message_id)
        from_email = ""
        if message.from_:
            from_email = message.from_[0].email if message.from_[0].email else ""

        return ParsedReply(
            external_message_id=message.id,
            thread_id=message.thread_id,
            from_email=from_email,
            subject=message.subject or "",
            body=message.body or "",
            received_at=str(message.date or ""),
        )
