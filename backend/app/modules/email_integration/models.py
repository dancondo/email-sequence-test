import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class EmailProvider(str, enum.Enum):
    GOOGLE = "google"
    MICROSOFT = "microsoft"


class IntegrationProvider(str, enum.Enum):
    NYLAS = "nylas"


class EmailAccount(Base):
    __tablename__ = "email_account"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    grant_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    provider: Mapped[EmailProvider] = mapped_column(
        Enum(EmailProvider), nullable=False, default=EmailProvider.GOOGLE
    )
    integration_provider: Mapped[IntegrationProvider] = mapped_column(
        Enum(IntegrationProvider), nullable=False, default=IntegrationProvider.NYLAS
    )
    connected_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
