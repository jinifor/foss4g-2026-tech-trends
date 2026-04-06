import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { ExplorerPresentation, KeywordCountItem } from "@/types/dashboard";

export function PresentationTable({
  rows,
  topKeywords,
}: {
  rows: ExplorerPresentation[];
  topKeywords: KeywordCountItem[];
}) {
  const { t } = useTranslation();
  const [query, setQuery] = useState("");
  const [activeKeyword, setActiveKeyword] = useState<string | null>(null);

  const filtered = useMemo(() => {
    const lowered = query.trim().toLowerCase();
    return rows.filter((row) => {
      const matchesKeyword = activeKeyword ? row.keywords.includes(activeKeyword) : true;
      const matchesQuery =
        lowered.length === 0 ||
        row.title.toLowerCase().includes(lowered) ||
        row.abstractSnippet.toLowerCase().includes(lowered) ||
        row.keywords.some((keyword) => keyword.toLowerCase().includes(lowered));
      return matchesKeyword && matchesQuery;
    });
  }, [activeKeyword, query, rows]);

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <Input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder={t("tables.keyword.search")}
          className="lg:max-w-md"
        />
        <div className="flex flex-wrap items-center gap-2">
          <Button variant={activeKeyword === null ? "default" : "outline"} size="sm" onClick={() => setActiveKeyword(null)}>
            {t("common.searchAll")}
          </Button>
          {topKeywords.slice(0, 12).map((item) => (
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
          <TableRow>
            <TableHead className="w-[70px]">{t("common.no")}</TableHead>
            <TableHead className="min-w-[260px]">{t("common.talkTitle")}</TableHead>
            <TableHead className="min-w-[360px]">{t("common.abstractSnippet")}</TableHead>
            <TableHead className="min-w-[280px]">{t("common.keywords")}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {filtered.map((row) => (
            <TableRow key={row.id}>
              <TableCell className="font-semibold text-muted-foreground">{row.id}</TableCell>
              <TableCell>
                <div className="space-y-2">
                  <div className="font-semibold">{row.title}</div>
                </div>
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
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <p className="text-sm text-muted-foreground">{t("common.results", { count: numberFormat.format(filtered.length) })}</p>
    </div>
  );
}

const numberFormat = new Intl.NumberFormat("en-US");
