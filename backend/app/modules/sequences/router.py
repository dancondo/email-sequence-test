from fastapi import APIRouter, Depends

from app.modules.sequences.dependencies import get_sequence_service
from app.modules.sequences.schemas import (
    SequenceCreate,
    SequenceListResponse,
    SequenceResponse,
    SequenceUpdate,
)
from app.modules.sequences.service import SequenceService

router = APIRouter(prefix="/api/sequences", tags=["sequences"])


@router.get("", response_model=list[SequenceListResponse])
async def list_sequences(
    service: SequenceService = Depends(get_sequence_service),
):
    sequences = await service.list_sequences()
    return [
        SequenceListResponse(
            id=seq.id,
            name=seq.name,
            is_active=seq.is_active,
            step_count=len(seq.steps),
            run_count=len(seq.runs),
            created_at=seq.created_at,
            updated_at=seq.updated_at,
        )
        for seq in sequences
    ]


@router.post("", response_model=SequenceResponse, status_code=201)
async def create_sequence(
    data: SequenceCreate,
    service: SequenceService = Depends(get_sequence_service),
):
    return await service.create_sequence(data)


@router.get("/{sequence_id}", response_model=SequenceResponse)
async def get_sequence(
    sequence_id: int,
    service: SequenceService = Depends(get_sequence_service),
):
    return await service.get_sequence(sequence_id)


@router.put("/{sequence_id}", response_model=SequenceResponse)
async def update_sequence(
    sequence_id: int,
    data: SequenceUpdate,
    service: SequenceService = Depends(get_sequence_service),
):
    return await service.update_sequence(sequence_id, data)


@router.delete("/{sequence_id}")
async def delete_sequence(
    sequence_id: int,
    service: SequenceService = Depends(get_sequence_service),
):
    await service.delete_sequence(sequence_id)
    return {"message": "Sequence deleted"}
