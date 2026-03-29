import csv
import io

from fastapi import HTTPException, UploadFile

from app.modules.candidate_lists.service import CandidateListService
from app.modules.candidates.models import Candidate
from app.modules.candidates.repository import CandidateRepository
from app.modules.candidates.schemas import CsvUploadResponse


class CandidateService:
    def __init__(
        self,
        repository: CandidateRepository,
        candidate_list_service: CandidateListService,
    ) -> None:
        self._repository = repository
        self._candidate_list_service = candidate_list_service

    async def get_candidate(self, candidate_id: int) -> Candidate:
        candidate = await self._repository.get_by_id(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return candidate

    async def upload_csv(
        self,
        file: UploadFile,
        list_id: int | None = None,
        list_name: str | None = None,
    ) -> CsvUploadResponse:
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

        if list_id or list_name:
            candidate_list = await self._candidate_list_service.get_or_create_list(
                list_id=list_id, list_name=list_name
            )
            candidate_ids = [c.id for c in all_candidates]
            if candidate_ids:
                await self._candidate_list_service.add_candidates_to_list(
                    candidate_list.id, candidate_ids
                )

        return CsvUploadResponse(
            total_rows=len(entries),
            candidates_created=len(created),
            candidates_existing=len(existing),
            candidates=[
                self._to_response(c) for c in all_candidates
            ],
            errors=errors,
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
