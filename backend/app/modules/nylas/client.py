from nylas import Client as NylasClient

from app.core.config import settings


def create_nylas_client() -> NylasClient:
    return NylasClient(
        api_key=settings.NYLAS_API_KEY,
        api_uri=settings.NYLAS_API_URI,
    )
