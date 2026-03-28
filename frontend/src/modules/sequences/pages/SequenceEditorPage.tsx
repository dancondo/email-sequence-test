import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { RichTextEditor } from "@/shared/components/RichTextEditor";
import { useSequence, useCreateSequence, useUpdateSequence } from "../hooks";
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

    if (isEdit) {
      await updateMutation.mutateAsync({
        id: sequenceId,
        data: { name, steps },
      });
    } else {
      await createMutation.mutateAsync({ name, steps });
    }
    navigate(PATHS.SEQUENCES);
  };

  const isSaving = createMutation.isPending || updateMutation.isPending;

  if (isEdit && isLoading) {
    return (
      <div className="mx-auto max-w-3xl p-6">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">
          {isEdit ? "Edit Sequence" : "Create Sequence"}
        </h1>
        <button
          onClick={() => navigate(PATHS.SEQUENCES)}
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          Cancel
        </button>
      </div>

      <div className="mb-6">
        <label className="mb-1 block text-sm font-medium text-gray-700">
          Sequence Name
        </label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g. Senior Engineer Outreach"
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      <div className="space-y-6">
        {steps.map((step, index) => (
          <div
            key={index}
            className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
          >
            <div className="mb-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-700">
                  Step {index + 1}
                </span>
                {index === 0 ? (
                  <span className="text-xs text-gray-400">
                    Sent on enrollment
                  </span>
                ) : (
                  <div className="flex items-center gap-1 text-xs text-gray-500">
                    <span>Send</span>
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
                      className="w-14 rounded border border-gray-300 px-1.5 py-0.5 text-center text-xs focus:border-blue-500 focus:outline-none"
                    />
                    <span>min after previous (= days)</span>
                  </div>
                )}
              </div>
              {steps.length > 1 && (
                <button
                  onClick={() => removeStep(index)}
                  className="text-xs text-red-500 hover:text-red-700"
                >
                  Remove
                </button>
              )}
            </div>

            <div className="mb-3">
              <label className="mb-1 block text-xs font-medium text-gray-600">
                Subject
              </label>
              <input
                type="text"
                value={step.subject}
                onChange={(e) => updateStep(index, "subject", e.target.value)}
                placeholder="Email subject line"
                className="w-full rounded border border-gray-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-gray-600">
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

      <button
        onClick={addStep}
        className="mt-4 w-full rounded-lg border-2 border-dashed border-gray-300 py-2 text-sm text-gray-500 hover:border-gray-400 hover:text-gray-600"
      >
        + Add Follow-up Step
      </button>

      <div className="mt-6 flex justify-end">
        <button
          onClick={handleSave}
          disabled={isSaving || !name.trim()}
          className="rounded bg-blue-600 px-6 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {isSaving
            ? "Saving..."
            : isEdit
              ? "Update Sequence"
              : "Create Sequence"}
        </button>
      </div>
    </div>
  );
}
