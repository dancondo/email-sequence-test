import { renderHook, waitFor, act } from "@testing-library/react";
import { createWrapper } from "@/test/wrapper";
import { useCandidate, useCandidates, useUploadCandidates } from "./hooks";
import { fetchCandidate, fetchCandidates, uploadCandidates } from "./api";

vi.mock("./api");

describe("candidates hooks", () => {
  afterEach(() => vi.restoreAllMocks());

  describe("useUploadCandidates", () => {
    it("calls uploadCandidates with file", async () => {
      const mockResult = {
        total_rows: 1,
        candidates_created: 1,
        candidates_existing: 0,
        candidates: [],
        errors: [],
      };
      vi.mocked(uploadCandidates).mockResolvedValueOnce(mockResult);

      const { wrapper } = createWrapper();
      const { result } = renderHook(() => useUploadCandidates(), { wrapper });

      const file = new File(["data"], "test.csv");
      await act(async () => {
        const data = await result.current.mutateAsync(file);
        expect(data).toEqual(mockResult);
      });

      expect(uploadCandidates).toHaveBeenCalledWith(file);
    });
  });

  describe("useCandidates", () => {
    it("fetches candidates without listIds", async () => {
      const mockData = [{ id: 1, email: "a@test.com", run_count: 0 }];
      vi.mocked(fetchCandidates).mockResolvedValueOnce(mockData as any);

      const { wrapper } = createWrapper();
      const { result } = renderHook(() => useCandidates(), { wrapper });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(fetchCandidates).toHaveBeenCalledWith(undefined);
      expect(result.current.data).toEqual(mockData);
    });

    it("fetches candidates with listIds", async () => {
      const mockData = [{ id: 2, email: "b@test.com", run_count: 1 }];
      vi.mocked(fetchCandidates).mockResolvedValueOnce(mockData as any);

      const { wrapper } = createWrapper();
      const { result } = renderHook(() => useCandidates([1, 2]), { wrapper });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(fetchCandidates).toHaveBeenCalledWith([1, 2]);
    });
  });

  describe("useCandidate", () => {
    it("fetches a single candidate", async () => {
      const mockData = { id: 5, email: "c@test.com", name: "Charlie", runs: [] };
      vi.mocked(fetchCandidate).mockResolvedValueOnce(mockData as any);

      const { wrapper } = createWrapper();
      const { result } = renderHook(() => useCandidate(5), { wrapper });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(fetchCandidate).toHaveBeenCalledWith(5);
      expect(result.current.data).toEqual(mockData);
    });

    it("is disabled when candidateId is 0", () => {
      const { wrapper } = createWrapper();
      const { result } = renderHook(() => useCandidate(0), { wrapper });

      expect(result.current.fetchStatus).toBe("idle");
    });
  });
});
