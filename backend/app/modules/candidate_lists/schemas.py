from pydantic import BaseModel


class CandidateListResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class AssignCandidatesRequest(BaseModel):
    list_id: int | None = None
    list_name: str | None = None
    candidate_ids: list[int]
