export interface SequenceStep {
  id: number;
  sequence_id: number;
  step_order: number;
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
  steps: SequenceStep[];
  created_at: string;
  updated_at: string;
}

export interface SequenceListItem {
  id: number;
  name: string;
  is_active: boolean;
  step_count: number;
  created_at: string;
  updated_at: string;
}

export interface SequenceStepInput {
  subject: string;
  body: string;
  delay_minutes: number;
}

export interface CreateSequencePayload {
  name: string;
  steps: SequenceStepInput[];
}

export interface UpdateSequencePayload {
  name?: string;
  steps?: SequenceStepInput[];
}
