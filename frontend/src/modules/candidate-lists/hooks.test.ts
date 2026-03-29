import { renderHook, waitFor, act } from "@testing-library/react";
import { createWrapper } from "@/test/wrapper";
import { useCandidateLists, useAssignCandidatesToList } from "./hooks";
import { assignCandidatesToList, fetchCandidateLists } from "./api";

vi.mock("./api");

describe("candidate-lists hooks", () => {
  afterEach(() => vi.restoreAllMocks());

  describe("useCandidateLists", () => {
    it("returns candidate lists", async () => {
      const mockData = [{ id: 1, name: "Engineers" }];
      vi.mocked(fetchCandidateLists).mockResolvedValueOnce(mockData);

      const { wrapper } = createWrapper();
      const { result } = renderHook(() => useCandidateLists(), { wrapper });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(result.current.data).toEqual(mockData);
    });
  });

  describe("useAssignCandidatesToList", () => {
    it("calls assignCandidatesToList with params", async () => {
      const mockResult = { id: 1, name: "Engineers" };
      vi.mocked(assignCandidatesToList).mockResolvedValueOnce(mockResult);

      const { wrapper } = createWrapper();
      const { result } = renderHook(() => useAssignCandidatesToList(), {
        wrapper,
      });

      await act(async () => {
        const data = await result.current.mutateAsync({
          listId: 1,
          candidateIds: [10, 20],
        });
        expect(data).toEqual(mockResult);
      });

      expect(assignCandidatesToList).toHaveBeenCalledWith({
        listId: 1,
        candidateIds: [10, 20],
      });
    });
  });
});
