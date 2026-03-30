import hashlib
import hmac
from unittest.mock import MagicMock, patch

from app.modules.webhooks.providers.nylas import NylasWebhookProvider


@patch("app.modules.webhooks.providers.nylas.settings")
def test_verify_signature_valid(mock_settings):
    mock_settings.NYLAS_WEBHOOK_SECRET = "secret123"
    client = MagicMock()
    provider = NylasWebhookProvider(client=client)

    body = b'{"type":"message.created"}'
    expected_sig = hmac.new(b"secret123", body, hashlib.sha256).hexdigest()

    assert provider.verify_signature(body, expected_sig) is True


@patch("app.modules.webhooks.providers.nylas.settings")
def test_verify_signature_invalid(mock_settings):
    mock_settings.NYLAS_WEBHOOK_SECRET = "secret123"
    client = MagicMock()
    provider = NylasWebhookProvider(client=client)

    assert provider.verify_signature(b"body", "wrong_signature") is False


def test_parse_notification_message_created():
    client = MagicMock()
    provider = NylasWebhookProvider(client=client)

    payload = {
        "type": "message.created",
        "data": {
            "object": {
                "grant_id": "grant_1",
                "id": "msg_1",
            }
        },
    }

    result = provider.parse_notification(payload)

    assert len(result) == 1
    assert result[0].trigger_type == "message.created"
    assert result[0].grant_id == "grant_1"
    assert result[0].message_id == "msg_1"


def test_parse_notification_unsupported_trigger():
    client = MagicMock()
    provider = NylasWebhookProvider(client=client)

    payload = {"type": "message.updated", "data": {"object": {}}}

    result = provider.parse_notification(payload)

    assert result == []


def test_parse_notification_missing_grant_id():
    client = MagicMock()
    provider = NylasWebhookProvider(client=client)

    payload = {
        "type": "message.created",
        "data": {"object": {"id": "msg_1"}},
    }

    result = provider.parse_notification(payload)

    assert result == []


def test_parse_notification_missing_message_id():
    client = MagicMock()
    provider = NylasWebhookProvider(client=client)

    payload = {
        "type": "message.created",
        "data": {"object": {"grant_id": "grant_1"}},
    }

    result = provider.parse_notification(payload)

    assert result == []


def test_fetch_message_sender_is_object():
    client = MagicMock()
    provider = NylasWebhookProvider(client=client)

    sender = MagicMock()
    sender.email = "alice@example.com"
    message = MagicMock()
    message.id = "msg_1"
    message.thread_id = "thr_1"
    message.from_ = [sender]
    message.subject = "Hello"
    message.body = "Hi there"
    message.date = 1700000000
    client.messages.find.return_value = MagicMock(data=message)

    result = provider.fetch_message("grant_1", "msg_1")

    assert result.external_message_id == "msg_1"
    assert result.thread_id == "thr_1"
    assert result.from_email == "alice@example.com"
    assert result.subject == "Hello"


def test_fetch_message_sender_is_dict():
    client = MagicMock()
    provider = NylasWebhookProvider(client=client)

    message = MagicMock()
    message.id = "msg_2"
    message.thread_id = None
    message.from_ = [{"email": "bob@example.com", "name": "Bob"}]
    message.subject = "Re: Hello"
    message.body = "Thanks"
    message.date = None
    client.messages.find.return_value = MagicMock(data=message)

    result = provider.fetch_message("grant_1", "msg_2")

    assert result.from_email == "bob@example.com"
    assert result.thread_id is None
    assert result.received_at == ""


def test_fetch_message_no_sender():
    client = MagicMock()
    provider = NylasWebhookProvider(client=client)

    message = MagicMock()
    message.id = "msg_3"
    message.thread_id = "thr_1"
    message.from_ = []
    message.subject = None
    message.body = None
    message.date = None
    client.messages.find.return_value = MagicMock(data=message)

    result = provider.fetch_message("grant_1", "msg_3")

    assert result.from_email == ""
    assert result.subject == ""
    assert result.body == ""
