import apiClient from "@/api/client";
import {
  createSequence,
  deleteSequence,
  fetchSequence,
  fetchSequences,
  updateSequence,
} from "./api";
import { CreateSequencePayload, UpdateSequencePayload } from "./types";

vi.mock("@/api/client");

describe("sequences api", () => {
  afterEach(() => vi.restoreAllMocks());

  it("fetchSequences calls GET /api/sequences", async () => {
    const mockData = [{ id: 1, name: "Seq 1", step_count: 2, run_count: 0 }];
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockData });

    const result = await fetchSequences();

    expect(apiClient.get).toHaveBeenCalledWith("/api/sequences");
    expect(result).toEqual(mockData);
  });

  it("fetchSequence calls GET /api/sequences/:id", async () => {
    const mockData = { id: 42, name: "Seq 42", steps: [] };
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockData });

    const result = await fetchSequence(42);

    expect(apiClient.get).toHaveBeenCalledWith("/api/sequences/42");
    expect(result).toEqual(mockData);
  });

  it("createSequence calls POST /api/sequences with payload", async () => {
    const payload: CreateSequencePayload = {
      name: "New Seq",
      steps: [{ subject: "Hi", body: "<p>Hello</p>", delay_minutes: 0 }],
    };
    const mockData = { id: 1, ...payload, steps: [] };
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: mockData });

    const result = await createSequence(payload);

    expect(apiClient.post).toHaveBeenCalledWith("/api/sequences", payload);
    expect(result).toEqual(mockData);
  });

  it("updateSequence calls PUT /api/sequences/:id with payload", async () => {
    const payload: UpdateSequencePayload = { name: "Updated" };
    const mockData = { id: 5, name: "Updated", steps: [] };
    vi.mocked(apiClient.put).mockResolvedValueOnce({ data: mockData });

    const result = await updateSequence(5, payload);

    expect(apiClient.put).toHaveBeenCalledWith("/api/sequences/5", payload);
    expect(result).toEqual(mockData);
  });

  it("deleteSequence calls DELETE /api/sequences/:id", async () => {
    vi.mocked(apiClient.delete).mockResolvedValueOnce({ data: undefined });

    await deleteSequence(10);

    expect(apiClient.delete).toHaveBeenCalledWith("/api/sequences/10");
  });
});
