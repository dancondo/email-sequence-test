import apiClient from "@/api/client";
import { CsvUploadParams, CsvUploadResult } from "./types";

export async function uploadCandidates(
  params: CsvUploadParams
): Promise<CsvUploadResult> {
  const formData = new FormData();
  formData.append("file", params.file);
  if (params.listId != null) {
    formData.append("list_id", String(params.listId));
  }
  if (params.listName) {
    formData.append("list_name", params.listName);
  }
  const { data } = await apiClient.post<CsvUploadResult>(
    "/api/candidates/upload",
    formData,
    { headers: { "Content-Type": "multipart/form-data" } }
  );
  return data;
}
