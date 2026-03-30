from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.modules.classification.schemas import ReplyIntent
from app.modules.email_integration.models import IntegrationProvider
from app.modules.email_integration.providers.base import SendResult
from app.modules.sequence_runs.models import (
    EventType,
    SequenceRunCandidateStatus,
    SequenceRunStatus,
)
from tests.conftest import (
    make_candidate,
    make_email_account,
    make_event,
    make_sequence,
    make_sequence_run,
    make_sequence_run_candidate,
)


# ── create_run ───────────────────────────────────────────────────────────

async def test_create_run(
    sequence_run_service, mock_sequence_repository, mock_sequence_run_repository
):
    mock_sequence_repository.get_by_id.return_value = make_sequence()
    expected_run = make_sequence_run()
    mock_sequence_run_repository.create.return_value = expected_run

    result = await sequence_run_service.create_run(sequence_id=1)

    assert result is expected_run


async def test_create_run_sequence_not_found(
    sequence_run_service, mock_sequence_repository
):
    mock_sequence_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await sequence_run_service.create_run(sequence_id=999)

    assert exc_info.value.status_code == 404


# ── list_runs ────────────────────────────────────────────────────────────

async def test_list_runs(
    sequence_run_service, mock_sequence_repository, mock_sequence_run_repository
):
    mock_sequence_repository.get_by_id.return_value = make_sequence()
    runs = [make_sequence_run(id=1), make_sequence_run(id=2)]
    mock_sequence_run_repository.list_by_sequence.return_value = runs

    result = await sequence_run_service.list_runs(sequence_id=1)

    assert len(result) == 2


# ── get_run ──────────────────────────────────────────────────────────────

async def test_get_run_found(
    sequence_run_service, mock_sequence_run_repository
):
    run = make_sequence_run(id=1, sequence_id=5)
    mock_sequence_run_repository.get_by_id.return_value = run

    result = await sequence_run_service.get_run(sequence_id=5, run_id=1)

    assert result is run


async def test_get_run_not_found(
    sequence_run_service, mock_sequence_run_repository
):
    mock_sequence_run_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await sequence_run_service.get_run(sequence_id=1, run_id=999)

    assert exc_info.value.status_code == 404


async def test_get_run_wrong_sequence_id(
    sequence_run_service, mock_sequence_run_repository
):
    run = make_sequence_run(id=1, sequence_id=5)
    mock_sequence_run_repository.get_by_id.return_value = run

    with pytest.raises(HTTPException) as exc_info:
        await sequence_run_service.get_run(sequence_id=99, run_id=1)

    assert exc_info.value.status_code == 404


# ── delete_run ───────────────────────────────────────────────────────────

async def test_delete_run_draft(
    sequence_run_service, mock_sequence_run_repository
):
    run = make_sequence_run(status=SequenceRunStatus.DRAFT)
    mock_sequence_run_repository.get_by_id.return_value = run

    await sequence_run_service.delete_run(sequence_id=1, run_id=1)

    mock_sequence_run_repository.delete.assert_awaited_once_with(run)


async def test_delete_run_not_draft(
    sequence_run_service, mock_sequence_run_repository
):
    run = make_sequence_run(status=SequenceRunStatus.ACTIVE)
    mock_sequence_run_repository.get_by_id.return_value = run

    with pytest.raises(HTTPException) as exc_info:
        await sequence_run_service.delete_run(sequence_id=1, run_id=1)

    assert exc_info.value.status_code == 409


# ── add_candidates ───────────────────────────────────────────────────────

async def test_add_candidates_all_new(
    sequence_run_service,
    mock_sequence_run_repository,
    mock_candidate_repository,
):
    run = make_sequence_run(status=SequenceRunStatus.DRAFT)
    run.candidates = []
    mock_sequence_run_repository.get_by_id.return_value = run
    mock_candidate_repository.get_by_id.return_value = make_candidate()

    result = await sequence_run_service.add_candidates(
        sequence_id=1, run_id=1, candidate_ids=[10, 20]
    )

    assert result.added == 2
    assert result.already_enrolled == 0
    assert result.not_found == 0


async def test_add_candidates_already_enrolled(
    sequence_run_service,
    mock_sequence_run_repository,
    mock_candidate_repository,
):
    existing_src = make_sequence_run_candidate(candidate_id=10)
    run = make_sequence_run(status=SequenceRunStatus.DRAFT)
    run.candidates = [existing_src]
    mock_sequence_run_repository.get_by_id.return_value = run
    mock_candidate_repository.get_by_id.return_value = make_candidate()

    result = await sequence_run_service.add_candidates(
        sequence_id=1, run_id=1, candidate_ids=[10, 20]
    )

    assert result.already_enrolled == 1
    assert result.added == 1


async def test_add_candidates_not_found(
    sequence_run_service,
    mock_sequence_run_repository,
    mock_candidate_repository,
):
    run = make_sequence_run(status=SequenceRunStatus.DRAFT)
    run.candidates = []
    mock_sequence_run_repository.get_by_id.return_value = run
    mock_candidate_repository.get_by_id.return_value = None

    result = await sequence_run_service.add_candidates(
        sequence_id=1, run_id=1, candidate_ids=[999]
    )

    assert result.not_found == 1
    assert result.added == 0


async def test_add_candidates_not_draft(
    sequence_run_service, mock_sequence_run_repository
):
    run = make_sequence_run(status=SequenceRunStatus.ACTIVE)
    mock_sequence_run_repository.get_by_id.return_value = run

    with pytest.raises(HTTPException) as exc_info:
        await sequence_run_service.add_candidates(
            sequence_id=1, run_id=1, candidate_ids=[1]
        )

    assert exc_info.value.status_code == 409


# ── remove_candidate ─────────────────────────────────────────────────────

async def test_remove_candidate_success(
    sequence_run_service, mock_sequence_run_repository
):
    run = make_sequence_run(status=SequenceRunStatus.DRAFT)
    mock_sequence_run_repository.get_by_id.return_value = run
    src = make_sequence_run_candidate()
    mock_sequence_run_repository.get_candidate.return_value = src

    await sequence_run_service.remove_candidate(
        sequence_id=1, run_id=1, candidate_id=1
    )

    mock_sequence_run_repository.remove_candidate.assert_awaited_once_with(src)


async def test_remove_candidate_not_draft(
    sequence_run_service, mock_sequence_run_repository
):
    run = make_sequence_run(status=SequenceRunStatus.ACTIVE)
    mock_sequence_run_repository.get_by_id.return_value = run

    with pytest.raises(HTTPException) as exc_info:
        await sequence_run_service.remove_candidate(
            sequence_id=1, run_id=1, candidate_id=1
        )

    assert exc_info.value.status_code == 409


async def test_remove_candidate_not_found(
    sequence_run_service, mock_sequence_run_repository
):
    run = make_sequence_run(status=SequenceRunStatus.DRAFT)
    mock_sequence_run_repository.get_by_id.return_value = run
    mock_sequence_run_repository.get_candidate.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await sequence_run_service.remove_candidate(
            sequence_id=1, run_id=1, candidate_id=999
        )

    assert exc_info.value.status_code == 404


# ── get_candidates / get_candidate_timeline ──────────────────────────────

async def test_get_candidates(
    sequence_run_service, mock_sequence_run_repository
):
    run = make_sequence_run()
    mock_sequence_run_repository.get_by_id.return_value = run
    candidates = [make_sequence_run_candidate()]
    mock_sequence_run_repository.list_candidates.return_value = candidates

    result = await sequence_run_service.get_candidates(sequence_id=1, run_id=1)

    assert result == candidates


async def test_get_candidate_timeline_success(
    sequence_run_service, mock_sequence_run_repository
):
    run = make_sequence_run()
    mock_sequence_run_repository.get_by_id.return_value = run
    src = make_sequence_run_candidate()
    mock_sequence_run_repository.get_candidate.return_value = src
    events = [make_event()]
    mock_sequence_run_repository.get_events.return_value = events

    result_src, result_events = await sequence_run_service.get_candidate_timeline(
        sequence_id=1, run_id=1, candidate_id=1
    )

    assert result_src is src
    assert result_events == events


async def test_get_candidate_timeline_not_found(
    sequence_run_service, mock_sequence_run_repository
):
    run = make_sequence_run()
    mock_sequence_run_repository.get_by_id.return_value = run
    mock_sequence_run_repository.get_candidate.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await sequence_run_service.get_candidate_timeline(
            sequence_id=1, run_id=1, candidate_id=999
        )

    assert exc_info.value.status_code == 404


# ── start_run ────────────────────────────────────────────────────────────

async def test_start_run_success(
    sequence_run_service,
    mock_sequence_run_repository,
    mock_sequence_repository,
    mock_email_account_repository,
    mock_email_provider,
):
    run = make_sequence_run(status=SequenceRunStatus.DRAFT)
    mock_sequence_run_repository.get_by_id.return_value = run

    src = make_sequence_run_candidate(id=10, candidate_id=1, email="c@ex.com")
    mock_sequence_run_repository.list_candidates.return_value = [src]

    account = make_email_account()
    mock_email_account_repository.get_active.return_value = account

    step1 = MagicMock()
    step1.step_order = 1
    step1.step_type.value = "default"
    step1.subject = "Hello"
    step1.body = "Hi there"
    step1.delay_minutes = 0
    step2 = MagicMock()
    step2.step_order = 2
    step2.step_type.value = "default"
    step2.subject = "Follow up"
    step2.body = "Following up"
    step2.delay_minutes = 2
    seq = make_sequence(steps=[step1, step2])
    mock_sequence_repository.get_by_id.return_value = seq

    mock_email_provider.send_message.return_value = SendResult(
        message_id="msg_1", schedule_id="sch_1", thread_id="thr_1"
    )
    mock_sequence_run_repository.add_event.return_value = make_event()

    result = await sequence_run_service.start_run(sequence_id=1, run_id=1)

    assert result.enrollments_started == 1
    assert mock_email_provider.send_message.call_count == 2

    # First call should be immediate (send_at=None)
    first_call = mock_email_provider.send_message.call_args_list[0]
    assert first_call.kwargs.get("send_at") is None

    # Second call should be scheduled
    second_call = mock_email_provider.send_message.call_args_list[1]
    assert second_call.kwargs.get("send_at") is not None

    mock_sequence_run_repository.update_status.assert_awaited_once()


async def test_start_run_not_draft(
    sequence_run_service, mock_sequence_run_repository
):
    run = make_sequence_run(status=SequenceRunStatus.ACTIVE)
    mock_sequence_run_repository.get_by_id.return_value = run

    with pytest.raises(HTTPException) as exc_info:
        await sequence_run_service.start_run(sequence_id=1, run_id=1)

    assert exc_info.value.status_code == 409


async def test_start_run_no_candidates(
    sequence_run_service, mock_sequence_run_repository
):
    run = make_sequence_run(status=SequenceRunStatus.DRAFT)
    mock_sequence_run_repository.get_by_id.return_value = run
    mock_sequence_run_repository.list_candidates.return_value = []

    with pytest.raises(HTTPException) as exc_info:
        await sequence_run_service.start_run(sequence_id=1, run_id=1)

    assert exc_info.value.status_code == 400
    assert "candidate" in exc_info.value.detail.lower()


async def test_start_run_no_email_account(
    sequence_run_service,
    mock_sequence_run_repository,
    mock_email_account_repository,
):
    run = make_sequence_run(status=SequenceRunStatus.DRAFT)
    mock_sequence_run_repository.get_by_id.return_value = run
    mock_sequence_run_repository.list_candidates.return_value = [
        make_sequence_run_candidate()
    ]
    mock_email_account_repository.get_active.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await sequence_run_service.start_run(sequence_id=1, run_id=1)

    assert exc_info.value.status_code == 400
    assert "email" in exc_info.value.detail.lower()


async def test_start_run_no_steps(
    sequence_run_service,
    mock_sequence_run_repository,
    mock_sequence_repository,
    mock_email_account_repository,
):
    run = make_sequence_run(status=SequenceRunStatus.DRAFT)
    mock_sequence_run_repository.get_by_id.return_value = run
    mock_sequence_run_repository.list_candidates.return_value = [
        make_sequence_run_candidate()
    ]
    mock_email_account_repository.get_active.return_value = make_email_account()
    mock_sequence_repository.get_by_id.return_value = make_sequence(steps=[])

    with pytest.raises(HTTPException) as exc_info:
        await sequence_run_service.start_run(sequence_id=1, run_id=1)

    assert exc_info.value.status_code == 400


async def test_start_run_email_send_failure(
    sequence_run_service,
    mock_sequence_run_repository,
    mock_sequence_repository,
    mock_email_account_repository,
    mock_email_provider,
):
    run = make_sequence_run(status=SequenceRunStatus.DRAFT)
    mock_sequence_run_repository.get_by_id.return_value = run

    src = make_sequence_run_candidate(id=10, email="c@ex.com")
    mock_sequence_run_repository.list_candidates.return_value = [src]
    mock_email_account_repository.get_active.return_value = make_email_account()

    step = MagicMock()
    step.step_order = 1
    step.step_type.value = "default"
    step.subject = "Hello"
    step.body = "Hi"
    step.delay_minutes = 0
    mock_sequence_repository.get_by_id.return_value = make_sequence(steps=[step])

    mock_email_provider.send_message.side_effect = Exception("Send failed")
    mock_sequence_run_repository.add_event.return_value = make_event()

    result = await sequence_run_service.start_run(sequence_id=1, run_id=1)

    # Should still complete — failure recorded as EMAIL_FAILED event
    assert result.enrollments_started == 1
    add_event_calls = mock_sequence_run_repository.add_event.call_args_list
    event_types = [c.kwargs["event_type"] for c in add_event_calls]
    assert EventType.EMAIL_FAILED in event_types


async def test_start_run_filters_non_default_steps(
    sequence_run_service,
    mock_sequence_run_repository,
    mock_sequence_repository,
    mock_email_account_repository,
    mock_email_provider,
):
    run = make_sequence_run(status=SequenceRunStatus.DRAFT)
    mock_sequence_run_repository.get_by_id.return_value = run
    mock_sequence_run_repository.list_candidates.return_value = [
        make_sequence_run_candidate(id=10, email="c@ex.com")
    ]
    mock_email_account_repository.get_active.return_value = make_email_account()

    default_step = MagicMock()
    default_step.step_order = 1
    default_step.step_type.value = "default"
    default_step.subject = "Hi"
    default_step.body = "Body"
    default_step.delay_minutes = 0

    referral_step = MagicMock()
    referral_step.step_order = 2
    referral_step.step_type.value = "referral_handoff"
    referral_step.subject = "Referral"
    referral_step.body = "Body"
    referral_step.delay_minutes = 0

    mock_sequence_repository.get_by_id.return_value = make_sequence(
        steps=[default_step, referral_step]
    )
    mock_email_provider.send_message.return_value = SendResult(message_id="msg_1")
    mock_sequence_run_repository.add_event.return_value = make_event()

    await sequence_run_service.start_run(sequence_id=1, run_id=1)

    # Only 1 email sent (the default step, not the referral_handoff)
    assert mock_email_provider.send_message.call_count == 1


# ── send_reply ───────────────────────────────────────────────────────────

async def test_send_reply_success(
    sequence_run_service,
    mock_sequence_run_repository,
    mock_email_account_repository,
    mock_email_provider,
):
    run = make_sequence_run()
    mock_sequence_run_repository.get_by_id.return_value = run

    src = make_sequence_run_candidate(
        status=SequenceRunCandidateStatus.REPLIED, email="c@ex.com"
    )
    mock_sequence_run_repository.get_candidate.return_value = src

    mock_email_account_repository.get_active.return_value = make_email_account()

    reply_event = make_event(
        external_message_id="original_msg",
        extra={"subject": "Opportunity"},
    )
    mock_sequence_run_repository.get_last_reply_received_event.return_value = (
        reply_event
    )
    mock_email_provider.send_message.return_value = SendResult(
        message_id="reply_msg", thread_id="thr_1"
    )
    sent_event = make_event(id=99)
    mock_sequence_run_repository.add_event.return_value = sent_event

    result = await sequence_run_service.send_reply(
        sequence_id=1, run_id=1, candidate_id=1, body="Thanks for the reply!"
    )

    assert result is sent_event
    call_kwargs = mock_email_provider.send_message.call_args.kwargs
    assert call_kwargs["subject"] == "Re: Opportunity"
    assert call_kwargs["reply_to_message_id"] == "original_msg"


async def test_send_reply_subject_already_has_re(
    sequence_run_service,
    mock_sequence_run_repository,
    mock_email_account_repository,
    mock_email_provider,
):
    run = make_sequence_run()
    mock_sequence_run_repository.get_by_id.return_value = run
    src = make_sequence_run_candidate(status=SequenceRunCandidateStatus.REPLIED)
    mock_sequence_run_repository.get_candidate.return_value = src
    mock_email_account_repository.get_active.return_value = make_email_account()

    reply_event = make_event(
        external_message_id="msg_1",
        extra={"subject": "Re: Opportunity"},
    )
    mock_sequence_run_repository.get_last_reply_received_event.return_value = (
        reply_event
    )
    mock_email_provider.send_message.return_value = SendResult(message_id="msg_2")
    mock_sequence_run_repository.add_event.return_value = make_event()

    await sequence_run_service.send_reply(
        sequence_id=1, run_id=1, candidate_id=1, body="Follow up"
    )

    call_kwargs = mock_email_provider.send_message.call_args.kwargs
    assert call_kwargs["subject"] == "Re: Opportunity"  # No double "Re: Re:"


async def test_send_reply_candidate_not_found(
    sequence_run_service, mock_sequence_run_repository
):
    run = make_sequence_run()
    mock_sequence_run_repository.get_by_id.return_value = run
    mock_sequence_run_repository.get_candidate.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await sequence_run_service.send_reply(
            sequence_id=1, run_id=1, candidate_id=999, body="Hi"
        )

    assert exc_info.value.status_code == 404


async def test_send_reply_wrong_status(
    sequence_run_service, mock_sequence_run_repository
):
    run = make_sequence_run()
    mock_sequence_run_repository.get_by_id.return_value = run
    src = make_sequence_run_candidate(status=SequenceRunCandidateStatus.ACTIVE)
    mock_sequence_run_repository.get_candidate.return_value = src

    with pytest.raises(HTTPException) as exc_info:
        await sequence_run_service.send_reply(
            sequence_id=1, run_id=1, candidate_id=1, body="Hi"
        )

    assert exc_info.value.status_code == 409


async def test_send_reply_no_email_account(
    sequence_run_service,
    mock_sequence_run_repository,
    mock_email_account_repository,
):
    run = make_sequence_run()
    mock_sequence_run_repository.get_by_id.return_value = run
    src = make_sequence_run_candidate(status=SequenceRunCandidateStatus.REPLIED)
    mock_sequence_run_repository.get_candidate.return_value = src
    mock_email_account_repository.get_active.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await sequence_run_service.send_reply(
            sequence_id=1, run_id=1, candidate_id=1, body="Hi"
        )

    assert exc_info.value.status_code == 400


async def test_send_reply_no_reply_event(
    sequence_run_service,
    mock_sequence_run_repository,
    mock_email_account_repository,
):
    run = make_sequence_run()
    mock_sequence_run_repository.get_by_id.return_value = run
    src = make_sequence_run_candidate(status=SequenceRunCandidateStatus.REPLIED)
    mock_sequence_run_repository.get_candidate.return_value = src
    mock_email_account_repository.get_active.return_value = make_email_account()
    mock_sequence_run_repository.get_last_reply_received_event.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await sequence_run_service.send_reply(
            sequence_id=1, run_id=1, candidate_id=1, body="Hi"
        )

    assert exc_info.value.status_code == 409


# ── Metrics ──────────────────────────────────────────────────────────────

async def test_get_run_metrics(
    sequence_run_service, mock_sequence_run_repository
):
    run = make_sequence_run()
    mock_sequence_run_repository.get_by_id.return_value = run
    mock_sequence_run_repository.get_run_metrics.return_value = {
        "total_sent": 5,
        "total_replies": 2,
    }

    result = await sequence_run_service.get_run_metrics(sequence_id=1, run_id=1)

    assert result["total_sent"] == 5


async def test_get_all_sequence_run_metrics(
    sequence_run_service,
    mock_sequence_run_repository,
    mock_sequence_repository,
):
    mock_sequence_repository.get_by_id.return_value = make_sequence()
    mock_sequence_run_repository.get_all_sequence_run_metrics.return_value = {
        "total_sent": 10,
    }

    result = await sequence_run_service.get_all_sequence_run_metrics(sequence_id=1)

    assert result["total_sent"] == 10


# ── Webhook-facing methods ───────────────────────────────────────────────

async def test_get_candidate_by_thread_id(
    sequence_run_service, mock_sequence_run_repository
):
    src = make_sequence_run_candidate()
    mock_sequence_run_repository.get_candidate_by_thread_id.return_value = src

    result = await sequence_run_service.get_candidate_by_thread_id(
        "thr_1", IntegrationProvider.NYLAS
    )

    assert result is src


async def test_get_candidate_by_message_id(
    sequence_run_service, mock_sequence_run_repository
):
    src = make_sequence_run_candidate()
    mock_sequence_run_repository.get_candidate_by_external_message_id.return_value = src

    result = await sequence_run_service.get_candidate_by_message_id(
        "msg_1", IntegrationProvider.NYLAS
    )

    assert result is src


async def test_has_event(
    sequence_run_service, mock_sequence_run_repository
):
    mock_sequence_run_repository.has_event.return_value = True

    result = await sequence_run_service.has_event(
        1, EventType.EMAIL_SENT, "msg_1"
    )

    assert result is True


async def test_mark_candidate_replied(
    sequence_run_service, mock_sequence_run_repository
):
    src = make_sequence_run_candidate()

    await sequence_run_service.mark_candidate_replied(
        src=src,
        external_message_id="msg_1",
        thread_id="thr_1",
        from_email="c@ex.com",
        subject="Re: Hi",
        body="Thanks",
        received_at="2025-01-01T00:00:00Z",
    )

    mock_sequence_run_repository.update_candidate_status.assert_awaited_once_with(
        src, SequenceRunCandidateStatus.REPLIED
    )
    mock_sequence_run_repository.add_event.assert_awaited_once()
    call_kwargs = mock_sequence_run_repository.add_event.call_args.kwargs
    assert call_kwargs["event_type"] == EventType.REPLY_RECEIVED
    assert call_kwargs["extra"]["from_email"] == "c@ex.com"


async def test_record_email_sent_with_scheduled_event(
    sequence_run_service, mock_sequence_run_repository
):
    src = make_sequence_run_candidate()
    scheduled = make_event(step_order=2, extra={"subject": "Follow up"})
    mock_sequence_run_repository.get_scheduled_event_by_message_id.return_value = (
        scheduled
    )

    await sequence_run_service.record_email_sent(
        src=src, external_message_id="msg_1", thread_id="thr_1"
    )

    add_call = mock_sequence_run_repository.add_event.call_args.kwargs
    assert add_call["step_order"] == 2
    assert add_call["event_type"] == EventType.EMAIL_SENT
    mock_sequence_run_repository.update_candidate_step_order.assert_awaited_once_with(
        src, 2
    )


async def test_record_email_sent_fallback_to_next_undelivered(
    sequence_run_service, mock_sequence_run_repository
):
    src = make_sequence_run_candidate()
    mock_sequence_run_repository.get_scheduled_event_by_message_id.return_value = None
    fallback = make_event(step_order=3, extra={"subject": "Step 3"})
    mock_sequence_run_repository.get_next_undelivered_scheduled_event.return_value = (
        fallback
    )

    await sequence_run_service.record_email_sent(
        src=src, external_message_id="msg_new", thread_id=None
    )

    add_call = mock_sequence_run_repository.add_event.call_args.kwargs
    assert add_call["step_order"] == 3


async def test_record_email_sent_no_scheduled_event(
    sequence_run_service, mock_sequence_run_repository
):
    src = make_sequence_run_candidate()
    mock_sequence_run_repository.get_scheduled_event_by_message_id.return_value = None
    mock_sequence_run_repository.get_next_undelivered_scheduled_event.return_value = (
        None
    )

    await sequence_run_service.record_email_sent(
        src=src, external_message_id="msg_x", thread_id=None
    )

    add_call = mock_sequence_run_repository.add_event.call_args.kwargs
    assert add_call["step_order"] is None
    assert add_call["extra"] is None


async def test_add_canceled_event(
    sequence_run_service, mock_sequence_run_repository
):
    await sequence_run_service.add_canceled_event(
        sequence_run_candidate_id=10,
        step_order=2,
        external_schedule_id="sch_1",
    )

    call_kwargs = mock_sequence_run_repository.add_event.call_args.kwargs
    assert call_kwargs["event_type"] == EventType.EMAIL_CANCELED
    assert call_kwargs["extra"]["canceled_schedule_id"] == "sch_1"


async def test_backfill_thread_id(
    sequence_run_service, mock_sequence_run_repository
):
    await sequence_run_service.backfill_thread_id(1, "msg_1", "thr_1")

    mock_sequence_run_repository.backfill_event_thread_id.assert_awaited_once_with(
        1, "msg_1", "thr_1"
    )


async def test_clear_schedule_id(
    sequence_run_service, mock_sequence_run_repository
):
    await sequence_run_service.clear_schedule_id(42)

    mock_sequence_run_repository.clear_schedule_id.assert_awaited_once_with(42)


async def test_get_pending_scheduled_events(
    sequence_run_service, mock_sequence_run_repository
):
    events = [make_event(), make_event(id=2)]
    mock_sequence_run_repository.get_pending_scheduled_events.return_value = events

    result = await sequence_run_service.get_pending_scheduled_events(10)

    assert result == events


# ── add_classification_event ─────────────────────────────────────────────

async def test_add_classification_event_interested(
    sequence_run_service, mock_sequence_run_repository
):
    src = make_sequence_run_candidate()

    await sequence_run_service.add_classification_event(
        src=src, intent="interested", confidence=0.9, reasoning="Positive reply"
    )

    mock_sequence_run_repository.add_event.assert_awaited_once()
    mock_sequence_run_repository.update_candidate_status.assert_awaited_once_with(
        src, SequenceRunCandidateStatus.INTERESTED
    )


async def test_add_classification_event_not_interested(
    sequence_run_service, mock_sequence_run_repository
):
    src = make_sequence_run_candidate()

    await sequence_run_service.add_classification_event(
        src=src,
        intent="not_interested",
        confidence=0.85,
        reasoning="Declined",
    )

    mock_sequence_run_repository.update_candidate_status.assert_awaited_once_with(
        src, SequenceRunCandidateStatus.NOT_INTERESTED
    )


async def test_add_classification_event_neutral(
    sequence_run_service, mock_sequence_run_repository
):
    src = make_sequence_run_candidate()

    await sequence_run_service.add_classification_event(
        src=src, intent="neutral", confidence=0.5, reasoning="OOO"
    )

    mock_sequence_run_repository.add_event.assert_awaited_once()
    mock_sequence_run_repository.update_candidate_status.assert_not_awaited()


# ── handle_referral ──────────────────────────────────────────────────────

async def test_handle_referral_with_referral_list(
    sequence_run_service,
    mock_sequence_run_repository,
    mock_sequence_repository,
    mock_candidate_repository,
    mock_candidate_list_repository,
    mock_email_account_repository,
    mock_email_provider,
):
    src = make_sequence_run_candidate()
    src.sequence_run.sequence_id = 1
    src.candidate_id = 1

    seq = make_sequence(referral_list_id=5)
    referral_list = MagicMock()
    referral_list.name = "Referrals"
    seq.referral_list = referral_list
    mock_sequence_repository.get_by_id.return_value = seq

    referred = make_candidate(id=99, email="ref@ex.com")
    mock_candidate_repository.get_by_email.return_value = None
    mock_candidate_repository.bulk_create_or_get.return_value = ([referred], [])

    mock_sequence_run_repository.add_event.return_value = make_event()

    # For the handoff email
    mock_email_account_repository.get_active.return_value = make_email_account()
    mock_email_provider.send_message.return_value = SendResult(message_id="msg_h")

    # Snapshot with handoff step
    src.sequence_run.snapshot = {
        "name": "Outreach",
        "steps": [
            {
                "step_order": 1,
                "step_type": "default",
                "subject": "Hi",
                "body": "Hello",
                "delay_minutes": 0,
            },
            {
                "step_order": 2,
                "step_type": "referral_handoff",
                "subject": "Referral Intro",
                "body": "Thanks for the referral",
                "delay_minutes": 0,
            },
        ],
    }

    await sequence_run_service.handle_referral(
        src=src, referral_email="ref@ex.com", referral_name="Ref"
    )

    mock_candidate_list_repository.add_candidates.assert_awaited_once_with(
        5, [99]
    )
    # Check REFERRAL_DETECTED event was recorded
    event_calls = mock_sequence_run_repository.add_event.call_args_list
    event_types = [c.kwargs["event_type"] for c in event_calls]
    assert EventType.REFERRAL_DETECTED in event_types


async def test_handle_referral_without_referral_list(
    sequence_run_service,
    mock_sequence_run_repository,
    mock_sequence_repository,
    mock_candidate_repository,
    mock_candidate_list_repository,
    mock_email_account_repository,
):
    src = make_sequence_run_candidate()
    src.sequence_run.sequence_id = 1

    seq = make_sequence(referral_list_id=None)
    mock_sequence_repository.get_by_id.return_value = seq

    referred = make_candidate(id=99)
    mock_candidate_repository.get_by_email.return_value = None
    mock_candidate_repository.bulk_create_or_get.return_value = ([referred], [])

    src.sequence_run.snapshot = None
    mock_sequence_run_repository.add_event.return_value = make_event()
    mock_email_account_repository.get_active.return_value = None

    await sequence_run_service.handle_referral(
        src=src, referral_email="ref@ex.com", referral_name=None
    )

    mock_candidate_list_repository.add_candidates.assert_not_awaited()


async def test_send_referral_handoff_no_snapshot(
    sequence_run_service,
    mock_sequence_run_repository,
    mock_sequence_repository,
    mock_candidate_repository,
    mock_email_provider,
):
    src = make_sequence_run_candidate()
    src.sequence_run.sequence_id = 1
    src.sequence_run.snapshot = None

    seq = make_sequence(referral_list_id=None)
    mock_sequence_repository.get_by_id.return_value = seq

    referred = make_candidate(id=99)
    mock_candidate_repository.get_by_email.return_value = None
    mock_candidate_repository.bulk_create_or_get.return_value = ([referred], [])
    mock_sequence_run_repository.add_event.return_value = make_event()

    await sequence_run_service.handle_referral(
        src=src, referral_email="ref@ex.com", referral_name=None
    )

    # No handoff email should be sent
    mock_email_provider.send_message.assert_not_called()


async def test_send_referral_handoff_no_handoff_step(
    sequence_run_service,
    mock_sequence_run_repository,
    mock_sequence_repository,
    mock_candidate_repository,
    mock_email_provider,
):
    src = make_sequence_run_candidate()
    src.sequence_run.sequence_id = 1
    src.sequence_run.snapshot = {
        "name": "Outreach",
        "steps": [
            {"step_order": 1, "step_type": "default", "subject": "Hi", "body": "Hello", "delay_minutes": 0},
        ],
    }

    seq = make_sequence(referral_list_id=None)
    mock_sequence_repository.get_by_id.return_value = seq

    referred = make_candidate(id=99)
    mock_candidate_repository.get_by_email.return_value = None
    mock_candidate_repository.bulk_create_or_get.return_value = ([referred], [])
    mock_sequence_run_repository.add_event.return_value = make_event()

    await sequence_run_service.handle_referral(
        src=src, referral_email="ref@ex.com", referral_name=None
    )

    mock_email_provider.send_message.assert_not_called()


async def test_send_referral_handoff_email_failure(
    sequence_run_service,
    mock_sequence_run_repository,
    mock_sequence_repository,
    mock_candidate_repository,
    mock_email_account_repository,
    mock_email_provider,
):
    src = make_sequence_run_candidate()
    src.sequence_run.sequence_id = 1
    src.sequence_run.snapshot = {
        "name": "Outreach",
        "steps": [
            {
                "step_order": 2,
                "step_type": "referral_handoff",
                "subject": "Referral",
                "body": "Thanks",
                "delay_minutes": 0,
            },
        ],
    }

    seq = make_sequence(referral_list_id=None)
    mock_sequence_repository.get_by_id.return_value = seq

    referred = make_candidate(id=99)
    mock_candidate_repository.get_by_email.return_value = None
    mock_candidate_repository.bulk_create_or_get.return_value = ([referred], [])
    mock_sequence_run_repository.add_event.return_value = make_event()

    mock_email_account_repository.get_active.return_value = make_email_account()
    mock_email_provider.send_message.side_effect = Exception("SMTP error")

    await sequence_run_service.handle_referral(
        src=src, referral_email="ref@ex.com", referral_name=None
    )

    # Should record EMAIL_FAILED event
    event_calls = mock_sequence_run_repository.add_event.call_args_list
    event_types = [c.kwargs["event_type"] for c in event_calls]
    assert EventType.EMAIL_FAILED in event_types
