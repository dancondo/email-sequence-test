import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createSequence,
  deleteSequence,
  fetchSequence,
  fetchSequences,
  updateSequence,
} from "./api";
import { CreateSequencePayload, UpdateSequencePayload } from "./types";

export function useSequences() {
  return useQuery({
    queryKey: ["sequences"],
    queryFn: fetchSequences,
  });
}

export function useSequence(id: number) {
  return useQuery({
    queryKey: ["sequences", id],
    queryFn: () => fetchSequence(id),
    enabled: !!id,
  });
}

export function useCreateSequence() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateSequencePayload) => createSequence(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sequences"] });
    },
  });
}

export function useUpdateSequence() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateSequencePayload }) =>
      updateSequence(id, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["sequences"] });
      queryClient.invalidateQueries({
        queryKey: ["sequences", variables.id],
      });
    },
  });
}

export function useDeleteSequence() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteSequence(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sequences"] });
    },
  });
}
