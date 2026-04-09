import { Boxes, Cloud, Cuboid, Home, Network, Sparkles, type LucideIcon } from "lucide-react";

export const ROUTE_IDS = ["home", "keyword", "library", "cloud", "threeD", "ai"] as const;
export const SECTION_IDS = ["overview", "network", "explorer"] as const;

export type RouteId = (typeof ROUTE_IDS)[number];
export type InsightRouteId = Exclude<RouteId, "home" | "ai">;
export type SectionId = (typeof SECTION_IDS)[number];

export type RouteDefinition = {
  id: RouteId;
  icon: LucideIcon;
  labelKey: string;
  descriptionKey: string;
};

export const ROUTE_DEFINITIONS: RouteDefinition[] = [
  { id: "home", icon: Home, labelKey: "routes.home.label", descriptionKey: "routes.home.description" },
  { id: "keyword", icon: Sparkles, labelKey: "routes.keyword.label", descriptionKey: "routes.keyword.description" },
  { id: "library", icon: Boxes, labelKey: "routes.library.label", descriptionKey: "routes.library.description" },
  { id: "cloud", icon: Cloud, labelKey: "routes.cloud.label", descriptionKey: "routes.cloud.description" },
  { id: "threeD", icon: Cuboid, labelKey: "routes.threeD.label", descriptionKey: "routes.threeD.description" },
  { id: "ai", icon: Network, labelKey: "routes.ai.label", descriptionKey: "routes.ai.description" },
];

export function isRouteId(value: string): value is RouteId {
  return ROUTE_IDS.includes(value as RouteId);
}

// 해시 문자열을 라우트 타입으로 안전하게 정규화한다.
export function getInitialRoute(hash: string): RouteId {
  const route = hash.replace("#", "");
  return isRouteId(route) ? route : "home";
}

// 해시 기반 이동 규칙을 한 함수로 모아 중복 분기를 없앤다.
export function navigateToRoute(route: RouteId) {
  window.location.hash = route;
}
