import { renderHook, waitFor } from "@testing-library/react";
import { createWrapper } from "@/test/wrapper";
import { useHealth } from "./hooks";
import { fetchHealth } from "./api";

vi.mock("./api");

describe("health hooks", () => {
  afterEach(() => vi.restoreAllMocks());

  it("useHealth returns health data on success", async () => {
    const mockData = { status: "healthy" as const, database: "connected" };
    vi.mocked(fetchHealth).mockResolvedValueOnce(mockData);

    const { wrapper } = createWrapper();
    const { result } = renderHook(() => useHealth(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockData);
    expect(fetchHealth).toHaveBeenCalledOnce();
  });

  it("useHealth handles error", async () => {
    vi.mocked(fetchHealth).mockRejectedValueOnce(new Error("Network error"));

    const { wrapper } = createWrapper();
    const { result } = renderHook(() => useHealth(), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error).toBeInstanceOf(Error);
  });
});
