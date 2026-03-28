import apiClient from "@/api/client";
import { HealthResponse } from "./types";

export async function fetchHealth(): Promise<HealthResponse> {
  const { data } = await apiClient.get<HealthResponse>("/api/health");
  return data;
}
