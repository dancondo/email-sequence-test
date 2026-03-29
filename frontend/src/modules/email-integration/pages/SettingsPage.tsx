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
    <div className="mx-auto max-w-4xl px-6 py-10">
      <header className="mb-10">
        <p className="text-xs font-semibold uppercase tracking-widest text-on-surface-variant">
          Connect Email
        </p>
      </header>

      {error && (
        <div className="mb-6 rounded bg-error-container p-4 text-sm text-error">
          Connection failed: {error}
        </div>
      )}
      {connected && (
        <div className="mb-6 rounded bg-surface-container p-4 text-sm text-on-surface">
          Gmail connected successfully!
        </div>
      )}

      {isLoading && <p className="text-on-surface-variant">Loading...</p>}

      {data?.connected && data.account ? (
        <ConnectedView
          email={data.account.email}
          connectedAt={data.account.connected_at}
          onDisconnect={() => disconnect.mutate()}
          isPending={disconnect.isPending}
        />
      ) : !isLoading ? (
        <NotConnectedView
          onConnect={() => connect.mutate()}
          isPending={connect.isPending}
        />
      ) : null}
    </div>
  );
}

function NotConnectedView({
  onConnect,
  isPending,
}: {
  onConnect: () => void;
  isPending: boolean;
}) {
  return (
    <div className="space-y-10">
      <h1 className="font-editorial text-5xl leading-tight text-on-surface">
        Your outreach,
        <br />
        <em>synchronized.</em>
      </h1>

      <p className="max-w-lg text-base leading-relaxed text-on-surface-variant">
        Jooba leverages the Nylas protocol to create a direct, secure bridge to
        your Gmail. Eliminate manual data entry and keep every candidate
        interaction in one precise ledger.
      </p>

      <div className="grid grid-cols-1 items-center gap-6 lg:grid-cols-2">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="rounded bg-surface-container-low p-6">
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded bg-surface-container">
              <svg
                className="h-5 w-5 text-on-surface-variant"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={1.5}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182"
                />
              </svg>
            </div>
            <h3 className="mb-1 text-sm font-semibold text-on-surface">
              Real-time Sync
            </h3>
            <p className="text-sm text-on-surface-variant">
              Instant updates for sent and received emails across all active
              sequences.
            </p>
          </div>

          <div className="rounded bg-surface-container-low p-6">
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded bg-surface-container">
              <svg
                className="h-5 w-5 text-on-surface-variant"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={1.5}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z"
                />
              </svg>
            </div>
            <h3 className="mb-1 text-sm font-semibold text-on-surface">
              SOC2 Compliant
            </h3>
            <p className="text-sm text-on-surface-variant">
              Your data is encrypted end-to-end. We never store your
              credentials.
            </p>
          </div>
        </div>

        <div className="flex justify-center">
          <div className="w-full rounded bg-surface-container-lowest p-8 shadow-ambient">
            <div className="mb-4 flex h-10 w-10 items-center justify-center rounded bg-surface-container-low font-editorial text-lg text-on-surface-variant">
              J
            </div>
            <h2 className="mb-2 text-lg font-semibold text-on-surface">
              Link your Gmail account to start
            </h2>
            <p className="mb-6 text-sm text-on-surface-variant">
              Connect through our secure Nylas gateway to begin automating your
              recruiter outreach.
            </p>
            <button
              onClick={onConnect}
              disabled={isPending}
              className="w-full rounded bg-gradient-to-br from-primary to-primary-container px-4 py-3 text-sm font-medium text-on-primary hover:opacity-90 disabled:opacity-50"
            >
              {isPending ? "Redirecting..." : "Connect Gmail →"}
            </button>
            <p className="mt-4 text-xs text-outline">
              You can disconnect your account at any time from the Settings
              panel.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function ConnectedView({
  email,
  connectedAt,
  onDisconnect,
  isPending,
}: {
  email: string;
  connectedAt: string;
  onDisconnect: () => void;
  isPending: boolean;
}) {
  return (
    <div className="space-y-10">
      <h1 className="font-editorial text-5xl leading-tight text-on-surface">
        You're all set.
      </h1>

      <div className="max-w-md rounded bg-surface-container-lowest p-6 shadow-ambient">
        <div className="mb-4 flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-secondary" />
          <span className="text-sm font-medium text-secondary">Connected</span>
        </div>

        <p className="text-sm text-on-surface">{email}</p>
        <p className="mt-1 text-xs text-on-surface-variant">
          Since {new Date(connectedAt).toLocaleDateString()}
        </p>

        <button
          onClick={onDisconnect}
          disabled={isPending}
          className="mt-6 w-full rounded border border-outline-variant/15 px-4 py-2.5 text-sm font-medium text-error hover:bg-error-container/30 disabled:opacity-50"
        >
          {isPending ? "Disconnecting..." : "Disconnect Gmail"}
        </button>
      </div>
    </div>
  );
}
