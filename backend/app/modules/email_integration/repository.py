from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.email_integration.models import (
    EmailAccount,
    EmailProvider,
    IntegrationProvider,
)


class EmailAccountRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def find_by_email(self, email: str) -> EmailAccount | None:
        stmt = select(EmailAccount).where(EmailAccount.email == email)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active(self) -> EmailAccount | None:
        stmt = select(EmailAccount).where(EmailAccount.is_active.is_(True)).limit(1)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def save(
        self,
        grant_id: str,
        email: str,
        provider: EmailProvider = EmailProvider.GOOGLE,
        integration_provider: IntegrationProvider = IntegrationProvider.NYLAS,
    ) -> EmailAccount:
        existing = await self.find_by_email(email)
        if existing:
            existing.grant_id = grant_id
            existing.is_active = True
            existing.connected_at = datetime.utcnow()
            await self._db.commit()
            await self._db.refresh(existing)
            return existing

        account = EmailAccount(
            grant_id=grant_id,
            email=email,
            provider=provider,
            integration_provider=integration_provider,
        )
        self._db.add(account)
        await self._db.commit()
        await self._db.refresh(account)
        return account

    async def disconnect(self) -> bool:
        account = await self.get_active()
        if not account:
            return False
        account.is_active = False
        await self._db.commit()
        return True
