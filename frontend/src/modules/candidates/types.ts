export interface Candidate {
  id: number;
  email: string;
  name: string | null;
  created_at: string;
  updated_at: string;
}

export interface CsvUploadResult {
  total_rows: number;
  candidates_created: number;
  candidates_existing: number;
  candidates: Candidate[];
  errors: string[];
}

export interface CsvUploadParams {
  file: File;
  listId?: number;
  listName?: string;
}
