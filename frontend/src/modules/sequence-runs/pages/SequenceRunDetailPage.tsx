import { Link, useNavigate, useParams } from "react-router-dom";
import { useRun } from "../hooks";
import { useSequence } from "@/modules/sequences/hooks";
import { SequenceRunCandidateStatus } from "../types";
import { DraftSequenceRunDetailPage } from "./DraftSequenceRunDetailPage";
import { PATHS } from "@/routes/paths";

const CANDIDATE_STATUS_CONFIG: Record<
  SequenceRunCandidateStatus,
  { label: string; className: string }
> = {
  active: {
    label: "ACTIVE",
    className: "bg-surface-container-high text-on-surface-variant",
  },
  completed: {
    label: "COMPLETED",
    className: "bg-primary text-on-primary",
  },
  replied: {
    label: "REPLIED",
    className: "bg-secondary/10 text-secondary",
  },
  interested: {
    label: "INTERESTED",
    className: "bg-primary text-on-primary",
  },
  not_interested: {
    label: "NOT INTERESTED",
    className: "border border-error text-error",
  },
  unsubscribed: {
    label: "UNSUBSCRIBED",
    className: "border border-outline-variant text-on-surface-variant",
  },
};

export function SequenceRunDetailPage() {
  const { id, runId } = useParams<{ id: string; runId: string }>();
  const sequenceId = Number(id);
  const runIdNum = Number(runId);
  const navigate = useNavigate();

  const { data: run, isLoading, refetch } = useRun(sequenceId, runIdNum);
  const { data: sequence } = useSequence(sequenceId);

  if (isLoading) {
    return (
      <div className="mx-auto max-w-5xl px-6 py-10">
        <p className="text-on-surface-variant">Loading...</p>
      </div>
    );
  }

  if (!run) {
    return (
      <div className="mx-auto max-w-5xl px-6 py-10">
        <p className="text-error">Run not found.</p>
      </div>
    );
  }

  if (run.status === "draft") {
    return (
      <DraftSequenceRunDetailPage
        run={run}
        sequence={sequence}
        sequenceId={sequenceId}
        runId={runIdNum}
        refetch={refetch}
      />
    );
  }

  // Active / Completed view
  return (
    <div className="mx-auto max-w-5xl px-6 py-10">
      {/* Header */}
      <div className="mb-8">
        {/* Breadcrumb */}
        <div className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-on-surface-variant">
          <Link to={PATHS.SEQUENCES} className="hover:text-on-surface">
            Sequences
          </Link>
          <span>&gt;</span>
          <Link
            to={PATHS.SEQUENCE_DETAIL.replace(":id", String(sequenceId))}
            className="hover:text-on-surface"
          >
            {sequence?.name ?? "..."}
          </Link>
          <span>&gt;</span>
          <span className="text-secondary">Run #{run.id}</span>
        </div>

        <p className="text-xs font-semibold uppercase tracking-widest text-on-surface-variant">
          {run.status === "active" ? "Active Sequence" : "Completed"}
        </p>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="font-editorial text-3xl text-on-surface">
              Run Performance
            </h1>
            {run.started_at && (
              <p className="mt-2 text-sm text-on-surface-variant">
                Started{" "}
                {new Date(run.started_at).toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                  year: "numeric",
                })}{" "}
                &middot; {run.candidates.length} candidate
                {run.candidates.length !== 1 ? "s" : ""}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Metrics Cards (mocked) */}
      <div className="mb-10">
        <h2 className="mb-4 text-xs font-medium uppercase tracking-wider text-on-surface-variant">
          Performance Overview
        </h2>
        <div className="grid grid-cols-3 gap-4">
          <div className="rounded-lg border border-outline-variant bg-surface-container-lowest p-5 shadow-ambient">
            <p className="text-xs uppercase tracking-wider text-on-surface-variant">
              Total Sent
            </p>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-bold text-on-surface">1,482</span>
              <span className="rounded-full bg-secondary/10 px-2 py-0.5 text-xs font-semibold text-secondary">
                +12%
              </span>
            </div>
            <p className="mt-1 text-xs text-outline">vs. previous run</p>
          </div>

          <div className="rounded-lg border border-outline-variant bg-surface-container-lowest p-5 shadow-ambient">
            <p className="text-xs uppercase tracking-wider text-on-surface-variant">
              Replies
            </p>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-bold text-on-surface">342</span>
            </div>
            <p className="mt-1 text-xs text-outline">23.1% rate</p>
          </div>

          <div className="rounded-lg border border-outline-variant bg-surface-container-lowest p-5 shadow-ambient">
            <p className="text-xs uppercase tracking-wider text-on-surface-variant">
              Interest %
            </p>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-bold text-on-surface">8.4%</span>
              <span className="rounded-full bg-secondary/10 px-2 py-0.5 text-xs font-semibold text-secondary">
                +2.1%
              </span>
            </div>
            <p className="mt-1 text-xs text-outline">above benchmark</p>
          </div>
        </div>
      </div>

      {/* Candidate Performance */}
      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xs font-medium uppercase tracking-wider text-on-surface-variant">
            Candidate Performance
          </h2>
          <div className="flex items-center gap-2">
            <span className="rounded-lg border border-outline-variant px-3 py-1.5 text-xs text-on-surface-variant">
              Filter
            </span>
            <span className="rounded-lg border border-outline-variant px-3 py-1.5 text-xs text-on-surface-variant">
              Sort
            </span>
          </div>
        </div>

        {run.candidates.length === 0 ? (
          <div className="rounded-lg border-2 border-dashed border-outline-variant p-12 text-center">
            <p className="text-on-surface-variant">
              No candidates enrolled yet.
            </p>
          </div>
        ) : (
          <div className="overflow-hidden rounded-lg border border-outline-variant bg-surface-container-lowest shadow-ambient">
            <table className="w-full">
              <thead>
                <tr className="border-b border-outline-variant bg-surface-container-low text-left text-xs font-medium uppercase tracking-wider text-on-surface-variant">
                  <th className="px-5 py-3">Candidate</th>
                  <th className="px-5 py-3">Status</th>
                  <th className="px-5 py-3">Last Interaction</th>
                  <th className="px-5 py-3">Activity</th>
                </tr>
              </thead>
              <tbody>
                {run.candidates.map((src) => {
                  const statusConfig = CANDIDATE_STATUS_CONFIG[src.status] ?? {
                    label: src.status.toUpperCase(),
                    className:
                      "bg-surface-container-high text-on-surface-variant",
                  };
                  return (
                    <tr
                      key={src.id}
                      onClick={() =>
                        navigate(
                          PATHS.CANDIDATE_TIMELINE.replace(
                            ":id",
                            String(sequenceId)
                          )
                            .replace(":runId", String(runIdNum))
                            .replace(
                              ":candidateId",
                              String(src.candidate_id)
                            )
                        )
                      }
                      className="cursor-pointer border-b border-surface-container last:border-0 hover:bg-surface-container-low"
                    >
                      <td className="px-5 py-3">
                        <div className="flex items-center gap-3">
                          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-surface-container-high text-xs font-bold text-on-surface">
                            {(src.candidate.name ?? src.candidate.email)
                              .charAt(0)
                              .toUpperCase()}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-on-surface">
                              {src.candidate.name ?? src.candidate.email}
                            </p>
                            {src.candidate.name && (
                              <p className="text-xs text-on-surface-variant">
                                {src.candidate.email}
                              </p>
                            )}
                          </div>
                        </div>
                      </td>

                      <td className="px-5 py-3">
                        <span
                          className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase ${statusConfig.className}`}
                        >
                          {statusConfig.label}
                        </span>
                      </td>

                      <td className="px-5 py-3 text-sm text-on-surface-variant">
                        {new Date(src.updated_at).toLocaleDateString("en-US", {
                          month: "short",
                          day: "numeric",
                          hour: "numeric",
                          minute: "2-digit",
                        })}
                      </td>

                      <td className="px-5 py-3">
                        <div className="flex items-center gap-1">
                          <span
                            className={`inline-block h-2 w-2 rounded-full ${
                              src.status === "replied"
                                ? "bg-secondary"
                                : src.status === "active"
                                  ? "bg-primary"
                                  : "bg-outline"
                            }`}
                          />
                          <span className="text-xs text-on-surface-variant">
                            Step {src.current_step_order}
                          </span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
