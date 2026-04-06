import * as React from "react";
import { type TooltipProps } from "recharts";
import { type NameType, type ValueType } from "recharts/types/component/DefaultTooltipContent";

import { cn } from "@/lib/utils";

export type ChartConfig = Record<
  string,
  {
    label: string;
    color: string;
  }
>;

export function ChartContainer({
  config,
  className,
  children,
}: {
  config: ChartConfig;
  className?: string;
  children: React.ReactNode;
}) {
  const style = Object.fromEntries(
    Object.entries(config).map(([key, value]) => [`--color-${key}`, value.color]),
  ) as React.CSSProperties;

  return (
    <div className={cn("h-[320px] w-full [&_.recharts-cartesian-axis-tick_text]:fill-hsl(var(--muted-foreground))", className)} style={style}>
      {children}
    </div>
  );
}

export function ChartTooltipContent({
  active,
  payload,
  label,
  indicator = "dot",
  formatter,
}: TooltipProps<ValueType, NameType> & {
  indicator?: "dot" | "line";
  formatter?: (value: ValueType, name: NameType) => React.ReactNode;
}) {
  if (!active || !payload?.length) {
    return null;
  }

  return (
    <div className="rounded-2xl border border-white/60 bg-card/95 px-3 py-2 shadow-soft backdrop-blur">
      {label ? <div className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">{label}</div> : null}
      <div className="space-y-1.5">
        {payload.map((item) => {
          const indicatorNode =
            indicator === "line" ? (
              <span className="mt-2 h-0.5 w-4 rounded-full" style={{ backgroundColor: item.color }} />
            ) : (
              <span className="mt-1.5 h-2.5 w-2.5 rounded-full" style={{ backgroundColor: item.color }} />
            );

          return (
            <div key={`${item.name}-${item.dataKey}`} className="flex items-start gap-2 text-sm">
              {indicatorNode}
              <div className="flex flex-col">
                <span className="font-semibold text-foreground">{String(item.name)}</span>
                <span className="text-muted-foreground">
                  {formatter ? formatter(item.value ?? "", item.name ?? "") : String(item.value ?? "")}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
