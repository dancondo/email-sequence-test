export interface EmailAccount {
  id: number;
  grant_id: string;
  email: string;
  provider: string;
  integration_provider: string;
  connected_at: string;
  is_active: boolean;
}

export interface ConnectionStatusResponse {
  connected: boolean;
  account: EmailAccount | null;
}

export interface AuthUrlResponse {
  auth_url: string;
}
