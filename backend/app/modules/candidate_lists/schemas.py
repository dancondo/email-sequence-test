from pydantic import BaseModel


class CandidateListResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
