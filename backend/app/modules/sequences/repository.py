from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.sequences.models import Sequence, SequenceStep


class SequenceRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_all(self) -> list[Sequence]:
        stmt = (
            select(Sequence)
            .options(selectinload(Sequence.runs))
            .order_by(Sequence.created_at.desc())
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, sequence_id: int) -> Sequence | None:
        stmt = select(Sequence).where(Sequence.id == sequence_id)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self, name: str, steps_data: list[dict], referral_list_id: int | None = None
    ) -> Sequence:
        sequence = Sequence(name=name, referral_list_id=referral_list_id)
        self._db.add(sequence)
        await self._db.flush()

        for i, step_data in enumerate(steps_data):
            step = SequenceStep(
                sequence_id=sequence.id,
                step_order=i,
                subject=step_data["subject"],
                body=step_data["body"],
                delay_minutes=step_data.get("delay_minutes", 0),
            )
            self._db.add(step)

        await self._db.commit()
        await self._db.refresh(sequence)
        return sequence

    async def update(
        self,
        sequence: Sequence,
        name: str | None = None,
        steps_data: list[dict] | None = None,
        referral_list_id: int | None = None,
    ) -> Sequence:
        if name is not None:
            sequence.name = name
        if referral_list_id is not None:
            sequence.referral_list_id = referral_list_id

        if steps_data is not None:
            await self._db.execute(
                delete(SequenceStep).where(
                    SequenceStep.sequence_id == sequence.id
                )
            )
            for i, step_data in enumerate(steps_data):
                step = SequenceStep(
                    sequence_id=sequence.id,
                    step_order=i,
                    subject=step_data["subject"],
                    body=step_data["body"],
                    delay_minutes=step_data.get("delay_minutes", 0),
                )
                self._db.add(step)

        await self._db.commit()
        await self._db.refresh(sequence)
        return sequence

    async def delete(self, sequence: Sequence) -> None:
        await self._db.delete(sequence)
        await self._db.commit()
