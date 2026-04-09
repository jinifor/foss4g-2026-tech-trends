import { useTranslation } from "react-i18next";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useLocaleFormatters } from "@/lib/format";
import type { ClusterGroup } from "@/types/dashboard";

export function ClusterMap({ clusters }: { clusters: ClusterGroup[] }) {
  const { t } = useTranslation();
  const { number } = useLocaleFormatters();

  return (
    <div className="grid gap-5 lg:grid-cols-2">
      {clusters.map((cluster) => (
        <Card key={cluster.id} className="overflow-hidden border-white/60">
          <CardHeader className="pb-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="metric-chip mb-3" style={{ color: cluster.color }}>
                  {t("common.cluster")}
                </div>
                <CardTitle>{cluster.name}</CardTitle>
              </div>
              <div className="rounded-full px-4 py-2 text-sm font-semibold text-white" style={{ backgroundColor: cluster.color }}>
                {number.format(cluster.total)} {t("common.mentions")}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {cluster.keywords.map((keyword) => (
                <Badge
                  key={keyword.keyword}
                  variant="muted"
                  className="border-0"
                  style={{
                    backgroundColor: `${cluster.color}18`,
                    color: cluster.color,
                    fontSize: `${0.72 + Math.min(keyword.count / 80, 0.5)}rem`,
                  }}
                >
                  {keyword.keyword}
                  <span className="ml-1 opacity-70">{number.format(keyword.count)}</span>
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
