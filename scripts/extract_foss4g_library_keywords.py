#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

from foss4g_csv import (
    ABSTRACT_COLUMN,
    LIBRARY_CSV_CANDIDATES,
    LIBRARY_KEYWORDS_COLUMN,
    SOURCE_CSV_CANDIDATES,
    TITLE_COLUMN,
    build_output_fieldnames,
    read_csv_rows,
    resolve_input_path,
    write_csv_rows,
)


DEFAULT_INPUT_CANDIDATES = SOURCE_CSV_CANDIDATES
DEFAULT_OUTPUT = LIBRARY_CSV_CANDIDATES[0]

LIBRARY_RULES: list[tuple[str, list[str]]] = [
    ("QGIS", [r"\bqgis\b"]),
    ("QField", [r"\bqfield\b", r"q field"]),
    ("GRASS GIS", [r"\bgrass\b"]),
    ("GeoServer", [r"geoserver"]),
    ("GeoNode", [r"geonode"]),
    ("GeoNetwork", [r"geonetwork"]),
    ("PostGIS", [r"postgis"]),
    ("PostgreSQL", [r"postgresql", r"\bpostgres\b"]),
    ("pgRouting", [r"pgrouting"]),
    ("MapLibre", [r"maplibre(?: gl(?: js)?)?"]),
    ("Leaflet", [r"leaflet"]),
    ("OpenLayers", [r"openlayers", r"open layers"]),
    ("CesiumJS", [r"cesiumjs", r"\bcesium\b"]),
    ("Re:Earth", [r"re:earth", r"\breearth\b"]),
    ("MapStore", [r"mapstore"]),
    ("TerriaJS", [r"terriajs"]),
    ("Maplat", [r"\bmaplat\b"]),
    ("TiTiler", [r"titiler"]),
    ("OpenDroneMap", [r"opendronemap", r"open drone map"]),
    ("GeoTools", [r"geotools"]),
    ("GeoPandas", [r"geopandas"]),
    ("GDAL", [r"\bgdal\b"]),
    ("PROJ", [r"\bproj\b"]),
    ("PDAL", [r"\bpdal\b"]),
    ("DuckDB", [r"duckdb"]),
    ("PyTorch", [r"pytorch"]),
    ("OpenCV", [r"opencv"]),
    ("pygeoapi", [r"pygeoapi"]),
    ("pycsw", [r"pycsw"]),
    ("ZOO-Project", [r"zoo-project"]),
    ("QWC", [r"\bqwc\b"]),
    ("DHIS2", [r"dhis2"]),
    ("SWMM", [r"swmm"]),
    ("ImageN", [r"\bimagen\b"]),
    ("GeoAgent", [r"geoagent"]),
    ("GeoPlegma", [r"geoplegma"]),
    ("GeoReports", [r"georeports"]),
    ("GeoGirafe", [r"geogirafe"]),
    ("GeoFence", [r"geofence"]),
    ("GeoCat Bridge", [r"geocat bridge"]),
    ("Ouranos GEX", [r"ouranos gex"]),
    ("MapConductor", [r"mapconductor"]),
    ("QMapCompare", [r"qmapcompare"]),
    ("DigiAgriApp", [r"digiagriapp"]),
    ("MakeGIS", [r"makegis"]),
    ("ChOWDER", [r"chowder"]),
    ("GIFramework", [r"giframework"]),
    ("TrustChain", [r"trustchain"]),
    ("PLATEAU", [r"\bplateau\b"]),
    ("Overture Maps", [r"overturemaps", r"overture maps"]),
    ("SensorThings", [r"sensorthings(?: api)?"]),
]

def normalize_text(text: str) -> str:
    lowered = text.lower()
    replacements = [
        ("map libre", "maplibre"),
        ("open layers", "openlayers"),
        ("re: earth", "re:earth"),
        ("open drone map", "opendronemap"),
        ("q field", "qfield"),
        ("overturemaps", "overture maps"),
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


def extract_library_keywords(title: str, abstract: str) -> list[str]:
    normalized = normalize_text(f"{title} {abstract}")
    matches: list[tuple[int, int, str]] = []

    for index, (label, patterns) in enumerate(LIBRARY_RULES):
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
    return dedupe_preserve_order(label for _, _, label in matches)

def create_output_csv(input_path: Path, output_path: Path) -> None:
    rows, fieldnames = read_csv_rows(input_path)
    output_rows: list[dict[str, str]] = []

    for row in rows:
        title = row.get(TITLE_COLUMN, "").strip()
        abstract = row.get(ABSTRACT_COLUMN, "").strip()
        updated_row = dict(row)
        updated_row[LIBRARY_KEYWORDS_COLUMN] = ", ".join(extract_library_keywords(title, abstract))
        output_rows.append(updated_row)

    output_fieldnames = build_output_fieldnames(fieldnames, [LIBRARY_KEYWORDS_COLUMN])
    write_csv_rows(output_path, output_fieldnames, output_rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract normalized library/tool keywords from the FOSS4G submissions CSV.")
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
