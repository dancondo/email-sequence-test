import { useHealth } from "../hooks";

export function HealthPage() {
  const { data, isLoading, isError, error } = useHealth();

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="rounded-lg bg-white p-8 shadow-md">
        <h1 className="mb-4 text-2xl font-bold text-gray-800">
          Jooba System Health
        </h1>

        {isLoading && <p className="text-gray-500">Checking...</p>}

        {isError && (
          <p className="text-red-600">
            Error: {error instanceof Error ? error.message : "Unknown error"}
          </p>
        )}

        {data && (
          <div className="space-y-2">
            <p>
              Status:{" "}
              <span
                className={
                  data.status === "healthy"
                    ? "font-semibold text-green-600"
                    : "font-semibold text-red-600"
                }
              >
                {data.status}
              </span>
            </p>
            <p className="text-sm text-gray-600">Database: {data.database}</p>
          </div>
        )}
      </div>
    </div>
  );
}
