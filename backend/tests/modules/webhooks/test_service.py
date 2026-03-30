from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.modules.classification.schemas import ClassificationResult, ReplyIntent
from app.modules.email_integration.models import IntegrationProvider
from app.modules.sequence_runs.models import (
    EventType,
    SequenceRunCandidateStatus,
)
from app.modules.webhooks.providers.base import ParsedReply, WebhookNotification
from tests.conftest import make_email_account, make_event, make_sequence_run_candidate


# ── process_webhook ──────────────────────────────────────────────────────

async def test_process_webhook_invalid_signature(webhook_service):
    webhook_service._provider.verify_signature.return_value = False

    with pytest.raises(HTTPException) as exc_info:
        await webhook_service.process_webhook(b"body", "bad_sig", {})

    assert exc_info.value.status_code == 401


async def test_process_webhook_valid_with_notifications(webhook_service):
    webhook_service._provider.verify_signature.return_value = True
    n1 = WebhookNotification(
        trigger_type="message.created", grant_id="g1", message_id="m1"
    )
    n2 = WebhookNotification(
        trigger_type="message.created", grant_id="g1", message_id="m2"
    )
    webhook_service._provider.parse_notification.return_value = [n1, n2]

    # Stub out _process_message to avoid complex setup
    webhook_service._process_message = AsyncMock()

    await webhook_service.process_webhook(b"body", "sig", {"type": "message.created"})

    assert webhook_service._process_message.await_count == 2


async def test_process_webhook_no_notifications(webhook_service):
    webhook_service._provider.verify_signature.return_value = True
    webhook_service._provider.parse_notification.return_value = []

    webhook_service._process_message = AsyncMock()

    await webhook_service.process_webhook(b"body", "sig", {})

    webhook_service._process_message.assert_not_awaited()


# ── _process_message ─────────────────────────────────────────────────────

async def test_process_message_found_by_thread_id(
    webhook_service, mock_email_account_repository
):
    run_svc = webhook_service._mock_run_service
    notification = WebhookNotification(
        trigger_type="message.created", grant_id="g1", message_id="m1"
    )
    message = ParsedReply(
        external_message_id="m1",
        thread_id="thr_1",
        from_email="candidate@ex.com",
        subject="Re: Hi",
        body="Thanks",
        received_at="2025-01-01",
    )
    webhook_service._provider.fetch_message.return_value = message

    src = make_sequence_run_candidate()
    run_svc.get_candidate_by_thread_id.return_value = src
    mock_email_account_repository.get_active.return_value = make_email_account(
        email="recruiter@company.com"
    )
    run_svc.has_event.return_value = False

    await webhook_service._process_message(notification)

    run_svc.get_candidate_by_thread_id.assert_awaited_once_with(
        "thr_1", IntegrationProvider.NYLAS
    )
    run_svc.mark_candidate_replied.assert_awaited_once()


async def test_process_message_fallback_to_message_id(
    webhook_service, mock_email_account_repository
):
    run_svc = webhook_service._mock_run_service
    notification = WebhookNotification(
        trigger_type="message.created", grant_id="g1", message_id="m1"
    )
    message = ParsedReply(
        external_message_id="m1",
        thread_id="thr_1",
        from_email="candidate@ex.com",
        subject="Re: Hi",
        body="Thanks",
        received_at="2025-01-01",
    )
    webhook_service._provider.fetch_message.return_value = message

    run_svc.get_candidate_by_thread_id.return_value = None
    src = make_sequence_run_candidate()
    run_svc.get_candidate_by_message_id.return_value = src
    mock_email_account_repository.get_active.return_value = make_email_account(
        email="recruiter@company.com"
    )
    run_svc.has_event.return_value = False

    await webhook_service._process_message(notification)

    run_svc.get_candidate_by_message_id.assert_awaited_once_with(
        "m1", IntegrationProvider.NYLAS
    )


async def test_process_message_no_enrollment_found(webhook_service):
    run_svc = webhook_service._mock_run_service
    notification = WebhookNotification(
        trigger_type="message.created", grant_id="g1", message_id="m1"
    )
    message = ParsedReply(
        external_message_id="m1",
        thread_id=None,
        from_email="unknown@ex.com",
        subject="Hi",
        body="Body",
        received_at="2025-01-01",
    )
    webhook_service._provider.fetch_message.return_value = message
    run_svc.get_candidate_by_thread_id.return_value = None
    run_svc.get_candidate_by_message_id.return_value = None

    # Should not raise
    await webhook_service._process_message(notification)

    run_svc.mark_candidate_replied.assert_not_awaited()


async def test_process_message_outbound(
    webhook_service, mock_email_account_repository
):
    run_svc = webhook_service._mock_run_service
    notification = WebhookNotification(
        trigger_type="message.created", grant_id="g1", message_id="m1"
    )
    message = ParsedReply(
        external_message_id="m1",
        thread_id="thr_1",
        from_email="recruiter@company.com",
        subject="Hi",
        body="Hello",
        received_at="2025-01-01",
    )
    webhook_service._provider.fetch_message.return_value = message
    src = make_sequence_run_candidate()
    run_svc.get_candidate_by_thread_id.return_value = src
    mock_email_account_repository.get_active.return_value = make_email_account(
        email="recruiter@company.com"
    )
    run_svc.has_event.return_value = False

    await webhook_service._process_message(notification)

    run_svc.record_email_sent.assert_awaited_once()
    run_svc.mark_candidate_replied.assert_not_awaited()


# ── _process_reply ───────────────────────────────────────────────────────

async def test_process_reply_already_terminal(webhook_service):
    run_svc = webhook_service._mock_run_service
    src = make_sequence_run_candidate(status=SequenceRunCandidateStatus.REPLIED)
    notification = WebhookNotification(
        trigger_type="message.created", grant_id="g1", message_id="m1"
    )
    message = ParsedReply(
        external_message_id="m1",
        thread_id="thr_1",
        from_email="c@ex.com",
        subject="Re: Hi",
        body="Ok",
        received_at="2025-01-01",
    )

    await webhook_service._process_reply(src, notification, message)

    run_svc.mark_candidate_replied.assert_not_awaited()


async def test_process_reply_duplicate_event(webhook_service):
    run_svc = webhook_service._mock_run_service
    src = make_sequence_run_candidate(status=SequenceRunCandidateStatus.ACTIVE)
    run_svc.has_event.return_value = True
    notification = WebhookNotification(
        trigger_type="message.created", grant_id="g1", message_id="m1"
    )
    message = ParsedReply(
        external_message_id="m1",
        thread_id="thr_1",
        from_email="c@ex.com",
        subject="Re: Hi",
        body="Ok",
        received_at="2025-01-01",
    )

    await webhook_service._process_reply(src, notification, message)

    run_svc.mark_candidate_replied.assert_not_awaited()


# ── _process_message_created ─────────────────────────────────────────────

async def test_process_message_created_duplicate(webhook_service):
    run_svc = webhook_service._mock_run_service
    run_svc.has_event.return_value = True
    src = make_sequence_run_candidate()
    notification = WebhookNotification(
        trigger_type="message.created", grant_id="g1", message_id="m1"
    )
    message = ParsedReply(
        external_message_id="m1",
        thread_id="thr_1",
        from_email="r@company.com",
        subject="Hi",
        body="Hello",
        received_at="2025-01-01",
    )

    await webhook_service._process_message_created(src, notification, message)

    run_svc.record_email_sent.assert_not_awaited()


async def test_process_message_created_with_thread_id(webhook_service):
    run_svc = webhook_service._mock_run_service
    run_svc.has_event.return_value = False
    src = make_sequence_run_candidate()
    notification = WebhookNotification(
        trigger_type="message.created", grant_id="g1", message_id="m1"
    )
    message = ParsedReply(
        external_message_id="m1",
        thread_id="thr_1",
        from_email="r@company.com",
        subject="Hi",
        body="Hello",
        received_at="2025-01-01",
    )

    await webhook_service._process_message_created(src, notification, message)

    run_svc.backfill_thread_id.assert_awaited_once()
    run_svc.record_email_sent.assert_awaited_once()


async def test_process_message_created_no_thread_id(webhook_service):
    run_svc = webhook_service._mock_run_service
    run_svc.has_event.return_value = False
    src = make_sequence_run_candidate()
    notification = WebhookNotification(
        trigger_type="message.created", grant_id="g1", message_id="m1"
    )
    message = ParsedReply(
        external_message_id="m1",
        thread_id=None,
        from_email="r@company.com",
        subject="Hi",
        body="Hello",
        received_at="2025-01-01",
    )

    await webhook_service._process_message_created(src, notification, message)

    run_svc.backfill_thread_id.assert_not_awaited()
    run_svc.record_email_sent.assert_awaited_once()


async def test_process_message_created_skipped_when_candidate_terminal(webhook_service):
    run_svc = webhook_service._mock_run_service
    run_svc.has_event.return_value = False
    src = make_sequence_run_candidate(status=SequenceRunCandidateStatus.INTERESTED)
    notification = WebhookNotification(
        trigger_type="message.created", grant_id="g1", message_id="m1"
    )
    message = ParsedReply(
        external_message_id="m1",
        thread_id="thr_1",
        from_email="r@company.com",
        subject="Follow up",
        body="Following up",
        received_at="2025-01-01",
    )

    await webhook_service._process_message_created(src, notification, message)

    run_svc.record_email_sent.assert_not_awaited()


# ── _classify_reply ──────────────────────────────────────────────────────

async def test_classify_reply_success(
    webhook_service, mock_classification_provider
):
    run_svc = webhook_service._mock_run_service
    src = make_sequence_run_candidate()

    mock_classification_provider.classify_reply.return_value = ClassificationResult(
        intent=ReplyIntent.INTERESTED,
        confidence=0.9,
        reasoning="Positive",
    )

    await webhook_service._classify_reply(src, "I'm interested!")

    run_svc.add_classification_event.assert_awaited_once()


async def test_classify_reply_with_referral(
    webhook_service, mock_classification_provider
):
    run_svc = webhook_service._mock_run_service
    src = make_sequence_run_candidate()

    mock_classification_provider.classify_reply.return_value = ClassificationResult(
        intent=ReplyIntent.NOT_INTERESTED,
        confidence=0.8,
        reasoning="Declined",
        referral_email="ref@ex.com",
        referral_name="Ref",
    )

    await webhook_service._classify_reply(src, "Not me, talk to Ref")

    run_svc.handle_referral.assert_awaited_once_with(
        src=src, referral_email="ref@ex.com", referral_name="Ref"
    )


async def test_classify_reply_failure_swallowed(
    webhook_service, mock_classification_provider
):
    run_svc = webhook_service._mock_run_service
    src = make_sequence_run_candidate()

    mock_classification_provider.classify_reply.side_effect = Exception("API error")

    # Should not raise
    await webhook_service._classify_reply(src, "Some reply")

    run_svc.add_classification_event.assert_not_awaited()


# ── _cancel_pending_followups ────────────────────────────────────────────

async def test_cancel_pending_followups_success(
    webhook_service, mock_email_provider
):
    run_svc = webhook_service._mock_run_service
    e1 = make_event(
        id=1,
        external_schedule_id="sch_1",
        step_order=2,
        sequence_run_candidate_id=10,
    )
    e2 = make_event(
        id=2,
        external_schedule_id="sch_2",
        step_order=3,
        sequence_run_candidate_id=10,
    )
    run_svc.get_pending_scheduled_events.return_value = [e1, e2]

    await webhook_service._cancel_pending_followups(
        sequence_run_candidate_id=10, grant_id="g1"
    )

    assert mock_email_provider.cancel_scheduled_message.call_count == 2
    assert run_svc.add_canceled_event.await_count == 2


async def test_cancel_pending_followups_no_schedule_id(
    webhook_service, mock_email_provider
):
    run_svc = webhook_service._mock_run_service
    event = make_event(id=1, external_schedule_id=None, step_order=2)
    run_svc.get_pending_scheduled_events.return_value = [event]

    await webhook_service._cancel_pending_followups(
        sequence_run_candidate_id=10, grant_id="g1"
    )

    mock_email_provider.cancel_scheduled_message.assert_not_called()
    run_svc.add_canceled_event.assert_not_awaited()


async def test_cancel_pending_followups_cancel_failure(
    webhook_service, mock_email_provider
):
    run_svc = webhook_service._mock_run_service
    e1 = make_event(
        id=1,
        external_schedule_id="sch_1",
        step_order=2,
        sequence_run_candidate_id=10,
    )
    e2 = make_event(
        id=2,
        external_schedule_id="sch_2",
        step_order=3,
        sequence_run_candidate_id=10,
    )
    run_svc.get_pending_scheduled_events.return_value = [e1, e2]
    mock_email_provider.cancel_scheduled_message.side_effect = [
        Exception("Nylas error"),
        True,
    ]

    # Should not raise — error is swallowed for first, second succeeds
    await webhook_service._cancel_pending_followups(
        sequence_run_candidate_id=10, grant_id="g1"
    )

    # Only the second event should have a canceled event recorded
    assert run_svc.add_canceled_event.await_count == 1
