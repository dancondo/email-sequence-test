from datetime import datetime

from pydantic import BaseModel


class SequenceStepCreate(BaseModel):
    subject: str
    body: str
    delay_minutes: int = 0
    step_type: str = "default"


class SequenceStepResponse(BaseModel):
    id: int
    sequence_id: int
    step_order: int
    subject: str
    body: str
    delay_minutes: int
    step_type: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SequenceCreate(BaseModel):
    name: str
    steps: list[SequenceStepCreate] = []
    referral_list_id: int | None = None
    referral_list_name: str | None = None


class SequenceUpdate(BaseModel):
    name: str | None = None
    steps: list[SequenceStepCreate] | None = None
    referral_list_id: int | None = None
    referral_list_name: str | None = None


class SequenceResponse(BaseModel):
    id: int
    name: str
    is_active: bool
    referral_list_id: int | None = None
    referral_list_name: str | None = None
    steps: list[SequenceStepResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SequenceListResponse(BaseModel):
    id: int
    name: str
    is_active: bool
    referral_list_id: int | None = None
    referral_list_name: str | None = None
    step_count: int
    run_count: int
    created_at: datetime
    updated_at: datetime
