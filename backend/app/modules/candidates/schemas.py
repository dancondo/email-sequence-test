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
