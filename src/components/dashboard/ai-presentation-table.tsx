import { Badge } from "@/components/ui/badge";
import { ExplorerTable } from "@/components/dashboard/explorer-table";
import { TableCell, TableHead } from "@/components/ui/table";
import type { AiExplorerPresentation, KeywordCountItem } from "@/types/dashboard";
import { useTranslation } from "react-i18next";

export function AiPresentationTable({
  rows,
  topAiKeywords,
}: {
  rows: AiExplorerPresentation[];
  topAiKeywords: KeywordCountItem[];
}) {
  const { t } = useTranslation();

  return (
    <ExplorerTable
      rows={rows}
      filterKeywords={topAiKeywords}
      searchPlaceholder={t("tables.ai.search")}
      allLabel={t("aiInsight.allAiTalks")}
      getRowKey={(row) => row.id}
      matchesKeyword={(row, keyword) => row.aiKeywords.includes(keyword)}
      matchesQuery={(row, loweredQuery) =>
        row.title.toLowerCase().includes(loweredQuery) ||
        row.abstractSnippet.toLowerCase().includes(loweredQuery) ||
        row.aiKeywords.some((keyword) => keyword.toLowerCase().includes(loweredQuery)) ||
        row.contextKeywords.some((keyword) => keyword.toLowerCase().includes(loweredQuery))
      }
      renderHeader={() => (
        <>
          <TableHead className="w-[70px]">{t("common.no")}</TableHead>
          <TableHead className="min-w-[260px]">{t("common.talkTitle")}</TableHead>
          <TableHead className="min-w-[340px]">{t("common.abstractSnippet")}</TableHead>
          <TableHead className="min-w-[220px]">{t("aiInsight.aiKeywords")}</TableHead>
          <TableHead className="min-w-[260px]">{t("aiInsight.contextKeywords")}</TableHead>
        </>
      )}
      renderRow={(row, { setActiveKeyword }) => (
        <>
          <TableCell className="font-semibold text-muted-foreground">{row.id}</TableCell>
          <TableCell className="font-semibold">{row.title}</TableCell>
          <TableCell className="text-sm leading-6 text-muted-foreground">{row.abstractSnippet}</TableCell>
          <TableCell>
            <div className="flex flex-wrap gap-2">
              {row.aiKeywords.map((keyword) => (
                <Badge key={`${row.id}-${keyword}`} className="cursor-pointer" onClick={() => setActiveKeyword(keyword)}>
                  {keyword}
                </Badge>
              ))}
            </div>
          </TableCell>
          <TableCell>
            <div className="flex flex-wrap gap-2">
              {row.contextKeywords.map((keyword) => (
                <Badge key={`${row.id}-${keyword}`} variant="muted">
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
