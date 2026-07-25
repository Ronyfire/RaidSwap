import { useEffect, useState, type ReactNode } from "react";
import { useParams, Link } from "react-router-dom";
import { getBoss, type Boss } from "../api/bosses";
import { getPositions } from "../api/positions";
import { getResponsibilities, type Responsibility } from "../api/responsibilities";
import { getAssignments, type Assignment } from "../api/assignments";
import { getRaiders, type Raider } from "../api/raiders";

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
    parts.push(<mark key={key++}>{match[1]}</mark>);
    lastIndex = pattern.lastIndex;
  }
  if (lastIndex < noteLine.length) {
    parts.push(noteLine.slice(lastIndex));
  }
  return parts;
}

export function ActiveNotePage() {
  const { bossId: bossIdParam } = useParams<{ bossId: string }>();
  const bossId = Number(bossIdParam);
  const validBossId = bossIdParam !== undefined && !Number.isNaN(bossId);

  const [boss, setBoss] = useState<Boss | null>(null);
  const [responsibilities, setResponsibilities] = useState<Responsibility[]>([]);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [raiders, setRaiders] = useState<Raider[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!validBossId) return;

    async function load() {
      try {
        const [bossData, positionsData, responsibilitiesData, assignmentsData, raidersData] =
          await Promise.all([
            getBoss(bossId),
            getPositions(bossId),
            getResponsibilities(),
            getAssignments(),
            getRaiders(),
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
        setResponsibilities(bossResponsibilities);
        setAssignments(assignmentsData);
        setRaiders(raidersData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Error desconocido");
      }
    }
    load();
  }, [bossId, validBossId]);

  function raidersFor(responsibilityId: number): Raider[] {
    const raiderIds = assignments
      .filter((a) => a.responsibility_id === responsibilityId)
      .map((a) => a.raider_id);
    return raiders.filter((r) => raiderIds.includes(r.id));
  }

  if (!validBossId) {
    return (
      <p>
        Seleccioná un boss primero. <Link to="/bosses">Ver bosses</Link>
      </p>
    );
  }

  if (error) return <p role="alert">{error}</p>;
  if (!boss) return <p>Cargando...</p>;

  return (
    <section>
      <p>
        <Link to={`/bosses/${boss.id}`}>← Volver al detalle</Link>
      </p>
      <h1>Nota activa — {boss.name}</h1>

      {responsibilities.length === 0 ? (
        <p>Este boss todavía no tiene responsibilities con nota.</p>
      ) : (
        <dl>
          {responsibilities.map((responsibility) => {
            const assignedRaiders = raidersFor(responsibility.id);
            return (
              <div key={responsibility.id}>
                <dt>{responsibility.name}</dt>
                <dd>
                  {responsibility.note_line ? parseNoteLine(responsibility.note_line) : "Sin nota"}
                </dd>
                <dd>
                  {assignedRaiders.length > 0
                    ? assignedRaiders.map((r) => r.name).join(", ")
                    : "Sin asignar"}
                </dd>
              </div>
            );
          })}
        </dl>
      )}
    </section>
  );
}
