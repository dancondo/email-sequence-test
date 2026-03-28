from nylas import Client as NylasClient

from app.modules.nylas.client import create_nylas_client


def get_nylas_client() -> NylasClient:
    return create_nylas_client()
