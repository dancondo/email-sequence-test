from fastapi import APIRouter, Depends

from app.modules.sequence_runs.dependencies import get_sequence_run_service
from app.modules.sequence_runs.schemas import (
    AddCandidatesRequest,
    AddCandidatesResponse,
    CandidateTimelineResponse,
    SequenceRunCandidateEventResponse,
    SequenceRunCandidateResponse,
    SequenceRunDetailResponse,
    SequenceRunListResponse,
    SequenceRunResponse,
    SequenceStartResponse,
)
from app.modules.sequence_runs.service import SequenceRunService

router = APIRouter(prefix="/api/sequences/{sequence_id}/runs", tags=["sequence-runs"])


@router.post("", response_model=SequenceRunResponse, status_code=201)
async def create_run(
    sequence_id: int,
    service: SequenceRunService = Depends(get_sequence_run_service),
):
    run = await service.create_run(sequence_id)
    return SequenceRunResponse(
        id=run.id,
        sequence_id=run.sequence_id,
        status=run.status.value,
        snapshot=run.snapshot,
        started_at=run.started_at,
        candidate_count=len(run.candidates),
        created_at=run.created_at,
        updated_at=run.updated_at,
    )


@router.get("", response_model=list[SequenceRunListResponse])
async def list_runs(
    sequence_id: int,
    service: SequenceRunService = Depends(get_sequence_run_service),
):
    runs = await service.list_runs(sequence_id)
    return [
        SequenceRunListResponse(
            id=run.id,
            sequence_id=run.sequence_id,
            status=run.status.value,
            started_at=run.started_at,
            candidate_count=len(run.candidates),
            created_at=run.created_at,
            updated_at=run.updated_at,
        )
        for run in runs
    ]


@router.get("/{run_id}", response_model=SequenceRunDetailResponse)
async def get_run(
    sequence_id: int,
    run_id: int,
    service: SequenceRunService = Depends(get_sequence_run_service),
):
    return await service.get_run(sequence_id, run_id)


@router.post("/{run_id}/start", response_model=SequenceStartResponse)
async def start_run(
    sequence_id: int,
    run_id: int,
    service: SequenceRunService = Depends(get_sequence_run_service),
):
    return await service.start_run(sequence_id, run_id)


@router.post(
    "/{run_id}/candidates",
    response_model=AddCandidatesResponse,
    status_code=201,
)
async def add_candidates(
    sequence_id: int,
    run_id: int,
    data: AddCandidatesRequest,
    service: SequenceRunService = Depends(get_sequence_run_service),
):
    return await service.add_candidates(sequence_id, run_id, data.candidate_ids)


@router.get(
    "/{run_id}/candidates",
    response_model=list[SequenceRunCandidateResponse],
)
async def list_candidates(
    sequence_id: int,
    run_id: int,
    service: SequenceRunService = Depends(get_sequence_run_service),
):
    return await service.get_candidates(sequence_id, run_id)


@router.delete("/{run_id}/candidates/{candidate_id}", status_code=204)
async def remove_candidate(
    sequence_id: int,
    run_id: int,
    candidate_id: int,
    service: SequenceRunService = Depends(get_sequence_run_service),
):
    await service.remove_candidate(sequence_id, run_id, candidate_id)


@router.get(
    "/{run_id}/candidates/{candidate_id}/timeline",
    response_model=CandidateTimelineResponse,
)
async def get_candidate_timeline(
    sequence_id: int,
    run_id: int,
    candidate_id: int,
    service: SequenceRunService = Depends(get_sequence_run_service),
):
    src, events = await service.get_candidate_timeline(
        sequence_id, run_id, candidate_id
    )
    return CandidateTimelineResponse(
        candidate=src,
        events=[
            SequenceRunCandidateEventResponse(
                id=e.id,
                sequence_run_candidate_id=e.sequence_run_candidate_id,
                event_type=e.event_type.value,
                step_order=e.step_order,
                external_message_id=e.external_message_id,
                external_schedule_id=e.external_schedule_id,
                external_provider=(
                    e.external_provider.value if e.external_provider else None
                ),
                metadata=e.extra,
                occurred_at=e.occurred_at,
                created_at=e.created_at,
            )
            for e in events
        ],
    )
