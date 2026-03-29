from fastapi import Depends
from nylas import Client as NylasClient

from app.modules.classification.dependencies import get_classification_service
from app.modules.classification.service import ClassificationService
from app.modules.email_integration.dependencies import get_email_service
from app.modules.email_integration.service import EmailIntegrationService
from app.modules.nylas.dependencies import get_nylas_client
from app.modules.sequence_runs.dependencies import get_sequence_run_service
from app.modules.sequence_runs.service import SequenceRunService
from app.modules.webhooks.providers.base import WebhookProvider
from app.modules.webhooks.providers.nylas import NylasWebhookProvider
from app.modules.webhooks.service import WebhookService


def get_webhook_provider(
    client: NylasClient = Depends(get_nylas_client),
) -> WebhookProvider:
    return NylasWebhookProvider(client=client)


def get_webhook_service(
    provider: WebhookProvider = Depends(get_webhook_provider),
    run_service: SequenceRunService = Depends(get_sequence_run_service),
    email_service: EmailIntegrationService = Depends(get_email_service),
    classification_service: ClassificationService = Depends(get_classification_service),
) -> WebhookService:
    return WebhookService(
        provider=provider,
        run_service=run_service,
        email_service=email_service,
        classification_service=classification_service,
    )
