import { apiFetch } from "./client";

export interface Responsibility {
  id: number;
  name: string;
  actor_label: string | null;
  difficulty_variant: string | null;
  requires_role: string | null;
  requires_prior_experience: boolean;
  description: string | null;
  confidence: string;
  note_line: string | null;
  last_updated: string | null;
}

export type ResponsibilityInput = Omit<Responsibility, "id" | "last_updated">;

export function getResponsibilities(): Promise<Responsibility[]> {
  return apiFetch<Responsibility[]>("/api/responsibilities");
}

export function getResponsibility(id: number): Promise<Responsibility> {
  return apiFetch<Responsibility>(`/api/responsibilities/${id}`);
}

export function createResponsibility(data: ResponsibilityInput): Promise<Responsibility> {
  return apiFetch<Responsibility>("/api/responsibilities", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateResponsibility(
  id: number,
  data: Partial<ResponsibilityInput>,
): Promise<Responsibility> {
  return apiFetch<Responsibility>(`/api/responsibilities/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function deleteResponsibility(id: number): Promise<void> {
  return apiFetch<void>(`/api/responsibilities/${id}`, { method: "DELETE" });
}
