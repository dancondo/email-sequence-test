from pydantic import BaseModel


class NylasWebhookObject(BaseModel):
    id: str = ""
    grant_id: str = ""
    message_id: str = ""

    model_config = {"extra": "ignore"}


class NylasWebhookData(BaseModel):
    application_id: str = ""
    grant_id: str = ""
    object: NylasWebhookObject

    model_config = {"extra": "ignore"}


class NylasWebhookPayload(BaseModel):
    type: str
    data: NylasWebhookData

    model_config = {"extra": "ignore"}
