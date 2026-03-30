from app.modules.email_integration.providers.base import OAuthResult, SendResult
from tests.conftest import make_email_account


async def test_get_auth_url(email_integration_service, mock_email_provider):
    mock_email_provider.generate_auth_url.return_value = "https://auth.example.com"

    result = email_integration_service.get_auth_url()

    assert result == "https://auth.example.com"


async def test_handle_callback(
    email_integration_service, mock_email_provider, mock_email_account_repository
):
    mock_email_provider.exchange_code.return_value = OAuthResult(
        grant_id="grant_abc", email="user@company.com"
    )
    saved = make_email_account(grant_id="grant_abc", email="user@company.com")
    mock_email_account_repository.save.return_value = saved

    result = await email_integration_service.handle_callback("auth_code_123")

    assert result is saved
    mock_email_provider.exchange_code.assert_called_once_with("auth_code_123")
    mock_email_account_repository.save.assert_awaited_once_with(
        grant_id="grant_abc", email="user@company.com"
    )


async def test_get_status(
    email_integration_service, mock_email_account_repository
):
    account = make_email_account()
    mock_email_account_repository.get_active.return_value = account

    result = await email_integration_service.get_status()

    assert result is account


async def test_get_status_none(
    email_integration_service, mock_email_account_repository
):
    mock_email_account_repository.get_active.return_value = None

    result = await email_integration_service.get_status()

    assert result is None


async def test_disconnect(
    email_integration_service, mock_email_account_repository
):
    mock_email_account_repository.disconnect.return_value = True

    result = await email_integration_service.disconnect()

    assert result is True


async def test_send_message_immediate(
    email_integration_service, mock_email_provider
):
    expected = SendResult(message_id="msg_1", thread_id="thr_1")
    mock_email_provider.send_message.return_value = expected

    result = email_integration_service.send_message(
        grant_id="g1", to_email="to@ex.com", subject="Hi", body="Hello"
    )

    assert result is expected
    mock_email_provider.send_message.assert_called_once_with(
        grant_id="g1",
        to_email="to@ex.com",
        subject="Hi",
        body="Hello",
        send_at=None,
        reply_to_message_id=None,
    )


async def test_send_message_scheduled(
    email_integration_service, mock_email_provider
):
    expected = SendResult(message_id="msg_2", schedule_id="sch_1")
    mock_email_provider.send_message.return_value = expected

    result = email_integration_service.send_message(
        grant_id="g1",
        to_email="to@ex.com",
        subject="Hi",
        body="Hello",
        send_at=1700000000,
    )

    assert result.schedule_id == "sch_1"


async def test_cancel_scheduled_message(
    email_integration_service, mock_email_provider
):
    mock_email_provider.cancel_scheduled_message.return_value = True

    result = email_integration_service.cancel_scheduled_message(
        grant_id="g1", schedule_id="sch_1"
    )

    assert result is True
    mock_email_provider.cancel_scheduled_message.assert_called_once_with(
        grant_id="g1", schedule_id="sch_1"
    )
