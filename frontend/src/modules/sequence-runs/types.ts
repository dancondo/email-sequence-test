import { Candidate } from "@/modules/candidates/types";

export type SequenceRunStatus = "draft" | "active" | "completed";
export type SequenceRunCandidateStatus =
  | "active"
  | "completed"
  | "replied"
  | "interested"
  | "not_interested"
  | "unsubscribed";
export type EventType =
  | "enrolled"
  | "email_scheduled"
  | "email_sent"
  | "email_failed"
  | "reply_received"
  | "reply_classified"
  | "reply_sent"
  | "referral_detected"
  | "completed"
  | "unsubscribed";

export interface SnapshotStep {
  step_order: number;
  subject: string;
  body: string;
  delay_minutes: number;
}

export interface Snapshot {
  name: string;
  steps: SnapshotStep[];
}

export interface SequenceRun {
  id: number;
  sequence_id: number;
  status: SequenceRunStatus;
  snapshot: Snapshot | null;
  started_at: string | null;
  candidate_count: number;
  created_at: string;
  updated_at: string;
}

export interface SequenceRunListItem {
  id: number;
  sequence_id: number;
  status: SequenceRunStatus;
  started_at: string | null;
  candidate_count: number;
  created_at: string;
  updated_at: string;
}

export interface SequenceRunCandidate {
  id: number;
  candidate_id: number;
  sequence_run_id: number;
  current_step_order: number;
  status: SequenceRunCandidateStatus;
  candidate: Candidate;
  created_at: string;
  updated_at: string;
}

export interface SequenceRunCandidateEvent {
  id: number;
  sequence_run_candidate_id: number;
  event_type: EventType;
  step_order: number | null;
  external_message_id: string | null;
  external_schedule_id: string | null;
  external_provider: string | null;
  metadata: Record<string, unknown> | null;
  occurred_at: string;
  created_at: string;
}

export interface SequenceRunDetail {
  id: number;
  sequence_id: number;
  status: SequenceRunStatus;
  snapshot: Snapshot | null;
  started_at: string | null;
  candidates: SequenceRunCandidate[];
  created_at: string;
  updated_at: string;
}

export interface AddCandidatesResult {
  added: number;
  already_enrolled: number;
  not_found: number;
}

export interface SequenceStartResult {
  message: string;
  enrollments_started: number;
}

export interface CandidateTimeline {
  candidate: SequenceRunCandidate;
  events: SequenceRunCandidateEvent[];
}

export interface SendReplyResult {
  message: string;
  event: SequenceRunCandidateEvent;
}

export interface Metrics {
  total_sent: number;
  total_replies: number;
  reply_rate: number;
  total_interested: number;
  interest_rate: number;
}
