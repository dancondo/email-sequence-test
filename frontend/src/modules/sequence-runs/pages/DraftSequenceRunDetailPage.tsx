import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useStartRun, useAddCandidates, useRemoveCandidate } from "../hooks";
import { SequenceRunDetail } from "../types";
import { CsvUploadResult } from "@/modules/candidates/types";
import { Sequence } from "@/modules/sequences/types";
import { UploadCsvModal } from "../components/UploadCsvModal";
import { SelectCandidatesModal } from "../components/SelectCandidatesModal";
import { PATHS } from "@/routes/paths";

interface DraftSequenceRunDetailPageProps {
  run: SequenceRunDetail;
  sequence: Sequence | undefined;
  sequenceId: number;
  runId: number;
  refetch: () => void;
}

export function DraftSequenceRunDetailPage({
  run,
  sequence,
  sequenceId,
  runId,
  refetch,
}: DraftSequenceRunDetailPageProps) {
  const navigate = useNavigate();
  const [activeModal, setActiveModal] = useState<"csv" | "existing" | null>(
    null
  );

  const startMutation = useStartRun(sequenceId, runId);
  const addCandidatesMutation = useAddCandidates(sequenceId, runId);
  const removeCandidateMutation = useRemoveCandidate(sequenceId, runId);

  const snapshot = run.snapshot;
  const stepCount = snapshot?.steps.length ?? sequence?.steps.length ?? 0;
  const totalDelayMinutes =
    snapshot?.steps.reduce((sum, s) => sum + s.delay_minutes, 0) ??
    sequence?.steps.reduce((sum, s) => sum + s.delay_minutes, 0) ??
    0;

  const handleUploadComplete = (result: CsvUploadResult) => {
    const candidateIds = result.candidates.map((c) => c.id);
    if (candidateIds.length > 0) {
      addCandidatesMutation.mutate(candidateIds, { onSuccess: () => refetch() });
    }
  };

  const handleSelectFromExisting = (candidateIds: number[]) => {
    if (candidateIds.length > 0) {
      addCandidatesMutation.mutate(candidateIds, { onSuccess: () => refetch() });
    }
  };

  const handleRemoveCandidate = (candidateId: number, email: string) => {
    if (window.confirm(`Remove ${email} from this run?`)) {
      removeCandidateMutation.mutate(candidateId, {
        onSuccess: () => refetch(),
      });
    }
  };

  const handleLaunch = () => {
    if (
      window.confirm(
        "Launch this sequence run? All emails will be scheduled for delivery."
      )
    ) {
      startMutation.mutate(undefined, { onSuccess: () => refetch() });
    }
  };

  const formatDuration = (minutes: number) => {
    if (minutes < 60) return `${minutes} Min`;
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    if (days > 0) return `${days} Day${days !== 1 ? "s" : ""}`;
    return `${hours} Hour${hours !== 1 ? "s" : ""}`;
  };

  return (
    <div className="mx-auto max-w-5xl px-6 py-10">
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

      {/* Header */}
      <div className="mb-8">
        <p className="mb-2 text-xs font-semibold uppercase tracking-widest text-on-surface-variant">
          Step 2 of 2
        </p>
        <h1 className="font-editorial text-3xl leading-tight text-on-surface">
          Configuration & Reach
        </h1>
        <p className="mt-2 text-sm text-on-surface-variant">
          Finalize your outreach strategy by defining the candidate pool for
          this sequence run.
        </p>
      </div>

      {/* Two-column: sidebar info + main content */}
      <div className="flex gap-8">
        {/* Left sidebar info */}
        <div className="w-64 shrink-0">
          {/* Current Template Card */}
          <div className="rounded-lg border border-outline-variant bg-surface-container-lowest p-5">
            <p className="mb-3 text-xs font-medium uppercase tracking-wider text-on-surface-variant">
              Current Template
            </p>
            <div className="mb-4 flex items-center gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-surface-container-high text-xs font-bold text-on-surface">
                {(sequence?.name ?? "S").charAt(0).toUpperCase()}
              </div>
              <div>
                <p className="text-sm font-semibold text-on-surface">
                  {sequence?.name ?? "Untitled Sequence"}
                </p>
                <p className="text-xs text-on-surface-variant">
                  Created{" "}
                  {sequence
                    ? new Date(sequence.created_at).toLocaleDateString(
                        "en-US",
                        { month: "short", day: "numeric", year: "numeric" }
                      )
                    : "..."}
                </p>
              </div>
            </div>

            <div className="space-y-2 border-t border-outline-variant pt-3">
              <div className="flex justify-between text-xs">
                <span className="text-on-surface-variant">Sequence Steps</span>
                <span className="font-medium text-on-surface">
                  {stepCount} Email{stepCount !== 1 ? "s" : ""}
                </span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-on-surface-variant">
                  Estimated Duration
                </span>
                <span className="font-medium text-on-surface">
                  {formatDuration(totalDelayMinutes)}
                </span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-on-surface-variant">Initial Delay</span>
                <span className="font-medium text-on-surface">Immediate</span>
              </div>
            </div>
          </div>

          {/* Tip Card */}
          <div className="mt-6 rounded-lg bg-surface-container p-5">
            <p className="mb-2 font-editorial text-sm text-on-surface">
              The Editorial Standard
            </p>
            <p className="text-xs leading-relaxed text-on-surface-variant">
              Ensure your candidate lists are clean and tagged correctly.
              High-quality outreach begins with precise segmentation.
            </p>
          </div>
        </div>

        {/* Right main content */}
        <div className="min-w-0 flex-1">
          {/* Action Cards */}
          <div className="mb-8 grid grid-cols-2 gap-4">
            <button
              onClick={() => setActiveModal("csv")}
              className="flex items-start gap-4 rounded-lg border border-outline-variant bg-surface-container-lowest p-5 text-left shadow-ambient transition-colors hover:bg-surface-container-low"
            >
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-error-container text-error">
                <svg
                  className="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
              </div>
              <div>
                <p className="text-sm font-semibold text-on-surface">
                  Upload CSV
                </p>
                <p className="mt-1 text-xs text-on-surface-variant">
                  Import candidates via file upload for bulk enrollment.
                </p>
              </div>
            </button>

            <button
              onClick={() => setActiveModal("existing")}
              className="flex items-start gap-4 rounded-lg border border-outline-variant bg-surface-container-lowest p-5 text-left shadow-ambient transition-colors hover:bg-surface-container-low"
            >
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-secondary-container text-on-secondary-container">
                <svg
                  className="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
              </div>
              <div>
                <p className="text-sm font-semibold text-on-surface">
                  Select from existing
                </p>
                <p className="mt-1 text-xs text-on-surface-variant">
                  Browse your saved candidate lists and static segments.
                </p>
              </div>
            </button>
          </div>

          {/* Error messages */}
          {startMutation.isError && (
            <div className="mb-4 rounded-lg border border-error/20 bg-error-container px-4 py-3 text-sm text-error">
              {startMutation.error instanceof Error
                ? startMutation.error.message
                : "Failed to start run"}
            </div>
          )}
          {addCandidatesMutation.isError && (
            <div className="mb-4 rounded-lg border border-error/20 bg-error-container px-4 py-3 text-sm text-error">
              {addCandidatesMutation.error instanceof Error
                ? addCandidatesMutation.error.message
                : "Failed to add candidates"}
            </div>
          )}

          {/* Selected Candidates */}
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xs font-medium uppercase tracking-wider text-on-surface-variant">
              Selected Candidates
            </h2>
            {run.candidates.length > 0 && (
              <span className="rounded border border-outline-variant px-2.5 py-1 text-xs text-on-surface-variant">
                {run.candidates.length} Record
                {run.candidates.length !== 1 ? "s" : ""} Found
              </span>
            )}
          </div>

          {run.candidates.length === 0 ? (
            <div className="rounded-lg border-2 border-dashed border-outline-variant p-12 text-center">
              <p className="text-on-surface-variant">
                No candidates enrolled yet.
              </p>
              <p className="mt-1 text-sm text-outline">
                Upload a CSV or select from existing candidates.
              </p>
            </div>
          ) : (
            <div className="overflow-hidden rounded-lg border border-outline-variant bg-surface-container-lowest shadow-ambient">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-outline-variant bg-surface-container-low text-left text-xs font-medium uppercase tracking-wider text-on-surface-variant">
                    <th className="px-5 py-3">Name</th>
                    <th className="px-5 py-3">Email Address</th>
                    <th className="px-5 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {run.candidates.map((src) => (
                    <tr
                      key={src.id}
                      className="border-b border-surface-container last:border-0"
                    >
                      <td className="px-5 py-3 text-sm font-medium text-on-surface">
                        {src.candidate.name ?? src.candidate.email}
                      </td>
                      <td className="px-5 py-3 text-sm text-on-surface-variant">
                        {src.candidate.email}
                      </td>
                      <td className="px-5 py-3 text-right">
                        <button
                          onClick={() =>
                            handleRemoveCandidate(
                              src.candidate_id,
                              src.candidate.email
                            )
                          }
                          disabled={removeCandidateMutation.isPending}
                          className="text-xs font-medium text-error hover:text-error/80 disabled:opacity-50"
                        >
                          Remove
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="mt-10 flex items-center justify-between border-t border-outline-variant pt-6">
        <p className="text-xs font-semibold uppercase tracking-wider text-on-surface-variant">
          Total Selection:{" "}
          <span className="text-on-surface">
            {run.candidates.length} Candidate
            {run.candidates.length !== 1 ? "s" : ""}
          </span>
        </p>
        <div className="flex items-center gap-4">
          <button
            onClick={() =>
              navigate(
                PATHS.SEQUENCE_DETAIL.replace(":id", String(sequenceId))
              )
            }
            className="text-sm font-medium text-on-surface-variant hover:text-on-surface"
          >
            Cancel & Discard
          </button>
          <button
            onClick={handleLaunch}
            disabled={
              startMutation.isPending || run.candidates.length === 0
            }
            className="inline-flex items-center gap-2 rounded-full bg-on-surface px-6 py-2.5 text-sm font-medium text-surface hover:bg-on-surface/90 disabled:opacity-50"
          >
            {startMutation.isPending ? "Launching..." : "Launch Sequence Run"}
            <svg
              className="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M14 5l7 7m0 0l-7 7m7-7H3"
              />
            </svg>
          </button>
        </div>
      </div>

      {/* Modals */}
      <UploadCsvModal
        open={activeModal === "csv"}
        onClose={() => setActiveModal(null)}
        onUploadComplete={handleUploadComplete}
      />
      <SelectCandidatesModal
        open={activeModal === "existing"}
        onClose={() => setActiveModal(null)}
        onAdd={handleSelectFromExisting}
        excludeCandidateIds={run.candidates.map((src) => src.candidate_id)}
      />
    </div>
  );
}
