import { useNavigate, useParams } from "react-router-dom";
import { useCandidate } from "../hooks";
import { PATHS } from "@/routes/paths";

const STATUS_STYLES: Record<string, string> = {
  draft: "bg-gray-100 text-gray-700",
  active: "bg-blue-100 text-blue-700",
  completed: "bg-green-100 text-green-700",
  replied: "bg-purple-100 text-purple-700",
  unsubscribed: "bg-red-100 text-red-700",
};

export function CandidateInfoPage() {
  const { id } = useParams<{ id: string }>();
  const candidateId = Number(id);
  const navigate = useNavigate();
  const { data: candidate, isLoading } = useCandidate(candidateId);

  if (isLoading) {
    return (
      <div className="mx-auto max-w-4xl px-6 py-10">
        <p className="text-on-surface-variant">Loading...</p>
      </div>
    );
  }

  if (!candidate) {
    return (
      <div className="mx-auto max-w-4xl px-6 py-10">
        <p className="text-error">Candidate not found.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      {/* Back link */}
      <button
        onClick={() => navigate(PATHS.CANDIDATES)}
        className="mb-4 text-sm text-on-surface-variant hover:text-on-surface"
      >
        &larr; Back to Candidates
      </button>

      {/* Header */}
      <div className="mb-8">
        <h1 className="font-editorial text-3xl text-on-surface">
          {candidate.name ?? candidate.email}
        </h1>
        {candidate.name && (
          <p className="mt-1 text-sm text-on-surface-variant">
            {candidate.email}
          </p>
        )}
      </div>

      {/* Info card */}
      <div className="mb-8 rounded-lg border border-outline-variant bg-surface-container-lowest p-5 shadow-ambient">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-outline">Created</p>
            <p className="text-sm font-medium text-on-surface">
              {new Date(candidate.created_at).toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
                year: "numeric",
              })}
            </p>
          </div>
          <div>
            <p className="text-xs text-outline">Updated</p>
            <p className="text-sm font-medium text-on-surface">
              {new Date(candidate.updated_at).toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
                year: "numeric",
              })}
            </p>
          </div>
        </div>
      </div>

      {/* Runs table */}
      <h2 className="mb-4 text-lg font-semibold text-on-surface">
        Runs ({candidate.runs.length})
      </h2>

      {candidate.runs.length === 0 ? (
        <div className="rounded bg-surface-container-low px-12 py-10 text-center">
          <p className="text-on-surface-variant">
            This candidate is not enrolled in any runs.
          </p>
        </div>
      ) : (
        <div className="overflow-hidden rounded-lg border border-outline-variant bg-surface-container-lowest shadow-ambient">
          <table className="w-full">
            <thead>
              <tr className="border-b border-outline-variant bg-surface-container-low text-left text-xs font-medium uppercase tracking-wider text-on-surface-variant">
                <th className="px-4 py-3">Sequence</th>
                <th className="px-4 py-3">Run Status</th>
                <th className="px-4 py-3">Candidate Status</th>
                <th className="px-4 py-3">Step</th>
                <th className="px-4 py-3">Enrolled</th>
              </tr>
            </thead>
            <tbody>
              {candidate.runs.map((run) => (
                <tr
                  key={run.sequence_run_candidate_id}
                  onClick={() =>
                    navigate(
                      PATHS.CANDIDATE_TIMELINE.replace(
                        ":id",
                        String(run.sequence_id)
                      )
                        .replace(":runId", String(run.sequence_run_id))
                        .replace(":candidateId", String(candidateId))
                    )
                  }
                  className="cursor-pointer border-b border-outline-variant last:border-0 hover:bg-surface-container-low"
                >
                  <td className="px-4 py-3 font-medium text-on-surface">
                    {run.sequence_name}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                        STATUS_STYLES[run.run_status] ?? ""
                      }`}
                    >
                      {run.run_status}
                    </span>
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
                  <td className="px-4 py-3 text-sm text-on-surface-variant">
                    {run.current_step_order}
                  </td>
                  <td className="px-4 py-3 text-sm text-on-surface-variant">
                    {new Date(run.created_at).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                      year: "numeric",
                    })}
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
