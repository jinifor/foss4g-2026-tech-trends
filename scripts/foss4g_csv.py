#!/usr/bin/env python3

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable


ID_COLUMN = "No."
PAGE_COLUMN = "Page"
TITLE_COLUMN = "발표 제목 (Title)"
ABSTRACT_COLUMN = "초록 (Abstract)"

KEYWORDS_COLUMN = "주요 키워드"
LIBRARY_KEYWORDS_COLUMN = "Library Keywords (Normalized)"
AI_KEYWORDS_COLUMN = "AI Keywords (Normalized)"
AI_CONTEXT_KEYWORDS_COLUMN = "AI Presentation Context Keywords"
THREE_D_KEYWORDS_COLUMN = "3D Keywords (Normalized)"
MAIN_THEME_COLUMN = "대주제"
TECH_TOOLS_COLUMN = "기술/도구"
APPLICATION_AREA_COLUMN = "활용 분야"

SOURCE_CSV_CANDIDATES = [
    "docs/foss4g_2026_talks.csv",
    "foss4g_2026_talks.csv",
]

KEYWORD_CSV_CANDIDATES = [
    "docs/foss4g_2026_talks_with_keywords.csv",
    "foss4g_2026_talks_with_keywords.csv",
]

LIBRARY_CSV_CANDIDATES = [
    "docs/foss4g_2026_talks_with_library_keywords.csv",
    "foss4g_2026_talks_with_library_keywords.csv",
]

AI_CSV_CANDIDATES = [
    "docs/foss4g_2026_talks_with_ai_keywords.csv",
    "foss4g_2026_talks_with_ai_keywords.csv",
]

THREE_D_CSV_CANDIDATES = [
    "docs/foss4g_2026_talks_with_3d_keywords.csv",
    "foss4g_2026_talks_with_3d_keywords.csv",
]

CATEGORY_CSV_CANDIDATES = [
    "docs/foss4g_2026_talks_with_categories.csv",
    "foss4g_2026_talks_with_categories.csv",
]


def find_existing_path(candidates: Iterable[str], root: Path) -> Path | None:
    for candidate in candidates:
        path = root / candidate
        if path.exists():
            return path
    return None


def resolve_existing_path(candidates: Iterable[str], root: Path) -> Path:
    path = find_existing_path(candidates, root)
    if path is None:
        raise FileNotFoundError(f"No matching file found for candidates: {list(candidates)}")
    return path


def resolve_input_path(explicit: str | None, candidates: Iterable[str]) -> Path:
    if explicit:
        path = Path(explicit)
        if not path.exists():
            raise SystemExit(f"Input file not found: {path}")
        return path

    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return path

    raise SystemExit(f"Input file not found. Checked: {list(candidates)}")


def read_csv_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [dict(row) for row in reader]
        return rows, list(reader.fieldnames or [])


def build_output_fieldnames(existing: Iterable[str], generated: Iterable[str]) -> list[str]:
    generated_list = list(generated)
    generated_set = set(generated_list)
    fieldnames: list[str] = []

    for field in existing:
        if field and field not in fieldnames and field not in generated_set:
            fieldnames.append(field)

    for field in generated_list:
        if field not in fieldnames:
            fieldnames.append(field)

    return fieldnames


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def split_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]
