import { apiFetch } from "./client";

export interface Assignment {
  id: number;
  raider_id: number;
  responsibility_id: number | null;
  position_id: number | null;
  active_note_ref: string | null;
}

export function getAssignments(): Promise<Assignment[]> {
  return apiFetch<Assignment[]>("/api/assignments");
}
