import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { RichTextEditor } from "@/shared/components/RichTextEditor";
import { useSequence, useCreateSequence, useUpdateSequence } from "../hooks";
import { createRun } from "@/modules/sequence-runs/api";
import { SequenceStepInput } from "../types";
import { PATHS } from "@/routes/paths";

const EMPTY_STEP: SequenceStepInput = {
  subject: "",
  body: "",
  delay_minutes: 0,
};

export function SequenceEditorPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;
  const sequenceId = id ? parseInt(id, 10) : 0;

  const { data: existing, isLoading } = useSequence(sequenceId);
  const createMutation = useCreateSequence();
  const updateMutation = useUpdateSequence();

  const [name, setName] = useState("");
  const [steps, setSteps] = useState<SequenceStepInput[]>([
    { ...EMPTY_STEP },
  ]);
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    if (isEdit && existing && !initialized) {
      setName(existing.name);
      setSteps(
        existing.steps.map((s) => ({
          subject: s.subject,
          body: s.body,
          delay_minutes: s.delay_minutes,
        }))
      );
      setInitialized(true);
    }
  }, [isEdit, existing, initialized]);

  const updateStep = (
    index: number,
    field: keyof SequenceStepInput,
    value: string | number
  ) => {
    setSteps((prev) =>
      prev.map((step, i) => (i === index ? { ...step, [field]: value } : step))
    );
  };

  const addStep = () => {
    setSteps((prev) => [...prev, { ...EMPTY_STEP, delay_minutes: 1 }]);
  };

  const removeStep = (index: number) => {
    if (steps.length <= 1) return;
    setSteps((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSave = async () => {
    if (!name.trim()) return;

    let seqId = sequenceId;
    if (isEdit) {
      await updateMutation.mutateAsync({
        id: sequenceId,
        data: { name, steps },
      });
    } else {
      const created = await createMutation.mutateAsync({ name, steps });
      seqId = created.id;
    }

    const run = await createRun(seqId);
    navigate(
      PATHS.SEQUENCE_RUN_DETAIL.replace(":id", String(seqId)).replace(
        ":runId",
        String(run.id)
      )
    );
  };

  const isSaving = createMutation.isPending || updateMutation.isPending;

  if (isEdit && isLoading) {
    return (
      <div className="mx-auto max-w-3xl px-6 py-10">
        <p className="text-on-surface-variant">Loading...</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      {/* Breadcrumb + Header */}
      <div className="mb-8">
        <div className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-on-surface-variant">
          <Link to={PATHS.SEQUENCES} className="hover:text-on-surface">
            Sequences
          </Link>
          <span>&gt;</span>
          <span className="text-secondary">
            {isEdit ? "Edit" : "New Editor"}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <h1 className="font-editorial text-3xl text-on-surface">
            {isEdit ? "Edit Sequence" : "Create Sequence"}
          </h1>
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate(PATHS.SEQUENCES)}
              className="rounded-lg border border-outline-variant px-4 py-2 text-sm font-medium text-on-surface hover:bg-surface-container-low"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving || !name.trim()}
              className="rounded-lg bg-primary px-5 py-2 text-sm font-medium text-on-primary hover:bg-primary-container disabled:opacity-50"
            >
              {isSaving
                ? "Saving..."
                : isEdit
                  ? "Update Sequence"
                  : "Launch Sequence"}
            </button>
          </div>
        </div>
      </div>

      {/* Sequence Foundations */}
      <div className="mb-6 rounded-lg border border-outline-variant bg-surface-container-lowest p-5 shadow-ambient">
        <div className="mb-4 flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-secondary">
            <svg
              className="h-4 w-4 text-on-secondary"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 6v6m0 0v6m0-6h6m-6 0H6"
              />
            </svg>
          </div>
          <h2 className="text-lg font-semibold text-on-surface">
            Sequence Foundations
          </h2>
        </div>
        <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-on-surface-variant">
          Internal Name
        </label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g., Q4 Engineering Outreach - Mid Level"
          className="w-full rounded-lg border border-outline-variant bg-surface px-3 py-2.5 text-sm text-on-surface placeholder:text-outline focus:border-secondary focus:outline-none focus:ring-1 focus:ring-secondary"
        />
      </div>

      {/* Steps */}
      <div className="space-y-6">
        {steps.map((step, index) => (
          <div
            key={index}
            className="rounded-lg border border-outline-variant bg-surface-container-lowest p-5 shadow-ambient"
          >
            {/* Step Header */}
            <div className="mb-4 flex items-start justify-between">
              <div className="flex items-start gap-3">
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-bold text-on-primary">
                  {index + 1}
                </div>
                <div>
                  <h3 className="text-base font-semibold text-on-surface">
                    {index === 0 ? "Initial Outreach" : `Follow-up ${index}`}
                  </h3>
                  {index === 0 ? (
                    <p className="mt-0.5 text-xs text-on-surface-variant">
                      Sends immediately after contact is added
                    </p>
                  ) : (
                    <div className="mt-1 flex items-center gap-2">
                      <span className="inline-flex items-center rounded-md border border-outline-variant px-2 py-0.5 text-xs font-semibold text-on-surface-variant">
                        <input
                          type="number"
                          min={1}
                          value={step.delay_minutes}
                          onChange={(e) =>
                            updateStep(
                              index,
                              "delay_minutes",
                              parseInt(e.target.value, 10) || 1
                            )
                          }
                          className="mr-1 w-10 rounded border border-outline-variant bg-transparent px-1 py-0 text-center text-xs text-on-surface-variant focus:outline-none"
                        />
                        {step.delay_minutes === 1 ? "min" : "mins"}
                      </span>
                      <span className="text-xs text-on-surface-variant">
                        Threaded reply to Step {index}
                      </span>
                    </div>
                  )}
                </div>
              </div>
              {steps.length > 1 && (
                <button
                  onClick={() => removeStep(index)}
                  className="rounded p-1 text-on-surface-variant hover:bg-surface-container hover:text-error"
                  title="Remove step"
                >
                  <svg
                    className="h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
              )}
            </div>

            {/* Subject Line */}
            <div className="mb-4">
              <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-on-surface-variant">
                Subject Line
              </label>
              <input
                type="text"
                value={step.subject}
                onChange={(e) => updateStep(index, "subject", e.target.value)}
                placeholder="Email subject line"
                className="w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 text-sm text-on-surface placeholder:text-outline focus:border-secondary focus:outline-none focus:ring-1 focus:ring-secondary"
              />
            </div>

            {/* Body */}
            <div>
              <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-on-surface-variant">
                Body
              </label>
              <RichTextEditor
                content={step.body}
                onChange={(html) => updateStep(index, "body", html)}
                placeholder="Write your email content..."
              />
            </div>
          </div>
        ))}
      </div>

      {/* Add Step */}
      <button
        onClick={addStep}
        className="mt-6 flex w-full flex-col items-center gap-1 rounded-lg border-2 border-dashed border-outline-variant py-4 text-on-surface-variant hover:border-secondary hover:text-secondary"
      >
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-on-primary">
          <svg
            className="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 4.5v15m7.5-7.5h-15"
            />
          </svg>
        </div>
        <span className="text-xs font-medium uppercase tracking-wider">
          Add Next Step
        </span>
      </button>
    </div>
  );
}
