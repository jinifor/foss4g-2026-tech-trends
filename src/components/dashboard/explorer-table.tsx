import { useMemo, useState, type ReactNode } from "react";
import { useTranslation } from "react-i18next";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableHeader, TableRow } from "@/components/ui/table";
import { EXPLORER_FILTER_LIMIT, sliceTopItems } from "@/lib/dashboard-utils";
import { useLocaleFormatters } from "@/lib/format";
import type { KeywordCountItem } from "@/types/dashboard";

type ExplorerTableProps<Row> = {
  rows: Row[];
  filterKeywords: KeywordCountItem[];
  searchPlaceholder: string;
  allLabel: string;
  getRowKey: (row: Row) => string;
  matchesKeyword: (row: Row, keyword: string) => boolean;
  matchesQuery: (row: Row, loweredQuery: string) => boolean;
  renderHeader: () => ReactNode;
  renderRow: (row: Row, helpers: { setActiveKeyword: (keyword: string) => void }) => ReactNode;
};

export function ExplorerTable<Row>({
  rows,
  filterKeywords,
  searchPlaceholder,
  allLabel,
  getRowKey,
  matchesKeyword,
  matchesQuery,
  renderHeader,
  renderRow,
}: ExplorerTableProps<Row>) {
  const { t } = useTranslation();
  const { number } = useLocaleFormatters();
  const [query, setQuery] = useState("");
  const [activeKeyword, setActiveKeyword] = useState<string | null>(null);
  const visibleFilterKeywords = useMemo(
    () => sliceTopItems(filterKeywords, EXPLORER_FILTER_LIMIT),
    [filterKeywords],
  );
  const filteredRows = useMemo(() => {
    const loweredQuery = query.trim().toLowerCase();

    // 검색어와 선택 키워드를 동시에 만족하는 행만 노출한다.
    return rows.filter((row) => {
      const matchesSelectedKeyword = activeKeyword ? matchesKeyword(row, activeKeyword) : true;
      const matchesSearchText = loweredQuery.length === 0 || matchesQuery(row, loweredQuery);
      return matchesSelectedKeyword && matchesSearchText;
    });
  }, [activeKeyword, matchesKeyword, matchesQuery, query, rows]);

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <Input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder={searchPlaceholder}
          className="lg:max-w-md"
        />
        <div className="flex flex-wrap items-center gap-2">
          <Button variant={activeKeyword === null ? "default" : "outline"} size="sm" onClick={() => setActiveKeyword(null)}>
            {allLabel}
          </Button>
          {visibleFilterKeywords.map((item) => (
            <Button
              key={item.keyword}
              variant={activeKeyword === item.keyword ? "default" : "outline"}
              size="sm"
              onClick={() => setActiveKeyword(item.keyword)}
            >
              {item.keyword}
            </Button>
          ))}
        </div>
      </div>

      <Table>
        <TableHeader>
          <TableRow>{renderHeader()}</TableRow>
        </TableHeader>
        <TableBody>
          {filteredRows.map((row) => (
            <TableRow key={getRowKey(row)}>{renderRow(row, { setActiveKeyword })}</TableRow>
          ))}
        </TableBody>
      </Table>
      <p className="text-sm text-muted-foreground">{t("common.results", { count: number.format(filteredRows.length) })}</p>
    </div>
  );
}
