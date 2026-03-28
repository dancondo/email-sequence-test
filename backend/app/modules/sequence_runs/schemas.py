from datetime import datetime

from pydantic import BaseModel

from app.modules.candidates.schemas import CandidateResponse


class SequenceRunCandidateEventResponse(BaseModel):
    id: int
    sequence_run_candidate_id: int
    event_type: str
    step_order: int | None
    external_message_id: str | None
    external_schedule_id: str | None
    external_provider: str | None
    metadata: dict | None
    occurred_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class SequenceRunCandidateResponse(BaseModel):
    id: int
    candidate_id: int
    sequence_run_id: int
    current_step_order: int
    status: str
    candidate: CandidateResponse
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SequenceRunResponse(BaseModel):
    id: int
    sequence_id: int
    status: str
    snapshot: dict | None
    started_at: datetime | None
    candidate_count: int
    created_at: datetime
    updated_at: datetime


class SequenceRunListResponse(BaseModel):
    id: int
    sequence_id: int
    status: str
    started_at: datetime | None
    candidate_count: int
    created_at: datetime
    updated_at: datetime


class SequenceRunDetailResponse(BaseModel):
    id: int
    sequence_id: int
    status: str
    snapshot: dict | None
    started_at: datetime | None
    candidates: list[SequenceRunCandidateResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CandidateTimelineResponse(BaseModel):
    candidate: SequenceRunCandidateResponse
    events: list[SequenceRunCandidateEventResponse]


class AddCandidatesRequest(BaseModel):
    candidate_ids: list[int]


class AddCandidatesResponse(BaseModel):
    added: int
    already_enrolled: int
    not_found: int


class SequenceStartResponse(BaseModel):
    message: str
    enrollments_started: int
