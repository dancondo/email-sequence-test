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

export interface CandidateWithRunCount {
  id: number;
  email: string;
  name: string | null;
  run_count: number;
  created_at: string;
  updated_at: string;
}

export interface CandidateRunSummary {
  sequence_run_candidate_id: number;
  sequence_run_id: number;
  sequence_id: number;
  sequence_name: string;
  run_status: string;
  status: string;
  current_step_order: number;
  created_at: string;
}

export interface CandidateReferrer {
  id: number;
  email: string;
  name: string | null;
}

export interface CandidateDetail {
  id: number;
  email: string;
  name: string | null;
  referred_by_candidate_id: number | null;
  referred_by: CandidateReferrer | null;
  created_at: string;
  updated_at: string;
  runs: CandidateRunSummary[];
}