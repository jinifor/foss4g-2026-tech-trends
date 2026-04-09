import { useMemo } from "react";
import { useTranslation } from "react-i18next";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { dashboardSummaries, type DashboardSummaryId } from "@/data/dashboard-summaries";
import { HOME_HIGHLIGHT_LIMIT, sliceTopItems } from "@/lib/dashboard-utils";
import { useLocaleFormatters } from "@/lib/format";
import type { RouteId } from "@/lib/routes";

const HOME_CARD_CONFIGS = [
  {
    id: "keyword",
    titleKey: "home.cards.keyword.title",
    descriptionKey: "home.cards.keyword.description",
    statKeys: ["home.stats.talks", "home.stats.uniqueKeywords", "home.stats.mentions"],
  },
  {
    id: "library",
    titleKey: "home.cards.library.title",
    descriptionKey: "home.cards.library.description",
    statKeys: ["home.stats.talks", "home.stats.uniqueLibraries", "home.stats.libraryMentions"],
  },
  {
    id: "cloud",
    titleKey: "home.cards.cloud.title",
    descriptionKey: "home.cards.cloud.description",
    statKeys: ["home.stats.cloudTalks", "home.stats.cloudKeywords", "home.stats.cloudMentions"],
  },
  {
    id: "threeD",
    titleKey: "home.cards.threeD.title",
    descriptionKey: "home.cards.threeD.description",
    statKeys: ["home.stats.threeDTalks", "home.stats.threeDKeywords", "home.stats.threeDMentions"],
  },
  {
    id: "ai",
    titleKey: "home.cards.ai.title",
    descriptionKey: "home.cards.ai.description",
    statKeys: ["home.stats.aiTalks", "home.stats.aiKeywords", "home.stats.contextKeywords"],
  },
] as const satisfies Array<{
  id: DashboardSummaryId;
  titleKey: string;
  descriptionKey: string;
  statKeys: [string, string, string];
}>;

export function HomePage({ onNavigate }: { onNavigate: (route: RouteId) => void }) {
  const { t } = useTranslation();
  const cards = useMemo(
    () =>
      HOME_CARD_CONFIGS.map((config) => {
        const summary = dashboardSummaries[config.id];

        // 홈 카드는 요약 데이터와 번역 키를 조합해 동일한 카드 구조로 만든다.
        return {
          id: config.id,
          title: t(config.titleKey),
          description: t(config.descriptionKey),
          stats: config.statKeys.map((labelKey, index) => ({
            label: t(labelKey),
            value: summary.stats[index],
          })),
          highlights: sliceTopItems(summary.highlights, HOME_HIGHLIGHT_LIMIT),
        };
      }),
    [t],
  );

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <Badge>{t("home.badge")}</Badge>
          <CardTitle className="text-3xl">{t("home.title")}</CardTitle>
          <CardDescription>{t("home.description")}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
            {cards.map((card) => (
              <HomeRouteCard
                key={card.id}
                title={card.title}
                description={card.description}
                stats={card.stats}
                highlights={card.highlights}
                onOpen={() => onNavigate(card.id)}
              />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function HomeRouteCard({
  title,
  description,
  stats,
  highlights,
  onOpen,
}: {
  title: string;
  description: string;
  stats: Array<{ label: string; value: number }>;
  highlights: Array<{ keyword: string; count: number }>;
  onOpen: () => void;
}) {
  const { t } = useTranslation();
  const { number } = useLocaleFormatters();

  return (
    <Card className="border-white/60 bg-white/70">
      <CardHeader>
        <Badge>{title}</Badge>
        <CardTitle className="text-3xl">{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="flex flex-col gap-3">
          {stats.map((item) => (
            <div key={item.label} className="flex items-center justify-between gap-4 rounded-[1.25rem] border border-border/60 bg-white/75 px-4 py-3">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">{item.label}</p>
              <p className="text-2xl font-semibold">{number.format(item.value)}</p>
            </div>
          ))}
        </div>
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">{t("home.topSignals")}</p>
          <div className="flex flex-wrap gap-2">
            {highlights.map((item) => (
              <Badge key={item.keyword} variant="muted">
                {item.keyword} ({number.format(item.count)})
              </Badge>
            ))}
          </div>
        </div>
        <Button onClick={onOpen}>{t("home.openDashboard")}</Button>
      </CardContent>
    </Card>
  );
}
