from datetime import datetime

from pydantic import BaseModel


class EmailAccountResponse(BaseModel):
    id: int
    grant_id: str
    email: str
    provider: str
    integration_provider: str
    connected_at: datetime
    is_active: bool

    model_config = {"from_attributes": True}


class ConnectionStatusResponse(BaseModel):
    connected: bool
    account: EmailAccountResponse | None = None


class AuthUrlResponse(BaseModel):
    auth_url: str
