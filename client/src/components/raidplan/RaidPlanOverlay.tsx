import { useState } from "react";
import type { Position } from "../../api/positions";
import type { Responsibility } from "../../api/responsibilities";
import type { Assignment } from "../../api/assignments";
import type { Raider } from "../../api/raiders";
import { roleColor } from "../../lib/wowClasses";
import { RAIDPLAN_IMAGES } from "../../lib/raidplanImages";

interface RaidPlanOverlayProps {
  bossName: string;
  positions: Position[];
  responsibilities: Responsibility[];
  assignments: Assignment[];
  raiders: Raider[];
}

const PHASE_TAG = /ph:(\d+);/;

export function RaidPlanOverlay({
  bossName,
  positions,
  responsibilities,
  assignments,
  raiders,
}: RaidPlanOverlayProps) {
  const images = RAIDPLAN_IMAGES[bossName];
  const [phase, setPhase] = useState(1);

  if (!images) {
    return (
      <p className="text-text-muted text-sm mt-6">No raid plan image yet for this boss.</p>
    );
  }

  const currentImage =
    images.length === 1 ? images[0] : images.find((img) => img.phases?.includes(phase)) ?? images[0];

  const responsibilityById = new Map(responsibilities.map((r) => [r.id, r]));

  function raiderNamesFor(responsibilityId: number): string {
    const raiderIds = assignments
      .filter((a) => a.responsibility_id === responsibilityId)
      .map((a) => a.raider_id);
    const names = raiders.filter((r) => raiderIds.includes(r.id)).map((r) => r.name);
    return names.length > 0 ? names.join(", ") : "Unassigned";
  }

  // Phase filtering only matters when there's more than one image to switch
  // between (Ula'tek today) — otherwise every position shows regardless of
  // any ph: tag its responsibility's note_line carries.
  const visiblePositions = positions.filter((position) => {
    if (position.responsibility_id === null) return false;
    if (images.length === 1) return true;
    const responsibility = responsibilityById.get(position.responsibility_id);
    const match = responsibility?.note_line?.match(PHASE_TAG);
    return match ? Number(match[1]) === phase : true;
  });

  return (
    <div className="mt-6">
      {images.length > 1 && (
        <div className="flex gap-1.5 mb-3">
          {[1, 2, 3].map((p) => (
            <button
              key={p}
              onClick={() => setPhase(p)}
              className={`px-3 py-1.5 rounded text-[12px] font-semibold border ${
                phase === p
                  ? "bg-accent text-accent-ink border-accent"
                  : "border-border-strong text-text-muted"
              }`}
            >
              Phase {p}
            </button>
          ))}
        </div>
      )}

      <div
        className="relative w-full rounded-md overflow-hidden border border-border"
        style={{ aspectRatio: "1200 / 675" }}
      >
        <img src={currentImage.src} alt={bossName} className="w-full h-full object-cover" />
        {visiblePositions.map((position) => {
          const responsibility = responsibilityById.get(position.responsibility_id!);
          if (!responsibility) return null;
          const label = raiderNamesFor(responsibility.id);
          const color = roleColor(position.requires_role ?? responsibility.requires_role ?? "");

          return (
            <div
              key={position.id}
              title={`${responsibility.name}: ${label}`}
              className="absolute -translate-x-1/2 -translate-y-1/2 flex items-center gap-1 px-2 py-1 rounded-full text-[11px] font-bold text-white whitespace-nowrap shadow-md"
              style={{
                left: `${(position.x / 1200) * 100}%`,
                top: `${(position.y / 675) * 100}%`,
                background: color,
              }}
            >
              {label}
            </div>
          );
        })}
      </div>
    </div>
  );
}
