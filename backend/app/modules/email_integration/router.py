from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.modules.email_integration.dependencies import get_email_service
from app.modules.email_integration.schemas import (
    AuthUrlResponse,
    ConnectionStatusResponse,
)
from app.modules.email_integration.service import EmailIntegrationService

router = APIRouter(prefix="/api/email-integration", tags=["email-integration"])


@router.get("/auth-url", response_model=AuthUrlResponse)
async def get_auth_url(
    service: EmailIntegrationService = Depends(get_email_service),
):
    auth_url = service.get_auth_url()
    return AuthUrlResponse(auth_url=auth_url)


@router.get("/callback")
async def oauth_callback(
    code: str = Query(default=None),
    error: str = Query(default=None),
    service: EmailIntegrationService = Depends(get_email_service),
):
    frontend_url = f"{settings.FRONTEND_URL}/settings"

    if error or not code:
        return RedirectResponse(url=f"{frontend_url}?error={error or 'no_code'}")

    try:
        await service.handle_callback(code)
        return RedirectResponse(url=f"{frontend_url}?connected=true")
    except Exception as e:
        return RedirectResponse(url=f"{frontend_url}?error={str(e)}")


@router.get("/status", response_model=ConnectionStatusResponse)
async def get_connection_status(
    service: EmailIntegrationService = Depends(get_email_service),
):
    account = await service.get_status()
    if account:
        return ConnectionStatusResponse(connected=True, account=account)
    return ConnectionStatusResponse(connected=False)


@router.delete("/disconnect")
async def disconnect(
    service: EmailIntegrationService = Depends(get_email_service),
):
    success = await service.disconnect()
    if not success:
        return {"message": "No active account to disconnect"}
    return {"message": "Account disconnected successfully"}
