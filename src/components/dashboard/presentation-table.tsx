import { useTranslation } from "react-i18next";

import { Badge } from "@/components/ui/badge";
import { ExplorerTable } from "@/components/dashboard/explorer-table";
import { TableCell, TableHead } from "@/components/ui/table";
import type { ExplorerPresentation, KeywordCountItem } from "@/types/dashboard";

export function PresentationTable({
  rows,
  topKeywords,
}: {
  rows: ExplorerPresentation[];
  topKeywords: KeywordCountItem[];
}) {
  const { t } = useTranslation();

  return (
    <ExplorerTable
      rows={rows}
      filterKeywords={topKeywords}
      searchPlaceholder={t("tables.keyword.search")}
      allLabel={t("common.searchAll")}
      getRowKey={(row) => row.id}
      matchesKeyword={(row, keyword) => row.keywords.includes(keyword)}
      matchesQuery={(row, loweredQuery) =>
        row.title.toLowerCase().includes(loweredQuery) ||
        row.abstractSnippet.toLowerCase().includes(loweredQuery) ||
        row.keywords.some((keyword) => keyword.toLowerCase().includes(loweredQuery))
      }
      renderHeader={() => (
        <>
          <TableHead className="w-[70px]">{t("common.no")}</TableHead>
          <TableHead className="min-w-[260px]">{t("common.talkTitle")}</TableHead>
          <TableHead className="min-w-[360px]">{t("common.abstractSnippet")}</TableHead>
          <TableHead className="min-w-[280px]">{t("common.keywords")}</TableHead>
        </>
      )}
      renderRow={(row, { setActiveKeyword }) => (
        <>
          <TableCell className="font-semibold text-muted-foreground">{row.id}</TableCell>
          <TableCell>
            <div className="font-semibold">{row.title}</div>
          </TableCell>
          <TableCell className="text-sm leading-6 text-muted-foreground">{row.abstractSnippet}</TableCell>
          <TableCell>
            <div className="flex flex-wrap gap-2">
              {row.keywords.map((keyword) => (
                <Badge
                  key={`${row.id}-${keyword}`}
                  variant={row.highlightedKeywords.includes(keyword) ? "default" : "muted"}
                  className="cursor-pointer"
                  onClick={() => setActiveKeyword(keyword)}
                >
                  {keyword}
                </Badge>
              ))}
            </div>
          </TableCell>
        </>
      )}
    />
  );
}
