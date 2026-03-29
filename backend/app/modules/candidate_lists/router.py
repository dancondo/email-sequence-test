from fastapi import APIRouter, Depends

from app.modules.candidate_lists.dependencies import get_candidate_list_service
from app.modules.candidate_lists.schemas import (
    AssignCandidatesRequest,
    CandidateListResponse,
)
from app.modules.candidate_lists.service import CandidateListService

router = APIRouter(prefix="/api/candidate-lists", tags=["candidate-lists"])


@router.get("", response_model=list[CandidateListResponse])
async def list_candidate_lists(
    service: CandidateListService = Depends(get_candidate_list_service),
):
    return await service.get_all_lists()


@router.post("/assign", response_model=CandidateListResponse, status_code=201)
async def assign_candidates_to_list(
    body: AssignCandidatesRequest,
    service: CandidateListService = Depends(get_candidate_list_service),
):
    candidate_list = await service.get_or_create_list(
        list_id=body.list_id, list_name=body.list_name
    )
    await service.add_candidates_to_list(candidate_list.id, body.candidate_ids)
    return candidate_list
