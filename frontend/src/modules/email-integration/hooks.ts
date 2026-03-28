import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { disconnectAccount, fetchAuthUrl, fetchConnectionStatus } from "./api";

export function useConnectionStatus() {
  return useQuery({
    queryKey: ["email-integration", "status"],
    queryFn: fetchConnectionStatus,
  });
}

export function useConnectEmail() {
  return useMutation({
    mutationFn: async () => {
      const { auth_url } = await fetchAuthUrl();
      window.location.href = auth_url;
    },
  });
}

export function useDisconnectEmail() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: disconnectAccount,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["email-integration", "status"] });
    },
  });
}
