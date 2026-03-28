from nylas import Client as NylasClient

from app.core.config import settings
from app.modules.email_integration.providers.base import EmailProvider, OAuthResult


class NylasEmailProvider(EmailProvider):
    def __init__(self) -> None:
        self._client = NylasClient(
            api_key=settings.NYLAS_API_KEY,
            api_uri=settings.NYLAS_API_URI,
        )

    def generate_auth_url(self) -> str:
        auth_url = self._client.auth.url_for_oauth2({
            "client_id": settings.NYLAS_CLIENT_ID,
            "redirect_uri": settings.NYLAS_REDIRECT_URI,
            "provider": "google",
        })
        return auth_url

    def exchange_code(self, code: str) -> OAuthResult:
        response = self._client.auth.exchange_code_for_token({
            "client_id": settings.NYLAS_CLIENT_ID,
            "redirect_uri": settings.NYLAS_REDIRECT_URI,
            "code": code,
        })
        return OAuthResult(
            grant_id=response.grant_id,
            email=response.email,
        )
