import { useEffect, useState } from "react";
import { getBosses, type Boss } from "../api/bosses";
import { getPositions, type Position } from "../api/positions";
import { getResponsibilities, type Responsibility } from "../api/responsibilities";
import { BossList } from "../components/bosses/BossList";

export function BossesPage() {
  const [bosses, setBosses] = useState<Boss[]>([]);
  const [positions, setPositions] = useState<Position[]>([]);
  const [responsibilities, setResponsibilities] = useState<Responsibility[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [bossesData, positionsData, responsibilitiesData] = await Promise.all([
          getBosses(),
          getPositions(),
          getResponsibilities(),
        ]);
        setBosses(bossesData);
        setPositions(positionsData);
        setResponsibilities(responsibilitiesData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <section className="p-8 px-10">
      <div className="flex items-baseline justify-between gap-4 mb-2">
        <h1 className="font-heading text-2xl font-semibold">The Venomous Abyss</h1>
        <div className="text-xs font-mono text-text-muted whitespace-nowrap">
          {bosses.length} boss{bosses.length === 1 ? "" : "es"}
        </div>
      </div>
      <div className="text-[13px] text-text-muted mb-7">Bosses in this raid tier</div>

      {error && (
        <p role="alert" className="text-danger text-sm mb-4">
          {error}
        </p>
      )}

      {loading ? (
        <div className="grid grid-cols-[repeat(auto-fill,minmax(260px,1fr))] gap-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div
              key={i}
              className="bg-surface border border-border rounded-md p-4 flex gap-3.5 items-center"
            >
              <div className="w-13 h-13 rounded bg-nav-active flex-shrink-0 animate-pulse" />
              <div className="flex-1 flex flex-col gap-2">
                <div className="h-3.5 w-2/3 rounded bg-nav-active animate-pulse" />
                <div className="h-1.5 w-full rounded bg-nav-active animate-pulse" />
              </div>
            </div>
          ))}
        </div>
      ) : (
        <BossList bosses={bosses} positions={positions} responsibilities={responsibilities} />
      )}
    </section>
  );
}
