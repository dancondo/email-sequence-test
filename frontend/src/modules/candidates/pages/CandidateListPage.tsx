import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useCandidates } from "../hooks";
import { useCandidateLists } from "@/modules/candidate-lists/hooks";
import { PATHS } from "@/routes/paths";

export function CandidateListPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [selectedListIds, setSelectedListIds] = useState<number[]>(() =>
    searchParams.getAll("list_ids").map(Number).filter((n) => !isNaN(n))
  );
  const [filterOpen, setFilterOpen] = useState(false);

  const { data: candidates, isLoading } = useCandidates(
    selectedListIds.length > 0 ? selectedListIds : undefined
  );
  const { data: lists } = useCandidateLists();

  const toggleList = (id: number) => {
    setSelectedListIds((prev) =>
      prev.includes(id) ? prev.filter((v) => v !== id) : [...prev, id]
    );
  };

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      <header className="mb-10">
        <p className="text-xs font-semibold uppercase tracking-widest text-on-surface-variant">
          Candidates
        </p>
      </header>

      <div className="mb-8 flex items-end justify-between">
        <div>
          <h1 className="font-editorial text-4xl leading-tight text-on-surface">
            All candidates
          </h1>
          <p className="mt-2 text-sm text-on-surface-variant">
            Browse and filter your candidate database.
          </p>
        </div>
      </div>

      {/* List filter */}
      {lists && lists.length > 0 && (
        <div className="relative mb-6">
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
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
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

      {isLoading && <p className="text-on-surface-variant">Loading...</p>}

      {candidates && candidates.length === 0 && (
        <div className="rounded bg-surface-container-low px-12 py-16 text-center">
          <p className="font-editorial text-2xl text-on-surface-variant">
            {selectedListIds.length > 0
              ? "No candidates in the selected lists."
              : "No candidates yet."}
          </p>
          <p className="mt-2 text-sm text-outline">
            Upload a CSV to add candidates.
          </p>
        </div>
      )}

      {candidates && candidates.length > 0 && (
        <div className="overflow-hidden rounded-lg border border-outline-variant bg-surface-container-lowest shadow-ambient">
          <table className="w-full">
            <thead>
              <tr className="border-b border-outline-variant bg-surface-container-low text-left text-xs font-medium uppercase tracking-wider text-on-surface-variant">
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Runs</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((c) => (
                <tr
                  key={c.id}
                  onClick={() =>
                    navigate(
                      PATHS.CANDIDATE_DETAIL.replace(":id", String(c.id))
                    )
                  }
                  className="cursor-pointer border-b border-outline-variant last:border-0 hover:bg-surface-container-low"
                >
                  <td className="px-4 py-3 font-medium text-on-surface">
                    {c.name ?? "—"}
                  </td>
                  <td className="px-4 py-3 text-sm text-on-surface-variant">
                    {c.email}
                  </td>
                  <td className="px-4 py-3 text-sm text-on-surface-variant">
                    {c.run_count}
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
