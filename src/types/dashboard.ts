export interface KeywordCountItem {
  keyword: string;
  count: number;
}

export interface RelatedKeyword {
  keyword: string;
  count: number;
}

export interface OverviewCard {
  keyword: string;
  count: number;
  related: RelatedKeyword[];
  samples: string[];
}

export interface LongtailPoint {
  rank: number;
  keyword: string;
  count: number;
  cumulativeShare: number;
}

export interface BubblePoint {
  keyword: string;
  x: number;
  y: number;
  z: number;
  connectionScore: number;
  share: number;
}

export interface TreemapNode {
  name: string;
  size: number;
  category: string;
  color: string;
}

export interface NetworkNode {
  id: string;
  keyword: string;
  count: number;
  degree: number;
  cluster: string;
}

export interface NetworkLink {
  source: string;
  target: string;
  count: number;
}

export interface ClusterKeyword {
  keyword: string;
  count: number;
}

export interface ClusterGroup {
  id: string;
  name: string;
  color: string;
  total: number;
  keywords: ClusterKeyword[];
}

export interface ExplorerPresentation {
  id: string;
  page: string;
  title: string;
  abstractSnippet: string;
  keywords: string[];
  highlightedKeywords: string[];
}

export interface DashboardData {
  meta: {
    sourceWorkbook: string;
    totalPresentations: number;
    uniqueKeywords: number;
    totalKeywordMentions: number;
    averageKeywordsPerPresentation: number;
    excludedKeywords: string[];
    presentationShare?: number;
    sourcePresentationCount?: number;
  };
  overview: {
    cards: OverviewCard[];
    topKeywords: KeywordCountItem[];
    wordCloud: KeywordCountItem[];
  };
  distribution: {
    longtail: LongtailPoint[];
    bubble: BubblePoint[];
    treemap: TreemapNode[];
  };
  relationships: {
    network: {
      nodes: NetworkNode[];
      links: NetworkLink[];
    };
    heatmap: {
      labels: string[];
      matrix: number[][];
      max: number;
    };
    clusters: ClusterGroup[];
    topPairs: NetworkLink[];
  };
  explorer: {
    presentations: ExplorerPresentation[];
  };
}

export interface AiScorecard {
  label: string;
  value: number;
  caption: string;
  format?: "percent";
}

export interface AiSignalBrief {
  keyword: string;
  count: number;
  family: string;
  relatedContexts: RelatedKeyword[];
  samples: string[];
}

export interface FamilyRadialItem {
  family: string;
  familyId: string;
  count: number;
  color: string;
  share: number;
  keywordCount: number;
}

export interface FamilyRadarItem {
  family: string;
  talks: number;
  contextBreadth: number;
  keywordBreadth: number;
}

export interface FlowNode {
  name: string;
}

export interface FlowLink {
  source: string;
  target: string;
  value: number;
}

export interface AiExplorerPresentation extends ExplorerPresentation {
  aiKeywords: string[];
  contextKeywords: string[];
}

export interface AiDashboardData {
  meta: {
    sourceWorkbook: string;
    totalPresentations: number;
    aiPresentationCount: number;
    aiPresentationShare: number;
    uniqueAiKeywords: number;
    uniqueContextKeywords: number;
  };
  overview: {
    scorecards: AiScorecard[];
    signalBriefs: AiSignalBrief[];
    topAiKeywords: KeywordCountItem[];
    topContextKeywords: KeywordCountItem[];
    treemap: TreemapNode[];
  };
  families: {
    radial: FamilyRadialItem[];
    radar: FamilyRadarItem[];
  };
  flows: {
    nodes: FlowNode[];
    links: FlowLink[];
  };
  explorer: {
    presentations: AiExplorerPresentation[];
  };
}
