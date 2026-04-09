import type { TFunction } from "i18next";

import type { MetricValueFormat } from "@/components/dashboard/metric-card";
import type { InsightRouteId } from "@/lib/routes";
import type { DashboardData } from "@/types/dashboard";

export type InsightSummaryMode = "default" | "library" | "cloud" | "threeD";

export type InsightCopy = {
  summaryMode: InsightSummaryMode;
  kicker: string;
  routeLabel: string;
  summary: string;
  cardsBadge: string;
  cardsTitle: string;
  cardsDescription: string;
  wordCloudBadge: string;
  wordCloudTitle: string;
  wordCloudDescription: string;
  topBadge: string;
  topTitle: string;
  topDescription: string;
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

export type InsightSummaryMetric = {
  label: string;
  value: number;
  format?: MetricValueFormat;
};

const INSIGHT_ROUTE_COPY_CONFIG: Record<
  InsightRouteId,
  { rootKey: string; summaryMode: InsightSummaryMode; emptyLabelKey: string }
> = {
  keyword: { rootKey: "keywordInsight", summaryMode: "default", emptyLabelKey: "common.noKeywordData" },
  library: { rootKey: "libraryInsight", summaryMode: "library", emptyLabelKey: "common.noLibraryData" },
  cloud: { rootKey: "cloudInsight", summaryMode: "cloud", emptyLabelKey: "common.noCloudData" },
  threeD: { rootKey: "threeDInsight", summaryMode: "threeD", emptyLabelKey: "common.noThreeDData" },
};

// 인사이트 문구는 루트 키 규칙만 다르고 구조는 같아서 공통 빌더로 생성한다.
export function buildInsightCopy(t: TFunction, routeId: InsightRouteId): InsightCopy {
  const routeConfig = INSIGHT_ROUTE_COPY_CONFIG[routeId];

  return {
    summaryMode: routeConfig.summaryMode,
    kicker: t(`${routeConfig.rootKey}.kicker`),
    routeLabel: t(`${routeConfig.rootKey}.routeLabel`),
    summary: t(`${routeConfig.rootKey}.summary`),
    cardsBadge: t(`${routeConfig.rootKey}.cardsBadge`),
    cardsTitle: t(`${routeConfig.rootKey}.cardsTitle`),
    cardsDescription: t(`${routeConfig.rootKey}.cardsDescription`),
    wordCloudBadge: t(`${routeConfig.rootKey}.wordCloudBadge`),
    wordCloudTitle: t(`${routeConfig.rootKey}.wordCloudTitle`),
    wordCloudDescription: t(`${routeConfig.rootKey}.wordCloudDescription`),
    topBadge: t(`${routeConfig.rootKey}.topBadge`),
    topTitle: t(`${routeConfig.rootKey}.topTitle`),
    topDescription: t(`${routeConfig.rootKey}.topDescription`),
    bubbleBadge: t(`${routeConfig.rootKey}.bubbleBadge`),
    bubbleTitle: t(`${routeConfig.rootKey}.bubbleTitle`),
    bubbleDescription: t(`${routeConfig.rootKey}.bubbleDescription`),
    treemapBadge: t(`${routeConfig.rootKey}.treemapBadge`),
    treemapTitle: t(`${routeConfig.rootKey}.treemapTitle`),
    treemapDescription: t(`${routeConfig.rootKey}.treemapDescription`),
    networkBadge: t(`${routeConfig.rootKey}.networkBadge`),
    networkTitle: t(`${routeConfig.rootKey}.networkTitle`),
    networkDescription: t(`${routeConfig.rootKey}.networkDescription`),
    heatmapBadge: t(`${routeConfig.rootKey}.heatmapBadge`),
    heatmapTitle: t(`${routeConfig.rootKey}.heatmapTitle`),
    heatmapDescription: t(`${routeConfig.rootKey}.heatmapDescription`),
    clusterBadge: t(`${routeConfig.rootKey}.clusterBadge`),
    clusterTitle: t(`${routeConfig.rootKey}.clusterTitle`),
    clusterDescription: t(`${routeConfig.rootKey}.clusterDescription`),
    explorerBadge: t(`${routeConfig.rootKey}.explorerBadge`),
    explorerTitle: t(`${routeConfig.rootKey}.explorerTitle`),
    explorerDescription: t(`${routeConfig.rootKey}.explorerDescription`),
    expandTitle: t(`${routeConfig.rootKey}.expandTitle`),
    expandDescription: t(`${routeConfig.rootKey}.expandDescription`),
    unitLabel: t("common.talksUnit"),
    topEmptyLabel: t(routeConfig.emptyLabelKey),
  };
}

// 요약 카드 값은 대시보드 성격에 맞는 지표만 골라서 반환한다.
export function buildInsightSummaryMetrics(
  t: TFunction,
  data: DashboardData,
  summaryMode: InsightSummaryMode,
): InsightSummaryMetric[] {
  if (summaryMode === "cloud") {
    return [
      { label: t("cloudInsight.scorecards.cloudTalks.label"), value: data.meta.totalPresentations },
      { label: t("cloudInsight.scorecards.cloudTalkShare.label"), value: data.meta.presentationShare ?? 0, format: "percent" },
      { label: t("cloudInsight.scorecards.uniqueCloudKeywords.label"), value: data.meta.uniqueKeywords },
    ];
  }

  if (summaryMode === "library") {
    const relatedTalkCount = data.explorer.presentations.filter((row) => row.keywords.length > 0).length;
    const talkShare = data.meta.totalPresentations ? relatedTalkCount / data.meta.totalPresentations : 0;

    return [
      { label: t("libraryInsight.scorecards.libraryTalks.label"), value: relatedTalkCount },
      { label: t("libraryInsight.scorecards.libraryTalkShare.label"), value: talkShare, format: "percent" },
      { label: t("libraryInsight.scorecards.uniqueLibraryKeywords.label"), value: data.meta.uniqueKeywords },
    ];
  }

  if (summaryMode === "threeD") {
    return [
      { label: t("threeDInsight.scorecards.threeDTalks.label"), value: data.meta.totalPresentations },
      { label: t("threeDInsight.scorecards.threeDTalkShare.label"), value: data.meta.presentationShare ?? 0, format: "percent" },
      { label: t("threeDInsight.scorecards.uniqueThreeDKeywords.label"), value: data.meta.uniqueKeywords },
    ];
  }

  return [
    { label: t("common.totalTalks"), value: data.meta.totalPresentations },
    { label: t("common.uniqueTerms"), value: data.meta.uniqueKeywords },
    { label: t("common.mentions"), value: data.meta.totalKeywordMentions },
  ];
}
