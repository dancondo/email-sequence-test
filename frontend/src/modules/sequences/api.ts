import apiClient from "@/api/client";
import {
  CreateSequencePayload,
  Sequence,
  SequenceListItem,
  UpdateSequencePayload,
} from "./types";

export async function fetchSequences(): Promise<SequenceListItem[]> {
  const { data } = await apiClient.get<SequenceListItem[]>("/api/sequences");
  return data;
}

export async function fetchSequence(id: number): Promise<Sequence> {
  const { data } = await apiClient.get<Sequence>(`/api/sequences/${id}`);
  return data;
}

export async function createSequence(
  payload: CreateSequencePayload
): Promise<Sequence> {
  const { data } = await apiClient.post<Sequence>("/api/sequences", payload);
  return data;
}

export async function updateSequence(
  id: number,
  payload: UpdateSequencePayload
): Promise<Sequence> {
  const { data } = await apiClient.put<Sequence>(
    `/api/sequences/${id}`,
    payload
  );
  return data;
}

export async function deleteSequence(id: number): Promise<void> {
  await apiClient.delete(`/api/sequences/${id}`);
}
