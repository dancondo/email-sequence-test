from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.modules.sequences.schemas import SequenceCreate, SequenceStepCreate, SequenceUpdate
from tests.conftest import make_sequence


async def test_list_sequences(sequence_service, mock_sequence_repository):
    seqs = [make_sequence(id=1), make_sequence(id=2)]
    mock_sequence_repository.list_all.return_value = seqs

    result = await sequence_service.list_sequences()

    assert result == seqs


async def test_get_sequence_found(sequence_service, mock_sequence_repository):
    seq = make_sequence(id=1)
    mock_sequence_repository.get_by_id.return_value = seq

    result = await sequence_service.get_sequence(1)

    assert result is seq


async def test_get_sequence_not_found(sequence_service, mock_sequence_repository):
    mock_sequence_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await sequence_service.get_sequence(999)

    assert exc_info.value.status_code == 404


async def test_create_sequence_basic(sequence_service, mock_sequence_repository):
    created = make_sequence(id=1, name="Outreach")
    mock_sequence_repository.create.return_value = created

    data = SequenceCreate(
        name="Outreach",
        steps=[SequenceStepCreate(subject="Hi", body="Hello", delay_minutes=0)],
    )

    result = await sequence_service.create_sequence(data)

    assert result is created
    mock_sequence_repository.create.assert_awaited_once()
    call_kwargs = mock_sequence_repository.create.call_args.kwargs
    assert call_kwargs["name"] == "Outreach"
    assert call_kwargs["referral_list_id"] is None


async def test_create_sequence_with_referral_list_id(
    sequence_service, mock_sequence_repository
):
    mock_sequence_repository.create.return_value = make_sequence()

    data = SequenceCreate(name="Seq", steps=[], referral_list_id=5)

    await sequence_service.create_sequence(data)

    call_kwargs = mock_sequence_repository.create.call_args.kwargs
    assert call_kwargs["referral_list_id"] == 5


async def test_create_sequence_with_referral_list_name(
    sequence_service, mock_sequence_repository, mock_candidate_list_repository
):
    mock_candidate_list_repository.get_by_name.return_value = None
    new_list = MagicMock()
    new_list.id = 7
    mock_candidate_list_repository.create.return_value = new_list
    mock_sequence_repository.create.return_value = make_sequence()

    data = SequenceCreate(name="Seq", steps=[], referral_list_name="Referrals")

    await sequence_service.create_sequence(data)

    call_kwargs = mock_sequence_repository.create.call_args.kwargs
    assert call_kwargs["referral_list_id"] == 7


async def test_update_sequence_name_only(
    sequence_service, mock_sequence_repository
):
    seq = make_sequence(id=1, name="Old")
    mock_sequence_repository.get_by_id.return_value = seq
    mock_sequence_repository.update.return_value = seq

    data = SequenceUpdate(name="New")

    await sequence_service.update_sequence(1, data)

    call_kwargs = mock_sequence_repository.update.call_args.kwargs
    assert call_kwargs["name"] == "New"
    assert call_kwargs["steps_data"] is None


async def test_update_sequence_with_steps(
    sequence_service, mock_sequence_repository
):
    seq = make_sequence(id=1)
    mock_sequence_repository.get_by_id.return_value = seq
    mock_sequence_repository.update.return_value = seq

    data = SequenceUpdate(
        steps=[SequenceStepCreate(subject="Step 1", body="Body", delay_minutes=5)]
    )

    await sequence_service.update_sequence(1, data)

    call_kwargs = mock_sequence_repository.update.call_args.kwargs
    assert len(call_kwargs["steps_data"]) == 1
    assert call_kwargs["steps_data"][0]["subject"] == "Step 1"


async def test_update_sequence_not_found(
    sequence_service, mock_sequence_repository
):
    mock_sequence_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await sequence_service.update_sequence(999, SequenceUpdate(name="X"))

    assert exc_info.value.status_code == 404


async def test_delete_sequence(sequence_service, mock_sequence_repository):
    seq = make_sequence(id=1)
    mock_sequence_repository.get_by_id.return_value = seq

    await sequence_service.delete_sequence(1)

    mock_sequence_repository.delete.assert_awaited_once_with(seq)


async def test_delete_sequence_not_found(
    sequence_service, mock_sequence_repository
):
    mock_sequence_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await sequence_service.delete_sequence(999)

    assert exc_info.value.status_code == 404
