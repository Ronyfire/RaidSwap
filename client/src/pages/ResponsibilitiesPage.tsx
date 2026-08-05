import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { getResponsibilities, type Responsibility } from "../api/responsibilities";
import { ResponsibilityList } from "../components/responsibilities/ResponsibilityList";

export function ResponsibilitiesPage() {
  const { t } = useTranslation();
  const [responsibilities, setResponsibilities] = useState<Responsibility[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setResponsibilities(await getResponsibilities());
      } catch (err) {
        setError(err instanceof Error ? err.message : t("common.unknownError"));
      } finally {
        setLoading(false);
      }
    }
    load();
    // 't' deliberately excluded — a language toggle shouldn't refetch this page.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <section className="p-8 px-10 max-w-[1100px]">
      <h1 className="font-heading text-2xl font-semibold mb-1">{t("responsibilitiesPage.title")}</h1>
      <div className="text-[13px] text-text-muted mb-7">{t("responsibilitiesPage.subtitle")}</div>

      {error && (
        <p role="alert" className="text-danger text-sm mb-4">
          {error}
        </p>
      )}

      {loading ? (
        <p className="text-text-muted text-sm">{t("common.loading")}</p>
      ) : (
        <ResponsibilityList responsibilities={responsibilities} />
      )}
    </section>
  );
}
