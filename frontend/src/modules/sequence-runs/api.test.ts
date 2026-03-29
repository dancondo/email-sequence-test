import apiClient from "@/api/client";
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

vi.mock("@/api/client");

describe("sequence-runs api", () => {
  afterEach(() => vi.restoreAllMocks());

  it("createRun calls POST /api/sequences/:seqId/runs", async () => {
    const mockData = { id: 1, sequence_id: 10, status: "draft" };
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: mockData });

    const result = await createRun(10);

    expect(apiClient.post).toHaveBeenCalledWith("/api/sequences/10/runs");
    expect(result).toEqual(mockData);
  });

  it("fetchRuns calls GET /api/sequences/:seqId/runs", async () => {
    const mockData = [{ id: 1, sequence_id: 10, status: "draft" }];
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockData });

    const result = await fetchRuns(10);

    expect(apiClient.get).toHaveBeenCalledWith("/api/sequences/10/runs");
    expect(result).toEqual(mockData);
  });

  it("fetchRun calls GET /api/sequences/:seqId/runs/:runId", async () => {
    const mockData = { id: 5, sequence_id: 10, status: "active" };
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockData });

    const result = await fetchRun(10, 5);

    expect(apiClient.get).toHaveBeenCalledWith("/api/sequences/10/runs/5");
    expect(result).toEqual(mockData);
  });

  it("deleteRun calls DELETE /api/sequences/:seqId/runs/:runId", async () => {
    vi.mocked(apiClient.delete).mockResolvedValueOnce({ data: undefined });

    await deleteRun(10, 5);

    expect(apiClient.delete).toHaveBeenCalledWith("/api/sequences/10/runs/5");
  });

  it("startRun calls POST /api/sequences/:seqId/runs/:runId/start", async () => {
    const mockData = { message: "Started", enrollments_started: 3 };
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: mockData });

    const result = await startRun(10, 5);

    expect(apiClient.post).toHaveBeenCalledWith(
      "/api/sequences/10/runs/5/start"
    );
    expect(result).toEqual(mockData);
  });

  it("addCandidatesToRun sends candidate_ids in body", async () => {
    const mockData = { added: 2, already_enrolled: 0, not_found: 0 };
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: mockData });

    const result = await addCandidatesToRun(10, 5, [1, 2]);

    expect(apiClient.post).toHaveBeenCalledWith(
      "/api/sequences/10/runs/5/candidates",
      { candidate_ids: [1, 2] }
    );
    expect(result).toEqual(mockData);
  });

  it("removeCandidateFromRun calls DELETE with candidate id in URL", async () => {
    vi.mocked(apiClient.delete).mockResolvedValueOnce({ data: undefined });

    await removeCandidateFromRun(10, 5, 3);

    expect(apiClient.delete).toHaveBeenCalledWith(
      "/api/sequences/10/runs/5/candidates/3"
    );
  });

  it("fetchCandidates calls GET /api/sequences/:seqId/runs/:runId/candidates", async () => {
    const mockData = [{ id: 1, candidate_id: 3, status: "active" }];
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockData });

    const result = await fetchCandidates(10, 5);

    expect(apiClient.get).toHaveBeenCalledWith(
      "/api/sequences/10/runs/5/candidates"
    );
    expect(result).toEqual(mockData);
  });

  it("sendReply sends body in POST payload", async () => {
    const mockData = { message: "Reply sent", event: { id: 1 } };
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: mockData });

    const result = await sendReply(10, 5, 3, "Thanks for the referral!");

    expect(apiClient.post).toHaveBeenCalledWith(
      "/api/sequences/10/runs/5/candidates/3/reply",
      { body: "Thanks for the referral!" }
    );
    expect(result).toEqual(mockData);
  });

  it("fetchRunMetrics calls GET /api/sequences/:seqId/runs/:runId/metrics", async () => {
    const mockData = {
      total_sent: 10,
      total_replies: 3,
      reply_rate: 0.3,
      total_interested: 1,
      interest_rate: 0.1,
    };
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockData });

    const result = await fetchRunMetrics(10, 5);

    expect(apiClient.get).toHaveBeenCalledWith(
      "/api/sequences/10/runs/5/metrics"
    );
    expect(result).toEqual(mockData);
  });

  it("fetchAllSequenceRunMetrics calls GET /api/sequences/:seqId/runs/metrics", async () => {
    const mockData = {
      total_sent: 50,
      total_replies: 10,
      reply_rate: 0.2,
      total_interested: 5,
      interest_rate: 0.1,
    };
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockData });

    const result = await fetchAllSequenceRunMetrics(10);

    expect(apiClient.get).toHaveBeenCalledWith(
      "/api/sequences/10/runs/metrics"
    );
    expect(result).toEqual(mockData);
  });

  it("fetchCandidateTimeline calls GET with full candidate path", async () => {
    const mockData = { candidate: { id: 3 }, events: [] };
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockData });

    const result = await fetchCandidateTimeline(10, 5, 3);

    expect(apiClient.get).toHaveBeenCalledWith(
      "/api/sequences/10/runs/5/candidates/3/timeline"
    );
    expect(result).toEqual(mockData);
  });
});
