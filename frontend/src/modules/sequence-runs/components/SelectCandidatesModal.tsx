import { useState, useMemo } from "react";
import { Modal } from "@/shared/components/Modal";
import { useCandidates } from "@/modules/candidates/hooks";
import { useCandidateLists } from "@/modules/candidate-lists/hooks";

interface SelectCandidatesModalProps {
  open: boolean;
  onClose: () => void;
  onAdd: (candidateIds: number[]) => void;
  excludeCandidateIds: number[];
}

export function SelectCandidatesModal({
  open,
  onClose,
  onAdd,
  excludeCandidateIds,
}: SelectCandidatesModalProps) {
  const [selectedListIds, setSelectedListIds] = useState<number[]>([]);
  const [selectedCandidateIds, setSelectedCandidateIds] = useState<Set<number>>(
    new Set()
  );
  const [filterOpen, setFilterOpen] = useState(false);

  const { data: candidates, isLoading } = useCandidates(
    selectedListIds.length > 0 ? selectedListIds : undefined
  );
  const { data: lists } = useCandidateLists();

  const excludeSet = useMemo(
    () => new Set(excludeCandidateIds),
    [excludeCandidateIds]
  );

  const availableCandidates = useMemo(
    () => candidates?.filter((c) => !excludeSet.has(c.id)) ?? [],
    [candidates, excludeSet]
  );

  const allSelected =
    availableCandidates.length > 0 &&
    availableCandidates.every((c) => selectedCandidateIds.has(c.id));

  const toggleList = (id: number) => {
    setSelectedListIds((prev) =>
      prev.includes(id) ? prev.filter((v) => v !== id) : [...prev, id]
    );
  };

  const toggleCandidate = (id: number) => {
    setSelectedCandidateIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const toggleAll = () => {
    if (allSelected) {
      setSelectedCandidateIds(new Set());
    } else {
      setSelectedCandidateIds(new Set(availableCandidates.map((c) => c.id)));
    }
  };

  const handleAdd = () => {
    onAdd(Array.from(selectedCandidateIds));
    setSelectedCandidateIds(new Set());
    onClose();
  };

  const handleCancel = () => {
    setSelectedCandidateIds(new Set());
    onClose();
  };

  return (
    <Modal open={open} onClose={handleCancel} title="Select Candidates" className="max-w-3xl">
      {/* List filter */}
      {lists && lists.length > 0 && (
        <div className="relative mb-4">
          <button
            onClick={() => setFilterOpen(!filterOpen)}
            className="inline-flex items-center gap-2 rounded border border-outline-variant bg-surface-container-lowest px-4 py-2 text-sm font-medium text-on-surface hover:bg-surface-container-low"
          >
            List
            {selectedListIds.length > 0 && (
              <span className="rounded-full bg-secondary-container px-2 py-0.5 text-xs text-on-secondary-container">
                {selectedListIds.length}
              </span>
            )}
            <svg
              className={`h-4 w-4 transition-transform ${filterOpen ? "rotate-180" : ""}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>

          {filterOpen && (
            <div className="absolute z-10 mt-1 w-64 rounded-lg border border-outline-variant bg-surface-container-lowest py-1 shadow-lg">
              {lists.map((list) => (
                <label
                  key={list.id}
                  className="flex cursor-pointer items-center gap-3 px-4 py-2 text-sm text-on-surface hover:bg-surface-container-low"
                >
                  <input
                    type="checkbox"
                    checked={selectedListIds.includes(list.id)}
                    onChange={() => toggleList(list.id)}
                    className="rounded border-outline-variant"
                  />
                  {list.name}
                </label>
              ))}
              {selectedListIds.length > 0 && (
                <button
                  onClick={() => setSelectedListIds([])}
                  className="w-full border-t border-outline-variant px-4 py-2 text-left text-xs text-on-surface-variant hover:bg-surface-container-low"
                >
                  Clear filters
                </button>
              )}
            </div>
          )}
        </div>
      )}

      {/* Candidate table */}
      {isLoading && (
        <p className="py-8 text-center text-on-surface-variant">Loading...</p>
      )}

      {!isLoading && availableCandidates.length === 0 && (
        <p className="py-8 text-center text-on-surface-variant">
          {excludeCandidateIds.length > 0
            ? "All candidates are already enrolled."
            : "No candidates found."}
        </p>
      )}

      {!isLoading && availableCandidates.length > 0 && (
        <div className="max-h-96 overflow-y-auto rounded-lg border border-outline-variant">
          <table className="w-full">
            <thead className="sticky top-0">
              <tr className="border-b border-outline-variant bg-surface-container-low text-left text-xs font-medium uppercase tracking-wider text-on-surface-variant">
                <th className="px-4 py-3">
                  <input
                    type="checkbox"
                    checked={allSelected}
                    onChange={toggleAll}
                    className="rounded border-outline-variant"
                  />
                </th>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Email</th>
              </tr>
            </thead>
            <tbody>
              {availableCandidates.map((c) => (
                <tr
                  key={c.id}
                  onClick={() => toggleCandidate(c.id)}
                  className="cursor-pointer border-b border-outline-variant last:border-0 hover:bg-surface-container-low"
                >
                  <td className="px-4 py-3">
                    <input
                      type="checkbox"
                      checked={selectedCandidateIds.has(c.id)}
                      onChange={() => toggleCandidate(c.id)}
                      className="rounded border-outline-variant"
                    />
                  </td>
                  <td className="px-4 py-3 text-sm font-medium text-on-surface">
                    {c.name ?? "-"}
                  </td>
                  <td className="px-4 py-3 text-sm text-on-surface-variant">
                    {c.email}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Footer */}
      <div className="mt-4 flex items-center justify-between">
        <p className="text-sm text-on-surface-variant">
          {selectedCandidateIds.size} selected
        </p>
        <div className="flex items-center gap-3">
          <button
            onClick={handleCancel}
            className="rounded-lg border border-outline-variant px-4 py-2 text-sm font-medium text-on-surface hover:bg-surface-container-low"
          >
            Cancel
          </button>
          <button
            onClick={handleAdd}
            disabled={selectedCandidateIds.size === 0}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary/90 disabled:opacity-50"
          >
            Add
          </button>
        </div>
      </div>
    </Modal>
  );
}
