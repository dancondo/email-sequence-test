import csv
import io

from fastapi import HTTPException, UploadFile

from app.modules.candidates.models import Candidate
from app.modules.candidates.repository import CandidateRepository
from app.modules.candidates.schemas import (
    CandidateDetailResponse,
    CandidateWithRunCount,
    CsvUploadResponse,
)


class CandidateService:
    def __init__(self, repository: CandidateRepository) -> None:
        self._repository = repository

    async def get_candidate(self, candidate_id: int) -> Candidate:
        candidate = await self._repository.get_by_id(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return candidate

    async def get_or_create_by_email(
        self, email: str, name: str | None = None
    ) -> Candidate:
        existing = await self._repository.get_by_email(email)
        if existing:
            return existing
        created, _ = await self._repository.bulk_create_or_get(
            [{"email": email, "name": name}]
        )
        return created[0]

    async def upload_csv(self, file: UploadFile) -> CsvUploadResponse:
        if not file.filename or not file.filename.endswith(".csv"):
            raise HTTPException(
                status_code=400, detail="File must be a CSV"
            )

        content = await file.read()
        text = content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))

        if not reader.fieldnames or "email" not in reader.fieldnames:
            raise HTTPException(
                status_code=400,
                detail="CSV must have an 'email' column",
            )

        entries: list[dict[str, str | None]] = []
        errors: list[str] = []

        for i, row in enumerate(reader, start=2):
            email = row.get("email", "").strip()
            if not email:
                errors.append(f"Row {i}: missing email")
                continue
            if "@" not in email:
                errors.append(f"Row {i}: invalid email '{email}'")
                continue

            entries.append({
                "email": email,
                "name": row.get("name", "").strip() or None,
            })

        if not entries and not errors:
            raise HTTPException(status_code=400, detail="CSV is empty")

        created, existing = await self._repository.bulk_create_or_get(entries)

        all_candidates = created + existing

        return CsvUploadResponse(
            total_rows=len(entries),
            candidates_created=len(created),
            candidates_existing=len(existing),
            candidates=[
                self._to_response(c) for c in all_candidates
            ],
            errors=errors,
        )

    async def list_candidates(
        self, list_ids: list[int] | None = None
    ) -> list[CandidateWithRunCount]:
        rows = await self._repository.list_all(list_ids)
        return [
            CandidateWithRunCount(
                id=candidate.id,
                email=candidate.email,
                name=candidate.name,
                run_count=run_count,
                created_at=candidate.created_at,
                updated_at=candidate.updated_at,
            )
            for candidate, run_count in rows
        ]

    async def get_candidate_detail(
        self, candidate_id: int
    ) -> CandidateDetailResponse:
        candidate = await self._repository.get_with_runs(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        runs = []
        for src in candidate.sequence_run_candidates:
            seq_run = src.sequence_run
            sequence_name = (
                seq_run.snapshot.get("name", "Unknown")
                if seq_run.snapshot
                else seq_run.sequence.name if seq_run.sequence else "Unknown"
            )
            runs.append({
                "sequence_run_candidate_id": src.id,
                "sequence_run_id": seq_run.id,
                "sequence_id": seq_run.sequence_id,
                "sequence_name": sequence_name,
                "run_status": seq_run.status.value,
                "status": src.status.value,
                "current_step_order": src.current_step_order,
                "created_at": src.created_at,
            })

        referred_by = None
        if candidate.referred_by:
            referred_by = {
                "id": candidate.referred_by.id,
                "email": candidate.referred_by.email,
                "name": candidate.referred_by.name,
                "created_at": candidate.referred_by.created_at,
                "updated_at": candidate.referred_by.updated_at,
            }

        return CandidateDetailResponse(
            id=candidate.id,
            email=candidate.email,
            name=candidate.name,
            referred_by_candidate_id=candidate.referred_by_candidate_id,
            referred_by=referred_by,
            created_at=candidate.created_at,
            updated_at=candidate.updated_at,
            runs=runs,
        )

    @staticmethod
    def _to_response(candidate: Candidate) -> dict:
        return {
            "id": candidate.id,
            "email": candidate.email,
            "name": candidate.name,
            "created_at": candidate.created_at,
            "updated_at": candidate.updated_at,
        }
