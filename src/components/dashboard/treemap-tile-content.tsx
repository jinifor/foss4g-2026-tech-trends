import { useTranslation } from "react-i18next";

import { useLocaleFormatters } from "@/lib/format";

type TreemapTileContentProps = {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  name?: string;
  size?: number;
  fill?: string;
  category?: string;
  color?: string;
  translateLabel: (category: string) => string;
};

export function TreemapTileContent(props: TreemapTileContentProps) {
  const {
    x = 0,
    y = 0,
    width = 0,
    height = 0,
    name = "",
    size = 0,
    fill = "#177e89",
    category = "",
    color,
    translateLabel,
  } = props;
  const { t } = useTranslation();
  const { number } = useLocaleFormatters();
  const resolvedFill = color || fill || "#177e89";
  const translatedCategory = translateLabel(category);

  if (width < 90 || height < 50) {
    return <g />;
  }

  return (
    <g>
      <title>
        {t("common.treemapTileTitle", {
          name,
          category: translatedCategory,
          count: number.format(size),
          unit: t("common.talksUnit"),
        })}
      </title>
      <rect x={x} y={y} width={width} height={height} rx={0} fill={resolvedFill} fillOpacity={0.9} />
      <text x={x + 14} y={y + 22} fill="white" fontSize="13" fontWeight="700">
        {name}
      </text>
      <text x={x + 14} y={y + 40} fill="rgba(255,255,255,0.92)" fontSize="12">
        {translatedCategory}
      </text>
      <text x={x + 14} y={y + 58} fill="rgba(255,255,255,0.88)" fontSize="12">
        {number.format(size)} {t("common.talksUnit")}
      </text>
    </g>
  );
}
