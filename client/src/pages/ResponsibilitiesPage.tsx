import { useEffect, useState } from "react";
import { getResponsibilities, type Responsibility } from "../api/responsibilities";
import { ResponsibilityList } from "../components/responsibilities/ResponsibilityList";

export function ResponsibilitiesPage() {
  const [responsibilities, setResponsibilities] = useState<Responsibility[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setResponsibilities(await getResponsibilities());
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <section className="p-8 px-10 max-w-[1100px]">
      <h1 className="font-heading text-2xl font-semibold mb-1">Responsibilities</h1>
      <div className="text-[13px] text-text-muted mb-7">
        Mechanic library for this raid tier — curated content, updated as encounters are verified
        on PTR.
      </div>

      {error && (
        <p role="alert" className="text-danger text-sm mb-4">
          {error}
        </p>
      )}

      {loading ? (
        <p className="text-text-muted text-sm">Loading...</p>
      ) : (
        <ResponsibilityList responsibilities={responsibilities} />
      )}
    </section>
  );
}
