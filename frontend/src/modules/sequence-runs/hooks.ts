import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  addCandidatesToRun,
  createRun,
  deleteRun,
  fetchAllSequenceRunMetrics,
  fetchCandidates,
  fetchCandidateTimeline,
  fetchRun,
  fetchRunMetrics,
  fetchRuns,
  removeCandidateFromRun,
  sendReply,
  startRun,
} from "./api";

export function useRuns(sequenceId: number) {
  return useQuery({
    queryKey: ["sequence-runs", sequenceId],
    queryFn: () => fetchRuns(sequenceId),
    enabled: !!sequenceId,
  });
}

export function useRun(sequenceId: number, runId: number) {
  return useQuery({
    queryKey: ["sequence-runs", sequenceId, runId],
    queryFn: () => fetchRun(sequenceId, runId),
    enabled: !!sequenceId && !!runId,
  });
}

export function useCreateRun(sequenceId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => createRun(sequenceId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["sequence-runs", sequenceId],
      });
    },
  });
}

export function useDeleteRun(sequenceId: number, runId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => deleteRun(sequenceId, runId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["sequence-runs", sequenceId],
      });
    },
  });
}

export function useStartRun(sequenceId: number, runId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => startRun(sequenceId, runId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["sequence-runs", sequenceId, runId],
      });
      queryClient.invalidateQueries({
        queryKey: ["sequence-runs", sequenceId],
      });
    },
  });
}

export function useAddCandidates(sequenceId: number, runId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (candidateIds: number[]) =>
      addCandidatesToRun(sequenceId, runId, candidateIds),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["sequence-runs", sequenceId, runId],
      });
    },
  });
}

export function useRemoveCandidate(sequenceId: number, runId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (candidateId: number) =>
      removeCandidateFromRun(sequenceId, runId, candidateId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["sequence-runs", sequenceId, runId],
      });
    },
  });
}

export function useRunMetrics(sequenceId: number, runId: number) {
  return useQuery({
    queryKey: ["run-metrics", sequenceId, runId],
    queryFn: () => fetchRunMetrics(sequenceId, runId),
    enabled: !!sequenceId && !!runId,
  });
}

export function useAllSequenceRunMetrics(sequenceId: number) {
  return useQuery({
    queryKey: ["sequence-run-metrics", sequenceId],
    queryFn: () => fetchAllSequenceRunMetrics(sequenceId),
    enabled: !!sequenceId,
  });
}

export function useCandidates(sequenceId: number, runId: number) {
  return useQuery({
    queryKey: ["sequence-run-candidates", sequenceId, runId],
    queryFn: () => fetchCandidates(sequenceId, runId),
    enabled: !!sequenceId && !!runId,
  });
}

export function useSendReply(
  sequenceId: number,
  runId: number,
  candidateId: number
) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: string) => sendReply(sequenceId, runId, candidateId, body),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["candidate-timeline", sequenceId, runId, candidateId],
      });
    },
  });
}

export function useCandidateTimeline(
  sequenceId: number,
  runId: number,
  candidateId: number
) {
  return useQuery({
    queryKey: ["candidate-timeline", sequenceId, runId, candidateId],
    queryFn: () => fetchCandidateTimeline(sequenceId, runId, candidateId),
    enabled: !!sequenceId && !!runId && !!candidateId,
  });
}
