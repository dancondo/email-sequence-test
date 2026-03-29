import apiClient from "@/api/client";
import {
  AddCandidatesResult,
  CandidateTimeline,
  Metrics,
  SendReplyResult,
  SequenceRun,
  SequenceRunCandidate,
  SequenceRunDetail,
  SequenceRunListItem,
  SequenceStartResult,
} from "./types";

export async function createRun(sequenceId: number): Promise<SequenceRun> {
  const { data } = await apiClient.post<SequenceRun>(
    `/api/sequences/${sequenceId}/runs`
  );
  return data;
}

export async function fetchRuns(
  sequenceId: number
): Promise<SequenceRunListItem[]> {
  const { data } = await apiClient.get<SequenceRunListItem[]>(
    `/api/sequences/${sequenceId}/runs`
  );
  return data;
}

export async function fetchRun(
  sequenceId: number,
  runId: number
): Promise<SequenceRunDetail> {
  const { data } = await apiClient.get<SequenceRunDetail>(
    `/api/sequences/${sequenceId}/runs/${runId}`
  );
  return data;
}

export async function deleteRun(
  sequenceId: number,
  runId: number
): Promise<void> {
  await apiClient.delete(`/api/sequences/${sequenceId}/runs/${runId}`);
}

export async function startRun(
  sequenceId: number,
  runId: number
): Promise<SequenceStartResult> {
  const { data } = await apiClient.post<SequenceStartResult>(
    `/api/sequences/${sequenceId}/runs/${runId}/start`
  );
  return data;
}

export async function addCandidatesToRun(
  sequenceId: number,
  runId: number,
  candidateIds: number[]
): Promise<AddCandidatesResult> {
  const { data } = await apiClient.post<AddCandidatesResult>(
    `/api/sequences/${sequenceId}/runs/${runId}/candidates`,
    { candidate_ids: candidateIds }
  );
  return data;
}

export async function removeCandidateFromRun(
  sequenceId: number,
  runId: number,
  candidateId: number
): Promise<void> {
  await apiClient.delete(
    `/api/sequences/${sequenceId}/runs/${runId}/candidates/${candidateId}`
  );
}

export async function fetchCandidates(
  sequenceId: number,
  runId: number
): Promise<SequenceRunCandidate[]> {
  const { data } = await apiClient.get<SequenceRunCandidate[]>(
    `/api/sequences/${sequenceId}/runs/${runId}/candidates`
  );
  return data;
}

export async function sendReply(
  sequenceId: number,
  runId: number,
  candidateId: number,
  body: string
): Promise<SendReplyResult> {
  const { data } = await apiClient.post<SendReplyResult>(
    `/api/sequences/${sequenceId}/runs/${runId}/candidates/${candidateId}/reply`,
    { body }
  );
  return data;
}

export async function fetchRunMetrics(
  sequenceId: number,
  runId: number
): Promise<Metrics> {
  const { data } = await apiClient.get<Metrics>(
    `/api/sequences/${sequenceId}/runs/${runId}/metrics`
  );
  return data;
}

export async function fetchAllSequenceRunMetrics(
  sequenceId: number
): Promise<Metrics> {
  const { data } = await apiClient.get<Metrics>(
    `/api/sequences/${sequenceId}/runs/metrics`
  );
  return data;
}

export async function fetchCandidateTimeline(
  sequenceId: number,
  runId: number,
  candidateId: number
): Promise<CandidateTimeline> {
  const { data } = await apiClient.get<CandidateTimeline>(
    `/api/sequences/${sequenceId}/runs/${runId}/candidates/${candidateId}/timeline`
  );
  return data;
}
