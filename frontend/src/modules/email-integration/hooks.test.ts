import { renderHook, waitFor, act } from "@testing-library/react";
import { createWrapper } from "@/test/wrapper";
import {
  useConnectionStatus,
  useConnectEmail,
  useDisconnectEmail,
} from "./hooks";
import { disconnectAccount, fetchAuthUrl, fetchConnectionStatus } from "./api";

vi.mock("./api");

describe("email-integration hooks", () => {
  afterEach(() => vi.restoreAllMocks());

  describe("useConnectionStatus", () => {
    it("returns connection status data", async () => {
      const mockData = { connected: true, account: { id: 1, email: "test@example.com" } };
      vi.mocked(fetchConnectionStatus).mockResolvedValueOnce(
        mockData as ReturnType<typeof fetchConnectionStatus> extends Promise<infer T> ? T : never
      );

      const { wrapper } = createWrapper();
      const { result } = renderHook(() => useConnectionStatus(), { wrapper });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(result.current.data).toEqual(mockData);
    });
  });

  describe("useConnectEmail", () => {
    it("fetches auth URL and redirects", async () => {
      const originalLocation = window.location;
      const mockLocation = { ...originalLocation, href: "" };
      Object.defineProperty(window, "location", {
        value: mockLocation,
        writable: true,
      });

      vi.mocked(fetchAuthUrl).mockResolvedValueOnce({
        auth_url: "https://oauth.example.com/auth",
      });

      const { wrapper } = createWrapper();
      const { result } = renderHook(() => useConnectEmail(), { wrapper });

      await act(async () => {
        await result.current.mutateAsync();
      });

      expect(fetchAuthUrl).toHaveBeenCalledOnce();
      expect(mockLocation.href).toBe("https://oauth.example.com/auth");

      Object.defineProperty(window, "location", {
        value: originalLocation,
        writable: true,
      });
    });
  });

  describe("useDisconnectEmail", () => {
    it("calls disconnect and invalidates status cache", async () => {
      vi.mocked(disconnectAccount).mockResolvedValueOnce();

      const { wrapper, queryClient } = createWrapper();
      queryClient.setQueryData(["email-integration", "status"], {
        connected: true,
      });

      const { result } = renderHook(() => useDisconnectEmail(), { wrapper });

      await act(async () => {
        await result.current.mutateAsync();
      });

      expect(disconnectAccount).toHaveBeenCalledOnce();
      expect(
        queryClient.getQueryState(["email-integration", "status"])?.isInvalidated
      ).toBe(true);
    });
  });
});
