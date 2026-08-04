import type { Position } from "../api/positions";
import type { Responsibility } from "../api/responsibilities";

export interface BossProgress {
  confirmed: number;
  total: number;
}

// "confirmed" is Responsibility.confidence, NOT assignment coverage — with
// the raid still on PTR, the metric that matters is "how much of this boss
// is confirmed live vs. still unverified" (#49), not "how much is assigned".
export function bossConfirmedProgress(
  bossId: number,
  positions: Position[],
  responsibilities: Responsibility[],
): BossProgress {
  const responsibilityById = new Map(responsibilities.map((r) => [r.id, r]));
  const seenResponsibilityIds = new Set<number>();
  let confirmed = 0;
  let total = 0;

  for (const position of positions) {
    if (position.boss_id !== bossId || position.responsibility_id === null) continue;
    if (seenResponsibilityIds.has(position.responsibility_id)) continue;
    seenResponsibilityIds.add(position.responsibility_id);

    const responsibility = responsibilityById.get(position.responsibility_id);
    if (!responsibility) continue;
    total += 1;
    if (responsibility.confidence === "confirmed") confirmed += 1;
  }

  return { confirmed, total };
}
