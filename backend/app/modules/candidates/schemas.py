from datetime import datetime

from pydantic import BaseModel


class CandidateResponse(BaseModel):
    id: int
    email: str
    name: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CsvUploadResponse(BaseModel):
    total_rows: int
    candidates_created: int
    candidates_existing: int
    candidates: list[CandidateResponse]
    errors: list[str]


class CandidateWithRunCount(BaseModel):
    id: int
    email: str
    name: str | None
    run_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CandidateRunSummary(BaseModel):
    sequence_run_candidate_id: int
    sequence_run_id: int
    sequence_id: int
    sequence_name: str
    run_status: str
    status: str
    current_step_order: int
    created_at: datetime


class CandidateDetailResponse(BaseModel):
    id: int
    email: str
    name: str | None
    referred_by_candidate_id: int | None = None
    referred_by: CandidateResponse | None = None
    created_at: datetime
    updated_at: datetime
    runs: list[CandidateRunSummary]

    model_config = {"from_attributes": True}
