from pydantic import BaseModel


class NylasWebhookObjectData(BaseModel):
    id: str
    grant_id: str

    model_config = {"extra": "ignore"}


class NylasWebhookDelta(BaseModel):
    type: str
    object_data: NylasWebhookObjectData

    model_config = {"extra": "ignore"}


class NylasWebhookPayload(BaseModel):
    deltas: list[NylasWebhookDelta]

    model_config = {"extra": "ignore"}
