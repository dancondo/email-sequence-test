import apiClient from "@/api/client";
import { fetchHealth } from "./api";

vi.mock("@/api/client");

describe("health api", () => {
  afterEach(() => vi.restoreAllMocks());

  it("fetchHealth calls GET /api/health and returns data", async () => {
    const mockResponse = { status: "healthy", database: "connected" };
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockResponse });

    const result = await fetchHealth();

    expect(apiClient.get).toHaveBeenCalledWith("/api/health");
    expect(result).toEqual(mockResponse);
  });
});
