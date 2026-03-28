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
    <div className="mx-auto max-w-4xl p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">Sequences</h1>
        <button
          onClick={() => navigate(PATHS.SEQUENCE_NEW)}
          className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          Create Sequence
        </button>
      </div>

      {isLoading && <p className="text-gray-500">Loading...</p>}

      {sequences && sequences.length === 0 && (
        <div className="rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
          <p className="text-gray-500">No sequences yet.</p>
          <p className="mt-1 text-sm text-gray-400">
            Create your first email sequence to get started.
          </p>
        </div>
      )}

      {sequences && sequences.length > 0 && (
        <div className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50 text-left text-sm font-medium text-gray-500">
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Steps</th>
                <th className="px-4 py-3">Created</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {sequences.map((seq) => (
                <tr
                  key={seq.id}
                  className="border-b border-gray-100 last:border-0"
                >
                  <td className="px-4 py-3 font-medium text-gray-800">
                    {seq.name}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {seq.step_count} step{seq.step_count !== 1 ? "s" : ""}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {new Date(seq.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() =>
                        navigate(
                          PATHS.SEQUENCE_EDIT.replace(
                            ":id",
                            String(seq.id)
                          )
                        )
                      }
                      className="mr-2 text-sm font-medium text-blue-600 hover:text-blue-800"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(seq.id, seq.name)}
                      disabled={deleteMutation.isPending}
                      className="text-sm font-medium text-red-600 hover:text-red-800 disabled:opacity-50"
                    >
                      Delete
                    </button>
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
