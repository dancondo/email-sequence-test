from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.candidate_lists.repository import CandidateListRepository
from app.modules.candidate_lists.service import CandidateListService
from app.modules.candidates.repository import CandidateRepository
from app.modules.candidates.service import CandidateService
from app.modules.classification.providers.base import ClassificationProvider
from app.modules.classification.service import ClassificationService
from app.modules.email_integration.providers.base import EmailProvider
from app.modules.email_integration.repository import EmailAccountRepository
from app.modules.email_integration.service import EmailIntegrationService
from app.modules.health.repository import HealthRepository
from app.modules.health.service import HealthService
from app.modules.sequence_runs.models import (
    SequenceRunCandidateStatus,
    SequenceRunStatus,
)
from app.modules.sequence_runs.repository import SequenceRunRepository
from app.modules.sequence_runs.service import SequenceRunService
from app.modules.sequences.repository import SequenceRepository
from app.modules.sequences.service import SequenceService
from app.modules.webhooks.providers.base import WebhookProvider
from app.modules.webhooks.service import WebhookService


# ---------------------------------------------------------------------------
# Repository mocks
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_candidate_repository():
    return AsyncMock(spec=CandidateRepository)


@pytest.fixture
def mock_candidate_list_repository():
    return AsyncMock(spec=CandidateListRepository)


@pytest.fixture
def mock_health_repository():
    return AsyncMock(spec=HealthRepository)


@pytest.fixture
def mock_sequence_repository():
    return AsyncMock(spec=SequenceRepository)


@pytest.fixture
def mock_sequence_run_repository():
    repo = AsyncMock(spec=SequenceRunRepository)
    repo._db = AsyncMock()
    return repo


@pytest.fixture
def mock_email_account_repository():
    return AsyncMock(spec=EmailAccountRepository)


# ---------------------------------------------------------------------------
# Provider mocks
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_email_provider():
    return MagicMock(spec=EmailProvider)


@pytest.fixture
def mock_classification_provider():
    return MagicMock(spec=ClassificationProvider)


@pytest.fixture
def mock_webhook_provider():
    return MagicMock(spec=WebhookProvider)


# ---------------------------------------------------------------------------
# Service instances with mocked dependencies
# ---------------------------------------------------------------------------

@pytest.fixture
def health_service(mock_health_repository):
    return HealthService(repository=mock_health_repository)


@pytest.fixture
def candidate_service(mock_candidate_repository):
    return CandidateService(repository=mock_candidate_repository)


@pytest.fixture
def candidate_list_service(mock_candidate_list_repository):
    return CandidateListService(repository=mock_candidate_list_repository)


@pytest.fixture
def classification_service(mock_classification_provider):
    return ClassificationService(provider=mock_classification_provider)


@pytest.fixture
def email_integration_service(mock_email_account_repository, mock_email_provider):
    return EmailIntegrationService(
        repository=mock_email_account_repository,
        provider=mock_email_provider,
    )


@pytest.fixture
def sequence_service(mock_sequence_repository, candidate_list_service):
    return SequenceService(
        repository=mock_sequence_repository,
        candidate_list_service=candidate_list_service,
    )


@pytest.fixture
def sequence_run_service(
    mock_sequence_run_repository,
    sequence_service,
    candidate_service,
    email_integration_service,
    candidate_list_service,
):
    return SequenceRunService(
        run_repository=mock_sequence_run_repository,
        sequence_service=sequence_service,
        candidate_service=candidate_service,
        email_service=email_integration_service,
        candidate_list_service=candidate_list_service,
    )


@pytest.fixture
def webhook_service(
    mock_webhook_provider,
    mock_email_account_repository,
    mock_email_provider,
    mock_classification_provider,
):
    """WebhookService with fully mocked SequenceRunService to avoid deep nesting."""
    run_service = AsyncMock(spec=SequenceRunService)
    email_service = EmailIntegrationService(
        repository=mock_email_account_repository,
        provider=mock_email_provider,
    )
    classification_service = ClassificationService(
        provider=mock_classification_provider,
    )
    service = WebhookService(
        provider=mock_webhook_provider,
        run_service=run_service,
        email_service=email_service,
        classification_service=classification_service,
    )
    service._mock_run_service = run_service
    return service


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------

def make_candidate(id=1, email="test@example.com", name=None, **kwargs):
    candidate = MagicMock()
    candidate.id = id
    candidate.email = email
    candidate.name = name
    candidate.created_at = datetime(2025, 1, 1)
    candidate.updated_at = datetime(2025, 1, 1)
    candidate.referred_by_candidate_id = None
    candidate.referred_by = None
    candidate.sequence_run_candidates = []
    for k, v in kwargs.items():
        setattr(candidate, k, v)
    return candidate


def make_sequence_run(
    id=1, sequence_id=1, status=SequenceRunStatus.DRAFT, **kwargs
):
    run = MagicMock()
    run.id = id
    run.sequence_id = sequence_id
    run.status = status
    run.candidates = []
    run.snapshot = None
    run.started_at = None
    run.created_at = datetime(2025, 1, 1)
    run.updated_at = datetime(2025, 1, 1)
    for k, v in kwargs.items():
        setattr(run, k, v)
    return run


def make_sequence_run_candidate(
    id=1,
    candidate_id=1,
    sequence_run_id=1,
    status=SequenceRunCandidateStatus.ACTIVE,
    email="candidate@example.com",
    **kwargs,
):
    src = MagicMock()
    src.id = id
    src.candidate_id = candidate_id
    src.sequence_run_id = sequence_run_id
    src.status = status
    src.current_step_order = 0
    src.candidate = make_candidate(id=candidate_id, email=email)
    src.sequence_run = make_sequence_run(id=sequence_run_id)
    src.events = []
    src.created_at = datetime(2025, 1, 1)
    src.updated_at = datetime(2025, 1, 1)
    for k, v in kwargs.items():
        setattr(src, k, v)
    return src


def make_email_account(grant_id="grant_1", email="recruiter@company.com"):
    account = MagicMock()
    account.grant_id = grant_id
    account.email = email
    account.is_active = True
    return account


def make_event(
    id=1,
    event_type=None,
    step_order=None,
    external_message_id=None,
    external_schedule_id=None,
    external_thread_id=None,
    extra=None,
    **kwargs,
):
    event = MagicMock()
    event.id = id
    event.event_type = event_type
    event.step_order = step_order
    event.external_message_id = external_message_id
    event.external_schedule_id = external_schedule_id
    event.external_thread_id = external_thread_id
    event.extra = extra
    event.sequence_run_candidate_id = kwargs.get("sequence_run_candidate_id", 1)
    event.occurred_at = datetime(2025, 1, 1)
    for k, v in kwargs.items():
        setattr(event, k, v)
    return event


def make_sequence(id=1, name="Test Sequence", steps=None, **kwargs):
    seq = MagicMock()
    seq.id = id
    seq.name = name
    seq.steps = steps or []
    seq.referral_list_id = None
    seq.referral_list = None
    seq.is_active = True
    seq.created_at = datetime(2025, 1, 1)
    seq.updated_at = datetime(2025, 1, 1)
    for k, v in kwargs.items():
        setattr(seq, k, v)
    return seq
