import { Link, useNavigate, useParams } from "react-router-dom";
import { useSequence } from "../hooks";
import { useRuns, useCreateRun } from "@/modules/sequence-runs/hooks";
import { PATHS } from "@/routes/paths";
import { SequenceRunListItem, SequenceRunStatus } from "@/modules/sequence-runs/types";

const RUN_STATUS_STYLES: Record<SequenceRunStatus, string> = {
  draft: "border border-outline-variant text-on-surface-variant",
  active: "bg-secondary text-on-secondary",
  completed: "bg-primary text-on-primary",
};

function stripHtml(html: string): string {
  const div = document.createElement("div");
  div.innerHTML = html;
  return div.textContent ?? "";
}

export function SequenceDetailPage() {
  const { id } = useParams<{ id: string }>();
  const sequenceId = Number(id);
  const navigate = useNavigate();

  const { data: sequence, isLoading: seqLoading } = useSequence(sequenceId);
  const { data: runs, isLoading: runsLoading } = useRuns(sequenceId);
  const createMutation = useCreateRun(sequenceId);

  const isLoading = seqLoading || runsLoading;

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
    <div className="mx-auto max-w-5xl px-6 py-10">
      {/* Header */}
      <div className="mb-8">
        <div className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-on-surface-variant">
          <Link to={PATHS.SEQUENCES} className="hover:text-on-surface">
            Sequences
          </Link>
          <span>&gt;</span>
          <span className="text-secondary">Sequence Detail</span>
        </div>
        <div className="flex items-start justify-between">
          <div className="max-w-xl">
            <h1 className="font-editorial text-3xl text-on-surface">
              {sequence?.name ?? "..."}
            </h1>
            {sequence && (
              <p className="mt-2 text-sm leading-relaxed text-on-surface-variant">
                {sequence.steps.length} step sequence &middot; Created{" "}
                {new Date(sequence.created_at).toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                  year: "numeric",
                })}
              </p>
            )}
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() =>
                navigate(
                  PATHS.SEQUENCE_EDIT.replace(":id", String(sequenceId))
                )
              }
              className="rounded-lg border border-outline-variant px-4 py-2 text-sm font-medium text-on-surface hover:bg-surface-container-low"
            >
              Edit Steps
            </button>
            <button
              onClick={handleCreateRun}
              disabled={createMutation.isPending}
              className="rounded-lg bg-primary px-5 py-2 text-sm font-medium text-on-primary hover:bg-primary-container disabled:opacity-50"
            >
              {createMutation.isPending ? "Creating..." : "Start New Run"}
            </button>
          </div>
        </div>
      </div>

      {/* Two-column: Workflow + Metrics */}
      <div className="mb-10 grid grid-cols-[1fr_280px] gap-6">
        {/* Workflow Definition */}
        <div>
          <h2 className="mb-4 text-xs font-medium uppercase tracking-wider text-on-surface-variant">
            Workflow Definition
          </h2>
          <div className="space-y-4">
            {sequence?.steps.map((step, index) => (
              <div key={index} className="flex gap-3">
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-bold text-on-primary">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <div className="mb-1 flex items-center gap-2">
                    <span className="text-sm font-semibold text-on-surface">
                      {index === 0 ? "Initial Outreach" : `Follow-up ${index}`}
                    </span>
                    {index > 0 && (
                      <span className="text-xs text-on-surface-variant">
                        After {step.delay_minutes}{" "}
                        {step.delay_minutes === 1 ? "minute" : "minutes"}
                      </span>
                    )}
                  </div>
                  <div className="rounded-lg border border-outline-variant bg-surface-container-low p-4">
                    <p className="mb-2 text-sm font-medium text-on-surface">
                      {step.subject || "No subject"}
                    </p>
                    <div className="border-t border-outline-variant pt-2">
                      <p className="line-clamp-3 text-sm italic leading-relaxed text-on-surface-variant">
                        &ldquo;{stripHtml(step.body) || "Empty body"}&rdquo;
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <p className="text-sm text-on-surface-variant">Loading...</p>
            )}
          </div>
        </div>

        {/* Global Metrics (mocked) */}
        <div>
          <h2 className="mb-4 text-xs font-medium uppercase tracking-wider text-on-surface-variant">
            Global Metrics
          </h2>
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-lg border border-outline-variant bg-surface-container-lowest p-4 shadow-ambient">
              <span className="text-2xl font-bold text-on-surface">1,204</span>
              <p className="mt-0.5 text-xs uppercase tracking-wider text-on-surface-variant">
                Total Enrolled
              </p>
            </div>
            <div className="rounded-lg border border-outline-variant bg-surface-container-lowest p-4 shadow-ambient">
              <span className="text-2xl font-bold text-on-surface">42%</span>
              <p className="mt-0.5 text-xs uppercase tracking-wider text-on-surface-variant">
                Acceptance
              </p>
            </div>
            <div className="rounded-lg border border-outline-variant bg-surface-container-lowest p-4 shadow-ambient">
              <span className="text-2xl font-bold text-on-surface">89</span>
              <p className="mt-0.5 text-xs uppercase tracking-wider text-on-surface-variant">
                Messages
              </p>
            </div>
            <div className="rounded-lg border border-outline-variant bg-surface-container-lowest p-4 shadow-ambient">
              <span className="text-2xl font-bold text-on-surface">14d</span>
              <p className="mt-0.5 text-xs uppercase tracking-wider text-on-surface-variant">
                Average
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Associated Runs History */}
      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xs font-medium uppercase tracking-wider text-on-surface-variant">
            Associated Runs History
          </h2>
          {runs && runs.length > 0 && (
            <span className="text-xs text-outline">
              Showing {runs.length} run{runs.length !== 1 ? "s" : ""}
            </span>
          )}
        </div>

        {runsLoading && (
          <p className="text-on-surface-variant">Loading...</p>
        )}

        {!runsLoading && (!runs || runs.length === 0) && (
          <div className="rounded-lg border-2 border-dashed border-outline-variant p-12 text-center">
            <p className="text-on-surface-variant">No runs yet.</p>
            <p className="mt-1 text-sm text-outline">
              Start a new run to begin sending this sequence.
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
                        className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase ${RUN_STATUS_STYLES[run.status]}`}
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
    </div>
  );
}
