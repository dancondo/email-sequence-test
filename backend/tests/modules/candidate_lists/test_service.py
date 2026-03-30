from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException


async def test_get_all_lists(candidate_list_service, mock_candidate_list_repository):
    mock_lists = [MagicMock(), MagicMock()]
    mock_candidate_list_repository.get_all.return_value = mock_lists

    result = await candidate_list_service.get_all_lists()

    assert result == mock_lists
    mock_candidate_list_repository.get_all.assert_awaited_once()


async def test_get_or_create_list_by_id_found(
    candidate_list_service, mock_candidate_list_repository
):
    mock_list = MagicMock()
    mock_candidate_list_repository.get_by_id.return_value = mock_list

    result = await candidate_list_service.get_or_create_list(list_id=5)

    assert result is mock_list
    mock_candidate_list_repository.get_by_id.assert_awaited_once_with(5)


async def test_get_or_create_list_by_id_not_found(
    candidate_list_service, mock_candidate_list_repository
):
    mock_candidate_list_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await candidate_list_service.get_or_create_list(list_id=5)

    assert exc_info.value.status_code == 404


async def test_get_or_create_list_by_name_existing(
    candidate_list_service, mock_candidate_list_repository
):
    mock_list = MagicMock()
    mock_candidate_list_repository.get_by_name.return_value = mock_list

    result = await candidate_list_service.get_or_create_list(list_name="Referrals")

    assert result is mock_list
    mock_candidate_list_repository.create.assert_not_awaited()


async def test_get_or_create_list_by_name_new(
    candidate_list_service, mock_candidate_list_repository
):
    mock_candidate_list_repository.get_by_name.return_value = None
    created = MagicMock()
    mock_candidate_list_repository.create.return_value = created

    result = await candidate_list_service.get_or_create_list(list_name="Referrals")

    assert result is created
    mock_candidate_list_repository.create.assert_awaited_once_with("Referrals")


async def test_get_or_create_list_no_params(candidate_list_service):
    with pytest.raises(HTTPException) as exc_info:
        await candidate_list_service.get_or_create_list()

    assert exc_info.value.status_code == 400


async def test_add_candidates_to_list(
    candidate_list_service, mock_candidate_list_repository
):
    await candidate_list_service.add_candidates_to_list(1, [10, 20])

    mock_candidate_list_repository.add_candidates.assert_awaited_once_with(1, [10, 20])
