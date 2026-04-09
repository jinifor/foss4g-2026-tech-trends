import type { RouteId } from "@/lib/routes";

export type DashboardSummaryId = Exclude<RouteId, "home">;

export type DashboardSummary = {
  stats: [number, number, number];
  highlights: Array<{ keyword: string; count: number }>;
};

// 홈 화면은 가벼운 요약 데이터만 먼저 읽어 초기 번들을 줄인다.
export const dashboardSummaries: Record<DashboardSummaryId, DashboardSummary> = {
  keyword: {
    stats: [376, 207, 765],
    highlights: [
      { keyword: "QGIS", count: 45 },
      { keyword: "Cloud", count: 28 },
      { keyword: "AI", count: 25 },
      { keyword: "Visualization", count: 24 },
      { keyword: "3D", count: 23 },
    ],
  },
  library: {
    stats: [376, 50, 211],
    highlights: [
      { keyword: "QGIS", count: 45 },
      { keyword: "MapLibre", count: 20 },
      { keyword: "GeoServer", count: 15 },
      { keyword: "PostGIS", count: 14 },
      { keyword: "PostgreSQL", count: 13 },
    ],
  },
  cloud: {
    stats: [46, 22, 77],
    highlights: [
      { keyword: "STAC", count: 12 },
      { keyword: "Cloud Native", count: 11 },
      { keyword: "COG", count: 7 },
      { keyword: "Cloud Infrastructure", count: 7 },
      { keyword: "Zarr", count: 4 },
    ],
  },
  threeD: {
    stats: [49, 16, 70],
    highlights: [
      { keyword: "3D", count: 17 },
      { keyword: "Digital Twin", count: 8 },
      { keyword: "Point Cloud", count: 8 },
      { keyword: "CesiumJS", count: 6 },
      { keyword: "PLATEAU", count: 6 },
    ],
  },
  ai: {
    stats: [56, 18, 53],
    highlights: [
      { keyword: "AI", count: 23 },
      { keyword: "GeoAI", count: 10 },
      { keyword: "LLM", count: 9 },
      { keyword: "Machine Learning", count: 5 },
      { keyword: "Natural Language Interface", count: 5 },
    ],
  },
};
