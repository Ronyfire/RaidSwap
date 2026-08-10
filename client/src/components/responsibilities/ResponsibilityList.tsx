import { useTranslation } from "react-i18next";
import type { Responsibility } from "../../api/responsibilities";
import { roleColor } from "../../lib/wowClasses";

interface ResponsibilityListProps {
  responsibilities: Responsibility[];
}

export function ResponsibilityList({ responsibilities }: ResponsibilityListProps) {
  const { t, i18n } = useTranslation();

  if (responsibilities.length === 0) {
    return <p className="text-text-muted text-sm">{t("responsibilityList.noResponsibilities")}</p>;
  }

  return (
    <div className="flex flex-col gap-2.5">
      {responsibilities.map((responsibility) => {
        const description = i18n.language.startsWith("es")
          ? responsibility.description_es ?? responsibility.description_en
          : responsibility.description_en ?? responsibility.description_es;

        return (
          <div key={responsibility.id} className="bg-surface border border-border rounded-md p-4">
            <div className="flex items-start justify-between gap-3 mb-1.5">
              <div>
                <div className="font-heading font-semibold text-[15px]">{responsibility.name}</div>
                {responsibility.actor_label && (
                  <div className="text-[12px] text-text-muted mt-0.5">
                    {responsibility.actor_label}
                  </div>
                )}
              </div>
              <span
                className={`text-[10.5px] font-mono px-2 py-1 rounded flex-shrink-0 ${
                  responsibility.confidence === "confirmed"
                    ? "bg-success/20 text-success"
                    : "bg-warning/20 text-warning"
                }`}
              >
                {responsibility.confidence === "confirmed"
                  ? t("common.confirmed")
                  : t("common.unconfirmed")}
              </span>
            </div>

            {description && (
              <div className="text-[12.5px] text-text-muted mb-2.5">
                {description}
              </div>
            )}

            <div className="flex items-center gap-2 flex-wrap">
              {responsibility.requires_role && (
                <span
                  className="text-[11px] font-semibold px-2 py-1 rounded bg-nav-active"
                  style={{ color: roleColor(responsibility.requires_role) }}
                >
                  {responsibility.requires_role}
                </span>
              )}
              {responsibility.difficulty_variant && (
                <span className="text-[11px] font-mono text-text-muted px-2 py-1 rounded border border-border-muted">
                  {responsibility.difficulty_variant}
                </span>
              )}
              {responsibility.requires_prior_experience && (
                <span className="text-[11px] font-mono text-warning">
                  {t("responsibilityList.requiresPriorExperience")}
                </span>
              )}
            </div>

            {responsibility.note_line && (
              <div className="mt-2.5 bg-background border border-border-muted rounded px-3 py-2 font-mono text-[11.5px] text-text-muted">
                {responsibility.note_line}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
