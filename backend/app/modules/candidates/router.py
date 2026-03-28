from fastapi import APIRouter, Depends, UploadFile

from app.modules.candidates.dependencies import get_candidate_service
from app.modules.candidates.schemas import CsvUploadResponse
from app.modules.candidates.service import CandidateService

router = APIRouter(prefix="/api/candidates", tags=["candidates"])


@router.post("/upload", response_model=CsvUploadResponse, status_code=201)
async def upload_candidates(
    file: UploadFile,
    service: CandidateService = Depends(get_candidate_service),
):
    return await service.upload_csv(file)
