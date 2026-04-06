#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

from foss4g_csv import (
    ABSTRACT_COLUMN,
    SOURCE_CSV_CANDIDATES,
    THREE_D_CSV_CANDIDATES,
    THREE_D_KEYWORDS_COLUMN,
    TITLE_COLUMN,
    build_output_fieldnames,
    read_csv_rows,
    resolve_input_path,
    write_csv_rows,
)


DEFAULT_INPUT_CANDIDATES = SOURCE_CSV_CANDIDATES
DEFAULT_OUTPUT = THREE_D_CSV_CANDIDATES[0]

THREE_D_RULES: list[tuple[str, list[str]]] = [
    ("3D", [r"\b3d\b", r"three-dimensional", r"3d gis", r"3d spatial"]),
    ("Digital Twin", [r"digital twin(?:s)?"]),
    ("3D City Model", [r"3d city model(?:s)?", r"digital urban model(?:s)?"]),
    ("Point Cloud", [r"point cloud(?:s)?"]),
    ("Photogrammetry", [r"photogrammetr"]),
    ("3D Tiles", [r"3d tiles?"]),
    ("CesiumJS", [r"cesiumjs", r"\bcesium\b"]),
    ("WebGL", [r"\bwebgl\b"]),
    ("WebGPU", [r"\bwebgpu\b"]),
    ("Deck.gl", [r"deck\.gl(?:-raster)?", r"deckgl"]),
    ("CityGML", [r"citygml"]),
    ("CityJSON", [r"cityjson"]),
    ("glTF / GLB", [r"\bgltf\b", r"\bglb\b"]),
    ("Voxel", [r"\bvoxel(?:ization)?\b"]),
    ("PLATEAU", [r"\bplateau\b"]),
    ("Point Tiler", [r"point[- ]tiler"]),
    ("LiDAR", [r"\blidar\b"]),
    ("BIM", [r"\bbim\b", r"building information model"]),
]

SUPPRESSION_RULES: dict[str, set[str]] = {
    "3D City Model": {"3D"},
    "3D Tiles": {"3D"},
}


def normalize_text(text: str) -> str:
    lowered = text.lower()
    replacements = [
        ("3 d", "3d"),
        ("3-d", "3d"),
        ("digital twins", "digital twin"),
        ("point clouds", "point cloud"),
        ("deckgl", "deck.gl"),
        ("deck gl", "deck.gl"),
        ("point-tiler", "point tiler"),
        ("gltf/glb", "gltf glb"),
    ]
    for source, target in replacements:
        lowered = lowered.replace(source, target)
    lowered = re.sub(r"[^a-z0-9:+#/\.\-\s]", " ", lowered)
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return lowered


def dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value and value not in seen:
            ordered.append(value)
            seen.add(value)
    return ordered


def extract_three_d_keywords(title: str, abstract: str) -> list[str]:
    normalized = normalize_text(f"{title} {abstract}")
    matches: list[tuple[int, int, str]] = []

    for index, (label, patterns) in enumerate(THREE_D_RULES):
        earliest: int | None = None
        for pattern in patterns:
            match = re.search(pattern, normalized)
            if match is None:
                continue
            if earliest is None or match.start() < earliest:
                earliest = match.start()
        if earliest is not None:
            matches.append((earliest, index, label))

    matches.sort(key=lambda item: (item[0], item[1]))
    keywords = dedupe_preserve_order(label for _, _, label in matches)

    suppressed: set[str] = set()
    for keyword in keywords:
        suppressed.update(SUPPRESSION_RULES.get(keyword, set()))

    return [keyword for keyword in keywords if keyword not in suppressed]


def create_output_csv(input_path: Path, output_path: Path) -> None:
    rows, fieldnames = read_csv_rows(input_path)
    output_rows: list[dict[str, str]] = []

    for row in rows:
        title = row.get(TITLE_COLUMN, "").strip()
        abstract = row.get(ABSTRACT_COLUMN, "").strip()
        updated_row = dict(row)
        updated_row[THREE_D_KEYWORDS_COLUMN] = ", ".join(extract_three_d_keywords(title, abstract))
        output_rows.append(updated_row)

    output_fieldnames = build_output_fieldnames(fieldnames, [THREE_D_KEYWORDS_COLUMN])
    write_csv_rows(output_path, output_fieldnames, output_rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract normalized 3D, digital-twin, and 3D-visualization keywords from the FOSS4G submissions CSV.")
    parser.add_argument("input", nargs="?", default=None, help="Input CSV path")
    parser.add_argument("output", nargs="?", default=DEFAULT_OUTPUT, help="Output CSV path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = resolve_input_path(args.input, DEFAULT_INPUT_CANDIDATES)
    output_path = Path(args.output)

    if input_path.resolve() == output_path.resolve():
        raise SystemExit("Output path must be different from input path.")

    create_output_csv(input_path, output_path)
    print(f"Created: {output_path}")


if __name__ == "__main__":
    main()
