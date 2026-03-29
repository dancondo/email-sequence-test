import apiClient from "@/api/client";
import { disconnectAccount, fetchAuthUrl, fetchConnectionStatus } from "./api";

vi.mock("@/api/client");

describe("email-integration api", () => {
  afterEach(() => vi.restoreAllMocks());

  it("fetchAuthUrl calls GET /api/email-integration/auth-url", async () => {
    const mockResponse = { auth_url: "https://oauth.example.com/auth" };
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockResponse });

    const result = await fetchAuthUrl();

    expect(apiClient.get).toHaveBeenCalledWith(
      "/api/email-integration/auth-url"
    );
    expect(result).toEqual(mockResponse);
  });

  it("fetchConnectionStatus calls GET /api/email-integration/status", async () => {
    const mockResponse = { connected: true, account: { id: 1, email: "test@example.com" } };
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockResponse });

    const result = await fetchConnectionStatus();

    expect(apiClient.get).toHaveBeenCalledWith("/api/email-integration/status");
    expect(result).toEqual(mockResponse);
  });

  it("disconnectAccount calls DELETE /api/email-integration/disconnect", async () => {
    vi.mocked(apiClient.delete).mockResolvedValueOnce({ data: undefined });

    await disconnectAccount();

    expect(apiClient.delete).toHaveBeenCalledWith(
      "/api/email-integration/disconnect"
    );
  });
});
