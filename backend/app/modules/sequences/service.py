from fastapi import HTTPException

from app.modules.sequences.models import Sequence
from app.modules.sequences.repository import SequenceRepository
from app.modules.sequences.schemas import SequenceCreate, SequenceUpdate


class SequenceService:
    def __init__(self, repository: SequenceRepository) -> None:
        self._repository = repository

    async def list_sequences(self) -> list[Sequence]:
        return await self._repository.list_all()

    async def get_sequence(self, sequence_id: int) -> Sequence:
        sequence = await self._repository.get_by_id(sequence_id)
        if not sequence:
            raise HTTPException(status_code=404, detail="Sequence not found")
        return sequence

    async def create_sequence(self, data: SequenceCreate) -> Sequence:
        steps_data = [step.model_dump() for step in data.steps]
        return await self._repository.create(name=data.name, steps_data=steps_data)

    async def update_sequence(
        self, sequence_id: int, data: SequenceUpdate
    ) -> Sequence:
        sequence = await self.get_sequence(sequence_id)
        steps_data = (
            [step.model_dump() for step in data.steps]
            if data.steps is not None
            else None
        )
        return await self._repository.update(
            sequence=sequence,
            name=data.name,
            steps_data=steps_data,
        )

    async def delete_sequence(self, sequence_id: int) -> None:
        sequence = await self.get_sequence(sequence_id)
        await self._repository.delete(sequence)
