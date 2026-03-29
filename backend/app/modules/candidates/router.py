from fastapi import APIRouter, Depends, Query, UploadFile

from app.modules.candidates.dependencies import get_candidate_service
from app.modules.candidates.schemas import (
    CandidateDetailResponse,
    CandidateWithRunCount,
    CsvUploadResponse,
)
from app.modules.candidates.service import CandidateService

router = APIRouter(prefix="/api/candidates", tags=["candidates"])


@router.get("", response_model=list[CandidateWithRunCount])
async def list_candidates(
    list_ids: list[int] | None = Query(None),
    service: CandidateService = Depends(get_candidate_service),
):
    return await service.list_candidates(list_ids)


@router.get("/{candidate_id}", response_model=CandidateDetailResponse)
async def get_candidate(
    candidate_id: int,
    service: CandidateService = Depends(get_candidate_service),
):
    return await service.get_candidate_detail(candidate_id)


@router.post("/upload", response_model=CsvUploadResponse, status_code=201)
async def upload_candidates(
    file: UploadFile,
    service: CandidateService = Depends(get_candidate_service),
):
    return await service.upload_csv(file)
