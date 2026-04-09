import { Suspense, lazy, useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import { AppHeader } from "@/components/app/app-header";
import { DashboardPlaceholder } from "@/components/dashboard/dashboard-placeholder";
import { normalizeLanguage } from "@/lib/format";
import {
  getInitialRoute,
  navigateToRoute,
  ROUTE_DEFINITIONS,
  type InsightRouteId,
  type RouteId,
} from "@/lib/routes";
import { HomePage } from "@/pages/home-page";

const InsightPage = lazy(() => import("@/pages/insight-page"));
const AiPage = lazy(() => import("@/pages/ai-page"));

export default function App() {
  const { t, i18n } = useTranslation();
  const [route, setRoute] = useState<RouteId>(() =>
    typeof window === "undefined" ? "home" : getInitialRoute(window.location.hash),
  );
  const routeItems = useMemo(
    () =>
      ROUTE_DEFINITIONS.map((item) => ({
        ...item,
        label: t(item.labelKey),
        description: t(item.descriptionKey),
      })),
    [t],
  );

  useEffect(() => {
    // 브라우저 해시 변경을 앱 상태와 동기화한다.
    const onHashChange = () => setRoute(getInitialRoute(window.location.hash));
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  const handleNavigate = (nextRoute: RouteId) => {
    navigateToRoute(nextRoute);
    setRoute(nextRoute);
  };

  return (
    <div className="min-h-screen px-4 py-4 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-[1560px] space-y-4">
        <AppHeader
          activeRoute={route}
          language={normalizeLanguage(i18n.language)}
          routeItems={routeItems}
          onLanguageChange={(language) => {
            void i18n.changeLanguage(language);
          }}
          onNavigate={handleNavigate}
        />

        {route === "home" ? <HomePage onNavigate={handleNavigate} /> : null}

        {route !== "home" ? (
          <Suspense fallback={<DashboardPlaceholder message={t("common.loadingDashboard")} />}>
            {route === "ai" ? <AiPage /> : <InsightPage routeId={route as InsightRouteId} />}
          </Suspense>
        ) : null}
      </div>
    </div>
  );
}
