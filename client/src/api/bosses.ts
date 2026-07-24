import { apiFetch } from "./client";

export interface Boss {
  id: number;
  name: string;
  raid: string;
  order: number;
}

export type BossInput = Omit<Boss, "id">;

export function getBosses(): Promise<Boss[]> {
  return apiFetch<Boss[]>("/api/bosses");
}

export function getBoss(id: number): Promise<Boss> {
  return apiFetch<Boss>(`/api/bosses/${id}`);
}

export function createBoss(data: BossInput): Promise<Boss> {
  return apiFetch<Boss>("/api/bosses", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateBoss(id: number, data: Partial<BossInput>): Promise<Boss> {
  return apiFetch<Boss>(`/api/bosses/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function deleteBoss(id: number): Promise<void> {
  return apiFetch<void>(`/api/bosses/${id}`, { method: "DELETE" });
}
