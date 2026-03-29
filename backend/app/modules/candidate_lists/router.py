from fastapi import APIRouter, Depends

from app.modules.candidate_lists.dependencies import get_candidate_list_service
from app.modules.candidate_lists.schemas import CandidateListResponse
from app.modules.candidate_lists.service import CandidateListService

router = APIRouter(prefix="/api/candidate-lists", tags=["candidate-lists"])


@router.get("", response_model=list[CandidateListResponse])
async def list_candidate_lists(
    service: CandidateListService = Depends(get_candidate_list_service),
):
    return await service.get_all_lists()
