import json
from unittest.mock import MagicMock, patch

from app.modules.email_integration.providers.nylas import NylasEmailProvider


@patch("app.modules.email_integration.providers.nylas.settings")
def test_generate_auth_url(mock_settings):
    mock_settings.NYLAS_CLIENT_ID = "client_id_1"
    mock_settings.NYLAS_REDIRECT_URI = "http://localhost/callback"
    client = MagicMock()
    client.auth.url_for_oauth2.return_value = "https://auth.nylas.com/oauth"
    provider = NylasEmailProvider(client=client)

    result = provider.generate_auth_url()

    assert result == "https://auth.nylas.com/oauth"
    call_args = client.auth.url_for_oauth2.call_args[0][0]
    assert call_args["client_id"] == "client_id_1"
    assert call_args["provider"] == "google"


@patch("app.modules.email_integration.providers.nylas.settings")
def test_exchange_code(mock_settings):
    mock_settings.NYLAS_CLIENT_ID = "client_id_1"
    mock_settings.NYLAS_REDIRECT_URI = "http://localhost/callback"
    client = MagicMock()
    token_response = MagicMock()
    token_response.grant_id = "grant_abc"
    token_response.email = "user@company.com"
    client.auth.exchange_code_for_token.return_value = token_response
    provider = NylasEmailProvider(client=client)

    result = provider.exchange_code("code_123")

    assert result.grant_id == "grant_abc"
    assert result.email == "user@company.com"


@patch("app.modules.email_integration.providers.nylas.requests")
def test_send_message_immediate(mock_requests):
    client = MagicMock()
    http = MagicMock()
    http.api_server = "https://api.nylas.com"
    http.api_key = "key_1"
    http.timeout = 30
    client.messages._http_client = http
    provider = NylasEmailProvider(client=client)

    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "data": {
            "id": "msg_1",
            "schedule_id": None,
            "thread_id": "thr_1",
        }
    }
    mock_requests.post.return_value = mock_resp

    result = provider.send_message(
        grant_id="g1", to_email="to@ex.com", subject="Hi", body="Hello"
    )

    assert result.message_id == "msg_1"
    assert result.schedule_id is None
    assert result.thread_id == "thr_1"

    call_kwargs = mock_requests.post.call_args
    sent_body = json.loads(call_kwargs.kwargs["data"])
    assert "send_at" not in sent_body


@patch("app.modules.email_integration.providers.nylas.requests")
def test_send_message_scheduled(mock_requests):
    client = MagicMock()
    http = MagicMock()
    http.api_server = "https://api.nylas.com"
    http.api_key = "key_1"
    http.timeout = 30
    client.messages._http_client = http
    provider = NylasEmailProvider(client=client)

    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "data": {"id": "msg_2", "schedule_id": "sch_1", "thread_id": None}
    }
    mock_requests.post.return_value = mock_resp

    result = provider.send_message(
        grant_id="g1",
        to_email="to@ex.com",
        subject="Hi",
        body="Hello",
        send_at=1700000000,
    )

    assert result.schedule_id == "sch_1"
    call_kwargs = mock_requests.post.call_args
    sent_body = json.loads(call_kwargs.kwargs["data"])
    assert sent_body["send_at"] == 1700000000


@patch("app.modules.email_integration.providers.nylas.requests")
def test_send_message_reply(mock_requests):
    client = MagicMock()
    http = MagicMock()
    http.api_server = "https://api.nylas.com"
    http.api_key = "key_1"
    http.timeout = 30
    client.messages._http_client = http
    provider = NylasEmailProvider(client=client)

    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "data": {"id": "msg_3", "schedule_id": None, "thread_id": "thr_1"}
    }
    mock_requests.post.return_value = mock_resp

    result = provider.send_message(
        grant_id="g1",
        to_email="to@ex.com",
        subject="Re: Hi",
        body="Thanks!",
        reply_to_message_id="msg_original",
    )

    call_kwargs = mock_requests.post.call_args
    sent_body = json.loads(call_kwargs.kwargs["data"])
    assert sent_body["reply_to_message_id"] == "msg_original"


def test_cancel_scheduled_message():
    client = MagicMock()
    provider = NylasEmailProvider(client=client)

    result = provider.cancel_scheduled_message(
        grant_id="g1", schedule_id="sch_1"
    )

    assert result is True
    client.messages.stop_scheduled_message.assert_called_once_with("g1", "sch_1")
