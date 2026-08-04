import { useRef, useState, type PointerEvent as ReactPointerEvent } from "react";
import { updatePosition, type Position } from "../../api/positions";
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
  onPositionMoved: () => void;
}

const PHASE_TAG = /ph:(\d+);/;
const IMAGE_WIDTH = 1200;
const IMAGE_HEIGHT = 675;

export function RaidPlanOverlay({
  bossName,
  positions,
  responsibilities,
  assignments,
  raiders,
  onPositionMoved,
}: RaidPlanOverlayProps) {
  const images = RAIDPLAN_IMAGES[bossName];
  const [phase, setPhase] = useState(1);
  const [editMode, setEditMode] = useState(false);
  const [draggingId, setDraggingId] = useState<number | null>(null);
  const [dragPos, setDragPos] = useState<{ x: number; y: number } | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

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

  function handlePointerDown(event: ReactPointerEvent<HTMLDivElement>, positionId: number) {
    if (!editMode) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    setDraggingId(positionId);
  }

  function handlePointerMove(event: ReactPointerEvent<HTMLDivElement>) {
    if (draggingId === null || !containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const relX = Math.min(1, Math.max(0, (event.clientX - rect.left) / rect.width));
    const relY = Math.min(1, Math.max(0, (event.clientY - rect.top) / rect.height));
    setDragPos({ x: relX * IMAGE_WIDTH, y: relY * IMAGE_HEIGHT });
  }

  async function handlePointerUp() {
    if (draggingId === null || !dragPos) {
      setDraggingId(null);
      return;
    }
    const id = draggingId;
    const finalPos = dragPos;
    setDraggingId(null);
    setDragPos(null);
    await updatePosition(id, { x: finalPos.x, y: finalPos.y });
    onPositionMoved();
  }

  return (
    <div className="mt-6">
      <div className="flex items-center justify-between mb-3">
        {images.length > 1 ? (
          <div className="flex gap-1.5">
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
        ) : (
          <div />
        )}

        <button
          onClick={() => setEditMode((v) => !v)}
          className={`px-3 py-1.5 rounded text-[12px] font-semibold border ${
            editMode
              ? "bg-accent text-accent-ink border-accent"
              : "border-border-strong text-text-muted"
          }`}
        >
          {editMode ? "Done placing" : "Edit positions"}
        </button>
      </div>

      {editMode && (
        <p className="text-[12px] text-text-muted mb-2">
          Drag a token to reposition it — saves automatically when you let go.
        </p>
      )}

      <div
        ref={containerRef}
        className="relative w-full"
        style={{ aspectRatio: `${IMAGE_WIDTH} / ${IMAGE_HEIGHT}` }}
      >
        {/* Image lives in its own clipped layer so rounded corners look
            right; tokens are direct children of the unclipped container so
            one placed exactly at the edge (x=0/1200, y=0/675) isn't half
            cut off by overflow-hidden and left un-clickable. */}
        <div className="absolute inset-0 rounded-md overflow-hidden border border-border">
          <img src={currentImage.src} alt={bossName} className="w-full h-full object-cover" />
        </div>
        {visiblePositions.map((position) => {
          const responsibility = responsibilityById.get(position.responsibility_id!);
          if (!responsibility) return null;
          const label = raiderNamesFor(responsibility.id);
          const color = roleColor(position.requires_role ?? responsibility.requires_role ?? "");
          const isDragging = draggingId === position.id && dragPos !== null;
          const x = isDragging ? dragPos.x : position.x;
          const y = isDragging ? dragPos.y : position.y;

          return (
            <div
              key={position.id}
              title={`${responsibility.name}: ${label}`}
              onPointerDown={(e) => handlePointerDown(e, position.id)}
              onPointerMove={handlePointerMove}
              onPointerUp={handlePointerUp}
              className={`absolute -translate-x-1/2 -translate-y-1/2 flex items-center gap-1 px-2 py-1 rounded-full text-[11px] font-bold text-white whitespace-nowrap shadow-md select-none ${
                editMode ? (isDragging ? "cursor-grabbing ring-2 ring-white" : "cursor-grab") : ""
              }`}
              style={{
                left: `${(x / IMAGE_WIDTH) * 100}%`,
                top: `${(y / IMAGE_HEIGHT) * 100}%`,
                background: color,
                touchAction: editMode ? "none" : undefined,
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
