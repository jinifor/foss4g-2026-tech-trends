import { useTranslation } from "react-i18next";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function DashboardPlaceholder({ message }: { message?: string }) {
  const { t } = useTranslation();

  return (
    <Card>
      <CardHeader>
        <Badge>{t("app.hub")}</Badge>
        <CardTitle className="text-3xl">{t("common.loadingDashboard")}</CardTitle>
        <CardDescription>{message ?? t("common.loadingDashboard")}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[280px] rounded-[1.75rem] border border-border/60 bg-white/60" />
      </CardContent>
    </Card>
  );
}
