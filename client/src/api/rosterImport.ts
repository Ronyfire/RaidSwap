import { apiFetch } from "./client";

export interface RosterEntry {
  name: string;
  wow_class: string;
  spec: string;
  role: string;
}

export interface RosterImportResult {
  created: string[];
  updated: string[];
}

export function previewWowAuditRoster(data: {
  region: string;
  realm: string;
  guild: string;
  team: string;
}): Promise<{ entries: RosterEntry[] }> {
  return apiFetch("/api/roster-import/wowaudit/preview", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function previewPastedRoster(
  text: string,
): Promise<{ entries: RosterEntry[]; skipped_lines: number }> {
  return apiFetch("/api/roster-import/paste/preview", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export function confirmRosterImport(entries: RosterEntry[]): Promise<RosterImportResult> {
  return apiFetch("/api/roster-import/confirm", {
    method: "POST",
    body: JSON.stringify({ entries }),
  });
}
