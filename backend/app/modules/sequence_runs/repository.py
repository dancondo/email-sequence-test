from datetime import datetime

from sqlalchemy import func, literal, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.email_integration.models import IntegrationProvider
from app.modules.sequence_runs.models import (
    EventType,
    SequenceRun,
    SequenceRunCandidate,
    SequenceRunCandidateEvent,
    SequenceRunCandidateStatus,
    SequenceRunStatus,
)


class SequenceRunRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # --- Run operations ---

    async def create(self, sequence_id: int) -> SequenceRun:
        run = SequenceRun(
            sequence_id=sequence_id,
            status=SequenceRunStatus.DRAFT,
        )
        self._db.add(run)
        await self._db.commit()
        await self._db.refresh(run)
        return run

    async def set_snapshot(self, run: SequenceRun, snapshot: dict) -> SequenceRun:
        run.snapshot = snapshot
        await self._db.commit()
        await self._db.refresh(run)
        return run

    async def get_by_id(self, run_id: int) -> SequenceRun | None:
        stmt = (
            select(SequenceRun)
            .where(SequenceRun.id == run_id)
            .options(
                selectinload(SequenceRun.candidates)
                .selectinload(SequenceRunCandidate.candidate)
            )
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_sequence(self, sequence_id: int) -> list[SequenceRun]:
        stmt = (
            select(SequenceRun)
            .where(SequenceRun.sequence_id == sequence_id)
            .order_by(SequenceRun.created_at.desc())
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self,
        run: SequenceRun,
        status: SequenceRunStatus,
        started_at: datetime | None = None,
    ) -> SequenceRun:
        run.status = status
        if started_at is not None:
            run.started_at = started_at
        await self._db.commit()
        await self._db.refresh(run)
        return run

    async def delete(self, run: SequenceRun) -> None:
        await self._db.delete(run)
        await self._db.commit()

    # --- Candidate operations ---

    async def add_candidate(
        self, run_id: int, candidate_id: int
    ) -> SequenceRunCandidate:
        src = SequenceRunCandidate(
            sequence_run_id=run_id,
            candidate_id=candidate_id,
            status=SequenceRunCandidateStatus.ACTIVE,
        )
        self._db.add(src)
        await self._db.flush()

        event = SequenceRunCandidateEvent(
            sequence_run_candidate_id=src.id,
            event_type=EventType.ENROLLED,
        )
        self._db.add(event)
        await self._db.commit()
        await self._db.refresh(src)
        return src

    async def list_candidates(self, run_id: int) -> list[SequenceRunCandidate]:
        stmt = (
            select(SequenceRunCandidate)
            .where(SequenceRunCandidate.sequence_run_id == run_id)
            .options(selectinload(SequenceRunCandidate.candidate))
            .order_by(SequenceRunCandidate.created_at)
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def get_candidate(
        self, run_id: int, candidate_id: int
    ) -> SequenceRunCandidate | None:
        stmt = (
            select(SequenceRunCandidate)
            .where(
                SequenceRunCandidate.sequence_run_id == run_id,
                SequenceRunCandidate.candidate_id == candidate_id,
            )
            .options(
                selectinload(SequenceRunCandidate.candidate),
                selectinload(SequenceRunCandidate.events),
            )
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def remove_candidate(self, src: SequenceRunCandidate) -> None:
        await self._db.delete(src)
        await self._db.commit()

    async def get_candidate_by_external_message_id(
        self, message_id: str, provider: IntegrationProvider
    ) -> SequenceRunCandidate | None:
        stmt = (
            select(SequenceRunCandidate)
            .join(SequenceRunCandidateEvent)
            .where(
                SequenceRunCandidateEvent.external_message_id == message_id,
                SequenceRunCandidateEvent.external_provider == provider,
            )
            .options(selectinload(SequenceRunCandidate.candidate))
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_candidate_status(
        self,
        src: SequenceRunCandidate,
        status: SequenceRunCandidateStatus,
    ) -> SequenceRunCandidate:
        src.status = status
        await self._db.commit()
        await self._db.refresh(src)
        return src

    # --- Event operations ---

    async def get_candidate_by_thread_id(
        self, thread_id: str, provider: IntegrationProvider
    ) -> SequenceRunCandidate | None:
        stmt = (
            select(SequenceRunCandidate)
            .join(SequenceRunCandidateEvent)
            .where(
                SequenceRunCandidateEvent.external_thread_id == thread_id,
                SequenceRunCandidateEvent.external_provider == provider,
            )
            .options(
                selectinload(SequenceRunCandidate.candidate),
                selectinload(SequenceRunCandidate.sequence_run),
            )
        )
        result = await self._db.execute(stmt)
        return result.scalars().first()

    async def get_pending_scheduled_events(
        self, sequence_run_candidate_id: int
    ) -> list[SequenceRunCandidateEvent]:
        # Subquery: step_orders that already have an EMAIL_SENT event
        sent_steps = (
            select(SequenceRunCandidateEvent.step_order)
            .where(
                SequenceRunCandidateEvent.sequence_run_candidate_id
                == sequence_run_candidate_id,
                SequenceRunCandidateEvent.event_type == EventType.EMAIL_SENT,
                SequenceRunCandidateEvent.step_order.isnot(None),
            )
            .scalar_subquery()
        )

        stmt = (
            select(SequenceRunCandidateEvent)
            .where(
                SequenceRunCandidateEvent.sequence_run_candidate_id
                == sequence_run_candidate_id,
                SequenceRunCandidateEvent.event_type == EventType.EMAIL_SCHEDULED,
                SequenceRunCandidateEvent.external_schedule_id.isnot(None),
                SequenceRunCandidateEvent.step_order.notin_(sent_steps),
            )
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def has_event(
        self,
        sequence_run_candidate_id: int,
        event_type: EventType,
        external_message_id: str,
    ) -> bool:
        stmt = (
            select(SequenceRunCandidateEvent.id)
            .where(
                SequenceRunCandidateEvent.sequence_run_candidate_id
                == sequence_run_candidate_id,
                SequenceRunCandidateEvent.event_type == event_type,
                SequenceRunCandidateEvent.external_message_id == external_message_id,
            )
            .limit(1)
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def add_event(
        self,
        sequence_run_candidate_id: int,
        event_type: EventType,
        step_order: int | None = None,
        external_message_id: str | None = None,
        external_schedule_id: str | None = None,
        external_thread_id: str | None = None,
        external_provider: IntegrationProvider | None = None,
        extra: dict | None = None,
    ) -> SequenceRunCandidateEvent:
        event = SequenceRunCandidateEvent(
            sequence_run_candidate_id=sequence_run_candidate_id,
            event_type=event_type,
            step_order=step_order,
            external_message_id=external_message_id,
            external_schedule_id=external_schedule_id,
            external_thread_id=external_thread_id,
            external_provider=external_provider,
            extra=extra,
        )
        self._db.add(event)
        await self._db.commit()
        await self._db.refresh(event)
        return event

    async def get_scheduled_event_by_message_id(
        self, sequence_run_candidate_id: int, external_message_id: str
    ) -> SequenceRunCandidateEvent | None:
        stmt = (
            select(SequenceRunCandidateEvent)
            .where(
                SequenceRunCandidateEvent.sequence_run_candidate_id
                == sequence_run_candidate_id,
                SequenceRunCandidateEvent.event_type == EventType.EMAIL_SCHEDULED,
                SequenceRunCandidateEvent.external_message_id == external_message_id,
            )
            .limit(1)
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def clear_schedule_id(self, event_id: int) -> None:
        stmt = (
            select(SequenceRunCandidateEvent)
            .where(SequenceRunCandidateEvent.id == event_id)
        )
        result = await self._db.execute(stmt)
        event = result.scalar_one_or_none()
        if event:
            event.external_schedule_id = None
            await self._db.commit()

    async def backfill_event_thread_id(
        self,
        sequence_run_candidate_id: int,
        external_message_id: str,
        thread_id: str,
    ) -> None:
        stmt = (
            select(SequenceRunCandidateEvent)
            .where(
                SequenceRunCandidateEvent.sequence_run_candidate_id
                == sequence_run_candidate_id,
                SequenceRunCandidateEvent.external_message_id == external_message_id,
                SequenceRunCandidateEvent.external_thread_id.is_(None),
            )
        )
        result = await self._db.execute(stmt)
        events = list(result.scalars().all())
        for event in events:
            event.external_thread_id = thread_id
        if events:
            await self._db.commit()

    async def get_next_undelivered_scheduled_event(
        self, sequence_run_candidate_id: int
    ) -> SequenceRunCandidateEvent | None:
        sent_steps = (
            select(SequenceRunCandidateEvent.step_order)
            .where(
                SequenceRunCandidateEvent.sequence_run_candidate_id
                == sequence_run_candidate_id,
                SequenceRunCandidateEvent.event_type == EventType.EMAIL_SENT,
                SequenceRunCandidateEvent.step_order.isnot(None),
            )
            .scalar_subquery()
        )

        stmt = (
            select(SequenceRunCandidateEvent)
            .where(
                SequenceRunCandidateEvent.sequence_run_candidate_id
                == sequence_run_candidate_id,
                SequenceRunCandidateEvent.event_type == EventType.EMAIL_SCHEDULED,
                SequenceRunCandidateEvent.step_order.isnot(None),
                SequenceRunCandidateEvent.step_order.notin_(sent_steps),
            )
            .order_by(SequenceRunCandidateEvent.step_order.asc())
            .limit(1)
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_candidate_step_order(
        self, src: SequenceRunCandidate, step_order: int
    ) -> SequenceRunCandidate:
        src.current_step_order = step_order
        await self._db.commit()
        await self._db.refresh(src)
        return src

    async def get_last_reply_received_event(
        self, sequence_run_candidate_id: int
    ) -> SequenceRunCandidateEvent | None:
        stmt = (
            select(SequenceRunCandidateEvent)
            .where(
                SequenceRunCandidateEvent.sequence_run_candidate_id
                == sequence_run_candidate_id,
                SequenceRunCandidateEvent.event_type == EventType.REPLY_RECEIVED.value,
            )
            .order_by(SequenceRunCandidateEvent.occurred_at.desc())
            .limit(1)
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_events(
        self, sequence_run_candidate_id: int
    ) -> list[SequenceRunCandidateEvent]:
        stmt = (
            select(SequenceRunCandidateEvent)
            .where(
                SequenceRunCandidateEvent.sequence_run_candidate_id
                == sequence_run_candidate_id
            )
            .order_by(SequenceRunCandidateEvent.occurred_at)
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    def _build_metrics(self, total_sent: int, total_replies: int, total_interested: int) -> dict:
        return {
            "total_sent": total_sent,
            "total_replies": total_replies,
            "reply_rate": total_replies / total_sent if total_sent > 0 else 0.0,
            "total_interested": total_interested,
            "interest_rate": total_interested / total_sent if total_sent > 0 else 0.0,
        }

    async def _count_events_for_run(
        self, run_id: int, event_type: EventType
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(SequenceRunCandidateEvent)
            .join(SequenceRunCandidate)
            .where(
                SequenceRunCandidate.sequence_run_id == run_id,
                SequenceRunCandidateEvent.event_type == literal(event_type.name).cast(
                    SequenceRunCandidateEvent.event_type.type
                ),
            )
        )
        return (await self._db.execute(stmt)).scalar() or 0

    async def _count_events_for_sequence(
        self, sequence_id: int, event_type: EventType
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(SequenceRunCandidateEvent)
            .join(SequenceRunCandidate)
            .join(SequenceRun)
            .where(
                SequenceRun.sequence_id == sequence_id,
                SequenceRunCandidateEvent.event_type == literal(event_type.name).cast(
                    SequenceRunCandidateEvent.event_type.type
                ),
            )
        )
        return (await self._db.execute(stmt)).scalar() or 0

    async def get_run_metrics(self, run_id: int) -> dict:
        total_sent = await self._count_events_for_run(run_id, EventType.EMAIL_SENT)
        total_replies = await self._count_events_for_run(run_id, EventType.REPLY_RECEIVED)

        interested_stmt = (
            select(func.count())
            .select_from(SequenceRunCandidate)
            .where(
                SequenceRunCandidate.sequence_run_id == run_id,
                SequenceRunCandidate.status == literal(
                    SequenceRunCandidateStatus.INTERESTED.name
                ).cast(SequenceRunCandidate.status.type),
            )
        )
        total_interested = (await self._db.execute(interested_stmt)).scalar() or 0

        return self._build_metrics(total_sent, total_replies, total_interested)

    async def get_all_sequence_run_metrics(self, sequence_id: int) -> dict:
        total_sent = await self._count_events_for_sequence(sequence_id, EventType.EMAIL_SENT)
        total_replies = await self._count_events_for_sequence(sequence_id, EventType.REPLY_RECEIVED)

        interested_stmt = (
            select(func.count())
            .select_from(SequenceRunCandidate)
            .join(SequenceRun)
            .where(
                SequenceRun.sequence_id == sequence_id,
                SequenceRunCandidate.status == literal(
                    SequenceRunCandidateStatus.INTERESTED.name
                ).cast(SequenceRunCandidate.status.type),
            )
        )
        total_interested = (await self._db.execute(interested_stmt)).scalar() or 0

        return self._build_metrics(total_sent, total_replies, total_interested)
