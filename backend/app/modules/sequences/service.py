from fastapi import HTTPException

from app.modules.candidate_lists.service import CandidateListService
from app.modules.sequences.models import Sequence
from app.modules.sequences.repository import SequenceRepository
from app.modules.sequences.schemas import SequenceCreate, SequenceUpdate


class SequenceService:
    def __init__(
        self,
        repository: SequenceRepository,
        candidate_list_service: CandidateListService,
    ) -> None:
        self._repository = repository
        self._candidate_list_service = candidate_list_service

    async def list_sequences(self) -> list[Sequence]:
        return await self._repository.list_all()

    async def get_sequence(self, sequence_id: int) -> Sequence:
        sequence = await self._repository.get_by_id(sequence_id)
        if not sequence:
            raise HTTPException(status_code=404, detail="Sequence not found")
        return sequence

    async def _resolve_referral_list_id(
        self,
        referral_list_id: int | None,
        referral_list_name: str | None,
    ) -> int | None:
        if referral_list_id is not None:
            return referral_list_id
        if referral_list_name:
            candidate_list = await self._candidate_list_service.get_or_create_list(
                list_name=referral_list_name,
            )
            return candidate_list.id
        return None

    async def create_sequence(self, data: SequenceCreate) -> Sequence:
        steps_data = [step.model_dump() for step in data.steps]
        referral_list_id = await self._resolve_referral_list_id(
            data.referral_list_id, data.referral_list_name,
        )
        return await self._repository.create(
            name=data.name,
            steps_data=steps_data,
            referral_list_id=referral_list_id,
        )

    async def update_sequence(
        self, sequence_id: int, data: SequenceUpdate
    ) -> Sequence:
        sequence = await self.get_sequence(sequence_id)
        steps_data = (
            [step.model_dump() for step in data.steps]
            if data.steps is not None
            else None
        )
        referral_list_id = await self._resolve_referral_list_id(
            data.referral_list_id, data.referral_list_name,
        )
        return await self._repository.update(
            sequence=sequence,
            name=data.name,
            steps_data=steps_data,
            referral_list_id=referral_list_id,
        )

    async def delete_sequence(self, sequence_id: int) -> None:
        sequence = await self.get_sequence(sequence_id)
        await self._repository.delete(sequence)
