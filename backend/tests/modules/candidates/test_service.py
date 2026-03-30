from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from tests.conftest import make_candidate


async def test_get_candidate_found(candidate_service, mock_candidate_repository):
    candidate = make_candidate(id=1)
    mock_candidate_repository.get_by_id.return_value = candidate

    result = await candidate_service.get_candidate(1)

    assert result is candidate


async def test_get_candidate_not_found(candidate_service, mock_candidate_repository):
    mock_candidate_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await candidate_service.get_candidate(999)

    assert exc_info.value.status_code == 404


async def test_get_or_create_by_email_existing(
    candidate_service, mock_candidate_repository
):
    existing = make_candidate(id=1, email="alice@example.com")
    mock_candidate_repository.get_by_email.return_value = existing

    result = await candidate_service.get_or_create_by_email("alice@example.com")

    assert result is existing
    mock_candidate_repository.bulk_create_or_get.assert_not_awaited()


async def test_get_or_create_by_email_new(
    candidate_service, mock_candidate_repository
):
    mock_candidate_repository.get_by_email.return_value = None
    created = make_candidate(id=2, email="bob@example.com")
    mock_candidate_repository.bulk_create_or_get.return_value = ([created], [])

    result = await candidate_service.get_or_create_by_email(
        "bob@example.com", name="Bob"
    )

    assert result is created
    mock_candidate_repository.bulk_create_or_get.assert_awaited_once_with(
        [{"email": "bob@example.com", "name": "Bob"}]
    )


async def test_upload_csv_not_csv_extension(candidate_service):
    file = MagicMock()
    file.filename = "data.txt"

    with pytest.raises(HTTPException) as exc_info:
        await candidate_service.upload_csv(file)

    assert exc_info.value.status_code == 400
    assert "CSV" in exc_info.value.detail


async def test_upload_csv_no_filename(candidate_service):
    file = MagicMock()
    file.filename = None

    with pytest.raises(HTTPException) as exc_info:
        await candidate_service.upload_csv(file)

    assert exc_info.value.status_code == 400


async def test_upload_csv_missing_email_column(candidate_service):
    csv_content = b"name,phone\nAlice,555-0100\n"
    file = MagicMock()
    file.filename = "data.csv"
    file.read = AsyncMock(return_value=csv_content)

    with pytest.raises(HTTPException) as exc_info:
        await candidate_service.upload_csv(file)

    assert exc_info.value.status_code == 400
    assert "email" in exc_info.value.detail.lower()


async def test_upload_csv_empty(candidate_service):
    csv_content = b"email,name\n"
    file = MagicMock()
    file.filename = "data.csv"
    file.read = AsyncMock(return_value=csv_content)

    with pytest.raises(HTTPException) as exc_info:
        await candidate_service.upload_csv(file)

    assert exc_info.value.status_code == 400
    assert "empty" in exc_info.value.detail.lower()


async def test_upload_csv_valid_rows(candidate_service, mock_candidate_repository):
    csv_content = (
        b"email,name\nalice@ex.com,Alice\nbob@ex.com,Bob\ncarol@ex.com,Carol\n"
    )
    file = MagicMock()
    file.filename = "data.csv"
    file.read = AsyncMock(return_value=csv_content)

    c1 = make_candidate(id=1, email="alice@ex.com", name="Alice")
    c2 = make_candidate(id=2, email="bob@ex.com", name="Bob")
    c3 = make_candidate(id=3, email="carol@ex.com", name="Carol")
    mock_candidate_repository.bulk_create_or_get.return_value = ([c1, c2], [c3])

    result = await candidate_service.upload_csv(file)

    assert result.total_rows == 3
    assert result.candidates_created == 2
    assert result.candidates_existing == 1
    assert len(result.candidates) == 3
    assert result.errors == []


async def test_upload_csv_with_invalid_emails(
    candidate_service, mock_candidate_repository
):
    csv_content = b"email,name\nalice@ex.com,Alice\nbademail,Bob\n"
    file = MagicMock()
    file.filename = "data.csv"
    file.read = AsyncMock(return_value=csv_content)

    c1 = make_candidate(id=1, email="alice@ex.com")
    mock_candidate_repository.bulk_create_or_get.return_value = ([c1], [])

    result = await candidate_service.upload_csv(file)

    assert result.total_rows == 1
    assert len(result.errors) == 1
    assert "invalid email" in result.errors[0].lower()


async def test_upload_csv_missing_email_in_row(
    candidate_service, mock_candidate_repository
):
    csv_content = b"email,name\n,Alice\nbob@ex.com,Bob\n"
    file = MagicMock()
    file.filename = "data.csv"
    file.read = AsyncMock(return_value=csv_content)

    c1 = make_candidate(id=1, email="bob@ex.com")
    mock_candidate_repository.bulk_create_or_get.return_value = ([c1], [])

    result = await candidate_service.upload_csv(file)

    assert result.total_rows == 1
    assert len(result.errors) == 1
    assert "missing email" in result.errors[0].lower()


async def test_list_candidates_no_filter(
    candidate_service, mock_candidate_repository
):
    c1 = make_candidate(id=1, email="a@ex.com")
    c2 = make_candidate(id=2, email="b@ex.com")
    mock_candidate_repository.list_all.return_value = [(c1, 2), (c2, 0)]

    result = await candidate_service.list_candidates()

    assert len(result) == 2
    assert result[0].id == 1
    assert result[0].run_count == 2
    mock_candidate_repository.list_all.assert_awaited_once_with(None)


async def test_list_candidates_with_list_filter(
    candidate_service, mock_candidate_repository
):
    mock_candidate_repository.list_all.return_value = []

    await candidate_service.list_candidates(list_ids=[1, 2])

    mock_candidate_repository.list_all.assert_awaited_once_with([1, 2])


async def test_get_candidate_detail_found(
    candidate_service, mock_candidate_repository
):
    src = MagicMock()
    src.id = 10
    src.status.value = "active"
    src.current_step_order = 1
    src.created_at = datetime(2025, 1, 1)

    seq_run = MagicMock()
    seq_run.id = 100
    seq_run.sequence_id = 5
    seq_run.snapshot = None
    seq_run.sequence.name = "Outreach V1"
    seq_run.status.value = "active"
    src.sequence_run = seq_run

    candidate = make_candidate(id=1, email="test@ex.com")
    candidate.sequence_run_candidates = [src]
    candidate.referred_by = None

    mock_candidate_repository.get_with_runs.return_value = candidate

    result = await candidate_service.get_candidate_detail(1)

    assert result.id == 1
    assert len(result.runs) == 1
    assert result.runs[0].sequence_name == "Outreach V1"


async def test_get_candidate_detail_not_found(
    candidate_service, mock_candidate_repository
):
    mock_candidate_repository.get_with_runs.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await candidate_service.get_candidate_detail(999)

    assert exc_info.value.status_code == 404


async def test_get_candidate_detail_snapshot_name(
    candidate_service, mock_candidate_repository
):
    src = MagicMock()
    src.id = 10
    src.status.value = "active"
    src.current_step_order = 0
    src.created_at = datetime(2025, 1, 1)

    seq_run = MagicMock()
    seq_run.id = 100
    seq_run.sequence_id = 5
    seq_run.snapshot = {"name": "Snapshot Name"}
    seq_run.status.value = "active"
    src.sequence_run = seq_run

    candidate = make_candidate(id=1)
    candidate.sequence_run_candidates = [src]
    candidate.referred_by = None

    mock_candidate_repository.get_with_runs.return_value = candidate

    result = await candidate_service.get_candidate_detail(1)

    assert result.runs[0].sequence_name == "Snapshot Name"
