from fastapi import APIRouter, Depends, Form, UploadFile

from app.modules.candidates.dependencies import get_candidate_service
from app.modules.candidates.schemas import CsvUploadResponse
from app.modules.candidates.service import CandidateService

router = APIRouter(prefix="/api/candidates", tags=["candidates"])


@router.post("/upload", response_model=CsvUploadResponse, status_code=201)
async def upload_candidates(
    file: UploadFile,
    list_id: int | None = Form(None),
    list_name: str | None = Form(None),
    service: CandidateService = Depends(get_candidate_service),
):
    return await service.upload_csv(file, list_id=list_id, list_name=list_name)
