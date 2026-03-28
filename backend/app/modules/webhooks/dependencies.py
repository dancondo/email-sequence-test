from fastapi import Depends
from nylas import Client as NylasClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.email_integration.dependencies import get_email_service
from app.modules.email_integration.service import EmailIntegrationService
from app.modules.nylas.dependencies import get_nylas_client
from app.modules.sequence_runs.repository import SequenceRunRepository
from app.modules.webhooks.providers.base import WebhookProvider
from app.modules.webhooks.providers.nylas import NylasWebhookProvider
from app.modules.webhooks.service import WebhookService


def get_webhook_provider(
    client: NylasClient = Depends(get_nylas_client),
) -> WebhookProvider:
    return NylasWebhookProvider(client=client)


def get_webhook_service(
    db: AsyncSession = Depends(get_db),
    provider: WebhookProvider = Depends(get_webhook_provider),
    email_service: EmailIntegrationService = Depends(get_email_service),
) -> WebhookService:
    return WebhookService(
        provider=provider,
        run_repository=SequenceRunRepository(db),
        email_service=email_service,
    )
