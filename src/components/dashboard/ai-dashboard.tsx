import { useMemo, useState } from "react";
import { Cell, ResponsiveContainer, Treemap } from "recharts";
import { useTranslation } from "react-i18next";

import { AiPresentationTable } from "@/components/dashboard/ai-presentation-table";
import { KeywordNetwork } from "@/components/dashboard/keyword-network";
import { MetricCard } from "@/components/dashboard/metric-card";
import { RankedBarChart } from "@/components/dashboard/ranked-bar-chart";
import { SectionTabs } from "@/components/dashboard/section-tabs";
import { TreemapTileContent } from "@/components/dashboard/treemap-tile-content";
import { WordCloud } from "@/components/dashboard/word-cloud";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartContainer, type ChartConfig } from "@/components/ui/chart";
import { translateCategory } from "@/lib/categories";
import {
  buildKeywordRankMap,
  buildTreemapLegend,
  pickRandomItems,
  sliceTopItems,
} from "@/lib/dashboard-utils";
import { useLocaleFormatters } from "@/lib/format";
import { SECTION_IDS, type SectionId } from "@/lib/routes";
import type { AiDashboardData, ClusterGroup, NetworkLink, NetworkNode } from "@/types/dashboard";

const AI_PRIMARY_COLOR = "#177e89";
const AI_CONTEXT_COLOR = "#d96c3d";

export function AiDashboard({ data }: { data: AiDashboardData }) {
  const { t } = useTranslation();
  const { number, percent } = useLocaleFormatters();
  const [activeSection, setActiveSection] = useState<SectionId>("overview");
  const sectionTabs = useMemo(
    () => SECTION_IDS.map((id) => ({ id, label: t(`sections.${id}`) })),
    [t],
  );
  const topAiKeyword = data.overview.topAiKeywords[0];
  const selectedContexts = useMemo(
    () => sliceTopItems(data.overview.topContextKeywords, 16),
    [data.overview.topContextKeywords],
  );
  const treemapLegend = useMemo(
    () => buildTreemapLegend(data.overview.treemap),
    [data.overview.treemap],
  );
  const aiKeywordRankMap = useMemo(
    () => buildKeywordRankMap(data.overview.topAiKeywords),
    [data.overview.topAiKeywords],
  );
  const randomizedSignalBriefs = useMemo(
    () =>
      data.overview.signalBriefs.map((brief) => ({
        ...brief,
        samples: pickRandomItems(brief.samples, 2),
      })),
    [data.overview.signalBriefs],
  );
  const treemapChartConfig = useMemo(
    () =>
      ({
        count: {
          label: t("common.talksUnit"),
          color: AI_PRIMARY_COLOR,
        },
      }) satisfies ChartConfig,
    [t],
  );
  const aiNetwork = useMemo(() => {
    const aiClusterId = "ai-keywords";
    const contextClusterId = "context-keywords";
    const aiNodes = sliceTopItems(data.overview.topAiKeywords, 10);
    const contextNodes = sliceTopItems(data.overview.topContextKeywords, 10);
    const aiNodeIds = new Set(aiNodes.map((item) => item.keyword));
    const contextNodeIds = new Set(contextNodes.map((item) => item.keyword));

    // AI 키워드와 컨텍스트 키워드 사이의 연결만 골라 전용 네트워크를 만든다.
    const links: NetworkLink[] = data.flows.links
      .filter((link) => aiNodeIds.has(link.source) && contextNodeIds.has(link.target))
      .map((link) => ({
        source: link.source,
        target: link.target,
        count: link.value,
      }));

    const degreeByNode = new Map<string, number>();
    links.forEach((link) => {
      degreeByNode.set(link.source, (degreeByNode.get(link.source) ?? 0) + 1);
      degreeByNode.set(link.target, (degreeByNode.get(link.target) ?? 0) + 1);
    });

    const nodes: NetworkNode[] = [
      ...aiNodes.map((item) => ({
        id: item.keyword,
        keyword: item.keyword,
        count: item.count,
        degree: degreeByNode.get(item.keyword) ?? 0,
        cluster: aiClusterId,
      })),
      ...contextNodes.map((item) => ({
        id: item.keyword,
        keyword: item.keyword,
        count: item.count,
        degree: degreeByNode.get(item.keyword) ?? 0,
        cluster: contextClusterId,
      })),
    ];

    const clusters: ClusterGroup[] = [
      {
        id: aiClusterId,
        name: t("aiInsight.networkAiKeywords"),
        color: AI_PRIMARY_COLOR,
        total: aiNodes.reduce((sum, item) => sum + item.count, 0),
        keywords: aiNodes.map((item) => ({
          keyword: item.keyword,
          count: item.count,
        })),
      },
      {
        id: contextClusterId,
        name: t("aiInsight.networkContextKeywords"),
        color: AI_CONTEXT_COLOR,
        total: contextNodes.reduce((sum, item) => sum + item.count, 0),
        keywords: contextNodes.map((item) => ({
          keyword: item.keyword,
          count: item.count,
        })),
      },
    ];

    return { nodes, links, clusters };
  }, [data.flows.links, data.overview.topAiKeywords, data.overview.topContextKeywords, t]);

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <Badge>{t("aiInsight.badge")}</Badge>
              <CardTitle className="mt-3 text-3xl">{t("aiInsight.title")}</CardTitle>
              <CardDescription className="mt-2 max-w-4xl text-sm leading-6">{t("aiInsight.description")}</CardDescription>
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              <MetricCard label={t("aiInsight.scorecards.aiTalks.label")} value={data.meta.aiPresentationCount} />
              <MetricCard label={t("aiInsight.scorecards.aiShare.label")} value={data.meta.aiPresentationShare} format="percent" />
              <MetricCard label={t("aiInsight.scorecards.uniqueAiKeywords.label")} value={data.meta.uniqueAiKeywords} />
            </div>
          </div>
          <SectionTabs activeId={activeSection} items={sectionTabs} onChange={setActiveSection} />
        </CardHeader>
      </Card>

      {activeSection === "overview" ? (
        <>
          <Card>
            <CardHeader>
              <div className="flex flex-wrap items-center gap-3">
                <Badge>{t("aiInsight.signalBoardBadge")}</Badge>
                {topAiKeyword ? (
                  <Badge variant="secondary">
                    {topAiKeyword.keyword} · {number.format(topAiKeyword.count)} {t("common.talksUnit")}
                  </Badge>
                ) : null}
              </div>
              <CardTitle className="text-3xl">{t("aiInsight.signalBoardTitle")}</CardTitle>
              <CardDescription>{t("aiInsight.signalBoardDescription")}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {randomizedSignalBriefs.map((brief) => (
                  <Card key={brief.keyword} className="border-white/60 bg-white/65 shadow-none">
                    <CardHeader className="pb-4">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <Badge variant="secondary">{translateCategory(t, brief.family)}</Badge>
                          <CardTitle className="mt-3 text-2xl">{brief.keyword}</CardTitle>
                          <CardDescription className="mt-1">
                            {number.format(brief.count)} {t("common.talksUnit")}
                          </CardDescription>
                        </div>
                        <div className="rounded-full bg-primary/10 px-3 py-2 text-sm font-semibold text-primary">
                          #{aiKeywordRankMap.get(brief.keyword) ?? 1}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <p className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">{t("common.relatedTerms")}</p>
                        <div className="flex flex-wrap gap-2">
                          {brief.relatedContexts.map((item) => (
                            <Badge key={`${brief.keyword}-${item.keyword}`} variant="muted">
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
                          {brief.samples.map((sample) => (
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
              <Badge>{t("aiInsight.wordCloudBadge")}</Badge>
              <CardTitle className="text-3xl">{t("aiInsight.wordCloudTitle")}</CardTitle>
              <CardDescription>{t("aiInsight.wordCloudDescription")}</CardDescription>
            </CardHeader>
            <CardContent>
              <WordCloud words={data.overview.topAiKeywords} maxWords={40} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Badge>{t("aiInsight.topBadge")}</Badge>
              <CardTitle className="mt-3 text-3xl">{t("aiInsight.topTitle")}</CardTitle>
              <CardDescription>{t("aiInsight.topDescription")}</CardDescription>
            </CardHeader>
            <CardContent>
              <RankedBarChart
                data={data.overview.topAiKeywords}
                color={AI_PRIMARY_COLOR}
                emptyLabel={t("aiInsight.noAiKeywordData")}
                unitLabel={t("common.talksUnit")}
                yAxisWidth={220}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Badge>{t("aiInsight.familyBadge")}</Badge>
              <CardTitle className="text-3xl">{t("aiInsight.familyTitle")}</CardTitle>
              <CardDescription>{t("aiInsight.familyDescription")}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
                {data.families.radial.map((item) => (
                  <div key={item.familyId} className="rounded-[1.5rem] border border-border/60 bg-white/75 p-5">
                    <div className="flex items-center gap-3">
                      <span className="h-3 w-3 rounded-full" style={{ backgroundColor: item.color }} />
                      <p className="font-semibold">{translateCategory(t, item.family)}</p>
                    </div>
                    <div className="mt-4 space-y-2 text-sm text-muted-foreground">
                      <div>{number.format(item.count)} {t("common.talksUnit")}</div>
                      <div>{percent.format(item.share)} · {t("aiInsight.scorecards.aiTalks.label")}</div>
                      <div>{number.format(item.keywordCount)} · {t("aiInsight.scorecards.uniqueAiKeywords.caption")}</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Badge>{t("aiInsight.treemapBadge")}</Badge>
              <CardTitle className="text-3xl">{t("aiInsight.treemapTitle")}</CardTitle>
              <CardDescription>{t("aiInsight.treemapDescription")}</CardDescription>
            </CardHeader>
            <CardContent>
              <ChartContainer config={treemapChartConfig} className="h-[420px]">
                <ResponsiveContainer width="100%" height="100%">
                  <Treemap
                    data={data.overview.treemap}
                    dataKey="size"
                    stroke="rgba(255,255,255,0.9)"
                    fill={AI_PRIMARY_COLOR}
                    content={<TreemapTileContent translateLabel={(category) => translateCategory(t, category)} />}
                  >
                    {data.overview.treemap.map((entry) => (
                      <Cell key={entry.name} fill={entry.color} />
                    ))}
                  </Treemap>
                </ResponsiveContainer>
              </ChartContainer>
              <div className="mt-4 rounded-[1.5rem] border border-border/60 bg-white/70 p-4">
                <p className="mb-3 text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">{t("aiInsight.familyLegend")}</p>
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
        </>
      ) : null}

      {activeSection === "network" ? (
        <>
          <Card>
            <CardHeader>
              <Badge>{t("aiInsight.networkBadge")}</Badge>
              <CardTitle className="text-3xl">{t("aiInsight.networkTitle")}</CardTitle>
              <CardDescription>{t("aiInsight.networkDescription")}</CardDescription>
            </CardHeader>
            <CardContent>
              <KeywordNetwork nodes={aiNetwork.nodes} links={aiNetwork.links} clusters={aiNetwork.clusters} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Badge>{t("aiInsight.contextBadge")}</Badge>
              <CardTitle className="text-3xl">{t("aiInsight.contextTitle")}</CardTitle>
              <CardDescription>{t("aiInsight.contextDescription")}</CardDescription>
            </CardHeader>
            <CardContent>
              <RankedBarChart
                data={selectedContexts}
                color={AI_CONTEXT_COLOR}
                unitLabel={t("common.talksUnit")}
                yAxisWidth={220}
                minHeight={360}
                tooltipCursorFill="rgba(217,108,61,0.08)"
              />
            </CardContent>
          </Card>
        </>
      ) : null}

      {activeSection === "explorer" ? (
        <Card>
          <CardHeader>
            <Badge>{t("aiInsight.explorerBadge")}</Badge>
            <CardTitle className="text-3xl">{t("aiInsight.explorerTitle")}</CardTitle>
            <CardDescription>{t("aiInsight.explorerDescription")}</CardDescription>
          </CardHeader>
          <CardContent>
            <AiPresentationTable rows={data.explorer.presentations} topAiKeywords={data.overview.topAiKeywords} />
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
