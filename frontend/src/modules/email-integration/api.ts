import apiClient from "@/api/client";
import { AuthUrlResponse, ConnectionStatusResponse } from "./types";

export async function fetchAuthUrl(): Promise<AuthUrlResponse> {
  const { data } = await apiClient.get<AuthUrlResponse>(
    "/api/email-integration/auth-url"
  );
  return data;
}

export async function fetchConnectionStatus(): Promise<ConnectionStatusResponse> {
  const { data } = await apiClient.get<ConnectionStatusResponse>(
    "/api/email-integration/status"
  );
  return data;
}

export async function disconnectAccount(): Promise<void> {
  await apiClient.delete("/api/email-integration/disconnect");
}
