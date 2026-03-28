from abc import ABC, abstractmethod

from app.modules.classification.schemas import ClassificationResult


class ClassificationProvider(ABC):
    @abstractmethod
    def classify_reply(self, reply_body: str) -> ClassificationResult:
        ...
