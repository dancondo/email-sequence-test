import hashlib
import hmac
import logging

from nylas import Client as NylasClient

from app.core.config import settings
from app.modules.webhooks.providers.base import (
    ParsedReply,
    WebhookNotification,
    WebhookProvider,
)

logger = logging.getLogger(__name__)

SUPPORTED_TRIGGERS = ("message.created",)


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

    def parse_notification(self, payload: dict) -> list[WebhookNotification]:
        trigger_type = payload.get("type", "")
        if trigger_type not in SUPPORTED_TRIGGERS:
            logger.debug("Ignoring unsupported trigger type: %s", trigger_type)
            return []

        data = payload.get("data", {})
        obj = data.get("object", {})
        grant_id = obj.get("grant_id", "")
        message_id = obj.get("id", "")

        if not grant_id or not message_id:
            logger.warning(
                "Missing grant_id or message_id in %s payload", trigger_type
            )
            return []

        return [
            WebhookNotification(
                trigger_type=trigger_type,
                grant_id=grant_id,
                message_id=message_id,
            )
        ]

    def fetch_message(self, grant_id: str, message_id: str) -> ParsedReply:
        message, _ = self._client.messages.find(grant_id, message_id)
        from_email = ""
        if message.from_:
            sender = message.from_[0]
            if isinstance(sender, dict):
                from_email = sender.get("email", "")
            else:
                from_email = sender.email or ""

        return ParsedReply(
            external_message_id=message.id,
            thread_id=message.thread_id,
            from_email=from_email,
            subject=message.subject or "",
            body=message.body or "",
            received_at=str(message.date or ""),
        )
