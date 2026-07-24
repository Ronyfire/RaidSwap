import { apiFetch } from "./client";

export interface Position {
  id: number;
  x: number;
  y: number;
  boss_id: number;
  requires_role: string | null;
  responsibility_id: number | null;
}

export type PositionInput = Omit<Position, "id">;

export function getPositions(bossId?: number): Promise<Position[]> {
  const query = bossId !== undefined ? `?boss_id=${bossId}` : "";
  return apiFetch<Position[]>(`/api/positions${query}`);
}

export function getPosition(id: number): Promise<Position> {
  return apiFetch<Position>(`/api/positions/${id}`);
}

export function createPosition(data: PositionInput): Promise<Position> {
  return apiFetch<Position>("/api/positions", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updatePosition(id: number, data: Partial<PositionInput>): Promise<Position> {
  return apiFetch<Position>(`/api/positions/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function deletePosition(id: number): Promise<void> {
  return apiFetch<void>(`/api/positions/${id}`, { method: "DELETE" });
}
