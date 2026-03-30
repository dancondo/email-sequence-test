import json
from unittest.mock import MagicMock, patch

from app.modules.classification.providers.openai import OpenAIClassificationProvider
from app.modules.classification.schemas import ReplyIntent


@patch("app.modules.classification.providers.openai.settings")
def test_classify_reply_interested(mock_settings):
    mock_settings.OPENAI_MODEL = "gpt-4o-mini"
    client = MagicMock()
    provider = OpenAIClassificationProvider(client=client)

    tool_call = MagicMock()
    tool_call.function.arguments = json.dumps({
        "intent": "interested",
        "confidence": 0.92,
        "reasoning": "Wants to learn more",
    })
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.tool_calls = [tool_call]
    client.chat.completions.create.return_value = response

    result = provider.classify_reply("I'd love to chat!")

    assert result.intent == ReplyIntent.INTERESTED
    assert result.confidence == 0.92
    assert result.referral_email is None


@patch("app.modules.classification.providers.openai.settings")
def test_classify_reply_not_interested(mock_settings):
    mock_settings.OPENAI_MODEL = "gpt-4o-mini"
    client = MagicMock()
    provider = OpenAIClassificationProvider(client=client)

    tool_call = MagicMock()
    tool_call.function.arguments = json.dumps({
        "intent": "not_interested",
        "confidence": 0.85,
        "reasoning": "Declined",
    })
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.tool_calls = [tool_call]
    client.chat.completions.create.return_value = response

    result = provider.classify_reply("Not interested, thanks.")

    assert result.intent == ReplyIntent.NOT_INTERESTED


@patch("app.modules.classification.providers.openai.settings")
def test_classify_reply_with_referral(mock_settings):
    mock_settings.OPENAI_MODEL = "gpt-4o-mini"
    client = MagicMock()
    provider = OpenAIClassificationProvider(client=client)

    tool_call = MagicMock()
    tool_call.function.arguments = json.dumps({
        "intent": "not_interested",
        "confidence": 0.80,
        "reasoning": "Declined but referred someone",
        "referral_email": "jing@example.com",
        "referral_name": "Jing",
    })
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.tool_calls = [tool_call]
    client.chat.completions.create.return_value = response

    result = provider.classify_reply("Not me, talk to Jing at jing@example.com")

    assert result.referral_email == "jing@example.com"
    assert result.referral_name == "Jing"


@patch("app.modules.classification.providers.openai.settings")
def test_classify_reply_correct_model_and_tool(mock_settings):
    mock_settings.OPENAI_MODEL = "gpt-4o-mini"
    client = MagicMock()
    provider = OpenAIClassificationProvider(client=client)

    tool_call = MagicMock()
    tool_call.function.arguments = json.dumps({
        "intent": "neutral",
        "confidence": 0.5,
        "reasoning": "Out of office",
    })
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.tool_calls = [tool_call]
    client.chat.completions.create.return_value = response

    provider.classify_reply("OOO until Monday")

    call_kwargs = client.chat.completions.create.call_args
    assert call_kwargs.kwargs["model"] == "gpt-4o-mini"
    assert call_kwargs.kwargs["tool_choice"] == {
        "type": "function",
        "function": {"name": "classify_reply_intent"},
    }
