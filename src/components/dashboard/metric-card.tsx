import { useLocaleFormatters } from "@/lib/format";

export type MetricValueFormat = "percent";

export function MetricCard({
  label,
  value,
  format,
}: {
  label: string;
  value: number;
  format?: MetricValueFormat;
}) {
  const { number, percent } = useLocaleFormatters();

  return (
    <div className="rounded-[1.25rem] border border-border/60 bg-white/75 p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{format === "percent" ? percent.format(value) : number.format(value)}</p>
    </div>
  );
}
