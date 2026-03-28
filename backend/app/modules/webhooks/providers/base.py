from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class WebhookDelta:
    grant_id: str
    message_id: str


@dataclass
class ParsedReply:
    external_message_id: str
    thread_id: str | None
    from_email: str
    subject: str
    body: str
    received_at: str


class WebhookProvider(ABC):
    @abstractmethod
    def verify_signature(self, raw_body: bytes, signature: str) -> bool:
        ...

    @abstractmethod
    def parse_notification(self, payload: dict) -> list[WebhookDelta]:
        ...

    @abstractmethod
    def fetch_message(self, grant_id: str, message_id: str) -> ParsedReply:
        ...
