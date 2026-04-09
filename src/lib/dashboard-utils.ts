import type { KeywordCountItem, TreemapNode } from "@/types/dashboard";

export const HOME_HIGHLIGHT_LIMIT = 5;
export const EXPLORER_FILTER_LIMIT = 12;
export const TOP_KEYWORD_LIMITS = [20, 50, 100] as const;

export type TopKeywordLimit = (typeof TOP_KEYWORD_LIMITS)[number];

// 화면별 상위 항목 개수를 같은 규칙으로 유지한다.
export function sliceTopItems<T>(items: T[], limit: number) {
  return items.slice(0, limit);
}

// 대표 예시는 기존 배열을 훼손하지 않고 셔플한 뒤 일부만 고른다.
export function pickRandomItems<T>(items: T[], count: number): T[] {
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

// treemap 범례는 카테고리별 첫 색상만 남겨 중복을 제거한다.
export function buildTreemapLegend(items: TreemapNode[]) {
  return Array.from(
    new Map(
      items.map((item) => [item.category, { category: item.category, color: item.color }]),
    ).values(),
  );
}

// 카드 순위 표시는 키워드별 인덱스를 미리 맵으로 만들어 재사용한다.
export function buildKeywordRankMap(items: KeywordCountItem[]) {
  return new Map(items.map((item, index) => [item.keyword, index + 1]));
}
