import { useMutation } from "@tanstack/react-query";
import { uploadCandidates } from "./api";
import { CsvUploadParams } from "./types";

export function useUploadCandidates() {
  return useMutation({
    mutationFn: (params: CsvUploadParams) => uploadCandidates(params),
  });
}
