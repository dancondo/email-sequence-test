import { useMutation, useQuery } from "@tanstack/react-query";
import { fetchCandidate, fetchCandidates, uploadCandidates } from "./api";

export function useUploadCandidates() {
  return useMutation({
    mutationFn: (file: File) => uploadCandidates(file),
  });
}

export function useCandidates(listIds?: number[]) {
  return useQuery({
    queryKey: ["candidates", listIds ?? []],
    queryFn: () => fetchCandidates(listIds),
  });
}

export function useCandidate(candidateId: number) {
  return useQuery({
    queryKey: ["candidate", candidateId],
    queryFn: () => fetchCandidate(candidateId),
    enabled: !!candidateId,
  });
}
