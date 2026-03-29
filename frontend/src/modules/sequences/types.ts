export type StepType = "default" | "referral_handoff";

export interface SequenceStep {
  id: number;
  sequence_id: number;
  step_order: number;
  step_type: StepType;
  subject: string;
  body: string;
  delay_minutes: number;
  created_at: string;
  updated_at: string;
}

export interface Sequence {
  id: number;
  name: string;
  is_active: boolean;
  referral_list_id: number | null;
  referral_list_name: string | null;
  steps: SequenceStep[];
  created_at: string;
  updated_at: string;
}

export interface SequenceListItem {
  id: number;
  name: string;
  is_active: boolean;
  referral_list_id: number | null;
  referral_list_name: string | null;
  step_count: number;
  run_count: number;
  created_at: string;
  updated_at: string;
}

export interface SequenceStepInput {
  subject: string;
  body: string;
  delay_minutes: number;
  step_type?: StepType;
}

export interface CreateSequencePayload {
  name: string;
  steps: SequenceStepInput[];
  referral_list_id?: number | null;
  referral_list_name?: string | null;
}

export interface UpdateSequencePayload {
  name?: string;
  steps?: SequenceStepInput[];
  referral_list_id?: number | null;
  referral_list_name?: string | null;
}
