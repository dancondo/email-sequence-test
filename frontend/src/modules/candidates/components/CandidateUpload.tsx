import { useRef, useState } from "react";
import { useUploadCandidates } from "../hooks";
import { useCandidateLists, useAssignCandidatesToList } from "@/modules/candidate-lists/hooks";
import { CsvUploadResult } from "../types";

interface CandidateUploadProps {
  onUploadComplete: (result: CsvUploadResult) => void;
  onCancel?: () => void;
}

export function CandidateUpload({ onUploadComplete, onCancel }: CandidateUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const uploadMutation = useUploadCandidates();
  const assignMutation = useAssignCandidatesToList();
  const { data: lists } = useCandidateLists();

  const [listInput, setListInput] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<CsvUploadResult | null>(
    null
  );
  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedFile(e.target.files?.[0] ?? null);
    setUploadError(null);
    setUploadResult(null);
  };

  const handleUpload = () => {
    if (!selectedFile) return;

    setUploadError(null);
    setUploadResult(null);

    uploadMutation.mutate(selectedFile, {
      onSuccess: (result) => {
        setUploadResult(result);
        setSelectedFile(null);
        if (fileInputRef.current) fileInputRef.current.value = "";

        const trimmedInput = listInput.trim();
        if (trimmedInput && result.candidates.length > 0) {
          const matchedList = lists?.find((l) => l.name === trimmedInput);
          const candidateIds = result.candidates.map((c) => c.id);

          assignMutation.mutate(
            {
              listId: matchedList?.id,
              listName: matchedList ? undefined : trimmedInput,
              candidateIds,
            },
            {
              onSuccess: () => onUploadComplete(result),
              onError: (err) => {
                setUploadError(
                  `Upload succeeded but list assignment failed: ${
                    err instanceof Error ? err.message : "Unknown error"
                  }`
                );
                onUploadComplete(result);
              },
            }
          );
        } else {
          onUploadComplete(result);
        }
      },
      onError: (err) => {
        setUploadError(
          err instanceof Error ? err.message : "Upload failed"
        );
      },
    });
  };

  const isPending = uploadMutation.isPending || assignMutation.isPending;

  return (
    <div>
      <div className="mb-4">
        <label
          htmlFor="list-name"
          className="mb-1 block text-sm font-medium text-on-surface"
        >
          List Name{" "}
          <span className="font-normal text-on-surface-variant">(optional)</span>
        </label>
        <input
          id="list-name"
          type="text"
          list="candidate-lists"
          value={listInput}
          onChange={(e) => setListInput(e.target.value)}
          placeholder="Select or type a new list name"
          className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-sm text-on-surface placeholder-outline focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
        />
        <datalist id="candidate-lists">
          {lists?.map((list) => (
            <option key={list.id} value={list.name} />
          ))}
        </datalist>
      </div>

      <div>
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          className="text-sm text-on-surface-variant file:mr-3 file:rounded-lg file:border file:border-outline-variant file:bg-surface-container-low file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-on-surface hover:file:bg-surface-container-high"
        />
        <p className="mt-2 text-xs text-on-surface-variant">
          CSV must have an "email" column. Optional: "name" column.
        </p>
      </div>

      {uploadError && (
        <p className="mt-3 text-sm text-error">{uploadError}</p>
      )}

      {uploadResult && (
        <div className="mt-4 rounded-lg border border-secondary/20 bg-secondary/5 px-4 py-3 text-sm text-on-surface">
          <p>
            Processed {uploadResult.total_rows} rows:{" "}
            {uploadResult.candidates_created} new,{" "}
            {uploadResult.candidates_existing} existing
          </p>
          {uploadResult.errors.length > 0 && (
            <ul className="mt-1 list-inside list-disc text-error">
              {uploadResult.errors.map((err, i) => (
                <li key={i}>{err}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="mt-4 flex items-center justify-end gap-3">
        {onCancel && (
          <button
            onClick={onCancel}
            className="rounded-lg border border-outline-variant px-4 py-2 text-sm font-medium text-on-surface hover:bg-surface-container-low"
          >
            Cancel
          </button>
        )}
        <button
          onClick={handleUpload}
          disabled={!selectedFile || isPending}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:bg-primary/90 disabled:opacity-50"
        >
          {isPending ? "Uploading..." : "Upload"}
        </button>
      </div>
    </div>
  );
}
