import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  LabelList,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip as RechartsTooltip,
  Treemap,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
import {
  Boxes,
  Cloud,
  Expand,
  Home,
  Languages,
  Network,
  Search,
  Sparkles,
  X,
  type LucideIcon,
} from "lucide-react";
import { useTranslation } from "react-i18next";

import keywordDashboardData from "@/data/dashboard-data.json";
import libraryDashboardData from "@/data/library-dashboard-data.json";
import aiDashboardData from "@/data/ai-dashboard-data.json";
import cloudDashboardData from "@/data/cloud-dashboard-data.json";
import { AiDashboard } from "@/components/dashboard/ai-dashboard";
import { ClusterMap } from "@/components/dashboard/cluster-map";
import { KeywordHeatmap } from "@/components/dashboard/keyword-heatmap";
import { KeywordNetwork } from "@/components/dashboard/keyword-network";
import { PresentationTable } from "@/components/dashboard/presentation-table";
import { WordCloud } from "@/components/dashboard/word-cloud";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartContainer, ChartTooltipContent, type ChartConfig } from "@/components/ui/chart";
import { cn } from "@/lib/utils";
import type { AiDashboardData, DashboardData } from "@/types/dashboard";
import type { TFunction } from "i18next";
import type { NameType, ValueType } from "recharts/types/component/DefaultTooltipContent";
import type { TooltipProps } from "recharts";

type RouteId = "home" | "keyword" | "library" | "cloud" | "ai";
type SectionId = "overview" | "network" | "explorer";

type RouteItem = {
  id: RouteId;
  label: string;
  description: string;
  icon: LucideIcon;
};

type InsightCopy = {
  routeLabel: string;
  routeDescription: string;
  kicker: string;
  summary: string;
  summaryMode?: "default" | "cloud";
  disabledSections?: SectionId[];
  cardsBadge: string;
  cardsTitle: string;
  cardsDescription: string;
  wordCloudBadge: string;
  wordCloudTitle: string;
  wordCloudDescription: string;
  topBadge: string;
  topTitle: string;
  topDescription: string;
  longtailBadge: string;
  longtailTitle: string;
  longtailDescription: string;
  bubbleBadge: string;
  bubbleTitle: string;
  bubbleDescription: string;
  treemapBadge: string;
  treemapTitle: string;
  treemapDescription: string;
  networkBadge: string;
  networkTitle: string;
  networkDescription: string;
  heatmapBadge: string;
  heatmapTitle: string;
  heatmapDescription: string;
  clusterBadge: string;
  clusterTitle: string;
  clusterDescription: string;
  explorerBadge: string;
  explorerTitle: string;
  explorerDescription: string;
  expandTitle: string;
  expandDescription: string;
  unitLabel: string;
  topEmptyLabel: string;
};

const keywordData = keywordDashboardData as DashboardData;
const libraryData = libraryDashboardData as DashboardData;
const cloudData = cloudDashboardData as DashboardData;
const aiData = aiDashboardData as AiDashboardData;

const CATEGORY_KEY_MAP: Record<string, string> = {
  "Open Geo Stack": "categories.openGeoStack",
  "Mapping & Cartography": "categories.mappingCartography",
  "Standards & Data Infra": "categories.standardsDataInfra",
  "AI & Automation": "categories.aiAutomation",
  "EO / 3D / Survey": "categories.eo3dSurvey",
  "Community & Programs": "categories.communityPrograms",
  "Domain Signals": "categories.domainSignals",
  "Other keywords": "categories.otherKeywords",
  "Desktop GIS": "categories.desktopGis",
  "Web Mapping": "categories.webMapping",
  "Server & APIs": "categories.serverApis",
  "Database & Storage": "categories.databaseStorage",
  "Geo Data Processing": "categories.geoDataProcessing",
  "3D & EO Platforms": "categories.eoPlatforms",
  "Other Libraries": "categories.otherLibraries",
  "Generative & Language AI": "categories.genaiLanguage",
  "Machine Learning & Prediction": "categories.mlPrediction",
  "Vision & Detection": "categories.visionDetection",
  "Graph & Neural Models": "categories.graphNeural",
  "GeoAI & Agents": "categories.geoaiAgents",
  "AI Tooling": "categories.aiTooling",
  "General AI Signals": "categories.generalAiSignals",
  "Other AI Signals": "categories.otherAiSignals",
  "Cloud Platforms & Architecture": "categories.cloudPlatformsArchitecture",
  "Cloud Storage & Delivery": "categories.cloudStorageDelivery",
  "Orchestration & Operations": "categories.orchestrationOperations",
  "Runtime & Scalable Processing": "categories.runtimeScalableProcessing",
  "Cloud Tooling": "categories.cloudTooling",
  "Other Cloud Signals": "categories.otherCloudSignals",
};

function buildRouteItems(t: TFunction): RouteItem[] {
  return [
    { id: "home", label: t("routes.home.label"), description: t("routes.home.description"), icon: Home },
    { id: "keyword", label: t("routes.keyword.label"), description: t("routes.keyword.description"), icon: Sparkles },
    { id: "library", label: t("routes.library.label"), description: t("routes.library.description"), icon: Boxes },
    { id: "cloud", label: t("routes.cloud.label"), description: t("routes.cloud.description"), icon: Cloud },
    { id: "ai", label: t("routes.ai.label"), description: t("routes.ai.description"), icon: Network },
  ];
}

function buildSectionTabs(t: TFunction): Array<{ id: SectionId; label: string }> {
  return [
    { id: "overview", label: t("sections.overview") },
    { id: "network", label: t("sections.network") },
    { id: "explorer", label: t("sections.explorer") },
  ];
}

function buildInsightCopy(t: TFunction): Record<Exclude<RouteId, "home" | "ai">, InsightCopy> {
  return {
    keyword: {
      routeLabel: t("keywordInsight.routeLabel"),
      routeDescription: t("routes.keyword.description"),
      kicker: t("keywordInsight.kicker"),
      summary: t("keywordInsight.summary"),
      summaryMode: "default",
      cardsBadge: t("keywordInsight.cardsBadge"),
      cardsTitle: t("keywordInsight.cardsTitle"),
      cardsDescription: t("keywordInsight.cardsDescription"),
      wordCloudBadge: t("keywordInsight.wordCloudBadge"),
      wordCloudTitle: t("keywordInsight.wordCloudTitle"),
      wordCloudDescription: t("keywordInsight.wordCloudDescription"),
      topBadge: t("keywordInsight.topBadge"),
      topTitle: t("keywordInsight.topTitle"),
      topDescription: t("keywordInsight.topDescription"),
      longtailBadge: "",
      longtailTitle: "",
      longtailDescription: "",
      bubbleBadge: t("keywordInsight.bubbleBadge"),
      bubbleTitle: t("keywordInsight.bubbleTitle"),
      bubbleDescription: t("keywordInsight.bubbleDescription"),
      treemapBadge: t("keywordInsight.treemapBadge"),
      treemapTitle: t("keywordInsight.treemapTitle"),
      treemapDescription: t("keywordInsight.treemapDescription"),
      networkBadge: t("keywordInsight.networkBadge"),
      networkTitle: t("keywordInsight.networkTitle"),
      networkDescription: t("keywordInsight.networkDescription"),
      heatmapBadge: t("keywordInsight.heatmapBadge"),
      heatmapTitle: t("keywordInsight.heatmapTitle"),
      heatmapDescription: t("keywordInsight.heatmapDescription"),
      clusterBadge: t("keywordInsight.clusterBadge"),
      clusterTitle: t("keywordInsight.clusterTitle"),
      clusterDescription: t("keywordInsight.clusterDescription"),
      explorerBadge: t("keywordInsight.explorerBadge"),
      explorerTitle: t("keywordInsight.explorerTitle"),
      explorerDescription: t("keywordInsight.explorerDescription"),
      expandTitle: t("keywordInsight.expandTitle"),
      expandDescription: t("keywordInsight.expandDescription"),
      unitLabel: t("common.talksUnit"),
      topEmptyLabel: t("common.noKeywordData"),
    },
    library: {
      routeLabel: t("libraryInsight.routeLabel"),
      routeDescription: t("routes.library.description"),
      kicker: t("libraryInsight.kicker"),
      summary: t("libraryInsight.summary"),
      summaryMode: "default",
      cardsBadge: t("libraryInsight.cardsBadge"),
      cardsTitle: t("libraryInsight.cardsTitle"),
      cardsDescription: t("libraryInsight.cardsDescription"),
      wordCloudBadge: t("libraryInsight.wordCloudBadge"),
      wordCloudTitle: t("libraryInsight.wordCloudTitle"),
      wordCloudDescription: t("libraryInsight.wordCloudDescription"),
      topBadge: t("libraryInsight.topBadge"),
      topTitle: t("libraryInsight.topTitle"),
      topDescription: t("libraryInsight.topDescription"),
      longtailBadge: "",
      longtailTitle: "",
      longtailDescription: "",
      bubbleBadge: t("libraryInsight.bubbleBadge"),
      bubbleTitle: t("libraryInsight.bubbleTitle"),
      bubbleDescription: t("libraryInsight.bubbleDescription"),
      treemapBadge: t("libraryInsight.treemapBadge"),
      treemapTitle: t("libraryInsight.treemapTitle"),
      treemapDescription: t("libraryInsight.treemapDescription"),
      networkBadge: t("libraryInsight.networkBadge"),
      networkTitle: t("libraryInsight.networkTitle"),
      networkDescription: t("libraryInsight.networkDescription"),
      heatmapBadge: t("libraryInsight.heatmapBadge"),
      heatmapTitle: t("libraryInsight.heatmapTitle"),
      heatmapDescription: t("libraryInsight.heatmapDescription"),
      clusterBadge: t("libraryInsight.clusterBadge"),
      clusterTitle: t("libraryInsight.clusterTitle"),
      clusterDescription: t("libraryInsight.clusterDescription"),
      explorerBadge: t("libraryInsight.explorerBadge"),
      explorerTitle: t("libraryInsight.explorerTitle"),
      explorerDescription: t("libraryInsight.explorerDescription"),
      expandTitle: t("libraryInsight.expandTitle"),
      expandDescription: t("libraryInsight.expandDescription"),
      unitLabel: t("common.talksUnit"),
      topEmptyLabel: t("common.noLibraryData"),
    },
    cloud: {
      routeLabel: t("cloudInsight.routeLabel"),
      routeDescription: t("routes.cloud.description"),
      kicker: t("cloudInsight.kicker"),
      summary: t("cloudInsight.summary"),
      summaryMode: "cloud",
      cardsBadge: t("cloudInsight.cardsBadge"),
      cardsTitle: t("cloudInsight.cardsTitle"),
      cardsDescription: t("cloudInsight.cardsDescription"),
      wordCloudBadge: t("cloudInsight.wordCloudBadge"),
      wordCloudTitle: t("cloudInsight.wordCloudTitle"),
      wordCloudDescription: t("cloudInsight.wordCloudDescription"),
      topBadge: t("cloudInsight.topBadge"),
      topTitle: t("cloudInsight.topTitle"),
      topDescription: t("cloudInsight.topDescription"),
      longtailBadge: "",
      longtailTitle: "",
      longtailDescription: "",
      bubbleBadge: t("cloudInsight.bubbleBadge"),
      bubbleTitle: t("cloudInsight.bubbleTitle"),
      bubbleDescription: t("cloudInsight.bubbleDescription"),
      treemapBadge: t("cloudInsight.treemapBadge"),
      treemapTitle: t("cloudInsight.treemapTitle"),
      treemapDescription: t("cloudInsight.treemapDescription"),
      networkBadge: t("cloudInsight.networkBadge"),
      networkTitle: t("cloudInsight.networkTitle"),
      networkDescription: t("cloudInsight.networkDescription"),
      heatmapBadge: t("cloudInsight.heatmapBadge"),
      heatmapTitle: t("cloudInsight.heatmapTitle"),
      heatmapDescription: t("cloudInsight.heatmapDescription"),
      clusterBadge: t("cloudInsight.clusterBadge"),
      clusterTitle: t("cloudInsight.clusterTitle"),
      clusterDescription: t("cloudInsight.clusterDescription"),
      explorerBadge: t("cloudInsight.explorerBadge"),
      explorerTitle: t("cloudInsight.explorerTitle"),
      explorerDescription: t("cloudInsight.explorerDescription"),
      expandTitle: t("cloudInsight.expandTitle"),
      expandDescription: t("cloudInsight.expandDescription"),
      unitLabel: t("common.talksUnit"),
      topEmptyLabel: t("common.noCloudData"),
    },
  };
}

const barChartConfig = {
  count: {
    label: "Talk count",
    color: "#177e89",
  },
} satisfies ChartConfig;

const bubbleChartConfig = {
  count: {
    label: "Mentions",
    color: "#177e89",
  },
} satisfies ChartConfig;

const treemapColors = ["#177e89", "#d96c3d", "#7a8f3c", "#7c5cff", "#b74f6f", "#3f7cac"];
const numberFormat = new Intl.NumberFormat("en-US");
const percentFormat = new Intl.NumberFormat("en-US", {
  style: "percent",
  maximumFractionDigits: 1,
});

function getInitialRoute(): RouteId {
  const hash = window.location.hash.replace("#", "") as RouteId;
  return ["home", "keyword", "library", "cloud", "ai"].includes(hash) ? hash : "home";
}

export default function App() {
  const { t, i18n } = useTranslation();
  const [route, setRoute] = useState<RouteId>(getInitialRoute);
  const routeItems = useMemo(() => buildRouteItems(t), [t]);
  const sectionTabs = useMemo(() => buildSectionTabs(t), [t]);
  const insightCopy = useMemo(() => buildInsightCopy(t), [t]);

  useEffect(() => {
    const onHashChange = () => setRoute(getInitialRoute());
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  return (
    <div className="min-h-screen px-4 py-4 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-[1560px] space-y-4">
        <header className="glass-panel relative overflow-hidden">
          <div className="absolute inset-x-0 top-0 h-full bg-[radial-gradient(circle_at_top_left,rgba(23,126,137,0.18),transparent_56%),radial-gradient(circle_at_top_right,rgba(217,108,61,0.16),transparent_44%)]" />
          <div className="relative px-6 py-6 sm:px-8">
            <div className="space-y-5">
              <div className="flex items-start justify-between gap-4">
                <span className="metric-chip">{t("app.hub")}</span>
                <LanguageSelector
                  value={i18n.language.startsWith("ko") ? "ko" : i18n.language.startsWith("ja") ? "ja" : "en"}
                  onChange={(language) => {
                    void i18n.changeLanguage(language);
                  }}
                />
              </div>
              <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
                <div className="space-y-3">
                  <h1 className="text-4xl leading-none sm:text-5xl">
                    {t("app.titleLine1")}
                    <br />
                    {t("app.titleLine2")}
                  </h1>
                  <p className="max-w-3xl text-sm leading-6 text-muted-foreground">
                    {t("app.description")}
                  </p>
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
                    active={item.id === route}
                    onClick={() => {
                      window.location.hash = item.id;
                      setRoute(item.id);
                    }}
                  />
                ))}
              </nav>
            </div>
          </div>
        </header>

        {route === "home" ? (
          <HomePage
            onOpenKeyword={() => {
              window.location.hash = "keyword";
              setRoute("keyword");
            }}
            onOpenLibrary={() => {
              window.location.hash = "library";
              setRoute("library");
            }}
            onOpenCloud={() => {
              window.location.hash = "cloud";
              setRoute("cloud");
            }}
            onOpenAi={() => {
              window.location.hash = "ai";
              setRoute("ai");
            }}
          />
        ) : null}

        {route === "keyword" ? <InsightDashboard data={keywordData} copy={insightCopy.keyword} sectionTabs={sectionTabs} /> : null}
        {route === "library" ? <InsightDashboard data={libraryData} copy={insightCopy.library} sectionTabs={sectionTabs} /> : null}
        {route === "cloud" ? <InsightDashboard data={cloudData} copy={insightCopy.cloud} sectionTabs={sectionTabs} /> : null}
        {route === "ai" ? <AiDashboard data={aiData} /> : null}
      </div>
    </div>
  );
}

function LanguageSelector({
  value,
  onChange,
}: {
  value: "en" | "ko" | "ja";
  onChange: (language: "en" | "ko" | "ja") => void;
}) {
  const { t } = useTranslation();

  return (
    <label className="inline-flex items-center gap-2 rounded-full border border-primary/15 bg-white/80 px-3 py-2 text-sm shadow-sm">
      <Languages className="h-4 w-4 text-primary" />
      <span className="text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">{t("language.label")}</span>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value as "en" | "ko" | "ja")}
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
  item: RouteItem;
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

function HomePage({
  onOpenKeyword,
  onOpenLibrary,
  onOpenCloud,
  onOpenAi,
}: {
  onOpenKeyword: () => void;
  onOpenLibrary: () => void;
  onOpenCloud: () => void;
  onOpenAi: () => void;
}) {
  const { t } = useTranslation();
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <Badge>{t("home.badge")}</Badge>
          <CardTitle className="text-3xl">{t("home.title")}</CardTitle>
          <CardDescription>{t("home.description")}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 xl:grid-cols-4">
            <HomeRouteCard
              title={t("home.cards.keyword.title")}
              description={t("home.cards.keyword.description")}
              stats={[
                { label: t("home.stats.talks"), value: keywordData.meta.totalPresentations },
                { label: t("home.stats.uniqueKeywords"), value: keywordData.meta.uniqueKeywords },
                { label: t("home.stats.mentions"), value: keywordData.meta.totalKeywordMentions },
              ]}
              highlights={keywordData.overview.topKeywords.slice(0, 5).map((item) => `${item.keyword} (${item.count})`)}
              onOpen={onOpenKeyword}
            />
            <HomeRouteCard
              title={t("home.cards.library.title")}
              description={t("home.cards.library.description")}
              stats={[
                { label: t("home.stats.talks"), value: libraryData.meta.totalPresentations },
                { label: t("home.stats.uniqueLibraries"), value: libraryData.meta.uniqueKeywords },
                { label: t("home.stats.libraryMentions"), value: libraryData.meta.totalKeywordMentions },
              ]}
              highlights={libraryData.overview.topKeywords.slice(0, 5).map((item) => `${item.keyword} (${item.count})`)}
              onOpen={onOpenLibrary}
            />
            <HomeRouteCard
              title={t("home.cards.cloud.title")}
              description={t("home.cards.cloud.description")}
              stats={[
                { label: t("home.stats.cloudTalks"), value: cloudData.meta.totalPresentations },
                { label: t("home.stats.cloudKeywords"), value: cloudData.meta.uniqueKeywords },
                { label: t("home.stats.cloudMentions"), value: cloudData.meta.totalKeywordMentions },
              ]}
              highlights={cloudData.overview.topKeywords.slice(0, 5).map((item) => `${item.keyword} (${item.count})`)}
              onOpen={onOpenCloud}
            />
            <HomeRouteCard
              title={t("home.cards.ai.title")}
              description={t("home.cards.ai.description")}
              stats={[
                { label: t("home.stats.aiTalks"), value: aiData.meta.aiPresentationCount },
                { label: t("home.stats.aiKeywords"), value: aiData.meta.uniqueAiKeywords },
                { label: t("home.stats.contextKeywords"), value: aiData.meta.uniqueContextKeywords },
              ]}
              highlights={aiData.overview.topAiKeywords.slice(0, 5).map((item) => `${item.keyword} (${item.count})`)}
              onOpen={onOpenAi}
            />
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
  highlights: string[];
  onOpen: () => void;
}) {
  const { t } = useTranslation();
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
              <p className="text-2xl font-semibold">{numberFormat.format(item.value)}</p>
            </div>
          ))}
        </div>
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">{t("home.topSignals")}</p>
          <div className="flex flex-wrap gap-2">
            {highlights.map((item) => (
              <Badge key={item} variant="muted">
                {item}
              </Badge>
            ))}
          </div>
        </div>
        <Button onClick={onOpen}>{t("home.openDashboard")}</Button>
      </CardContent>
    </Card>
  );
}

function InsightDashboard({
  data,
  copy,
  sectionTabs,
}: {
  data: DashboardData;
  copy: InsightCopy;
  sectionTabs: Array<{ id: SectionId; label: string }>;
}) {
  const { t } = useTranslation();
  const [activeSection, setActiveSection] = useState<SectionId>("overview");
  const disabledSections = copy.disabledSections ?? [];
  const summaryMetrics =
    copy.summaryMode === "cloud"
      ? [
        { label: t("cloudInsight.scorecards.cloudTalks.label"), value: data.meta.totalPresentations },
        { label: t("cloudInsight.scorecards.cloudTalkShare.label"), value: data.meta.presentationShare ?? 0, format: "percent" as const },
        { label: t("cloudInsight.scorecards.uniqueCloudKeywords.label"), value: data.meta.uniqueKeywords },
      ]
      : [
        { label: t("common.totalTalks"), value: data.meta.totalPresentations },
        { label: t("common.uniqueTerms"), value: data.meta.uniqueKeywords },
        { label: t("common.mentions"), value: data.meta.totalKeywordMentions },
      ];

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
                <InsightMetric key={item.label} label={item.label} value={item.value} format={item.format} />
              ))}
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-2 rounded-[1.5rem] border border-primary/20 bg-primary/12 px-3 py-3">
            {sectionTabs.map((tab) => (
              <Button
                key={tab.id}
                variant={activeSection === tab.id ? "default" : "secondary"}
                onClick={() => setActiveSection(tab.id)}
                disabled={disabledSections.includes(tab.id)}
                className={disabledSections.includes(tab.id) ? "cursor-not-allowed opacity-45" : undefined}
              >
                {tab.label}
              </Button>
            ))}
          </div>
        </CardHeader>
      </Card>

      {activeSection === "overview" ? <OverviewSection data={data} copy={copy} /> : null}
      {activeSection === "network" ? <NetworkSection data={data} copy={copy} /> : null}
      {activeSection === "explorer" ? <ExplorerSection data={data} copy={copy} /> : null}
    </div>
  );
}

function InsightMetric({ label, value, format }: { label: string; value: number; format?: "percent" }) {
  return (
    <div className="rounded-[1.25rem] border border-border/60 bg-white/75 p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{format === "percent" ? percentFormat.format(value) : numberFormat.format(value)}</p>
    </div>
  );
}

function OverviewSection({ data, copy }: { data: DashboardData; copy: InsightCopy }) {
  const { t } = useTranslation();
  const [limit, setLimit] = useState<20 | 50 | 100>(20);
  const [expanded, setExpanded] = useState(false);
  const topKeyword = data.overview.topKeywords[0];
  const selectedKeywords = data.overview.topKeywords.slice(0, limit);
  const chartHeight = Math.max(420, selectedKeywords.length * 34);
  const randomizedCards = useMemo(
    () =>
      data.overview.cards.map((card) => ({
        ...card,
        samples: pickRandomItems(card.samples, 2),
      })),
    [data.overview.cards],
  );
  const treemapLegend = Array.from(
    new Map(
      data.distribution.treemap.map((item) => [item.category, { category: item.category, color: item.color }]),
    ).values(),
  );

  useEffect(() => {
    if (!expanded) {
      return;
    }

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
            {topKeyword ? <Badge variant="secondary">{topKeyword.keyword} · {topKeyword.count} {copy.unitLabel}</Badge> : null}
            {data.meta.excludedKeywords.length ? <Badge variant="muted">{t("common.filtered")}: {data.meta.excludedKeywords.join(", ")}</Badge> : null}
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
                      <CardDescription className="mt-1">{numberFormat.format(card.count)} {copy.unitLabel}</CardDescription>
                    </div>
                    <div className="rounded-full bg-primary/10 px-3 py-2 text-sm font-semibold text-primary">
                      #{Math.max(1, data.overview.topKeywords.findIndex((item) => item.keyword === card.keyword) + 1)}
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
                          <span className="ml-1 opacity-70">{item.count}</span>
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
              {[20, 50, 100].map((value) => (
                <Button key={value} variant={limit === value ? "default" : "outline"} onClick={() => setLimit(value as 20 | 50 | 100)}>
                  {t("common.topButton", { count: value })}
                </Button>
              ))}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="max-h-[720px] overflow-auto pr-2">
            <ChartContainer config={barChartConfig} className="min-h-[420px]">
              <ResponsiveContainer width="100%" height={chartHeight}>
                <BarChart data={selectedKeywords} layout="vertical" margin={{ top: 8, right: 92, left: 16, bottom: 8 }}>
                  <CartesianGrid horizontal={false} stroke="rgba(23, 54, 64, 0.08)" />
                  <XAxis type="number" tickLine={false} axisLine={false} />
                  <YAxis type="category" dataKey="keyword" width={180} tickLine={false} axisLine={false} interval={0} tick={{ fontSize: 12 }} />
                  <RechartsTooltip
                    cursor={{ fill: "rgba(23,126,137,0.08)" }}
                    content={<ChartTooltipContent formatter={(value) => `${numberFormat.format(Number(value))} ${copy.unitLabel}`} />}
                  />
                  <Bar dataKey="count" radius={[0, 999, 999, 0]} fill="var(--color-count)">
                    <LabelList
                      dataKey="count"
                      position="right"
                      offset={10}
                      formatter={(value: number) => `${numberFormat.format(value)} ${copy.unitLabel}`}
                      className="fill-foreground text-xs font-semibold"
                    />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>
          </div>
          {!selectedKeywords.length ? <p className="mt-4 text-sm text-muted-foreground">{copy.topEmptyLabel}</p> : null}
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
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(23, 54, 64, 0.08)" />
                <XAxis type="number" dataKey="x" name="Talk count" tickLine={false} axisLine={false} />
                <YAxis type="number" dataKey="y" name="Average companion terms" tickLine={false} axisLine={false} />
                <ZAxis type="number" dataKey="z" range={[90, 1100]} />
                <RechartsTooltip
                  cursor={{ strokeDasharray: "3 3" }}
                  content={<BubbleTooltip unitLabel={copy.unitLabel} />}
                />
                <Scatter data={data.distribution.bubble} fill="var(--color-count)">
                  {data.distribution.bubble.map((entry, index) => (
                    <Cell key={entry.keyword} fill={treemapColors[index % treemapColors.length]} fillOpacity={0.88} />
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
          <ChartContainer config={barChartConfig} className="h-[420px]">
            <ResponsiveContainer width="100%" height="100%">
              <Treemap data={data.distribution.treemap} dataKey="size" stroke="rgba(255,255,255,0.9)" fill="#177e89" content={<TreemapContent />}>
                {data.distribution.treemap.map((entry, index) => (
                  <Cell key={entry.name} fill={entry.color ?? treemapColors[index % treemapColors.length]} />
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
    <div className="space-y-4">
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
    </div>
  );
}

function translateCategory(t: TFunction, category: string) {
  const key = CATEGORY_KEY_MAP[category];
  return key ? t(key) : category;
}

function TreemapContent(props: {
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
      <title>{`${name} · ${translateCategory(t, category)} · ${numberFormat.format(size)} ${t("common.talksUnit")}`}</title>
      <rect x={x} y={y} width={width} height={height} rx={0} fill={resolvedFill} fillOpacity={0.9} />
      <text x={x + 14} y={y + 22} fill="white" fontSize="13" fontWeight="700">
        {name}
      </text>
      <text x={x + 14} y={y + 40} fill="rgba(255,255,255,0.92)" fontSize="12">
        {translateCategory(t, category)}
      </text>
      <text x={x + 14} y={y + 58} fill="rgba(255,255,255,0.88)" fontSize="12">
        {numberFormat.format(size)} {t("common.talksUnit")}
      </text>
    </g>
  );
}

function BubbleTooltip({
  active,
  payload,
  unitLabel,
}: TooltipProps<ValueType, NameType> & {
  unitLabel: string;
}) {
  const { t } = useTranslation();
  if (!active || !payload?.length) {
    return null;
  }

  const datum = payload[0]?.payload as
    | {
      keyword?: string;
      x?: number;
      y?: number;
      connectionScore?: number;
      share?: number;
    }
    | undefined;

  if (!datum) {
    return null;
  }

  return (
    <div className="rounded-2xl border border-white/60 bg-card/95 px-3 py-3 shadow-soft backdrop-blur">
      <div className="mb-2 text-sm font-semibold text-foreground">{datum.keyword ?? t("common.bubbleTooltip.unknownKeyword")}</div>
      <div className="space-y-1 text-sm text-muted-foreground">
        <div>{t("common.bubbleTooltip.talkCount")}: {numberFormat.format(Number(datum.x ?? 0))} {unitLabel}</div>
        <div>{t("common.bubbleTooltip.averageCompanionTerms")}: {Number(datum.y ?? 0).toFixed(2)}</div>
        <div>{t("common.bubbleTooltip.connectionScore")}: {numberFormat.format(Number(datum.connectionScore ?? 0))}</div>
        <div>{t("common.bubbleTooltip.talkShare")}: {percentFormat.format(Number(datum.share ?? 0))}</div>
      </div>
    </div>
  );
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
