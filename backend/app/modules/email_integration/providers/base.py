from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class OAuthResult:
    grant_id: str
    email: str


@dataclass
class SendResult:
    message_id: str
    schedule_id: str | None = None
    thread_id: str | None = None


class EmailProvider(ABC):
    @abstractmethod
    def generate_auth_url(self) -> str:
        """Generate the OAuth authorization URL for the user to visit."""
        ...

    @abstractmethod
    def exchange_code(self, code: str) -> OAuthResult:
        """Exchange an authorization code for a grant. Returns grant_id and email."""
        ...

    @abstractmethod
    def send_message(
        self,
        grant_id: str,
        to_email: str,
        subject: str,
        body: str,
        send_at: int | None = None,
    ) -> SendResult:
        """Send an email. When send_at (unix timestamp) is provided, schedule for later delivery."""
        ...

    @abstractmethod
    def cancel_scheduled_message(self, grant_id: str, schedule_id: str) -> bool:
        """Cancel a previously scheduled message."""
        ...
