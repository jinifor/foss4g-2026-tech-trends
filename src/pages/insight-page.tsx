import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import { DashboardPlaceholder } from "@/components/dashboard/dashboard-placeholder";
import { buildInsightCopy } from "@/components/dashboard/insight-copy";
import { InsightDashboard } from "@/components/dashboard/insight-dashboard";
import type { InsightRouteId } from "@/lib/routes";
import type { DashboardData } from "@/types/dashboard";

const dashboardDataCache = new Map<InsightRouteId, DashboardData>();

const insightDataLoaders: Record<InsightRouteId, () => Promise<{ default: unknown }>> = {
  keyword: () => import("@/data/dashboard-data.json"),
  library: () => import("@/data/library-dashboard-data.json"),
  cloud: () => import("@/data/cloud-dashboard-data.json"),
  threeD: () => import("@/data/three-d-dashboard-data.json"),
};

async function loadInsightData(routeId: InsightRouteId) {
  const cachedData = dashboardDataCache.get(routeId);
  if (cachedData) {
    return cachedData;
  }

  const module = await insightDataLoaders[routeId]();
  const data = module.default as DashboardData;
  dashboardDataCache.set(routeId, data);
  return data;
}

export default function InsightPage({ routeId }: { routeId: InsightRouteId }) {
  const { t } = useTranslation();
  const copy = useMemo(() => buildInsightCopy(t, routeId), [routeId, t]);
  const [data, setData] = useState<DashboardData | null>(() => dashboardDataCache.get(routeId) ?? null);

  useEffect(() => {
    let isMounted = true;
    setData(dashboardDataCache.get(routeId) ?? null);

    // 라우트가 바뀌면 해당 JSON만 비동기로 불러와 캐시에 저장한다.
    void loadInsightData(routeId).then((nextData) => {
      if (isMounted) {
        setData(nextData);
      }
    });

    return () => {
      isMounted = false;
    };
  }, [routeId]);

  if (!data) {
    return <DashboardPlaceholder message={t("common.loadingDashboard")} />;
  }

  return <InsightDashboard data={data} copy={copy} />;
}
