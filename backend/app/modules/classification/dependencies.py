from fastapi import Depends
from openai import OpenAI

from app.modules.classification.providers.base import ClassificationProvider
from app.modules.classification.providers.openai import OpenAIClassificationProvider
from app.modules.classification.service import ClassificationService
from app.modules.openai_llm.dependencies import get_openai_client


def get_classification_provider(
    client: OpenAI = Depends(get_openai_client),
) -> ClassificationProvider:
    return OpenAIClassificationProvider(client=client)


def get_classification_service(
    provider: ClassificationProvider = Depends(get_classification_provider),
) -> ClassificationService:
    return ClassificationService(provider=provider)
