import json
import logging

from openai import OpenAI

from app.core.config import settings
from app.modules.classification.providers.base import ClassificationProvider
from app.modules.classification.schemas import ClassificationResult

logger = logging.getLogger(__name__)

CLASSIFY_TOOL = {
    "type": "function",
    "function": {
        "name": "classify_reply_intent",
        "description": "Classify a candidate's email reply intent in a recruiting outreach context.",
        "parameters": {
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "enum": ["interested", "not_interested", "neutral"],
                    "description": "The candidate's intent: interested (wants to learn more / open to conversation), not_interested (declines / not looking), neutral (unclear, out-of-office, or unrelated).",
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "Confidence score between 0 and 1.",
                },
                "reasoning": {
                    "type": "string",
                    "description": "Brief explanation of why this intent was chosen.",
                },
            },
            "required": ["intent", "confidence", "reasoning"],
        },
    },
}

SYSTEM_PROMPT = (
    "You are a recruiting email classifier. "
    "Given a candidate's reply to a recruiter outreach email, "
    "classify their intent using the provided tool. "
    "Focus on whether the candidate is open to the opportunity, "
    "explicitly declining, or giving an ambiguous/unrelated response."
)


class OpenAIClassificationProvider(ClassificationProvider):
    def __init__(self, client: OpenAI) -> None:
        self._client = client

    def classify_reply(self, reply_body: str) -> ClassificationResult:
        response = self._client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": reply_body},
            ],
            tools=[CLASSIFY_TOOL],
            tool_choice={"type": "function", "function": {"name": "classify_reply_intent"}},
        )

        tool_call = response.choices[0].message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)

        return ClassificationResult(
            intent=args["intent"],
            confidence=args["confidence"],
            reasoning=args["reasoning"],
        )
