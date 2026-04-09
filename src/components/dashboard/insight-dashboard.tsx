import { useEffect, useMemo, useState } from "react";
import {
  Cell,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip as RechartsTooltip,
  Treemap,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
import { Expand, X } from "lucide-react";
import { useTranslation } from "react-i18next";

import { ClusterMap } from "@/components/dashboard/cluster-map";
import { MetricCard } from "@/components/dashboard/metric-card";
import { KeywordHeatmap } from "@/components/dashboard/keyword-heatmap";
import { KeywordNetwork } from "@/components/dashboard/keyword-network";
import { PresentationTable } from "@/components/dashboard/presentation-table";
import { RankedBarChart } from "@/components/dashboard/ranked-bar-chart";
import { SectionTabs } from "@/components/dashboard/section-tabs";
import { TreemapTileContent } from "@/components/dashboard/treemap-tile-content";
import { WordCloud } from "@/components/dashboard/word-cloud";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartContainer, type ChartConfig } from "@/components/ui/chart";
import { translateCategory } from "@/lib/categories";
import {
  buildKeywordRankMap,
  buildTreemapLegend,
  pickRandomItems,
  sliceTopItems,
  TOP_KEYWORD_LIMITS,
  type TopKeywordLimit,
} from "@/lib/dashboard-utils";
import { useLocaleFormatters } from "@/lib/format";
import { SECTION_IDS, type SectionId } from "@/lib/routes";
import type { DashboardData } from "@/types/dashboard";
import { buildInsightSummaryMetrics, type InsightCopy } from "@/components/dashboard/insight-copy";

const TREEMAP_COLORS = ["#177e89", "#d96c3d", "#7a8f3c", "#7c5cff", "#b74f6f", "#3f7cac"];
const PRIMARY_CHART_COLOR = "#177e89";

export function InsightDashboard({
  data,
  copy,
}: {
  data: DashboardData;
  copy: InsightCopy;
}) {
  const { t } = useTranslation();
  const [activeSection, setActiveSection] = useState<SectionId>("overview");
  const sectionTabs = useMemo(
    () => SECTION_IDS.map((id) => ({ id, label: t(`sections.${id}`) })),
    [t],
  );
  const summaryMetrics = useMemo(
    () => buildInsightSummaryMetrics(t, data, copy.summaryMode),
    [copy.summaryMode, data, t],
  );

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <Badge>{copy.kicker}</Badge>
              <CardTitle className="mt-3 text-3xl">{copy.routeLabel}</CardTitle>
              <CardDescription className="mt-2 max-w-4xl text-sm leading-6">{copy.summary}</CardDescription>
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              {summaryMetrics.map((item) => (
                <MetricCard key={item.label} label={item.label} value={item.value} format={item.format} />
              ))}
            </div>
          </div>
          <SectionTabs activeId={activeSection} items={sectionTabs} onChange={setActiveSection} />
        </CardHeader>
      </Card>

      {activeSection === "overview" ? <OverviewSection data={data} copy={copy} /> : null}
      {activeSection === "network" ? <NetworkSection data={data} copy={copy} /> : null}
      {activeSection === "explorer" ? <ExplorerSection data={data} copy={copy} /> : null}
    </div>
  );
}

function OverviewSection({ data, copy }: { data: DashboardData; copy: InsightCopy }) {
  const { t } = useTranslation();
  const { number } = useLocaleFormatters();
  const [limit, setLimit] = useState<TopKeywordLimit>(20);
  const [expanded, setExpanded] = useState(false);
  const topKeyword = data.overview.topKeywords[0];
  const selectedKeywords = useMemo(
    () => sliceTopItems(data.overview.topKeywords, limit),
    [data.overview.topKeywords, limit],
  );
  const rankMap = useMemo(
    () => buildKeywordRankMap(data.overview.topKeywords),
    [data.overview.topKeywords],
  );
  const randomizedCards = useMemo(
    () =>
      data.overview.cards.map((card) => ({
        ...card,
        samples: pickRandomItems(card.samples, 2),
      })),
    [data.overview.cards],
  );
  const treemapLegend = useMemo(
    () => buildTreemapLegend(data.distribution.treemap),
    [data.distribution.treemap],
  );
  const bubbleChartConfig = useMemo(
    () =>
      ({
        count: {
          label: t("common.mentions"),
          color: PRIMARY_CHART_COLOR,
        },
      }) satisfies ChartConfig,
    [t],
  );

  useEffect(() => {
    if (!expanded) {
      return;
    }

    // 전체 화면 워드클라우드가 열리면 스크롤과 ESC 닫기를 함께 제어한다.
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setExpanded(false);
      }
    };

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", handleKeyDown);

    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [expanded]);

  return (
    <div className="space-y-4">
      <Card className="overflow-hidden">
        <CardHeader>
          <div className="flex flex-wrap items-center gap-3">
            <Badge>{copy.cardsBadge}</Badge>
            {topKeyword ? (
              <Badge variant="secondary">
                {topKeyword.keyword} · {number.format(topKeyword.count)} {copy.unitLabel}
              </Badge>
            ) : null}
            {data.meta.excludedKeywords.length ? (
              <Badge variant="muted">
                {t("common.filtered")}: {data.meta.excludedKeywords.join(", ")}
              </Badge>
            ) : null}
          </div>
          <CardTitle className="text-3xl">{copy.cardsTitle}</CardTitle>
          <CardDescription>{copy.cardsDescription}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {randomizedCards.map((card) => (
              <Card key={card.keyword} className="border-white/60 bg-white/65 shadow-none">
                <CardHeader className="pb-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <CardTitle className="text-2xl">{card.keyword}</CardTitle>
                      <CardDescription className="mt-1">
                        {number.format(card.count)} {copy.unitLabel}
                      </CardDescription>
                    </div>
                    <div className="rounded-full bg-primary/10 px-3 py-2 text-sm font-semibold text-primary">
                      #{rankMap.get(card.keyword) ?? 1}
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">{t("common.relatedTerms")}</p>
                    <div className="flex flex-wrap gap-2">
                      {card.related.map((item) => (
                        <Badge key={`${card.keyword}-${item.keyword}`} variant="muted">
                          {item.keyword}
                          <span className="ml-1 opacity-70">{number.format(item.count)}</span>
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <div>
                    <div className="mb-2 flex items-center gap-2">
                      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">{t("common.representativeTalks")}</p>
                      <span className="text-[11px] text-muted-foreground/80">{t("common.randomTalksNote")}</span>
                    </div>
                    <ul className="space-y-2 text-sm leading-6 text-muted-foreground">
                      {card.samples.map((sample) => (
                        <li key={sample} className="rounded-2xl bg-muted/50 px-3 py-2">
                          {sample}
                        </li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-start justify-between gap-4">
            <div>
              <Badge>{copy.wordCloudBadge}</Badge>
              <CardTitle className="mt-3 text-3xl">{copy.wordCloudTitle}</CardTitle>
              <CardDescription>{copy.wordCloudDescription}</CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={() => setExpanded(true)}>
              <Expand className="h-4 w-4" />
              {t("common.expand")}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <WordCloud words={data.overview.wordCloud} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <Badge>{copy.topBadge}</Badge>
              <CardTitle className="mt-3 text-3xl">{copy.topTitle}</CardTitle>
              <CardDescription>{copy.topDescription}</CardDescription>
            </div>
            <div className="flex gap-2">
              {TOP_KEYWORD_LIMITS.map((value) => (
                <Button key={value} variant={limit === value ? "default" : "outline"} onClick={() => setLimit(value)}>
                  {t("common.topButton", { count: value })}
                </Button>
              ))}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <RankedBarChart
            data={selectedKeywords}
            color={PRIMARY_CHART_COLOR}
            emptyLabel={copy.topEmptyLabel}
            unitLabel={copy.unitLabel}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <Badge>{copy.bubbleBadge}</Badge>
          <CardTitle className="text-3xl">{copy.bubbleTitle}</CardTitle>
          <CardDescription>{copy.bubbleDescription}</CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer config={bubbleChartConfig} className="h-[480px]">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 16, right: 24, bottom: 16, left: 8 }}>
                <XAxis type="number" dataKey="x" name={t("common.bubbleTooltip.talkCount")} tickLine={false} axisLine={false} />
                <YAxis type="number" dataKey="y" name={t("common.bubbleTooltip.averageCompanionTerms")} tickLine={false} axisLine={false} />
                <ZAxis type="number" dataKey="z" range={[90, 1100]} />
                <RechartsTooltip cursor={{ strokeDasharray: "3 3" }} content={<BubbleTooltip unitLabel={copy.unitLabel} />} />
                <Scatter data={data.distribution.bubble} fill="var(--color-count)">
                  {data.distribution.bubble.map((entry, index) => (
                    <Cell key={entry.keyword} fill={TREEMAP_COLORS[index % TREEMAP_COLORS.length]} fillOpacity={0.88} />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </ChartContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <Badge>{copy.treemapBadge}</Badge>
          <CardTitle className="text-3xl">{copy.treemapTitle}</CardTitle>
          <CardDescription>{copy.treemapDescription}</CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer config={bubbleChartConfig} className="h-[420px]">
            <ResponsiveContainer width="100%" height="100%">
              <Treemap
                data={data.distribution.treemap}
                dataKey="size"
                stroke="rgba(255,255,255,0.9)"
                fill={PRIMARY_CHART_COLOR}
                content={
                  <TreemapTileContent
                    translateLabel={(category) => translateCategory(t, category)}
                  />
                }
              >
                {data.distribution.treemap.map((entry, index) => (
                  <Cell key={entry.name} fill={entry.color ?? TREEMAP_COLORS[index % TREEMAP_COLORS.length]} />
                ))}
              </Treemap>
            </ResponsiveContainer>
          </ChartContainer>
          <div className="mt-4 rounded-[1.5rem] border border-border/60 bg-white/70 p-4">
            <p className="mb-3 text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">{t("common.treemapLegend")}</p>
            <div className="flex flex-wrap gap-3">
              {treemapLegend.map((item) => (
                <div key={item.category} className="inline-flex items-center gap-2 rounded-full bg-white/80 px-3 py-2 text-sm">
                  <span className="h-3 w-3 rounded-full" style={{ backgroundColor: item.color }} />
                  <span>{translateCategory(t, item.category)}</span>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {expanded ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/45 px-4 py-4 backdrop-blur-sm sm:px-6" onClick={() => setExpanded(false)}>
          <div className="glass-panel flex h-[min(92vh,980px)] w-full max-w-[1500px] flex-col overflow-hidden" onClick={(event) => event.stopPropagation()}>
            <div className="flex items-start justify-between gap-4 border-b border-border/60 px-6 py-5">
              <div>
                <Badge>{copy.wordCloudBadge}</Badge>
                <h3 className="mt-3 text-3xl">{copy.expandTitle}</h3>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">{copy.expandDescription}</p>
              </div>
              <Button variant="outline" size="sm" onClick={() => setExpanded(false)}>
                <X className="h-4 w-4" />
                {t("common.close")}
              </Button>
            </div>
            <div className="flex-1 p-6">
              <WordCloud words={data.overview.wordCloud} maxWords={72} className="h-full min-h-[70vh] rounded-[2rem]" />
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function NetworkSection({ data, copy }: { data: DashboardData; copy: InsightCopy }) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <Badge>{copy.networkBadge}</Badge>
          <CardTitle className="text-3xl">{copy.networkTitle}</CardTitle>
          <CardDescription>{copy.networkDescription}</CardDescription>
        </CardHeader>
        <CardContent>
          <KeywordNetwork nodes={data.relationships.network.nodes} links={data.relationships.network.links} clusters={data.relationships.clusters} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <Badge>{copy.heatmapBadge}</Badge>
          <CardTitle className="text-3xl">{copy.heatmapTitle}</CardTitle>
          <CardDescription>{copy.heatmapDescription}</CardDescription>
        </CardHeader>
        <CardContent>
          <KeywordHeatmap labels={data.relationships.heatmap.labels} matrix={data.relationships.heatmap.matrix} max={data.relationships.heatmap.max} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <Badge>{copy.clusterBadge}</Badge>
          <CardTitle className="text-3xl">{copy.clusterTitle}</CardTitle>
          <CardDescription>{copy.clusterDescription}</CardDescription>
        </CardHeader>
        <CardContent>
          <ClusterMap clusters={data.relationships.clusters} />
        </CardContent>
      </Card>
    </div>
  );
}

function ExplorerSection({ data, copy }: { data: DashboardData; copy: InsightCopy }) {
  return (
    <Card>
      <CardHeader>
        <Badge>{copy.explorerBadge}</Badge>
        <CardTitle className="text-3xl">{copy.explorerTitle}</CardTitle>
        <CardDescription>{copy.explorerDescription}</CardDescription>
      </CardHeader>
      <CardContent>
        <PresentationTable rows={data.explorer.presentations} topKeywords={data.overview.topKeywords} />
      </CardContent>
    </Card>
  );
}

function BubbleTooltip({
  active,
  payload,
  unitLabel,
}: {
  active?: boolean;
  payload?: Array<{ payload?: { keyword?: string; x?: number; y?: number; connectionScore?: number; share?: number } }>;
  unitLabel: string;
}) {
  const { t } = useTranslation();
  const { number, percent } = useLocaleFormatters();

  if (!active || !payload?.length) {
    return null;
  }

  const datum = payload[0]?.payload;
  if (!datum) {
    return null;
  }

  return (
    <div className="rounded-2xl border border-white/60 bg-card/95 px-3 py-3 shadow-soft backdrop-blur">
      <div className="mb-2 text-sm font-semibold text-foreground">{datum.keyword ?? t("common.bubbleTooltip.unknownKeyword")}</div>
      <div className="space-y-1 text-sm text-muted-foreground">
        <div>{t("common.bubbleTooltip.talkCount")}: {number.format(Number(datum.x ?? 0))} {unitLabel}</div>
        <div>{t("common.bubbleTooltip.averageCompanionTerms")}: {Number(datum.y ?? 0).toFixed(2)}</div>
        <div>{t("common.bubbleTooltip.connectionScore")}: {number.format(Number(datum.connectionScore ?? 0))}</div>
        <div>{t("common.bubbleTooltip.talkShare")}: {percent.format(Number(datum.share ?? 0))}</div>
      </div>
    </div>
  );
}
