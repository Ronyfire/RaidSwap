import { apiFetch } from "./client";

export interface MechanicProfile {
  id: number;
  raider_id: number;
  responsibility_id: number;
  proficiency_level: string;
}

export type MechanicProfileInput = Omit<MechanicProfile, "id">;

export function getMechanicProfiles(): Promise<MechanicProfile[]> {
  return apiFetch<MechanicProfile[]>("/api/mechanic-profiles");
}

export function getMechanicProfile(id: number): Promise<MechanicProfile> {
  return apiFetch<MechanicProfile>(`/api/mechanic-profiles/${id}`);
}

export function createMechanicProfile(data: MechanicProfileInput): Promise<MechanicProfile> {
  return apiFetch<MechanicProfile>("/api/mechanic-profiles", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateMechanicProfile(
  id: number,
  data: Partial<MechanicProfileInput>,
): Promise<MechanicProfile> {
  return apiFetch<MechanicProfile>(`/api/mechanic-profiles/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function deleteMechanicProfile(id: number): Promise<void> {
  return apiFetch<void>(`/api/mechanic-profiles/${id}`, { method: "DELETE" });
}
