import { cn } from "@/lib/utils";
import { useTranslation } from "react-i18next";

export function KeywordHeatmap({
  labels,
  matrix,
  max,
}: {
  labels: string[];
  matrix: number[][];
  max: number;
}) {
  const { t } = useTranslation();
  return (
    <div className="overflow-auto rounded-[1.75rem] border border-border/60 bg-white/70">
      <table className="min-w-[980px] border-collapse">
        <thead>
          <tr>
            <th className="sticky left-0 top-0 z-20 bg-background/95 px-4 py-3 text-left text-xs font-bold uppercase tracking-[0.18em] text-muted-foreground backdrop-blur">
              {t("common.keywordColumn")}
            </th>
            {labels.map((label) => (
              <th
                key={label}
                className="sticky top-0 z-10 min-w-[96px] bg-background/95 px-3 py-3 text-center text-xs font-bold uppercase tracking-[0.18em] text-muted-foreground backdrop-blur"
              >
                {label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {labels.map((rowLabel, rowIndex) => (
            <tr key={rowLabel} className="border-b border-border/40">
              <th className="sticky left-0 z-10 bg-background/95 px-4 py-3 text-left text-sm font-semibold backdrop-blur">
                {rowLabel}
              </th>
              {matrix[rowIndex].map((value, colIndex) => {
                const intensity = value / max;
                return (
                  <td
                    key={`${rowLabel}-${labels[colIndex]}`}
                    title={t("common.heatmapTitle", { row: rowLabel, col: labels[colIndex], count: value })}
                    className={cn(
                      "px-3 py-3 text-center text-sm font-semibold transition-colors",
                      value > max * 0.45 ? "text-white" : "text-foreground",
                    )}
                    style={{ backgroundColor: `rgba(23,126,137,${0.06 + intensity * 0.88})` }}
                  >
                    {value}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
