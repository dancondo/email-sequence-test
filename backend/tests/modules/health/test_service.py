async def test_check_healthy(health_service, mock_health_repository):
    mock_health_repository.check_connection.return_value = True

    result = await health_service.check()

    assert result == {"status": "healthy", "database": "connected"}
    mock_health_repository.check_connection.assert_awaited_once()


async def test_check_unhealthy(health_service, mock_health_repository):
    mock_health_repository.check_connection.side_effect = Exception("connection refused")

    result = await health_service.check()

    assert result == {"status": "unhealthy", "database": "connection refused"}
