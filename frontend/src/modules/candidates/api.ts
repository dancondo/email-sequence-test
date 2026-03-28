import apiClient from "@/api/client";
import { CsvUploadResult } from "./types";

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
