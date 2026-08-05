import { useTranslation } from "react-i18next";

export function SoonBadge() {
  const { t } = useTranslation();
  return (
    <span className="ml-1.5 align-middle text-[9px] font-bold uppercase tracking-wide px-1.5 py-0.5 rounded-full bg-badge-future-bg text-badge-future-text">
      {t("nav.soon")}
    </span>
  );
}
