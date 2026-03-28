import { useNavigate, useParams } from "react-router-dom";
import { useRuns, useCreateRun } from "../hooks";
import { PATHS } from "@/routes/paths";
import { useSequence } from "@/modules/sequences/hooks";

const STATUS_STYLES: Record<string, string> = {
  draft: "bg-gray-100 text-gray-700",
  active: "bg-blue-100 text-blue-700",
  completed: "bg-green-100 text-green-700",
};

export function SequenceRunsPage() {
  const { id } = useParams<{ id: string }>();
  const sequenceId = Number(id);
  const navigate = useNavigate();

  const { data: sequence } = useSequence(sequenceId);
  const { data: runs, isLoading } = useRuns(sequenceId);
  const createMutation = useCreateRun(sequenceId);

  const handleCreateRun = () => {
    createMutation.mutate(undefined, {
      onSuccess: (run) => {
        navigate(
          PATHS.SEQUENCE_RUN_DETAIL.replace(":id", String(sequenceId)).replace(
            ":runId",
            String(run.id)
          )
        );
      },
    });
  };

  return (
    <div className="mx-auto max-w-4xl p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <button
            onClick={() => navigate(PATHS.SEQUENCES)}
            className="mb-1 text-sm text-gray-500 hover:text-gray-700"
          >
            &larr; Back to Sequences
          </button>
          <h1 className="text-2xl font-bold text-gray-800">
            {sequence?.name ?? "..."} &mdash; Runs
          </h1>
        </div>
        <button
          onClick={handleCreateRun}
          disabled={createMutation.isPending}
          className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {createMutation.isPending ? "Creating..." : "New Run"}
        </button>
      </div>

      {isLoading && <p className="text-gray-500">Loading...</p>}

      {runs && runs.length === 0 && (
        <div className="rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
          <p className="text-gray-500">No runs yet.</p>
          <p className="mt-1 text-sm text-gray-400">
            Create a new run to start sending this sequence.
          </p>
        </div>
      )}

      {runs && runs.length > 0 && (
        <div className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50 text-left text-sm font-medium text-gray-500">
                <th className="px-4 py-3">Run #</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Candidates</th>
                <th className="px-4 py-3">Started</th>
                <th className="px-4 py-3">Created</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr
                  key={run.id}
                  onClick={() =>
                    navigate(
                      PATHS.SEQUENCE_RUN_DETAIL.replace(
                        ":id",
                        String(sequenceId)
                      ).replace(":runId", String(run.id))
                    )
                  }
                  className="cursor-pointer border-b border-gray-100 last:border-0 hover:bg-gray-50"
                >
                  <td className="px-4 py-3 font-medium text-gray-800">
                    #{run.id}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                        STATUS_STYLES[run.status] ?? ""
                      }`}
                    >
                      {run.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {run.candidate_count}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {run.started_at
                      ? new Date(run.started_at).toLocaleString()
                      : "—"}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {new Date(run.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
