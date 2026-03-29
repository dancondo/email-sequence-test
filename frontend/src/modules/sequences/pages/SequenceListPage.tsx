import { useNavigate } from "react-router-dom";
import { useSequences, useDeleteSequence } from "../hooks";
import { PATHS } from "@/routes/paths";

export function SequenceListPage() {
  const navigate = useNavigate();
  const { data: sequences, isLoading } = useSequences();
  const deleteMutation = useDeleteSequence();

  const handleDelete = (id: number, name: string) => {
    if (window.confirm(`Delete sequence "${name}"?`)) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      <header className="mb-10">
        <p className="text-xs font-semibold uppercase tracking-widest text-on-surface-variant">
          Sequences
        </p>
      </header>

      <div className="mb-8 flex items-end justify-between">
        <div>
          <h1 className="font-editorial text-4xl leading-tight text-on-surface">
            Your sequences
          </h1>
          <p className="mt-2 text-sm text-on-surface-variant">
            Manage your multi-step outreach campaigns and track engagement.
          </p>
        </div>
        <button
          onClick={() => navigate(PATHS.SEQUENCE_NEW)}
          className="rounded bg-gradient-to-br from-primary to-primary-container px-5 py-2.5 text-sm font-medium text-on-primary hover:opacity-90"
        >
          Create New Sequence
        </button>
      </div>

      {isLoading && <p className="text-on-surface-variant">Loading...</p>}

      {sequences && sequences.length === 0 && (
        <div className="rounded bg-surface-container-low px-12 py-16 text-center">
          <p className="font-editorial text-2xl text-on-surface-variant">
            No sequences yet.
          </p>
          <p className="mt-2 text-sm text-outline">
            Create your first email sequence to get started.
          </p>
        </div>
      )}

      {sequences && sequences.length > 0 && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {sequences.map((seq) => (
              <div
                key={seq.id}
                className="group rounded bg-surface-container-lowest p-5 shadow-ambient transition-shadow hover:shadow-ambient-lg"
              >
                <div className="mb-4 flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <span
                      className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        seq.is_active
                          ? "bg-secondary-container text-on-secondary-container"
                          : "bg-surface-container-high text-on-surface-variant"
                      }`}
                    >
                      {seq.is_active ? "Active" : "Draft"}
                    </span>
                  </div>
                  <button
                    onClick={() => handleDelete(seq.id, seq.name)}
                    disabled={deleteMutation.isPending}
                    className="text-xs text-outline opacity-0 transition-opacity hover:text-error group-hover:opacity-100 disabled:opacity-50"
                  >
                    Delete
                  </button>
                </div>

                <h3 className="mb-3 text-base font-semibold text-on-surface">
                  {seq.name}
                </h3>

                <div className="mb-4 grid grid-cols-3 gap-3">
                  <div>
                    <p className="text-xs text-outline">Steps</p>
                    <p className="text-lg font-semibold text-on-surface">
                      {seq.step_count}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-outline">Runs</p>
                    <p className="text-lg font-semibold text-on-surface">
                      {seq.run_count}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-outline">Created</p>
                    <p className="text-sm font-medium text-on-surface">
                      {new Date(seq.created_at).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                      })}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <button
                    onClick={() =>
                      navigate(
                        PATHS.SEQUENCE_DETAIL.replace(":id", String(seq.id))
                      )
                    }
                    className="text-xs font-semibold uppercase tracking-wider text-secondary hover:text-secondary-container"
                  >
                    View Runs
                  </button>
                  <button
                    onClick={() =>
                      navigate(
                        PATHS.SEQUENCE_EDIT.replace(":id", String(seq.id))
                      )
                    }
                    className="text-xs font-semibold uppercase tracking-wider text-on-surface-variant hover:text-on-surface"
                  >
                    Edit
                  </button>
                </div>
              </div>
          ))}
        </div>
      )}
    </div>
  );
}
