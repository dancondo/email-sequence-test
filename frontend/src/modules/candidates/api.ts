import apiClient from "@/api/client";
import { CandidateDetail, CandidateWithRunCount, CsvUploadResult } from "./types";

export async function uploadCandidates(file: File): Promise<CsvUploadResult> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await apiClient.post<CsvUploadResult>(
    "/api/candidates/upload",
    formData,
    { headers: { "Content-Type": "multipart/form-data" } }
  );
  return data;
}

export async function fetchCandidates(
  listIds?: number[]
): Promise<CandidateWithRunCount[]> {
  const params = new URLSearchParams();
  if (listIds && listIds.length > 0) {
    listIds.forEach((id) => params.append("list_ids", String(id)));
  }
  const query = params.toString();
  const { data } = await apiClient.get<CandidateWithRunCount[]>(
    `/api/candidates${query ? `?${query}` : ""}`
  );
  return data;
}

export async function fetchCandidate(
  candidateId: number
): Promise<CandidateDetail> {
  const { data } = await apiClient.get<CandidateDetail>(
    `/api/candidates/${candidateId}`
  );
  return data;
}
