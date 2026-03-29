import apiClient from "@/api/client";
import { assignCandidatesToList, fetchCandidateLists } from "./api";

vi.mock("@/api/client");

describe("candidate-lists api", () => {
  afterEach(() => vi.restoreAllMocks());

  it("fetchCandidateLists calls GET /api/candidate-lists", async () => {
    const mockData = [{ id: 1, name: "List A" }];
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockData });

    const result = await fetchCandidateLists();

    expect(apiClient.get).toHaveBeenCalledWith("/api/candidate-lists");
    expect(result).toEqual(mockData);
  });

  it("assignCandidatesToList sends correct snake_case body", async () => {
    const mockData = { id: 1, name: "List A" };
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: mockData });

    const result = await assignCandidatesToList({
      listId: 1,
      listName: "List A",
      candidateIds: [10, 20],
    });

    expect(apiClient.post).toHaveBeenCalledWith(
      "/api/candidate-lists/assign",
      {
        list_id: 1,
        list_name: "List A",
        candidate_ids: [10, 20],
      }
    );
    expect(result).toEqual(mockData);
  });

  it("assignCandidatesToList handles undefined optional fields", async () => {
    const mockData = { id: 2, name: "New List" };
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: mockData });

    await assignCandidatesToList({ candidateIds: [5] });

    expect(apiClient.post).toHaveBeenCalledWith(
      "/api/candidate-lists/assign",
      {
        list_id: undefined,
        list_name: undefined,
        candidate_ids: [5],
      }
    );
  });
});
