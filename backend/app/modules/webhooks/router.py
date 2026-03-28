from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response

from app.modules.webhooks.dependencies import get_webhook_service
from app.modules.webhooks.service import WebhookService

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

PROVIDER_REGISTRY = {"nylas"}


def _validate_provider(provider: str) -> None:
    if provider not in PROVIDER_REGISTRY:
        raise HTTPException(status_code=404, detail="Unknown provider")


@router.get("/{provider}")
async def webhook_challenge(provider: str, challenge: str = Query(...)) -> Response:
    _validate_provider(provider)
    return Response(content=challenge, media_type="text/plain")


@router.post("/{provider}")
async def receive_webhook(
    provider: str,
    request: Request,
    service: WebhookService = Depends(get_webhook_service),
) -> dict:
    _validate_provider(provider)

    raw_body = await request.body()
    signature = request.headers.get("x-nylas-signature", "")
    payload = await request.json()

    await service.process_webhook(raw_body, signature, payload)
    return {"status": "ok"}
