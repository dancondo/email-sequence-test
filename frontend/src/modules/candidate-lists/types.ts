export interface CandidateList {
  id: number;
  name: string;
}

export interface AssignCandidatesParams {
  listId?: number;
  listName?: string;
  candidateIds: number[];
}
