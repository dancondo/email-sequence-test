import enum
from dataclasses import dataclass


class ReplyIntent(str, enum.Enum):
    INTERESTED = "interested"
    NOT_INTERESTED = "not_interested"
    NEUTRAL = "neutral"


@dataclass
class ClassificationResult:
    intent: ReplyIntent
    confidence: float
    reasoning: str
