import { useRef, useState } from "react";
import { useUploadCandidates } from "../hooks";
import { useCandidateLists, useAssignCandidatesToList } from "@/modules/candidate-lists/hooks";
import { CsvUploadResult } from "../types";

interface CandidateUploadProps {
  onUploadComplete: (result: CsvUploadResult) => void;
}

export function CandidateUpload({ onUploadComplete }: CandidateUploadProps) {
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
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h2 className="mb-3 text-lg font-semibold text-gray-800">
        Upload Candidates
      </h2>

      <div className="mb-3">
        <label
          htmlFor="list-name"
          className="mb-1 block text-sm font-medium text-gray-700"
        >
          List Name{" "}
          <span className="font-normal text-gray-400">(optional)</span>
        </label>
        <input
          id="list-name"
          type="text"
          list="candidate-lists"
          value={listInput}
          onChange={(e) => setListInput(e.target.value)}
          placeholder="Select or type a new list name"
          className="w-full rounded border border-gray-300 px-3 py-1.5 text-sm text-gray-800 placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
        <datalist id="candidate-lists">
          {lists?.map((list) => (
            <option key={list.id} value={list.name} />
          ))}
        </datalist>
      </div>

      <div className="flex items-center gap-3">
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          className="text-sm text-gray-500 file:mr-3 file:rounded file:border-0 file:bg-blue-50 file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-blue-700 hover:file:bg-blue-100"
        />
        <button
          onClick={handleUpload}
          disabled={!selectedFile || isPending}
          className="rounded bg-blue-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {isPending ? "Uploading..." : "Upload"}
        </button>
      </div>

      {uploadError && (
        <p className="mt-2 text-sm text-red-600">{uploadError}</p>
      )}

      {uploadResult && (
        <div className="mt-3 rounded border border-green-200 bg-green-50 px-3 py-2 text-sm text-green-700">
          <p>
            Processed {uploadResult.total_rows} rows:{" "}
            {uploadResult.candidates_created} new,{" "}
            {uploadResult.candidates_existing} existing
          </p>
          {uploadResult.errors.length > 0 && (
            <ul className="mt-1 list-inside list-disc text-amber-600">
              {uploadResult.errors.map((err, i) => (
                <li key={i}>{err}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      <p className="mt-2 text-xs text-gray-400">
        CSV must have an "email" column. Optional: "name" column.
      </p>
    </div>
  );
}
