import logging

from fastapi import HTTPException

from app.modules.email_integration.models import IntegrationProvider
from app.modules.email_integration.service import EmailIntegrationService
from app.modules.sequence_runs.models import (
    EventType,
    SequenceRunCandidateStatus,
)
from app.modules.sequence_runs.repository import SequenceRunRepository
from app.modules.webhooks.providers.base import WebhookProvider

logger = logging.getLogger(__name__)


class WebhookService:
    def __init__(
        self,
        provider: WebhookProvider,
        run_repository: SequenceRunRepository,
        email_service: EmailIntegrationService,
    ) -> None:
        self._provider = provider
        self._run_repo = run_repository
        self._email_service = email_service

    async def process_webhook(
        self, raw_body: bytes, signature: str, payload: dict
    ) -> None:
        if not self._provider.verify_signature(raw_body, signature):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

        deltas = self._provider.parse_notification(payload)

        for delta in deltas:
            await self._process_delta(delta.grant_id, delta.message_id)

    async def _process_delta(self, grant_id: str, message_id: str) -> None:
        message = self._provider.fetch_message(grant_id, message_id)

        if not message.thread_id:
            logger.warning("Reply %s has no thread_id, skipping", message_id)
            return

        src = await self._run_repo.get_candidate_by_thread_id(
            message.thread_id, IntegrationProvider.NYLAS
        )
        if not src:
            logger.info(
                "No enrollment found for thread_id=%s, skipping", message.thread_id
            )
            return

        if src.status == SequenceRunCandidateStatus.REPLIED:
            return

        already_exists = await self._run_repo.has_event(
            src.id, EventType.REPLY_RECEIVED, message.external_message_id
        )
        if already_exists:
            return

        await self._run_repo.update_candidate_status(
            src, SequenceRunCandidateStatus.REPLIED
        )

        await self._run_repo.add_event(
            sequence_run_candidate_id=src.id,
            event_type=EventType.REPLY_RECEIVED,
            external_message_id=message.external_message_id,
            external_thread_id=message.thread_id,
            external_provider=IntegrationProvider.NYLAS,
            extra={
                "from_email": message.from_email,
                "subject": message.subject,
                "body": message.body,
                "received_at": message.received_at,
            },
        )

        await self._cancel_pending_followups(src.id, grant_id)

    async def _cancel_pending_followups(
        self, sequence_run_candidate_id: int, grant_id: str
    ) -> None:
        pending_events = await self._run_repo.get_pending_scheduled_events(
            sequence_run_candidate_id
        )
        for event in pending_events:
            if not event.external_schedule_id:
                continue
            try:
                self._email_service.cancel_scheduled_message(
                    grant_id=grant_id,
                    schedule_id=event.external_schedule_id,
                )
            except Exception:
                logger.warning(
                    "Failed to cancel scheduled message %s",
                    event.external_schedule_id,
                    exc_info=True,
                )
