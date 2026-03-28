from app.modules.classification.providers.base import ClassificationProvider
from app.modules.classification.schemas import ClassificationResult


class ClassificationService:
    def __init__(self, provider: ClassificationProvider) -> None:
        self._provider = provider

    def classify_reply(self, reply_body: str) -> ClassificationResult:
        return self._provider.classify_reply(reply_body)
