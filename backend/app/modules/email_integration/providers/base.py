from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class OAuthResult:
    grant_id: str
    email: str


class EmailProvider(ABC):
    @abstractmethod
    def generate_auth_url(self) -> str:
        """Generate the OAuth authorization URL for the user to visit."""
        ...

    @abstractmethod
    def exchange_code(self, code: str) -> OAuthResult:
        """Exchange an authorization code for a grant. Returns grant_id and email."""
        ...
