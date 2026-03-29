import { useQuery } from "@tanstack/react-query";
import { fetchCandidateLists } from "./api";

export function useCandidateLists() {
  return useQuery({
    queryKey: ["candidate-lists"],
    queryFn: fetchCandidateLists,
  });
}
