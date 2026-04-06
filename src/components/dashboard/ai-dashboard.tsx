import { useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  LabelList,
  ResponsiveContainer,
  Treemap,
  Tooltip as RechartsTooltip,
  XAxis,
  YAxis,
} from "recharts";

import { KeywordNetwork } from "@/components/dashboard/keyword-network";
import { WordCloud } from "@/components/dashboard/word-cloud";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartContainer, ChartTooltipContent } from "@/components/ui/chart";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useTranslation } from "react-i18next";
import type { AiDashboardData, AiExplorerPresentation, ClusterGroup, NetworkLink, NetworkNode } from "@/types/dashboard";

const numberFormat = new Intl.NumberFormat("en-US");
const percentFormat = new Intl.NumberFormat("en-US", {
  style: "percent",
  maximumFractionDigits: 1,
});

const aiSectionTabs = [
  { id: "overview", label: "Overview" },
  { id: "network", label: "Network" },
  { id: "explorer", label: "Explorer" },
] as const;

type AiSectionId = (typeof aiSectionTabs)[number]["id"];

export function AiDashboard({ data }: { data: AiDashboardData }) {
  const { t } = useTranslation();
  const [activeSection, setActiveSection] = useState<AiSectionId>("overview");
  const topAiKeyword = data.overview.topAiKeywords[0];
  const selectedKeywords = data.overview.topAiKeywords;
  const selectedContexts = data.overview.topContextKeywords.slice(0, 16);
  const chartHeight = Math.max(420, selectedKeywords.length * 34);
  const contextChartHeight = Math.max(360, selectedContexts.length * 34);
  const treemapLegend = Array.from(
    new Map(
      data.overview.treemap.map((item) => [item.category, { category: item.category, color: item.color }]),
    ).values(),
  );
  const randomizedSignalBriefs = useMemo(
    () =>
      data.overview.signalBriefs.map((brief) => ({
        ...brief,
        samples: pickRandomItems(brief.samples, 2),
      })),
    [data.overview.signalBriefs],
  );
  const aiNetwork = useMemo(() => {
    const aiClusterId = "ai-keywords";
    const contextClusterId = "context-keywords";
    const aiNodes = data.overview.topAiKeywords.slice(0, 10);
    const contextNodes = data.overview.topContextKeywords.slice(0, 10);
    const aiNodeIds = new Set(aiNodes.map((item) => item.keyword));
    const contextNodeIds = new Set(contextNodes.map((item) => item.keyword));

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
        color: "#177e89",
        total: aiNodes.reduce((sum, item) => sum + item.count, 0),
        keywords: aiNodes.map((item) => ({
          keyword: item.keyword,
          count: item.count,
        })),
      },
      {
        id: contextClusterId,
        name: t("aiInsight.networkContextKeywords"),
        color: "#d96c3d",
        total: contextNodes.reduce((sum, item) => sum + item.count, 0),
        keywords: contextNodes.map((item) => ({
          keyword: item.keyword,
          count: item.count,
        })),
      },
    ];

    return {
      nodes,
      links,
      clusters,
    };
  }, [data.flows.links, data.overview.topAiKeywords, data.overview.topContextKeywords, t]);

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <Badge>{t("aiInsight.badge")}</Badge>
              <CardTitle className="mt-3 text-3xl">{t("aiInsight.title")}</CardTitle>
              <CardDescription className="mt-2 max-w-4xl text-sm leading-6">
                {t("aiInsight.description")}
              </CardDescription>
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              <MetricBox label={t("aiInsight.scorecards.aiTalks.label")} value={data.meta.aiPresentationCount} />
              <MetricBox label={t("aiInsight.scorecards.aiShare.label")} value={data.meta.aiPresentationShare} format="percent" />
              <MetricBox label={t("aiInsight.scorecards.uniqueAiKeywords.label")} value={data.meta.uniqueAiKeywords} />
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-2 rounded-[1.5rem] border border-primary/20 bg-primary/12 px-3 py-3">
            {aiSectionTabs.map((tab) => (
              <Button
                key={tab.id}
                variant={activeSection === tab.id ? "default" : "secondary"}
                onClick={() => setActiveSection(tab.id)}
              >
                {t(`sections.${tab.id}`)}
              </Button>
            ))}
          </div>
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
                    {topAiKeyword.keyword} · {topAiKeyword.count} {t("common.talksUnit")}
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
                          <Badge variant="secondary">{translateAiCategory(t, brief.family)}</Badge>
                          <CardTitle className="mt-3 text-2xl">{brief.keyword}</CardTitle>
                          <CardDescription className="mt-1">
                            {numberFormat.format(brief.count)} {t("common.talksUnit")}
                          </CardDescription>
                        </div>
                        <div className="rounded-full bg-primary/10 px-3 py-2 text-sm font-semibold text-primary">
                          #{Math.max(1, data.overview.topAiKeywords.findIndex((item) => item.keyword === brief.keyword) + 1)}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <p className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                          {t("common.relatedTerms")}
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {brief.relatedContexts.map((item) => (
                            <Badge key={`${brief.keyword}-${item.keyword}`} variant="muted">
                              {item.keyword}
                              <span className="ml-1 opacity-70">{item.count}</span>
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <div>
                        <div className="mb-2 flex items-center gap-2">
                          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                            {t("common.representativeTalks")}
                          </p>
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
              <div className="max-h-[720px] overflow-auto pr-2">
                <ChartContainer
                  config={{
                    count: {
                      label: "Talk count",
                      color: "#177e89",
                    },
                  }}
                  className="min-h-[420px]"
                >
                  <ResponsiveContainer width="100%" height={chartHeight}>
                    <BarChart data={selectedKeywords} layout="vertical" margin={{ top: 8, right: 88, left: 16, bottom: 8 }}>
                      <CartesianGrid horizontal={false} stroke="rgba(23, 54, 64, 0.08)" />
                      <XAxis type="number" tickLine={false} axisLine={false} />
                      <YAxis
                        type="category"
                        dataKey="keyword"
                        width={220}
                        tickLine={false}
                        axisLine={false}
                        interval={0}
                        tick={{ fontSize: 12 }}
                      />
                      <RechartsTooltip
                        cursor={{ fill: "rgba(23,126,137,0.08)" }}
                        content={<ChartTooltipContent formatter={(value) => `${numberFormat.format(Number(value))} ${t("common.talksUnit")}`} />}
                      />
                      <Bar dataKey="count" radius={[0, 999, 999, 0]} fill="var(--color-count)">
                        <LabelList
                          dataKey="count"
                          position="right"
                          offset={10}
                          formatter={(value: number) => `${numberFormat.format(value)} ${t("common.talksUnit")}`}
                          className="fill-foreground text-xs font-semibold"
                        />
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </div>
              {!selectedKeywords.length ? <p className="mt-4 text-sm text-muted-foreground">{t("aiInsight.noAiKeywordData")}</p> : null}
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
                      <p className="font-semibold">{translateAiCategory(t, item.family)}</p>
                    </div>
                    <div className="mt-4 space-y-2 text-sm text-muted-foreground">
                      <div>{numberFormat.format(item.count)} {t("common.talksUnit")}</div>
                      <div>{percentFormat.format(item.share)} · {t("aiInsight.scorecards.aiTalks.label")}</div>
                      <div>{numberFormat.format(item.keywordCount)} · {t("aiInsight.scorecards.uniqueAiKeywords.caption")}</div>
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
              <ChartContainer
                config={{
                  count: {
                    label: "Talk count",
                    color: "#177e89",
                  },
                }}
                className="h-[420px]"
              >
                <ResponsiveContainer width="100%" height="100%">
                  <Treemap data={data.overview.treemap} dataKey="size" stroke="rgba(255,255,255,0.9)" fill="#177e89" content={<AiTreemapContent />}>
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
                      <span>{translateAiCategory(t, item.category)}</span>
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
              <div className="max-h-[720px] overflow-auto pr-2">
                <ChartContainer
                  config={{
                    count: {
                      label: "Talk count",
                      color: "#d96c3d",
                    },
                  }}
                  className="min-h-[360px]"
                >
                  <ResponsiveContainer width="100%" height={contextChartHeight}>
                    <BarChart data={selectedContexts} layout="vertical" margin={{ top: 8, right: 88, left: 16, bottom: 8 }}>
                      <CartesianGrid horizontal={false} stroke="rgba(23, 54, 64, 0.08)" />
                      <XAxis type="number" tickLine={false} axisLine={false} />
                      <YAxis
                        type="category"
                        dataKey="keyword"
                        width={220}
                        tickLine={false}
                        axisLine={false}
                        interval={0}
                        tick={{ fontSize: 12 }}
                      />
                      <RechartsTooltip
                        cursor={{ fill: "rgba(217,108,61,0.08)" }}
                        content={<ChartTooltipContent formatter={(value) => `${numberFormat.format(Number(value))} ${t("common.talksUnit")}`} />}
                      />
                      <Bar dataKey="count" radius={[0, 999, 999, 0]} fill="var(--color-count)">
                        <LabelList
                          dataKey="count"
                          position="right"
                          offset={10}
                          formatter={(value: number) => `${numberFormat.format(value)} ${t("common.talksUnit")}`}
                          className="fill-foreground text-xs font-semibold"
                        />
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </div>
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
            <AiExplorerTable rows={data.explorer.presentations} topAiKeywords={data.overview.topAiKeywords} />
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}

function MetricBox({ label, value, format }: { label: string; value: number; format?: "percent" }) {
  return (
    <div className="rounded-[1.25rem] border border-border/60 bg-white/75 p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{format === "percent" ? percentFormat.format(value) : numberFormat.format(value)}</p>
    </div>
  );
}

function AiTreemapContent(props: {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  name?: string;
  size?: number;
  fill?: string;
  category?: string;
  color?: string;
}) {
  const {
    x = 0,
    y = 0,
    width = 0,
    height = 0,
    name = "",
    size = 0,
    fill = "#177e89",
    category = "",
    color,
  } = props;
  const { t } = useTranslation();
  const resolvedFill = color || fill || "#177e89";
  if (width < 90 || height < 50) {
    return <g />;
  }

  return (
    <g>
      <title>{`${name} · ${translateAiCategory(t, category)} · ${numberFormat.format(size)} ${t("common.talksUnit")}`}</title>
      <rect x={x} y={y} width={width} height={height} rx={0} fill={resolvedFill} fillOpacity={0.9} />
      <text x={x + 14} y={y + 22} fill="white" fontSize="13" fontWeight="700">
        {name}
      </text>
      <text x={x + 14} y={y + 40} fill="rgba(255,255,255,0.92)" fontSize="12">
        {translateAiCategory(t, category)}
      </text>
      <text x={x + 14} y={y + 58} fill="rgba(255,255,255,0.88)" fontSize="12">
        {numberFormat.format(size)} {t("common.talksUnit")}
      </text>
    </g>
  );
}

function AiExplorerTable({
  rows,
  topAiKeywords,
}: {
  rows: AiExplorerPresentation[];
  topAiKeywords: Array<{ keyword: string; count: number }>;
}) {
  const { t } = useTranslation();
  const [query, setQuery] = useState("");
  const [activeAiKeyword, setActiveAiKeyword] = useState<string | null>(null);

  const filteredRows = useMemo(() => {
    const lowered = query.trim().toLowerCase();
    return rows.filter((row: AiExplorerPresentation) => {
      const matchesAiKeyword = activeAiKeyword ? row.aiKeywords.includes(activeAiKeyword) : true;
      const matchesQuery =
        lowered.length === 0 ||
        row.title.toLowerCase().includes(lowered) ||
        row.abstractSnippet.toLowerCase().includes(lowered) ||
        row.aiKeywords.some((keyword: string) => keyword.toLowerCase().includes(lowered)) ||
        row.contextKeywords.some((keyword: string) => keyword.toLowerCase().includes(lowered));
      return matchesAiKeyword && matchesQuery;
    });
  }, [activeAiKeyword, query, rows]);

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <Input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder={t("tables.ai.search")}
          className="lg:max-w-md"
        />
        <div className="flex flex-wrap gap-2">
          <Button variant={activeAiKeyword === null ? "default" : "outline"} size="sm" onClick={() => setActiveAiKeyword(null)}>
            {t("aiInsight.allAiTalks")}
          </Button>
          {topAiKeywords.slice(0, 12).map((item) => (
            <Button
              key={item.keyword}
              variant={activeAiKeyword === item.keyword ? "default" : "outline"}
              size="sm"
              onClick={() => setActiveAiKeyword(item.keyword)}
            >
              {item.keyword}
            </Button>
          ))}
        </div>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[70px]">{t("common.no")}</TableHead>
            <TableHead className="min-w-[260px]">{t("common.talkTitle")}</TableHead>
            <TableHead className="min-w-[340px]">{t("common.abstractSnippet")}</TableHead>
            <TableHead className="min-w-[220px]">{t("aiInsight.aiKeywords")}</TableHead>
            <TableHead className="min-w-[260px]">{t("aiInsight.contextKeywords")}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {filteredRows.map((row) => (
            <TableRow key={row.id}>
              <TableCell className="font-semibold text-muted-foreground">{row.id}</TableCell>
              <TableCell className="font-semibold">{row.title}</TableCell>
              <TableCell className="text-sm leading-6 text-muted-foreground">{row.abstractSnippet}</TableCell>
              <TableCell>
                <div className="flex flex-wrap gap-2">
                  {row.aiKeywords.map((keyword) => (
                    <Badge key={`${row.id}-${keyword}`} className="cursor-pointer" onClick={() => setActiveAiKeyword(keyword)}>
                      {keyword}
                    </Badge>
                  ))}
                </div>
              </TableCell>
              <TableCell>
                <div className="flex flex-wrap gap-2">
                  {row.contextKeywords.map((keyword) => (
                    <Badge key={`${row.id}-${keyword}`} variant="muted">
                      {keyword}
                    </Badge>
                  ))}
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <p className="text-sm text-muted-foreground">{t("common.results", { count: numberFormat.format(filteredRows.length) })}</p>
    </div>
  );
}

function translateAiCategory(t: ReturnType<typeof useTranslation>["t"], category: string) {
  const map: Record<string, string> = {
    "Generative & Language AI": "categories.genaiLanguage",
    "Machine Learning & Prediction": "categories.mlPrediction",
    "Vision & Detection": "categories.visionDetection",
    "Graph & Neural Models": "categories.graphNeural",
    "GeoAI & Agents": "categories.geoaiAgents",
    "AI Tooling": "categories.aiTooling",
    "General AI Signals": "categories.generalAiSignals",
    "Other AI Signals": "categories.otherAiSignals",
  };
  return map[category] ? t(map[category]) : category;
}

function pickRandomItems<T>(items: T[], count: number): T[] {
  if (items.length <= count) {
    return items;
  }

  const pool = [...items];
  for (let index = pool.length - 1; index > 0; index -= 1) {
    const randomIndex = Math.floor(Math.random() * (index + 1));
    [pool[index], pool[randomIndex]] = [pool[randomIndex], pool[index]];
  }

  return pool.slice(0, count);
}
