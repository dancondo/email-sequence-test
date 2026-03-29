import { useMutation, useQuery } from "@tanstack/react-query";
import { assignCandidatesToList, fetchCandidateLists } from "./api";
import { AssignCandidatesParams } from "./types";

export function useCandidateLists() {
  return useQuery({
    queryKey: ["candidate-lists"],
    queryFn: fetchCandidateLists,
  });
}

export function useAssignCandidatesToList() {
  return useMutation({
    mutationFn: (params: AssignCandidatesParams) =>
      assignCandidatesToList(params),
  });
}
