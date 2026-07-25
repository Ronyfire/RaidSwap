import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getBoss, type Boss } from "../api/bosses";
import { getPositions, type Position } from "../api/positions";
import { getResponsibilities, type Responsibility } from "../api/responsibilities";
import { useRaidContext } from "../context/useRaidContext";

export function BossDetailPage() {
  const { id } = useParams<{ id: string }>();
  const bossId = Number(id);
  const { setSelectedBoss } = useRaidContext();

  const [boss, setBoss] = useState<Boss | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [responsibilities, setResponsibilities] = useState<Responsibility[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [bossData, positionsData, responsibilitiesData] = await Promise.all([
          getBoss(bossId),
          getPositions(bossId),
          getResponsibilities(),
        ]);
        setBoss(bossData);
        setSelectedBoss(bossData);
        setPositions(positionsData);
        setResponsibilities(responsibilitiesData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Error desconocido");
      }
    }
    load();
  }, [bossId, setSelectedBoss]);

  function responsibilityFor(position: Position): Responsibility | undefined {
    if (position.responsibility_id === null) return undefined;
    return responsibilities.find((r) => r.id === position.responsibility_id);
  }

  if (error) return <p role="alert">{error}</p>;
  if (!boss) return <p>Cargando...</p>;

  return (
    <section>
      <p>
        <Link to="/bosses">← Volver a Bosses</Link>
      </p>
      <h1>{boss.name}</h1>
      <p>
        {boss.raid} — orden {boss.order}
      </p>
      <p>
        <Link to={`/active-note/${boss.id}`}>Ver nota activa</Link>
      </p>

      <h2>Posiciones</h2>
      {positions.length === 0 ? (
        <p>Este boss todavía no tiene posiciones cargadas.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>X</th>
              <th>Y</th>
              <th>Rol requerido</th>
              <th>Responsabilidad</th>
            </tr>
          </thead>
          <tbody>
            {positions.map((position) => {
              const responsibility = responsibilityFor(position);
              return (
                <tr key={position.id}>
                  <td>{position.x}</td>
                  <td>{position.y}</td>
                  <td>{position.requires_role ?? "—"}</td>
                  <td>{responsibility ? responsibility.name : "Sin asignar"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </section>
  );
}
