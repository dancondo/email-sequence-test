from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.email_integration.providers.base import EmailProvider
from app.modules.email_integration.providers.nylas import NylasEmailProvider
from app.modules.email_integration.repository import EmailAccountRepository
from app.modules.email_integration.service import EmailIntegrationService


def get_email_provider() -> EmailProvider:
    return NylasEmailProvider()


def get_email_repository(
    db: AsyncSession = Depends(get_db),
) -> EmailAccountRepository:
    return EmailAccountRepository(db)


def get_email_service(
    repository: EmailAccountRepository = Depends(get_email_repository),
    provider: EmailProvider = Depends(get_email_provider),
) -> EmailIntegrationService:
    return EmailIntegrationService(repository=repository, provider=provider)
