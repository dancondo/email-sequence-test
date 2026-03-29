import { renderHook, waitFor, act } from "@testing-library/react";
import { createWrapper } from "@/test/wrapper";
import {
  useAddCandidates,
  useAllSequenceRunMetrics,
  useCandidates,
  useCandidateTimeline,
  useCreateRun,
  useDeleteRun,
  useRemoveCandidate,
  useRun,
  useRunMetrics,
  useRuns,
  useSendReply,
  useStartRun,
} from "./hooks";
import {
  addCandidatesToRun,
  createRun,
  deleteRun,
  fetchAllSequenceRunMetrics,
  fetchCandidates,
  fetchCandidateTimeline,
  fetchRun,
  fetchRunMetrics,
  fetchRuns,
  removeCandidateFromRun,
  sendReply,
  startRun,
} from "./api";

vi.mock("./api");

describe("sequence-runs hooks", () => {
  afterEach(() => vi.restoreAllMocks());

  // ── Query hooks ──

  describe("useRuns", () => {
    it("fetches runs for a sequence", async () => {
      const mockData = [{ id: 1, sequence_id: 10, status: "draft" }];
      vi.mocked(fetchRuns).mockResolvedValueOnce(mockData as any);

      const { wrapper } = createWrapper();
      const { result } = renderHook(() => useRuns(10), { wrapper });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(fetchRuns).toHaveBeenCalledWith(10);
      expect(result.current.data).toEqual(mockData);
    });

    it("is disabled when sequenceId is 0", () => {
      const { wrapper } = createWrapper();
      const { result } = renderHook(() => useRuns(0), { wrapper });
      expect(result.current.fetchStatus).toBe("idle");
    });
  });

  describe("useRun", () => {
    it("fetches a single run", async () => {
      const mockData = { id: 5, sequence_id: 10, status: "active" };
      vi.mocked(fetchRun).mockResolvedValueOnce(mockData as any);

      const { wrapper } = createWrapper();
      const { result } = renderHook(() => useRun(10, 5), { wrapper });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(fetchRun).toHaveBeenCalledWith(10, 5);
    });

    it("is disabled when runId is 0", () => {
      const { wrapper } = createWrapper();
      const { result } = renderHook(() => useRun(10, 0), { wrapper });
      expect(result.current.fetchStatus).toBe("idle");
    });
  });

  describe("useRunMetrics", () => {
    it("fetches run metrics", async () => {
      const mockData = { total_sent: 10, total_replies: 3, reply_rate: 0.3, total_interested: 1, interest_rate: 0.1 };
      vi.mocked(fetchRunMetrics).mockResolvedValueOnce(mockData);

      const { wrapper } = createWrapper();
      const { result } = renderHook(() => useRunMetrics(10, 5), { wrapper });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(fetchRunMetrics).toHaveBeenCalledWith(10, 5);
      expect(result.current.data).toEqual(mockData);
    });
  });

  describe("useAllSequenceRunMetrics", () => {
    it("fetches aggregate metrics for a sequence", async () => {
      const mockData = { total_sent: 50, total_replies: 10, reply_rate: 0.2, total_interested: 5, interest_rate: 0.1 };
      vi.mocked(fetchAllSequenceRunMetrics).mockResolvedValueOnce(mockData);

      const { wrapper } = createWrapper();
      const { result } = renderHook(() => useAllSequenceRunMetrics(10), { wrapper });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(fetchAllSequenceRunMetrics).toHaveBeenCalledWith(10);
    });
  });

  describe("useCandidates", () => {
    it("fetches candidates for a run", async () => {
      const mockData = [{ id: 1, candidate_id: 3, status: "active" }];
      vi.mocked(fetchCandidates).mockResolvedValueOnce(mockData as any);

      const { wrapper } = createWrapper();
      const { result } = renderHook(() => useCandidates(10, 5), { wrapper });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(fetchCandidates).toHaveBeenCalledWith(10, 5);
    });
  });

  describe("useCandidateTimeline", () => {
    it("fetches candidate timeline", async () => {
      const mockData = { candidate: { id: 3 }, events: [] };
      vi.mocked(fetchCandidateTimeline).mockResolvedValueOnce(mockData as any);

      const { wrapper } = createWrapper();
      const { result } = renderHook(() => useCandidateTimeline(10, 5, 3), { wrapper });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(fetchCandidateTimeline).toHaveBeenCalledWith(10, 5, 3);
    });

    it("is disabled when candidateId is 0", () => {
      const { wrapper } = createWrapper();
      const { result } = renderHook(() => useCandidateTimeline(10, 5, 0), { wrapper });
      expect(result.current.fetchStatus).toBe("idle");
    });
  });

  // ── Mutation hooks ──

  describe("useCreateRun", () => {
    it("calls createRun and invalidates runs cache", async () => {
      const mockData = { id: 1, sequence_id: 10, status: "draft" };
      vi.mocked(createRun).mockResolvedValueOnce(mockData as any);

      const { wrapper, queryClient } = createWrapper();
      queryClient.setQueryData(["sequence-runs", 10], []);

      const { result } = renderHook(() => useCreateRun(10), { wrapper });

      await act(async () => {
        await result.current.mutateAsync();
      });

      expect(createRun).toHaveBeenCalledWith(10);
      expect(
        queryClient.getQueryState(["sequence-runs", 10])?.isInvalidated
      ).toBe(true);
    });
  });

  describe("useDeleteRun", () => {
    it("calls deleteRun and invalidates runs cache", async () => {
      vi.mocked(deleteRun).mockResolvedValueOnce();

      const { wrapper, queryClient } = createWrapper();
      queryClient.setQueryData(["sequence-runs", 10], [{ id: 5 }]);

      const { result } = renderHook(() => useDeleteRun(10, 5), { wrapper });

      await act(async () => {
        await result.current.mutateAsync();
      });

      expect(deleteRun).toHaveBeenCalledWith(10, 5);
      expect(
        queryClient.getQueryState(["sequence-runs", 10])?.isInvalidated
      ).toBe(true);
    });
  });

  describe("useStartRun", () => {
    it("calls startRun and invalidates both run detail and runs list", async () => {
      const mockData = { message: "Started", enrollments_started: 3 };
      vi.mocked(startRun).mockResolvedValueOnce(mockData);

      const { wrapper, queryClient } = createWrapper();
      queryClient.setQueryData(["sequence-runs", 10], []);
      queryClient.setQueryData(["sequence-runs", 10, 5], { id: 5, status: "draft" });

      const { result } = renderHook(() => useStartRun(10, 5), { wrapper });

      await act(async () => {
        await result.current.mutateAsync();
      });

      expect(startRun).toHaveBeenCalledWith(10, 5);
      expect(
        queryClient.getQueryState(["sequence-runs", 10])?.isInvalidated
      ).toBe(true);
      expect(
        queryClient.getQueryState(["sequence-runs", 10, 5])?.isInvalidated
      ).toBe(true);
    });
  });

  describe("useAddCandidates", () => {
    it("calls addCandidatesToRun and invalidates run detail cache", async () => {
      const mockData = { added: 2, already_enrolled: 0, not_found: 0 };
      vi.mocked(addCandidatesToRun).mockResolvedValueOnce(mockData);

      const { wrapper, queryClient } = createWrapper();
      queryClient.setQueryData(["sequence-runs", 10, 5], { id: 5 });

      const { result } = renderHook(() => useAddCandidates(10, 5), { wrapper });

      await act(async () => {
        await result.current.mutateAsync([1, 2]);
      });

      expect(addCandidatesToRun).toHaveBeenCalledWith(10, 5, [1, 2]);
      expect(
        queryClient.getQueryState(["sequence-runs", 10, 5])?.isInvalidated
      ).toBe(true);
    });
  });

  describe("useRemoveCandidate", () => {
    it("calls removeCandidateFromRun and invalidates run detail cache", async () => {
      vi.mocked(removeCandidateFromRun).mockResolvedValueOnce();

      const { wrapper, queryClient } = createWrapper();
      queryClient.setQueryData(["sequence-runs", 10, 5], { id: 5 });

      const { result } = renderHook(() => useRemoveCandidate(10, 5), { wrapper });

      await act(async () => {
        await result.current.mutateAsync(3);
      });

      expect(removeCandidateFromRun).toHaveBeenCalledWith(10, 5, 3);
      expect(
        queryClient.getQueryState(["sequence-runs", 10, 5])?.isInvalidated
      ).toBe(true);
    });
  });

  describe("useSendReply", () => {
    it("calls sendReply and invalidates timeline cache", async () => {
      const mockData = { message: "Reply sent", event: { id: 1 } };
      vi.mocked(sendReply).mockResolvedValueOnce(mockData as any);

      const { wrapper, queryClient } = createWrapper();
      queryClient.setQueryData(["candidate-timeline", 10, 5, 3], {
        candidate: { id: 3 },
        events: [],
      });

      const { result } = renderHook(() => useSendReply(10, 5, 3), { wrapper });

      await act(async () => {
        await result.current.mutateAsync("Thanks!");
      });

      expect(sendReply).toHaveBeenCalledWith(10, 5, 3, "Thanks!");
      expect(
        queryClient.getQueryState(["candidate-timeline", 10, 5, 3])?.isInvalidated
      ).toBe(true);
    });
  });
});
