import { renderHook, waitFor, act } from "@testing-library/react";
import { createWrapper } from "@/test/wrapper";
import {
  useCreateSequence,
  useDeleteSequence,
  useSequence,
  useSequences,
  useUpdateSequence,
} from "./hooks";
import {
  createSequence,
  deleteSequence,
  fetchSequence,
  fetchSequences,
  updateSequence,
} from "./api";

vi.mock("./api");

describe("sequences hooks", () => {
  afterEach(() => vi.restoreAllMocks());

  describe("useSequences", () => {
    it("returns sequences list", async () => {
      const mockData = [{ id: 1, name: "Seq 1", step_count: 2 }];
      vi.mocked(fetchSequences).mockResolvedValueOnce(mockData as any);

      const { wrapper } = createWrapper();
      const { result } = renderHook(() => useSequences(), { wrapper });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(result.current.data).toEqual(mockData);
    });
  });

  describe("useSequence", () => {
    it("fetches a single sequence by id", async () => {
      const mockData = { id: 5, name: "Seq 5", steps: [] };
      vi.mocked(fetchSequence).mockResolvedValueOnce(mockData as any);

      const { wrapper } = createWrapper();
      const { result } = renderHook(() => useSequence(5), { wrapper });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(fetchSequence).toHaveBeenCalledWith(5);
      expect(result.current.data).toEqual(mockData);
    });

    it("is disabled when id is 0", () => {
      const { wrapper } = createWrapper();
      const { result } = renderHook(() => useSequence(0), { wrapper });

      expect(result.current.fetchStatus).toBe("idle");
    });
  });

  describe("useCreateSequence", () => {
    it("calls createSequence and invalidates sequences cache", async () => {
      const newSeq = { id: 10, name: "New", steps: [] };
      vi.mocked(createSequence).mockResolvedValueOnce(newSeq as any);

      const { wrapper, queryClient } = createWrapper();
      queryClient.setQueryData(["sequences"], []);

      const { result } = renderHook(() => useCreateSequence(), { wrapper });

      await act(async () => {
        await result.current.mutateAsync({
          name: "New",
          steps: [{ subject: "Hi", body: "Hello", delay_minutes: 0 }],
        });
      });

      expect(createSequence).toHaveBeenCalledWith({
        name: "New",
        steps: [{ subject: "Hi", body: "Hello", delay_minutes: 0 }],
      });
      expect(
        queryClient.getQueryState(["sequences"])?.isInvalidated
      ).toBe(true);
    });
  });

  describe("useUpdateSequence", () => {
    it("calls updateSequence and invalidates both list and detail cache", async () => {
      const updated = { id: 5, name: "Updated", steps: [] };
      vi.mocked(updateSequence).mockResolvedValueOnce(updated as any);

      const { wrapper, queryClient } = createWrapper();
      queryClient.setQueryData(["sequences"], []);
      queryClient.setQueryData(["sequences", 5], { id: 5, name: "Old" });

      const { result } = renderHook(() => useUpdateSequence(), { wrapper });

      await act(async () => {
        await result.current.mutateAsync({
          id: 5,
          data: { name: "Updated" },
        });
      });

      expect(updateSequence).toHaveBeenCalledWith(5, { name: "Updated" });
      expect(
        queryClient.getQueryState(["sequences"])?.isInvalidated
      ).toBe(true);
      expect(
        queryClient.getQueryState(["sequences", 5])?.isInvalidated
      ).toBe(true);
    });
  });

  describe("useDeleteSequence", () => {
    it("calls deleteSequence and invalidates sequences cache", async () => {
      vi.mocked(deleteSequence).mockResolvedValueOnce();

      const { wrapper, queryClient } = createWrapper();
      queryClient.setQueryData(["sequences"], [{ id: 3 }]);

      const { result } = renderHook(() => useDeleteSequence(), { wrapper });

      await act(async () => {
        await result.current.mutateAsync(3);
      });

      expect(deleteSequence).toHaveBeenCalledWith(3);
      expect(
        queryClient.getQueryState(["sequences"])?.isInvalidated
      ).toBe(true);
    });
  });
});
