import { useMutation } from "@tanstack/react-query";
import { uploadCandidates } from "./api";

export function useUploadCandidates() {
  return useMutation({
    mutationFn: (file: File) => uploadCandidates(file),
  });
}
