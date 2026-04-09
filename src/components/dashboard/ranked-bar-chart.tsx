import { useMemo } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
  XAxis,
  YAxis,
} from "recharts";

import { ChartContainer, ChartTooltipContent, type ChartConfig } from "@/components/ui/chart";
import { useLocaleFormatters } from "@/lib/format";

type RankedBarChartProps = {
  data: Array<{ keyword: string; count: number }>;
  color: string;
  emptyLabel?: string;
  unitLabel: string;
  yAxisWidth?: number;
  minHeight?: number;
  tooltipCursorFill?: string;
};

export function RankedBarChart({
  data,
  color,
  emptyLabel,
  unitLabel,
  yAxisWidth = 180,
  minHeight = 420,
  tooltipCursorFill = "rgba(23,126,137,0.08)",
}: RankedBarChartProps) {
  const { number } = useLocaleFormatters();
  const chartHeight = Math.max(minHeight, data.length * 34);
  const chartConfig = useMemo(
    () =>
      ({
        count: {
          label: unitLabel,
          color,
        },
      }) satisfies ChartConfig,
    [color, unitLabel],
  );

  return (
    <>
      <div className="max-h-[720px] overflow-auto pr-2">
        <ChartContainer config={chartConfig} style={{ height: Math.max(chartHeight, minHeight) }}>
          <ResponsiveContainer width="100%" height={chartHeight}>
            <BarChart data={data} layout="vertical" margin={{ top: 8, right: 92, left: 16, bottom: 8 }}>
              <CartesianGrid horizontal={false} stroke="rgba(23, 54, 64, 0.08)" />
              <XAxis type="number" tickLine={false} axisLine={false} />
              <YAxis type="category" dataKey="keyword" width={yAxisWidth} tickLine={false} axisLine={false} interval={0} tick={{ fontSize: 12 }} />
              <RechartsTooltip
                cursor={{ fill: tooltipCursorFill }}
                content={<ChartTooltipContent formatter={(value) => `${number.format(Number(value))} ${unitLabel}`} />}
              />
              <Bar dataKey="count" radius={[0, 999, 999, 0]} fill="var(--color-count)">
                <LabelList
                  dataKey="count"
                  position="right"
                  offset={10}
                  formatter={(value: number) => `${number.format(value)} ${unitLabel}`}
                  className="fill-foreground text-xs font-semibold"
                />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartContainer>
      </div>
      {!data.length && emptyLabel ? <p className="mt-4 text-sm text-muted-foreground">{emptyLabel}</p> : null}
    </>
  );
}
