import time
from datetime import datetime

from fastapi import HTTPException

from app.modules.candidates.service import CandidateService
from app.modules.classification.schemas import ReplyIntent
from app.modules.email_integration.models import IntegrationProvider
from app.modules.email_integration.service import EmailIntegrationService
from app.modules.sequence_runs.models import (
    EventType,
    SequenceRun,
    SequenceRunCandidate,
    SequenceRunCandidateEvent,
    SequenceRunCandidateStatus,
    SequenceRunStatus,
)
from app.modules.sequence_runs.repository import SequenceRunRepository
from app.modules.sequence_runs.schemas import (
    AddCandidatesResponse,
    SendReplyResponse,
    SequenceStartResponse,
)
from app.modules.sequences.service import SequenceService

_INTENT_TO_STATUS = {
    ReplyIntent.INTERESTED: SequenceRunCandidateStatus.INTERESTED,
    ReplyIntent.NOT_INTERESTED: SequenceRunCandidateStatus.NOT_INTERESTED,
}


class SequenceRunService:
    def __init__(
        self,
        run_repository: SequenceRunRepository,
        sequence_service: SequenceService,
        candidate_service: CandidateService,
        email_service: EmailIntegrationService,
    ) -> None:
        self._run_repo = run_repository
        self._sequence_service = sequence_service
        self._candidate_service = candidate_service
        self._email_service = email_service

    async def create_run(self, sequence_id: int) -> SequenceRun:
        await self._sequence_service.get_sequence(sequence_id)
        return await self._run_repo.create(sequence_id=sequence_id)

    async def list_runs(self, sequence_id: int) -> list[SequenceRun]:
        await self._sequence_service.get_sequence(sequence_id)
        return await self._run_repo.list_by_sequence(sequence_id)

    async def get_run(self, sequence_id: int, run_id: int) -> SequenceRun:
        run = await self._run_repo.get_by_id(run_id)
        if not run or run.sequence_id != sequence_id:
            raise HTTPException(status_code=404, detail="Sequence run not found")
        return run

    async def delete_run(self, sequence_id: int, run_id: int) -> None:
        run = await self.get_run(sequence_id, run_id)

        if run.status != SequenceRunStatus.DRAFT:
            raise HTTPException(
                status_code=409,
                detail="Only draft runs can be deleted",
            )

        await self._run_repo.delete(run)

    async def add_candidates(
        self, sequence_id: int, run_id: int, candidate_ids: list[int]
    ) -> AddCandidatesResponse:
        run = await self.get_run(sequence_id, run_id)

        if run.status != SequenceRunStatus.DRAFT:
            raise HTTPException(
                status_code=409,
                detail="Cannot add candidates to a run that is not in DRAFT status",
            )

        existing_candidate_ids = {src.candidate_id for src in run.candidates}
        added = 0
        already_enrolled = 0
        not_found = 0

        for cid in candidate_ids:
            if cid in existing_candidate_ids:
                already_enrolled += 1
                continue

            try:
                await self._candidate_service.get_candidate(cid)
            except HTTPException:
                not_found += 1
                continue

            await self._run_repo.add_candidate(run_id=run_id, candidate_id=cid)
            added += 1

        return AddCandidatesResponse(
            added=added,
            already_enrolled=already_enrolled,
            not_found=not_found,
        )

    async def remove_candidate(
        self, sequence_id: int, run_id: int, candidate_id: int
    ) -> None:
        run = await self.get_run(sequence_id, run_id)

        if run.status != SequenceRunStatus.DRAFT:
            raise HTTPException(
                status_code=409,
                detail="Cannot remove candidates from a run that is not in DRAFT status",
            )

        src = await self._run_repo.get_candidate(run_id, candidate_id)
        if not src:
            raise HTTPException(
                status_code=404, detail="Candidate not found in this run"
            )

        await self._run_repo.remove_candidate(src)

    async def get_candidates(self, sequence_id: int, run_id: int):
        await self.get_run(sequence_id, run_id)
        return await self._run_repo.list_candidates(run_id)

    async def get_candidate_timeline(
        self, sequence_id: int, run_id: int, candidate_id: int
    ):
        await self.get_run(sequence_id, run_id)

        src = await self._run_repo.get_candidate(run_id, candidate_id)
        if not src:
            raise HTTPException(
                status_code=404, detail="Candidate not found in this run"
            )

        events = await self._run_repo.get_events(src.id)
        return src, events

    async def start_run(
        self, sequence_id: int, run_id: int
    ) -> SequenceStartResponse:
        run = await self.get_run(sequence_id, run_id)

        if run.status != SequenceRunStatus.DRAFT:
            raise HTTPException(
                status_code=409,
                detail="Run is not in DRAFT status",
            )

        candidates = await self._run_repo.list_candidates(run_id)
        if not candidates:
            raise HTTPException(
                status_code=400,
                detail="Run must have at least one candidate to start",
            )

        # Eagerly resolve emails before any commits invalidate lazy state
        candidate_emails = {src.id: src.candidate.email for src in candidates}

        account = await self._email_service.get_status()
        if not account:
            raise HTTPException(
                status_code=400,
                detail="No active email account connected",
            )

        # Snapshot the sequence template at start time
        sequence = await self._sequence_service.get_sequence(run.sequence_id)
        if not sequence.steps:
            raise HTTPException(
                status_code=400,
                detail="Sequence has no steps",
            )

        snapshot = {
            "name": sequence.name,
            "steps": [
                {
                    "step_order": step.step_order,
                    "subject": step.subject,
                    "body": step.body,
                    "delay_minutes": step.delay_minutes,
                }
                for step in sequence.steps
            ],
        }
        await self._run_repo.set_snapshot(run, snapshot)

        steps = snapshot["steps"]

        now_ts = int(time.time())
        enrollments_started = 0

        for src in candidates:
            cumulative_delay = 0

            for step in steps:
                cumulative_delay += step["delay_minutes"] * 60
                send_at = now_ts + cumulative_delay if cumulative_delay > 0 else None

                try:
                    result = self._email_service.send_message(
                        grant_id=account.grant_id,
                        to_email=candidate_emails[src.id],
                        subject=step["subject"],
                        body=step["body"],
                        send_at=send_at,
                    )

                    await self._run_repo.add_event(
                        sequence_run_candidate_id=src.id,
                        event_type=EventType.EMAIL_SCHEDULED,
                        step_order=step["step_order"],
                        external_message_id=result.message_id,
                        external_schedule_id=result.schedule_id,
                        external_thread_id=result.thread_id,
                        external_provider=IntegrationProvider.NYLAS,
                    )
                except Exception as e:
                    await self._run_repo.add_event(
                        sequence_run_candidate_id=src.id,
                        event_type=EventType.EMAIL_FAILED,
                        step_order=step["step_order"],
                        extra={"error": str(e)},
                    )

            await self._run_repo.update_candidate_status(
                src, SequenceRunCandidateStatus.ACTIVE
            )
            enrollments_started += 1

        await self._run_repo.update_status(
            run,
            SequenceRunStatus.ACTIVE,
            started_at=datetime.utcnow(),
        )

        return SequenceStartResponse(
            message=f"Sequence run started with {enrollments_started} candidates",
            enrollments_started=enrollments_started,
        )

    async def send_reply(
        self, sequence_id: int, run_id: int, candidate_id: int, body: str
    ) -> SequenceRunCandidateEvent:
        await self.get_run(sequence_id, run_id)

        src = await self._run_repo.get_candidate(run_id, candidate_id)
        if not src:
            raise HTTPException(
                status_code=404, detail="Candidate not found in this run"
            )

        reply_statuses = {
            SequenceRunCandidateStatus.REPLIED,
            SequenceRunCandidateStatus.INTERESTED,
            SequenceRunCandidateStatus.NOT_INTERESTED,
        }
        if src.status not in reply_statuses:
            raise HTTPException(
                status_code=409,
                detail="Can only reply to candidates who have replied first",
            )

        account = await self._email_service.get_status()
        if not account:
            raise HTTPException(
                status_code=400,
                detail="No active email account connected",
            )

        reply_event = await self._run_repo.get_last_reply_received_event(src.id)
        if not reply_event:
            raise HTTPException(
                status_code=409,
                detail="No reply received event found for this candidate",
            )

        original_subject = (reply_event.extra or {}).get("subject", "")
        subject = (
            original_subject
            if original_subject.lower().startswith("re:")
            else f"Re: {original_subject}"
        )
        to_email = src.candidate.email

        result = self._email_service.send_message(
            grant_id=account.grant_id,
            to_email=to_email,
            subject=subject,
            body=body,
            reply_to_message_id=reply_event.external_message_id,
        )

        event = await self._run_repo.add_event(
            sequence_run_candidate_id=src.id,
            event_type=EventType.REPLY_SENT,
            external_message_id=result.message_id,
            external_thread_id=result.thread_id,
            external_provider=IntegrationProvider.NYLAS,
            extra={
                "subject": subject,
                "body": body,
                "to_email": to_email,
            },
        )

        return event

    # --- Metrics ---

    async def get_run_metrics(self, sequence_id: int, run_id: int) -> dict:
        await self.get_run(sequence_id, run_id)
        return await self._run_repo.get_run_metrics(run_id)

    async def get_all_sequence_run_metrics(self, sequence_id: int) -> dict:
        await self._sequence_service.get_sequence(sequence_id)
        return await self._run_repo.get_all_sequence_run_metrics(sequence_id)

    # --- Webhook-facing methods ---

    async def get_candidate_by_thread_id(
        self, thread_id: str, provider: IntegrationProvider
    ) -> SequenceRunCandidate | None:
        return await self._run_repo.get_candidate_by_thread_id(thread_id, provider)

    async def has_event(
        self,
        sequence_run_candidate_id: int,
        event_type: EventType,
        external_message_id: str,
    ) -> bool:
        return await self._run_repo.has_event(
            sequence_run_candidate_id, event_type, external_message_id
        )

    async def mark_candidate_replied(
        self,
        src: SequenceRunCandidate,
        external_message_id: str,
        thread_id: str,
        from_email: str,
        subject: str,
        body: str,
        received_at: str,
    ) -> None:
        await self._run_repo.update_candidate_status(
            src, SequenceRunCandidateStatus.REPLIED
        )
        await self._run_repo.add_event(
            sequence_run_candidate_id=src.id,
            event_type=EventType.REPLY_RECEIVED,
            external_message_id=external_message_id,
            external_thread_id=thread_id,
            external_provider=IntegrationProvider.NYLAS,
            extra={
                "from_email": from_email,
                "subject": subject,
                "body": body,
                "received_at": received_at,
            },
        )

    async def record_email_sent(
        self,
        src: SequenceRunCandidate,
        external_message_id: str,
        thread_id: str | None,
    ) -> None:
        scheduled_event = await self._run_repo.get_scheduled_event_by_message_id(
            src.id, external_message_id
        )
        step_order = scheduled_event.step_order if scheduled_event else None

        await self._run_repo.add_event(
            sequence_run_candidate_id=src.id,
            event_type=EventType.EMAIL_SENT,
            step_order=step_order,
            external_message_id=external_message_id,
            external_thread_id=thread_id,
            external_provider=IntegrationProvider.NYLAS,
        )

        if step_order is not None:
            await self._run_repo.update_candidate_step_order(src, step_order)

    async def get_pending_scheduled_events(
        self, sequence_run_candidate_id: int
    ) -> list[SequenceRunCandidateEvent]:
        return await self._run_repo.get_pending_scheduled_events(
            sequence_run_candidate_id
        )

    async def add_classification_event(
        self,
        src: SequenceRunCandidate,
        intent: str,
        confidence: float,
        reasoning: str,
    ) -> None:
        await self._run_repo.add_event(
            sequence_run_candidate_id=src.id,
            event_type=EventType.REPLY_CLASSIFIED,
            extra={
                "intent": intent,
                "confidence": confidence,
                "reasoning": reasoning,
            },
        )

        new_status = _INTENT_TO_STATUS.get(ReplyIntent(intent))
        if new_status:
            await self._run_repo.update_candidate_status(src, new_status)
