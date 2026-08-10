import { useEffect, useRef, useState, type PointerEvent as ReactPointerEvent } from "react";
import { useTranslation } from "react-i18next";
import { updatePosition, type Position } from "../../api/positions";
import type { Responsibility } from "../../api/responsibilities";
import type { Assignment } from "../../api/assignments";
import type { Raider } from "../../api/raiders";
import { getClassIcon, getClassIconBlobUrl } from "../../api/blizzard";
import { classId as blizzardClassId, roleColor } from "../../lib/wowClasses";
import { RAIDPLAN_IMAGES } from "../../lib/raidplanImages";
import { drawRaidPlanImage, downloadCanvasAsPng } from "../../lib/raidplanExport";

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
  const { t } = useTranslation();
  const images = RAIDPLAN_IMAGES[bossName];
  const [phase, setPhase] = useState(1);
  const [editMode, setEditMode] = useState(false);
  const [draggingId, setDraggingId] = useState<number | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);
  // Live drag position lives in a ref, not state — updating state on every
  // pointermove was re-rendering the whole overlay (re-filtering positions,
  // rebuilding the responsibility map, recomputing every token's label) on
  // every mouse-move event, which is what caused the pick-up/drag lag. The
  // dragged token's position is mutated directly on its DOM node instead;
  // only the FINAL position on pointerup goes through React/the API.
  const dragPosRef = useRef<{ x: number; y: number } | null>(null);
  // classId -> resolved icon URL, or null if resolution failed (e.g. no
  // Blizzard credentials configured) — null is cached too so a failed
  // lookup doesn't get retried on every render.
  const [classIcons, setClassIcons] = useState<Record<number, string | null>>({});

  useEffect(() => {
    const neededIds = new Set<number>();
    for (const position of positions) {
      if (position.responsibility_id === null) continue;
      const raiderIds = assignments
        .filter((a) => a.responsibility_id === position.responsibility_id)
        .map((a) => a.raider_id);
      if (raiderIds.length !== 1) continue; // ambiguous class with >1 raider, skip
      const raider = raiders.find((r) => r.id === raiderIds[0]);
      const cId = raider ? blizzardClassId(raider.wow_class) : null;
      if (cId !== null && !(cId in classIcons)) neededIds.add(cId);
    }
    if (neededIds.size === 0) return;

    let cancelled = false;
    Promise.all([...neededIds].map(async (cId) => [cId, await getClassIcon(cId)] as const)).then(
      (resolved) => {
        if (cancelled) return;
        setClassIcons((prev) => ({ ...prev, ...Object.fromEntries(resolved) }));
      },
    );
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [positions, assignments, raiders]);

  if (!images) {
    return <p className="text-text-muted text-sm mt-6">{t("raidPlanOverlay.noImage")}</p>;
  }

  const currentImage =
    images.length === 1 ? images[0] : images.find((img) => img.phases?.includes(phase)) ?? images[0];

  const responsibilityById = new Map(responsibilities.map((r) => [r.id, r]));

  function raiderNamesFor(responsibilityId: number): string {
    const raiderIds = assignments
      .filter((a) => a.responsibility_id === responsibilityId)
      .map((a) => a.raider_id);
    const names = raiders.filter((r) => raiderIds.includes(r.id)).map((r) => r.name);
    return names.length > 0 ? names.join(", ") : t("common.unassigned");
  }

  // Only resolves a class when exactly one raider is assigned — with 0 or
  // 2+ raiders there's no single class to represent.
  function singleAssignedClassIdFor(responsibilityId: number): number | null {
    const raiderIds = assignments
      .filter((a) => a.responsibility_id === responsibilityId)
      .map((a) => a.raider_id);
    if (raiderIds.length !== 1) return null;
    const raider = raiders.find((r) => r.id === raiderIds[0]);
    return raider ? blizzardClassId(raider.wow_class) : null;
  }

  function classIconFor(responsibilityId: number): string | null {
    const cId = singleAssignedClassIdFor(responsibilityId);
    return cId !== null ? (classIcons[cId] ?? null) : null;
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
    dragPosRef.current = { x: relX * IMAGE_WIDTH, y: relY * IMAGE_HEIGHT };
    // Direct DOM mutation — no setState, no re-render, no lag.
    event.currentTarget.style.left = `${relX * 100}%`;
    event.currentTarget.style.top = `${relY * 100}%`;
  }

  async function handlePointerUp() {
    const finalPos = dragPosRef.current;
    const id = draggingId;
    setDraggingId(null);
    dragPosRef.current = null;
    if (id === null || !finalPos) return;
    await updatePosition(id, { x: finalPos.x, y: finalPos.y });
    onPositionMoved();
  }

  async function handleExport() {
    const image = imgRef.current;
    if (!image) return;

    const baseTokens = visiblePositions
      .map((position) => {
        const responsibility = responsibilityById.get(position.responsibility_id!);
        if (!responsibility) return null;
        return {
          x: position.x,
          y: position.y,
          label: raiderNamesFor(responsibility.id),
          color: roleColor(position.requires_role ?? responsibility.requires_role ?? ""),
          classId: singleAssignedClassIdFor(responsibility.id),
        };
      })
      .filter((token): token is NonNullable<typeof token> => token !== null);

    // Blizzard's icon CDN sends no CORS header, so the export needs the
    // bytes proxied through our own origin (see api/blizzard.ts) — a
    // plain <img src> in the live overlay doesn't need this, only reading
    // pixels back out of a <canvas> does.
    const blobUrls: string[] = [];
    const tokens = await Promise.all(
      baseTokens.map(async ({ classId, ...token }) => {
        const iconUrl = classId !== null ? await getClassIconBlobUrl(classId) : null;
        if (iconUrl) blobUrls.push(iconUrl);
        return { ...token, iconUrl };
      }),
    );

    const canvas = document.createElement("canvas");
    await drawRaidPlanImage(canvas, image, tokens, IMAGE_WIDTH, IMAGE_HEIGHT);
    blobUrls.forEach((url) => URL.revokeObjectURL(url));

    const slug = bossName.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
    const suffix = images.length > 1 ? `-phase${phase}` : "";
    downloadCanvasAsPng(canvas, `${slug}${suffix}-raidplan.png`);
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
                {t("raidPlanOverlay.phase", { n: p })}
              </button>
            ))}
          </div>
        ) : (
          <div />
        )}

        <div className="flex gap-1.5">
          <button
            onClick={handleExport}
            className="px-3 py-1.5 rounded text-[12px] font-semibold border border-border-strong text-text-muted"
          >
            {t("raidPlanOverlay.downloadImage")}
          </button>
          <button
            onClick={() => setEditMode((v) => !v)}
            className={`px-3 py-1.5 rounded text-[12px] font-semibold border ${
              editMode
                ? "bg-accent text-accent-ink border-accent"
                : "border-border-strong text-text-muted"
            }`}
          >
            {editMode ? t("raidPlanOverlay.donePlacing") : t("raidPlanOverlay.editPositions")}
          </button>
        </div>
      </div>

      {editMode && (
        <p className="text-[12px] text-text-muted mb-2">{t("raidPlanOverlay.dragHint")}</p>
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
          <img
            ref={imgRef}
            src={currentImage.src}
            alt={bossName}
            crossOrigin="anonymous"
            className="w-full h-full object-cover"
          />
        </div>
        {visiblePositions.map((position) => {
          const responsibility = responsibilityById.get(position.responsibility_id!);
          if (!responsibility) return null;
          const label = raiderNamesFor(responsibility.id);
          const color = roleColor(position.requires_role ?? responsibility.requires_role ?? "");
          const iconUrl = classIconFor(responsibility.id);
          const isDragging = draggingId === position.id;

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
                left: `${(position.x / IMAGE_WIDTH) * 100}%`,
                top: `${(position.y / IMAGE_HEIGHT) * 100}%`,
                background: color,
                touchAction: editMode ? "none" : undefined,
              }}
            >
              {iconUrl && (
                <img
                  src={iconUrl}
                  alt=""
                  className="w-4 h-4 rounded-full border border-white/60 flex-shrink-0"
                  draggable={false}
                />
              )}
              {label}
            </div>
          );
        })}
      </div>
    </div>
  );
}
