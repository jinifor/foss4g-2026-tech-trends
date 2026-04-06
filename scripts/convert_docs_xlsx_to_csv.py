#!/usr/bin/env python3

from __future__ import annotations

import csv
import re
import unicodedata
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
}

BASE_NAME_MAP = {
    "FOSS4G_2026_발표목록.xlsx": "foss4g_2026_talks",
    "FOSS4G_2026_발표목록_키워드추가.xlsx": "foss4g_2026_talks_with_keywords",
    "FOSS4G_2026_발표목록_분류추가.xlsx": "foss4g_2026_talks_with_categories",
    "FOSS4G_2026_발표목록_라이브러리키워드추가.xlsx": "foss4g_2026_talks_with_library_keywords",
    "FOSS4G_2026_발표목록_AI키워드추가.xlsx": "foss4g_2026_talks_with_ai_keywords",
}


def normalized_name(path: Path) -> str:
    return unicodedata.normalize("NFC", path.name)


def english_base_name(path: Path) -> str:
    name = normalized_name(path)
    if name in BASE_NAME_MAP:
        return BASE_NAME_MAP[name]
    cleaned = Path(name).stem.lower()
    cleaned = re.sub(r"[^a-z0-9]+", "_", cleaned).strip("_")
    return cleaned


def col_to_index(col_ref: str) -> int:
    result = 0
    for char in col_ref:
        if not char.isalpha():
            break
        result = result * 26 + (ord(char.upper()) - 64)
    return result


def load_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    values: list[str] = []
    for item in root.findall("a:si", NS):
        text = "".join(node.text or "" for node in item.iterfind(".//a:t", NS))
        values.append(text)
    return values


def cell_text(cell: ET.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        return "".join((node.text or "") for node in cell.iterfind(".//a:t", NS))
    if cell_type == "s":
        value = cell.find("a:v", NS)
        if value is None or value.text is None:
            return ""
        index = int(value.text)
        return shared_strings[index] if 0 <= index < len(shared_strings) else ""
    value = cell.find("a:v", NS)
    return "" if value is None or value.text is None else value.text


def workbook_sheets(archive: zipfile.ZipFile) -> list[tuple[str, str]]:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    target_map = {
        rel.attrib["Id"]: rel.attrib["Target"].lstrip("/")
        for rel in rels.findall("pr:Relationship", NS)
    }
    sheets: list[tuple[str, str]] = []
    for sheet in workbook.find("a:sheets", NS):
        rel_id = sheet.attrib.get(f"{{{NS['r']}}}id")
        if not rel_id or rel_id not in target_map:
            continue
        sheets.append((sheet.attrib["name"], target_map[rel_id]))
    return sheets


def read_sheet_rows(archive: zipfile.ZipFile, sheet_path: str, shared_strings: list[str]) -> list[list[str]]:
    root = ET.fromstring(archive.read(sheet_path))
    sheet_data = root.find("a:sheetData", NS)
    if sheet_data is None:
        return []

    rows: list[dict[int, str]] = []
    max_col = 0
    for row in sheet_data.findall("a:row", NS):
        cells: dict[int, str] = {}
        for cell in row.findall("a:c", NS):
            ref = cell.attrib.get("r", "")
            col_index = col_to_index(ref)
            max_col = max(max_col, col_index)
            cells[col_index] = cell_text(cell, shared_strings)
        rows.append(cells)

    normalized_rows: list[list[str]] = []
    for row in rows:
        normalized_rows.append([row.get(index, "") for index in range(1, max_col + 1)])
    return normalized_rows


def output_name(base_name: str, sheet_name: str, sheet_index: int) -> str:
    sheet_name_nfc = unicodedata.normalize("NFC", sheet_name)
    if sheet_index == 0:
        return f"{base_name}.csv"
    if "요약" in sheet_name_nfc or "summary" in sheet_name_nfc.lower():
        return f"{base_name}_summary.csv"
    slug = re.sub(r"[^a-z0-9]+", "_", sheet_name_nfc.lower()).strip("_")
    return f"{base_name}_{slug}.csv"


def write_csv(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(rows)


def convert_workbook(path: Path) -> list[Path]:
    outputs: list[Path] = []
    base_name = english_base_name(path)

    with zipfile.ZipFile(path) as archive:
        shared_strings = load_shared_strings(archive)
        sheets = workbook_sheets(archive)
        for index, (sheet_name, sheet_path) in enumerate(sheets):
            rows = read_sheet_rows(archive, sheet_path, shared_strings)
            if not rows:
                continue
            output_path = DOCS_DIR / output_name(base_name, sheet_name, index)
            write_csv(output_path, rows)
            outputs.append(output_path)

    return outputs


def main() -> None:
    created: list[Path] = []
    for path in sorted(DOCS_DIR.glob("*.xlsx")):
        if path.name.startswith("~$"):
            continue
        created.extend(convert_workbook(path))

    for path in created:
        print(f"Created: {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
