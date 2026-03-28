import { useSearchParams } from "react-router-dom";
import {
  useConnectionStatus,
  useConnectEmail,
  useDisconnectEmail,
} from "../hooks";

export function SettingsPage() {
  const [searchParams] = useSearchParams();
  const { data, isLoading } = useConnectionStatus();
  const connect = useConnectEmail();
  const disconnect = useDisconnectEmail();

  const error = searchParams.get("error");
  const connected = searchParams.get("connected");

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-96 rounded-lg bg-white p-8 shadow-md">
        <h1 className="mb-4 text-2xl font-bold text-gray-800">
          Email Settings
        </h1>

        {error && (
          <div className="mb-4 rounded bg-red-100 p-3 text-sm text-red-700">
            Connection failed: {error}
          </div>
        )}
        {connected && (
          <div className="mb-4 rounded bg-green-100 p-3 text-sm text-green-700">
            Gmail connected successfully!
          </div>
        )}

        {isLoading && <p className="text-gray-500">Loading...</p>}

        {data?.connected && data.account ? (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-green-500" />
              <span className="text-sm font-medium text-green-700">
                Connected
              </span>
            </div>
            <p className="text-sm text-gray-600">{data.account.email}</p>
            <p className="text-xs text-gray-400">
              Since{" "}
              {new Date(data.account.connected_at).toLocaleDateString()}
            </p>
            <button
              onClick={() => disconnect.mutate()}
              disabled={disconnect.isPending}
              className="w-full rounded bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700 disabled:opacity-50"
            >
              {disconnect.isPending ? "Disconnecting..." : "Disconnect Gmail"}
            </button>
          </div>
        ) : !isLoading ? (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-gray-400" />
              <span className="text-sm text-gray-500">Not connected</span>
            </div>
            <button
              onClick={() => connect.mutate()}
              disabled={connect.isPending}
              className="w-full rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {connect.isPending ? "Redirecting..." : "Connect Gmail"}
            </button>
          </div>
        ) : null}
      </div>
    </div>
  );
}
