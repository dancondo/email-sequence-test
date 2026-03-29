import apiClient from "@/api/client";
import { AssignCandidatesParams, CandidateList } from "./types";

export async function fetchCandidateLists(): Promise<CandidateList[]> {
  const { data } = await apiClient.get<CandidateList[]>(
    "/api/candidate-lists"
  );
  return data;
}

export async function assignCandidatesToList(
  params: AssignCandidatesParams
): Promise<CandidateList> {
  const { data } = await apiClient.post<CandidateList>(
    "/api/candidate-lists/assign",
    {
      list_id: params.listId,
      list_name: params.listName,
      candidate_ids: params.candidateIds,
    }
  );
  return data;
}
