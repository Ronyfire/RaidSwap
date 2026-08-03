import { apiFetch } from "./client";

export interface Raider {
  id: number;
  name: string;
  wow_class: string;
  spec: string;
  role: string;
  status: "active" | "bench";
}

export type RaiderInput = Omit<Raider, "id">;

export function getRaiders(): Promise<Raider[]> {
  return apiFetch<Raider[]>("/api/raiders");
}

export function getRaider(id: number): Promise<Raider> {
  return apiFetch<Raider>(`/api/raiders/${id}`);
}

export function createRaider(data: RaiderInput): Promise<Raider> {
  return apiFetch<Raider>("/api/raiders", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateRaider(id: number, data: Partial<RaiderInput>): Promise<Raider> {
  return apiFetch<Raider>(`/api/raiders/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function deleteRaider(id: number): Promise<void> {
  return apiFetch<void>(`/api/raiders/${id}`, { method: "DELETE" });
}
