import apiClient from "@/api/client";
import { fetchCandidate, fetchCandidates, uploadCandidates } from "./api";

vi.mock("@/api/client");

describe("candidates api", () => {
  afterEach(() => vi.restoreAllMocks());

  it("uploadCandidates sends FormData with multipart header", async () => {
    const mockResult = {
      total_rows: 2,
      candidates_created: 2,
      candidates_existing: 0,
      candidates: [],
      errors: [],
    };
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: mockResult });

    const file = new File(["name,email\nJohn,john@test.com"], "test.csv", {
      type: "text/csv",
    });
    const result = await uploadCandidates(file);

    expect(apiClient.post).toHaveBeenCalledWith(
      "/api/candidates/upload",
      expect.any(FormData),
      { headers: { "Content-Type": "multipart/form-data" } }
    );
    const formData = vi.mocked(apiClient.post).mock.calls[0][1] as FormData;
    expect(formData.get("file")).toBe(file);
    expect(result).toEqual(mockResult);
  });

  it("fetchCandidates without listIds calls GET /api/candidates", async () => {
    const mockData = [{ id: 1, email: "a@test.com", name: null, run_count: 0 }];
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockData });

    const result = await fetchCandidates();

    expect(apiClient.get).toHaveBeenCalledWith("/api/candidates");
    expect(result).toEqual(mockData);
  });

  it("fetchCandidates with listIds appends query params", async () => {
    const mockData = [{ id: 1, email: "a@test.com", name: null, run_count: 0 }];
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockData });

    const result = await fetchCandidates([1, 2]);

    expect(apiClient.get).toHaveBeenCalledWith(
      "/api/candidates?list_ids=1&list_ids=2"
    );
    expect(result).toEqual(mockData);
  });

  it("fetchCandidates with empty listIds calls without query params", async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: [] });

    await fetchCandidates([]);

    expect(apiClient.get).toHaveBeenCalledWith("/api/candidates");
  });

  it("fetchCandidate calls GET /api/candidates/:id", async () => {
    const mockData = { id: 5, email: "b@test.com", name: "Bob", runs: [] };
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockData });

    const result = await fetchCandidate(5);

    expect(apiClient.get).toHaveBeenCalledWith("/api/candidates/5");
    expect(result).toEqual(mockData);
  });
});
