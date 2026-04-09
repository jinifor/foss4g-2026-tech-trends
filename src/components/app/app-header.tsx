import { Languages, type LucideIcon } from "lucide-react";
import { useTranslation } from "react-i18next";

import { cn } from "@/lib/utils";
import type { RouteId } from "@/lib/routes";
import type { SupportedLanguage } from "@/lib/format";

type RouteNavItem = {
  id: RouteId;
  label: string;
  description: string;
  icon: LucideIcon;
};

type AppHeaderProps = {
  activeRoute: RouteId;
  language: SupportedLanguage;
  routeItems: RouteNavItem[];
  onLanguageChange: (language: SupportedLanguage) => void;
  onNavigate: (route: RouteId) => void;
};

export function AppHeader({
  activeRoute,
  language,
  routeItems,
  onLanguageChange,
  onNavigate,
}: AppHeaderProps) {
  const { t } = useTranslation();

  return (
    <header className="glass-panel relative overflow-hidden">
      <div className="absolute inset-x-0 top-0 h-full bg-[radial-gradient(circle_at_top_left,rgba(23,126,137,0.18),transparent_56%),radial-gradient(circle_at_top_right,rgba(217,108,61,0.16),transparent_44%)]" />
      <div className="relative px-6 py-6 sm:px-8">
        <div className="space-y-5">
          <div className="flex items-start justify-between gap-4">
            <span className="metric-chip">{t("app.hub")}</span>
            <LanguageSelector value={language} onChange={onLanguageChange} />
          </div>
          <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div className="space-y-3">
              <h1 className="text-4xl leading-none sm:text-5xl">
                {t("app.titleLine1")}
                <br />
                {t("app.titleLine2")}
              </h1>
              <p className="max-w-3xl text-sm leading-6 text-muted-foreground">{t("app.description")}</p>
              <div>
                <a
                  href="https://2026.foss4g.org/en/"
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-white/75 px-4 py-2 text-sm font-semibold text-primary transition-colors hover:bg-primary/10"
                >
                  {t("app.officialSite")}
                </a>
              </div>
            </div>
          </div>
          <nav className="grid gap-3 [grid-template-columns:repeat(auto-fit,minmax(220px,1fr))]">
            {routeItems.map((item) => (
              <RouteButton
                key={item.id}
                item={item}
                active={item.id === activeRoute}
                onClick={() => onNavigate(item.id)}
              />
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
}

function LanguageSelector({
  value,
  onChange,
}: {
  value: SupportedLanguage;
  onChange: (language: SupportedLanguage) => void;
}) {
  const { t } = useTranslation();

  return (
    <label className="inline-flex items-center gap-2 rounded-full border border-primary/15 bg-white/80 px-3 py-2 text-sm shadow-sm">
      <Languages className="h-4 w-4 text-primary" />
      <span className="text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">{t("language.label")}</span>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value as SupportedLanguage)}
        className="bg-transparent text-sm font-semibold text-foreground outline-none"
      >
        <option value="ko">{t("language.options.ko")}</option>
        <option value="en">{t("language.options.en")}</option>
        <option value="ja">{t("language.options.ja")}</option>
      </select>
    </label>
  );
}

function RouteButton({
  item,
  active,
  onClick,
}: {
  item: RouteNavItem;
  active: boolean;
  onClick: () => void;
}) {
  const Icon = item.icon;

  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "flex min-h-[110px] w-full items-start gap-3 rounded-[1.5rem] border px-4 py-4 text-left transition-all duration-200",
        active
          ? "border-primary/70 bg-primary text-primary-foreground shadow-md shadow-primary/20"
          : "border-white/50 bg-white/65 hover:border-border/70 hover:bg-white/85",
      )}
    >
      <div
        className={cn(
          "rounded-full p-2",
          active ? "bg-white/15 text-primary-foreground" : "bg-muted text-muted-foreground",
        )}
      >
        <Icon className="h-4 w-4" />
      </div>
      <div>
        <div className="font-semibold">{item.label}</div>
        <div className={cn("mt-1 text-sm leading-5", active ? "text-primary-foreground/85" : "text-muted-foreground")}>
          {item.description}
        </div>
      </div>
    </button>
  );
}
