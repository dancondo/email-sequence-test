from fastapi import Depends
from nylas import Client as NylasClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.email_integration.providers.base import EmailProvider
from app.modules.email_integration.providers.nylas import NylasEmailProvider
from app.modules.email_integration.repository import EmailAccountRepository
from app.modules.email_integration.service import EmailIntegrationService
from app.modules.nylas.dependencies import get_nylas_client


def get_email_provider(
    client: NylasClient = Depends(get_nylas_client),
) -> EmailProvider:
    return NylasEmailProvider(client=client)


def get_email_repository(
    db: AsyncSession = Depends(get_db),
) -> EmailAccountRepository:
    return EmailAccountRepository(db)


def get_email_service(
    repository: EmailAccountRepository = Depends(get_email_repository),
    provider: EmailProvider = Depends(get_email_provider),
) -> EmailIntegrationService:
    return EmailIntegrationService(repository=repository, provider=provider)
