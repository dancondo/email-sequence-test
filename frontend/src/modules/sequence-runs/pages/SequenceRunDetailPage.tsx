import { useNavigate, useParams } from "react-router-dom";
import { useRun, useStartRun, useAddCandidates, useRemoveCandidate } from "../hooks";
import { useSequence } from "@/modules/sequences/hooks";
import { CsvUploadResult } from "@/modules/candidates/types";
import { CandidateUpload } from "@/modules/candidates/components/CandidateUpload";
import { SnapshotStep } from "../types";
import { PATHS } from "@/routes/paths";

const STATUS_STYLES: Record<string, string> = {
  draft: "bg-gray-100 text-gray-700",
  active: "bg-blue-100 text-blue-700",
  completed: "bg-green-100 text-green-700",
  replied: "bg-purple-100 text-purple-700",
  unsubscribed: "bg-red-100 text-red-700",
};

export function SequenceRunDetailPage() {
  const { id, runId } = useParams<{ id: string; runId: string }>();
  const sequenceId = Number(id);
  const runIdNum = Number(runId);
  const navigate = useNavigate();

  const { data: run, isLoading, refetch } = useRun(sequenceId, runIdNum);
  const { data: sequence } = useSequence(sequenceId);
  const startMutation = useStartRun(sequenceId, runIdNum);
  const addCandidatesMutation = useAddCandidates(sequenceId, runIdNum);
  const removeCandidateMutation = useRemoveCandidate(sequenceId, runIdNum);

  const isDraft = run?.status === "draft";

  // Use live sequence data for DRAFT, snapshot for started runs
  const stepsSource: { name: string; steps: SnapshotStep[] } | null =
    run?.snapshot
      ? run.snapshot
      : sequence
        ? {
            name: sequence.name,
            steps: sequence.steps.map((s) => ({
              step_order: s.step_order,
              subject: s.subject,
              body: s.body,
              delay_minutes: s.delay_minutes,
            })),
          }
        : null;

  const handleUploadComplete = (result: CsvUploadResult) => {
    const candidateIds = result.candidates.map((c) => c.id);
    if (candidateIds.length > 0) {
      addCandidatesMutation.mutate(candidateIds, {
        onSuccess: () => refetch(),
      });
    }
  };

  const handleStart = () => {
    if (
      window.confirm(
        "Start this run? All emails will be scheduled for delivery."
      )
    ) {
      startMutation.mutate(undefined, {
        onSuccess: () => refetch(),
      });
    }
  };

  const handleRemoveCandidate = (candidateId: number, email: string) => {
    if (window.confirm(`Remove ${email} from this run?`)) {
      removeCandidateMutation.mutate(candidateId, {
        onSuccess: () => refetch(),
      });
    }
  };

  if (isLoading) {
    return (
      <div className="mx-auto max-w-4xl p-6">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  if (!run) {
    return (
      <div className="mx-auto max-w-4xl p-6">
        <p className="text-red-600">Run not found.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl p-6">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() =>
            navigate(PATHS.SEQUENCE_DETAIL.replace(":id", String(sequenceId)))
          }
          className="mb-1 text-sm text-on-surface-variant hover:text-on-surface"
        >
          &larr; Back to Sequence
        </button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">
              Run #{run.id}
            </h1>
            {stepsSource && (
              <p className="text-sm text-gray-500">
                Sequence: {stepsSource.name} &middot;{" "}
                {stepsSource.steps.length} step
                {stepsSource.steps.length !== 1 ? "s" : ""}
                {isDraft && (
                  <span className="ml-1 text-amber-500">(live preview)</span>
                )}
              </p>
            )}
          </div>
          <div className="flex items-center gap-3">
            <span
              className={`inline-block rounded-full px-3 py-1 text-sm font-medium ${
                STATUS_STYLES[run.status] ?? ""
              }`}
            >
              {run.status}
            </span>
            {isDraft && (
              <button
                onClick={handleStart}
                disabled={
                  startMutation.isPending || run.candidates.length === 0
                }
                className="rounded bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
              >
                {startMutation.isPending ? "Starting..." : "Start Run"}
              </button>
            )}
          </div>
        </div>
        {run.started_at && (
          <p className="mt-1 text-sm text-gray-500">
            Started: {new Date(run.started_at).toLocaleString()}
          </p>
        )}
      </div>

      {/* Start error */}
      {startMutation.isError && (
        <div className="mb-4 rounded border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {startMutation.error instanceof Error
            ? startMutation.error.message
            : "Failed to start run"}
        </div>
      )}

      {/* CSV Upload (only in DRAFT) */}
      {isDraft && (
        <div className="mb-6">
          <CandidateUpload onUploadComplete={handleUploadComplete} />
        </div>
      )}

      {/* Sequence Steps */}
      {stepsSource && stepsSource.steps.length > 0 && (
        <div className="mb-6 rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <h2 className="mb-3 text-lg font-semibold text-gray-800">
            Sequence Steps{" "}
            {run.snapshot ? "(Snapshot)" : "(Live)"}
          </h2>
          <div className="space-y-2">
            {stepsSource.steps.map((step, i) => (
              <div
                key={i}
                className="flex items-center gap-3 rounded border border-gray-100 bg-gray-50 px-3 py-2 text-sm"
              >
                <span className="font-medium text-gray-600">
                  Step {step.step_order}
                </span>
                <span className="text-gray-800">{step.subject}</span>
                <span className="ml-auto text-gray-400">
                  {step.delay_minutes > 0
                    ? `+${step.delay_minutes}min`
                    : "Immediate"}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Candidates Table */}
      <div className="rounded-lg border border-gray-200 bg-white shadow-sm">
        <div className="border-b border-gray-200 px-4 py-3">
          <h2 className="text-lg font-semibold text-gray-800">
            Candidates ({run.candidates.length})
          </h2>
        </div>

        {run.candidates.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-gray-500">No candidates enrolled yet.</p>
            {isDraft && (
              <p className="mt-1 text-sm text-gray-400">
                Upload a CSV to add candidates.
              </p>
            )}
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50 text-left text-sm font-medium text-gray-500">
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Step</th>
                <th className="px-4 py-3">Enrolled</th>
                {isDraft && (
                  <th className="px-4 py-3 text-right">Actions</th>
                )}
              </tr>
            </thead>
            <tbody>
              {run.candidates.map((src) => (
                <tr
                  key={src.id}
                  className="border-b border-gray-100 last:border-0 hover:bg-gray-50"
                >
                  <td
                    onClick={() =>
                      !isDraft &&
                      navigate(
                        PATHS.CANDIDATE_TIMELINE.replace(
                          ":id",
                          String(sequenceId)
                        )
                          .replace(":runId", String(runIdNum))
                          .replace(":candidateId", String(src.candidate_id))
                      )
                    }
                    className={`px-4 py-3 font-medium text-gray-800 ${
                      !isDraft ? "cursor-pointer" : ""
                    }`}
                  >
                    {src.candidate.email}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {src.candidate.name ?? "—"}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                        STATUS_STYLES[src.status] ?? ""
                      }`}
                    >
                      {src.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {src.current_step_order}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {new Date(src.created_at).toLocaleString()}
                  </td>
                  {isDraft && (
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() =>
                          handleRemoveCandidate(
                            src.candidate_id,
                            src.candidate.email
                          )
                        }
                        disabled={removeCandidateMutation.isPending}
                        className="text-sm font-medium text-red-600 hover:text-red-800 disabled:opacity-50"
                      >
                        Remove
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
