import { useTranslation } from "react-i18next";

const LANGUAGES = ["en", "es"] as const;

export function LanguageToggle() {
  const { i18n } = useTranslation();
  const current = i18n.resolvedLanguage;

  return (
    <div className="fixed top-4 right-5 z-20 flex gap-1 bg-surface border border-border rounded px-1 py-1">
      {LANGUAGES.map((lang) => (
        <button
          key={lang}
          onClick={() => i18n.changeLanguage(lang)}
          className={`px-2 py-0.5 rounded text-[11px] font-bold uppercase ${
            current === lang ? "bg-accent text-accent-ink" : "text-text-muted"
          }`}
        >
          {lang}
        </button>
      ))}
    </div>
  );
}
