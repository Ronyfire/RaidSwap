import { useEffect, useState, type ReactNode } from "react";
import { useParams, Link } from "react-router-dom";
import { getBoss, getBossNote, type Boss } from "../api/bosses";
import { getPositions } from "../api/positions";
import { getResponsibilities, type Responsibility } from "../api/responsibilities";
import { getAssignments, type Assignment } from "../api/assignments";
import { getRaiders, type Raider } from "../api/raiders";
import { useRaidContext } from "../context/useRaidContext";
import { classColor } from "../lib/wowClasses";
import { AgentChat } from "../components/agent/AgentChat";

const ICON_COLORS = [
  classColor("Warrior"),
  classColor("Mage"),
  classColor("Priest"),
  classColor("Rogue"),
  classColor("Druid"),
];

function iconColor(id: number): string {
  return ICON_COLORS[id % ICON_COLORS.length];
}

function parseNoteLine(noteLine: string): ReactNode[] {
  const parts: ReactNode[] = [];
  const pattern = /tag:([^;]+);/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  let key = 0;

  while ((match = pattern.exec(noteLine)) !== null) {
    if (match.index > lastIndex) {
      parts.push(noteLine.slice(lastIndex, match.index));
    }
    parts.push(
      <mark key={key++} className="bg-accent/30 text-accent px-1.5 py-0.5 rounded font-bold">
        {match[1]}
      </mark>,
    );
    lastIndex = pattern.lastIndex;
  }
  if (lastIndex < noteLine.length) {
    parts.push(noteLine.slice(lastIndex));
  }
  return parts;
}

type Tab = "assignments" | "notes";

export function BossDetailPage() {
  const { id } = useParams<{ id: string }>();
  const bossId = Number(id);
  const { setSelectedBoss } = useRaidContext();

  const [tab, setTab] = useState<Tab>("notes");
  const [boss, setBoss] = useState<Boss | null>(null);
  const [responsibilities, setResponsibilities] = useState<Responsibility[]>([]);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [raiders, setRaiders] = useState<Raider[]>([]);
  const [note, setNote] = useState("");
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    async function load() {
      try {
        const [bossData, positionsData, responsibilitiesData, assignmentsData, raidersData, noteData] =
          await Promise.all([
            getBoss(bossId),
            getPositions(bossId),
            getResponsibilities(),
            getAssignments(),
            getRaiders(),
            getBossNote(bossId),
          ]);

        const responsibilityIds = new Set(
          positionsData
            .map((p) => p.responsibility_id)
            .filter((responsibilityId): responsibilityId is number => responsibilityId !== null),
        );
        const bossResponsibilities = responsibilitiesData.filter((r) =>
          responsibilityIds.has(r.id),
        );

        setBoss(bossData);
        setSelectedBoss(bossData);
        setResponsibilities(bossResponsibilities);
        setAssignments(assignmentsData);
        setRaiders(raidersData);
        setNote(noteData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      }
    }
    load();
  }, [bossId, setSelectedBoss, refreshKey]);

  async function copyNote() {
    await navigator.clipboard.writeText(note);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  function raidersFor(responsibilityId: number): Raider[] {
    const raiderIds = assignments
      .filter((a) => a.responsibility_id === responsibilityId)
      .map((a) => a.raider_id);
    return raiders.filter((r) => raiderIds.includes(r.id));
  }

  if (error) return <p className="p-8 text-danger text-sm">{error}</p>;
  if (!boss) return <p className="p-8 text-text-muted text-sm">Loading...</p>;

  const tabClass = (active: boolean) =>
    `px-3.5 py-2 rounded-t text-[13px] font-semibold ${
      active ? "bg-surface text-text" : "text-text-muted"
    }`;

  return (
    <section>
      <div className="px-8 pt-6 flex items-center gap-3.5">
        <Link to="/bosses" className="text-text-muted text-[13px]">
          ← Bosses
        </Link>
        <div
          className="w-8 h-8 rounded flex-shrink-0 rotate-45"
          style={{ background: iconColor(boss.id) }}
        />
        <h1 className="font-heading text-xl font-semibold">{boss.name}</h1>
      </div>

      <div className="px-8 pt-3.5 flex gap-1">
        <button className={tabClass(tab === "assignments")} onClick={() => setTab("assignments")}>
          Assignments
        </button>
        <button className={tabClass(tab === "notes")} onClick={() => setTab("notes")}>
          Notes
        </button>
      </div>

      <div className="p-8 pt-0">
        {tab === "assignments" && (
          <div className="mt-6 max-w-[420px]">
            <AgentChat onApplied={() => setRefreshKey((k) => k + 1)} bossId={bossId} />
          </div>
        )}

        {tab === "notes" && note && (
          <div className="mt-6">
            <div className="flex items-center justify-between mb-1.5">
              <div className="font-heading font-semibold text-[13.5px]">Export note (MRT/NSRT)</div>
              <button
                onClick={copyNote}
                className="text-[12px] font-semibold px-2.5 py-1 rounded border border-border-strong text-text-muted"
              >
                {copied ? "Copied!" : "Copy"}
              </button>
            </div>
            <pre className="bg-background border border-border-muted rounded px-3 py-2.5 font-mono text-[12px] leading-6 text-text-muted whitespace-pre-wrap">
              {note}
            </pre>
          </div>
        )}

        {tab === "notes" &&
          (responsibilities.length === 0 ? (
            <p className="text-text-muted text-sm mt-6">This boss has no responsibilities yet.</p>
          ) : (
            <div className="flex flex-col gap-2.5 mt-6">
              {responsibilities.map((responsibility) => {
                const assignedRaiders = raidersFor(responsibility.id);
                return (
                  <div
                    key={responsibility.id}
                    className="bg-surface border border-border rounded-md p-4"
                  >
                    <div className="font-heading font-semibold text-[15px] mb-1.5">
                      {responsibility.name}
                    </div>
                    {responsibility.note_line ? (
                      <div className="bg-background border border-border-muted rounded px-3 py-2.5 font-mono text-[12px] leading-7 text-text-muted mb-2.5">
                        {parseNoteLine(responsibility.note_line)}
                      </div>
                    ) : (
                      <div className="text-[12px] text-text-faint italic mb-2.5">No note</div>
                    )}
                    <div className="text-[12.5px] text-text-muted">
                      {assignedRaiders.length > 0
                        ? assignedRaiders.map((r) => r.name).join(", ")
                        : "Unassigned"}
                    </div>
                  </div>
                );
              })}
            </div>
          ))}
      </div>
    </section>
  );
}
