import apiClient from "@/api/client";
import { CandidateList } from "./types";

export async function fetchCandidateLists(): Promise<CandidateList[]> {
  const { data } = await apiClient.get<CandidateList[]>(
    "/api/candidate-lists"
  );
  return data;
}
