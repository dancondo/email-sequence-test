import { Link, useNavigate, useParams } from "react-router-dom";
import { useRuns, useCreateRun } from "../hooks";
import { PATHS } from "@/routes/paths";
import { useSequence } from "@/modules/sequences/hooks";
import { SequenceRunListItem, SequenceRunStatus } from "../types";

const STATUS_STYLES: Record<SequenceRunStatus, string> = {
  draft: "border border-outline-variant text-on-surface-variant",
  active: "bg-secondary text-on-secondary",
  completed: "bg-primary text-on-primary",
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
    <div className="mx-auto max-w-4xl px-6 py-10">
      {/* Header */}
      <div className="mb-8">
        <div className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-on-surface-variant">
          <Link
            to={PATHS.SEQUENCE_DETAIL.replace(":id", String(sequenceId))}
            className="hover:text-on-surface"
          >
            {sequence?.name ?? "Sequence"}
          </Link>
          <span>&gt;</span>
          <span className="text-secondary">Runs</span>
        </div>
        <div className="flex items-center justify-between">
          <h1 className="font-editorial text-3xl text-on-surface">
            {sequence?.name ?? "..."} &mdash; Runs
          </h1>
          <button
            onClick={handleCreateRun}
            disabled={createMutation.isPending}
            className="rounded-lg bg-primary px-5 py-2 text-sm font-medium text-on-primary hover:bg-primary-container disabled:opacity-50"
          >
            {createMutation.isPending ? "Creating..." : "New Run"}
          </button>
        </div>
      </div>

      {isLoading && (
        <p className="text-on-surface-variant">Loading...</p>
      )}

      {runs && runs.length === 0 && (
        <div className="rounded-lg border-2 border-dashed border-outline-variant p-12 text-center">
          <p className="text-on-surface-variant">No runs yet.</p>
          <p className="mt-1 text-sm text-outline">
            Create a new run to start sending this sequence.
          </p>
        </div>
      )}

      {runs && runs.length > 0 && (
        <div className="overflow-hidden rounded-lg border border-outline-variant bg-surface-container-lowest shadow-ambient">
          <table className="w-full">
            <thead>
              <tr className="border-b border-outline-variant bg-surface-container-low text-left text-xs font-medium uppercase tracking-wider text-on-surface-variant">
                <th className="px-5 py-3">Run #</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3">Candidates</th>
                <th className="px-5 py-3">Started</th>
                <th className="px-5 py-3">Created</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run: SequenceRunListItem) => (
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
                  className="cursor-pointer border-b border-surface-container last:border-0 hover:bg-surface-container-low"
                >
                  <td className="px-5 py-3 text-sm font-medium text-on-surface">
                    #{run.id}
                  </td>
                  <td className="px-5 py-3">
                    <span
                      className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase ${STATUS_STYLES[run.status]}`}
                    >
                      {run.status}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-sm text-on-surface-variant">
                    {run.candidate_count}
                  </td>
                  <td className="px-5 py-3 text-sm text-on-surface-variant">
                    {run.started_at
                      ? new Date(run.started_at).toLocaleString()
                      : "—"}
                  </td>
                  <td className="px-5 py-3 text-sm text-on-surface-variant">
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
