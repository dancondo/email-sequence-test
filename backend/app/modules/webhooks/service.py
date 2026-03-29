import logging

from fastapi import HTTPException

from app.modules.classification.service import ClassificationService
from app.modules.email_integration.models import IntegrationProvider
from app.modules.email_integration.service import EmailIntegrationService
from app.modules.sequence_runs.models import (
    EventType,
    SequenceRunCandidateStatus,
)
from app.modules.sequence_runs.service import SequenceRunService
from app.modules.webhooks.providers.base import WebhookNotification, WebhookProvider

logger = logging.getLogger(__name__)


class WebhookService:
    def __init__(
        self,
        provider: WebhookProvider,
        run_service: SequenceRunService,
        email_service: EmailIntegrationService,
        classification_service: ClassificationService,
    ) -> None:
        self._provider = provider
        self._run_service = run_service
        self._email_service = email_service
        self._classification_service = classification_service

    async def process_webhook(
        self, raw_body: bytes, signature: str, payload: dict
    ) -> None:
        if not self._provider.verify_signature(raw_body, signature):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

        notifications = self._provider.parse_notification(payload)

        for notification in notifications:
            await self._process_message(notification)

    async def _process_message(self, notification: WebhookNotification) -> None:
        message = self._provider.fetch_message(
            notification.grant_id, notification.message_id
        )

        src = None
        if message.thread_id:
            src = await self._run_service.get_candidate_by_thread_id(
                message.thread_id, IntegrationProvider.NYLAS
            )

        # Fallback: look up by message_id when thread_id is missing or
        # didn't match any stored events (common for scheduled sends).
        if not src:
            src = await self._run_service.get_candidate_by_message_id(
                message.external_message_id, IntegrationProvider.NYLAS
            )

        if not src:
            logger.info(
                "No enrollment found for message_id=%s thread_id=%s, skipping",
                notification.message_id,
                message.thread_id,
            )
            return

        is_inbound = await self._is_inbound_message(message.from_email)
        if is_inbound:
            await self._process_reply(src, notification, message)
        else:
            await self._process_message_created(src, notification, message)

    async def _is_inbound_message(self, from_email: str) -> bool:
        account = await self._email_service.get_status()
        if not account:
            return False
        return from_email.lower() != account.email.lower()

    async def _process_reply(self, src, notification, message) -> None:
        terminal_statuses = {
            SequenceRunCandidateStatus.REPLIED,
            SequenceRunCandidateStatus.INTERESTED,
            SequenceRunCandidateStatus.NOT_INTERESTED,
        }
        if src.status in terminal_statuses:
            return

        already_exists = await self._run_service.has_event(
            src.id, EventType.REPLY_RECEIVED, message.external_message_id
        )
        if already_exists:
            return

        await self._run_service.mark_candidate_replied(
            src=src,
            external_message_id=message.external_message_id,
            thread_id=message.thread_id,
            from_email=message.from_email,
            subject=message.subject,
            body=message.body,
            received_at=message.received_at,
        )

        await self._classify_reply(src, message.body)

        await self._cancel_pending_followups(src.id, notification.grant_id)

    async def _process_message_created(self, src, notification, message) -> None:
        already_exists = await self._run_service.has_event(
            src.id, EventType.EMAIL_SENT, message.external_message_id
        )
        if already_exists:
            return

        # Backfill thread_id on the original EMAIL_SCHEDULED event so future
        # inbound replies on this thread can be matched to the candidate.
        if message.thread_id:
            await self._run_service.backfill_thread_id(
                sequence_run_candidate_id=src.id,
                external_message_id=message.external_message_id,
                thread_id=message.thread_id,
            )

        await self._run_service.record_email_sent(
            src=src,
            external_message_id=message.external_message_id,
            thread_id=message.thread_id,
        )

    async def _classify_reply(self, src, reply_body: str) -> None:
        try:
            result = self._classification_service.classify_reply(reply_body)
            await self._run_service.add_classification_event(
                src=src,
                intent=result.intent,
                confidence=result.confidence,
                reasoning=result.reasoning,
            )

            if result.referral_email:
                await self._run_service.handle_referral(
                    src=src,
                    referral_email=result.referral_email,
                    referral_name=result.referral_name,
                )
        except Exception:
            logger.warning(
                "Failed to classify reply for candidate %s",
                src.id,
                exc_info=True,
            )

    async def _cancel_pending_followups(
        self, sequence_run_candidate_id: int, grant_id: str
    ) -> None:
        pending_events = await self._run_service.get_pending_scheduled_events(
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
                await self._run_service.add_canceled_event(
                    sequence_run_candidate_id=event.sequence_run_candidate_id,
                    step_order=event.step_order,
                    external_schedule_id=event.external_schedule_id,
                )
            except Exception:
                logger.warning(
                    "Failed to cancel scheduled message %s",
                    event.external_message_id,
                    exc_info=True,
                )
