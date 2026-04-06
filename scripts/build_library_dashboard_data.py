#!/usr/bin/env python3

from __future__ import annotations

import csv
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

from foss4g_csv import (
    ABSTRACT_COLUMN,
    ID_COLUMN,
    LIBRARY_CSV_CANDIDATES,
    LIBRARY_KEYWORDS_COLUMN,
    PAGE_COLUMN,
    SOURCE_CSV_CANDIDATES,
    TITLE_COLUMN,
    find_existing_path,
    resolve_existing_path,
    split_csv_list,
)


LIBRARY_FILE_CANDIDATES = LIBRARY_CSV_CANDIDATES
SOURCE_FILE_CANDIDATES = SOURCE_CSV_CANDIDATES

LIBRARY_CATEGORY_RULES = [
    {
        "name": "Desktop GIS",
        "color": "#177e89",
        "patterns": [r"qgis", r"qfield", r"grass gis"],
    },
    {
        "name": "Web Mapping",
        "color": "#d96c3d",
        "patterns": [r"maplibre", r"leaflet", r"openlayers", r"re:earth", r"mapstore", r"terriajs", r"maplat", r"overture maps"],
    },
    {
        "name": "Server & APIs",
        "color": "#7a8f3c",
        "patterns": [r"geoserver", r"geonode", r"geonetwork", r"pygeoapi", r"titiler", r"zoo-project", r"qwc", r"sensorthings"],
    },
    {
        "name": "Database & Storage",
        "color": "#7c5cff",
        "patterns": [r"postgis", r"postgresql", r"duckdb"],
    },
    {
        "name": "Geo Data Processing",
        "color": "#b74f6f",
        "patterns": [r"gdal", r"proj", r"pdal", r"geotools", r"geopandas", r"swmm"],
    },
    {
        "name": "3D & EO Platforms",
        "color": "#3f7cac",
        "patterns": [r"cesiumjs", r"plateau", r"opendronemap"],
    },
]


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def split_keywords(value: str) -> list[str]:
    return split_csv_list(value)


def classify_library_category(keyword: str) -> dict[str, str]:
    lowered = keyword.lower()
    for rule in LIBRARY_CATEGORY_RULES:
        if any(re.search(pattern, lowered) for pattern in rule["patterns"]):
            return {
                "category": rule["name"],
                "color": rule["color"],
            }
    return {
        "category": "Other Libraries",
        "color": "#9aa8b3",
    }


def read_rows(root: Path, library_extractor: Any) -> tuple[list[dict[str, Any]], str]:
    source_path = find_existing_path(LIBRARY_FILE_CANDIDATES, root) or resolve_existing_path(SOURCE_FILE_CANDIDATES, root)
    rows_out: list[dict[str, Any]] = []

    with source_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            title = row[TITLE_COLUMN].strip()
            abstract = row[ABSTRACT_COLUMN].strip()
            keywords = split_keywords(row.get(LIBRARY_KEYWORDS_COLUMN, ""))
            if not keywords:
                keywords = library_extractor.extract_library_keywords(title, abstract)

            rows_out.append(
                {
                    "id": row[ID_COLUMN].strip(),
                    "page": row[PAGE_COLUMN].strip(),
                    "title": title,
                    "abstract": abstract,
                    "abstractSnippet": abstract[:220] + ("..." if len(abstract) > 220 else ""),
                    "keywords": keywords,
                    "visualKeywords": keywords,
                    "keywordCount": len(keywords),
                }
            )

    return rows_out, source_path.name


def build_dashboard_payload(root: Path) -> dict[str, Any]:
    base = load_module(root / "scripts" / "build_keyword_dashboard_data.py", "keyword_dashboard_builder")
    library_extractor = load_module(root / "scripts" / "extract_foss4g_library_keywords.py", "library_extractor")

    rows, source_name = read_rows(root, library_extractor)
    keyword_counts, pair_counts, adjacency, keyword_titles = base.compute_keyword_stats(rows)

    total_keywords = sum(keyword_counts.values())
    avg_keywords = round(total_keywords / len(rows), 2) if rows else 0
    network = base.build_network(keyword_counts, pair_counts)
    clusters = base.compute_clusters(keyword_counts, pair_counts)

    node_cluster_lookup: dict[str, str] = {}
    for cluster in clusters:
      for keyword in cluster["keywords"]:
          node_cluster_lookup[keyword["keyword"]] = cluster["id"]

    for node in network["nodes"]:
        node["cluster"] = node_cluster_lookup.get(node["id"], "")
        node["degree"] = len(adjacency.get(node["id"], set()))

    top_keywords = [{"keyword": keyword, "count": count} for keyword, count in keyword_counts.most_common(100)]
    library_treemap = []
    for keyword, count in keyword_counts.most_common(18):
        category = classify_library_category(keyword)
        library_treemap.append(
            {
                "name": keyword,
                "size": count,
                "category": category["category"],
                "color": category["color"],
            }
        )
    other = sum(keyword_counts.values()) - sum(item["size"] for item in library_treemap)
    if other > 0:
        library_treemap.append(
            {
                "name": "Others",
                "size": other,
                "category": "Other Libraries",
                "color": "#9aa8b3",
            }
        )

    return {
        "meta": {
            "sourceWorkbook": source_name,
            "totalPresentations": len(rows),
            "uniqueKeywords": len(keyword_counts),
            "totalKeywordMentions": total_keywords,
            "averageKeywordsPerPresentation": avg_keywords,
            "excludedKeywords": [],
        },
        "overview": {
            "cards": base.build_top_keyword_cards(keyword_counts, pair_counts, keyword_titles),
            "topKeywords": top_keywords,
            "wordCloud": [{"keyword": keyword, "count": count} for keyword, count in keyword_counts.most_common(80)],
        },
        "distribution": {
            "longtail": base.build_longtail(keyword_counts),
            "bubble": base.build_bubble_series(keyword_counts, pair_counts, rows),
            "treemap": library_treemap,
        },
        "relationships": {
            "network": network,
            "heatmap": base.build_heatmap(keyword_counts, pair_counts),
            "clusters": clusters,
            "topPairs": [
                {"source": left, "target": right, "count": count}
                for (left, right), count in pair_counts.most_common(60)
            ],
        },
        "explorer": {
            "presentations": base.build_explorer_rows(rows, keyword_counts),
        },
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    output_path = root / "src" / "data" / "library-dashboard-data.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = build_dashboard_payload(root)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Created: {output_path}")


if __name__ == "__main__":
    main()
