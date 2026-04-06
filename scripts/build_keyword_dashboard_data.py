#!/usr/bin/env python3

from __future__ import annotations

import csv
import importlib.util
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from foss4g_csv import (
    ABSTRACT_COLUMN,
    ID_COLUMN,
    KEYWORD_CSV_CANDIDATES,
    KEYWORDS_COLUMN,
    PAGE_COLUMN,
    SOURCE_CSV_CANDIDATES,
    TITLE_COLUMN,
    find_existing_path,
    resolve_existing_path,
    split_csv_list,
)

KEYWORD_FILE_CANDIDATES = KEYWORD_CSV_CANDIDATES
SOURCE_FILE_CANDIDATES = SOURCE_CSV_CANDIDATES

CLUSTER_COLOR_PALETTE = [
    "#177e89",
    "#d96c3d",
    "#7a8f3c",
    "#7c5cff",
    "#b74f6f",
    "#3f7cac",
    "#c48a29",
    "#4f9d69",
]

EXCLUDED_VISUALIZATION_KEYWORDS = {
    "Open Source",
    "GIS",
    "FOSS4G",
    "OSGeo",
    "Open Data",
    "Spatial Data",
    "Geospatial Data",
    "Spatial Information",
    "Geospatial Tools",
}

SEMANTIC_CLUSTER_RULES = [
    {
        "id": "open-geo-stack",
        "name": "Open Geo Stack",
        "color": "#177e89",
        "patterns": [
            r"open source",
            r"\bgis\b",
            r"qgis",
            r"geoserver",
            r"postgis",
            r"geonode",
            r"geonetwork",
            r"osgeo",
            r"foss4g",
            r"qfield",
            r"grass",
            r"re:earth",
            r"pgrouting",
        ],
    },
    {
        "id": "mapping-cartography",
        "name": "Mapping & Cartography",
        "color": "#d96c3d",
        "patterns": [
            r"maplibre",
            r"leaflet",
            r"openlayers",
            r"vector tiles",
            r"raster tiles",
            r"pmtiles",
            r"interactive map",
            r"web mapping",
            r"cartography",
            r"visualization",
            r"map design",
            r"map applications",
            r"projection",
            r"infographics",
            r"font rendering",
        ],
    },
    {
        "id": "standards-data",
        "name": "Standards & Data Infra",
        "color": "#7a8f3c",
        "patterns": [
            r"spatial data",
            r"geospatial data",
            r"api",
            r"ogc",
            r"stac",
            r"geoparquet",
            r"geoarrow",
            r"flatgeobuf",
            r"geojson",
            r"json",
            r"xml",
            r"rdf",
            r"linked data",
            r"metadata",
            r"sql",
            r"postgres",
            r"duckdb",
            r"data gateway",
            r"data publishing",
            r"spatial data infrastructure",
            r"crs",
        ],
    },
    {
        "id": "ai-automation",
        "name": "AI & Automation",
        "color": "#7c5cff",
        "patterns": [
            r"\bai\b",
            r"llm",
            r"geollm",
            r"geoai",
            r"machine learning",
            r"deep learning",
            r"natural language",
            r"computer vision",
            r"graphrag",
            r"graph neural",
            r"pytorch",
            r"opencv",
            r"mcp",
            r"automation",
        ],
    },
    {
        "id": "eo-3d-survey",
        "name": "EO / 3D / Survey",
        "color": "#b74f6f",
        "patterns": [
            r"\b3d\b",
            r"digital twin",
            r"point cloud",
            r"lidar",
            r"remote sensing",
            r"earth observation",
            r"satellite",
            r"sar",
            r"nisar",
            r"photogrammetry",
            r"\buav\b",
            r"drone",
            r"gnss",
            r"digital elevation model",
            r"digital terrain model",
            r"bim",
            r"citygml",
            r"ndvi",
            r"cesiumjs",
        ],
    },
    {
        "id": "community-programs",
        "name": "Community & Programs",
        "color": "#3f7cac",
        "patterns": [
            r"open mapping",
            r"hot",
            r"youthmappers",
            r"localization",
            r"foss workflows",
            r"foss stack",
            r"open-access platform",
            r"web app",
            r"plugin",
            r"dashboard",
            r"devtools",
            r"community",
        ],
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


def filter_visual_keywords(keywords: list[str]) -> list[str]:
    return [keyword for keyword in keywords if keyword not in EXCLUDED_VISUALIZATION_KEYWORDS]

def read_rows(root: Path) -> tuple[list[dict[str, Any]], str]:
    extractor = load_module(root / "scripts" / "extract_foss4g_keywords.py", "keyword_extractor")
    source_path = find_existing_path(KEYWORD_FILE_CANDIDATES, root) or resolve_existing_path(SOURCE_FILE_CANDIDATES, root)
    source_name = source_path.name
    rows_out: list[dict[str, Any]] = []

    with source_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            title = row[TITLE_COLUMN].strip()
            abstract = row[ABSTRACT_COLUMN].strip()
            keywords = split_keywords(row.get(KEYWORDS_COLUMN, ""))
            if not keywords:
                keywords = extractor.extract_keywords(title, abstract)

            rows_out.append(
                {
                    "id": row[ID_COLUMN].strip(),
                    "page": row[PAGE_COLUMN].strip(),
                    "title": title,
                    "abstract": abstract,
                    "abstractSnippet": abstract[:220] + ("..." if len(abstract) > 220 else ""),
                    "keywords": keywords,
                    "visualKeywords": filter_visual_keywords(keywords),
                    "keywordCount": len(keywords),
                }
            )

    return rows_out, source_name


def compute_keyword_stats(rows: list[dict[str, Any]]) -> tuple[Counter, Counter, dict[str, set[str]], dict[str, list[str]]]:
    keyword_counts: Counter = Counter()
    pair_counts: Counter = Counter()
    adjacency: dict[str, set[str]] = defaultdict(set)
    keyword_titles: dict[str, list[str]] = defaultdict(list)

    for row in rows:
        keywords = list(dict.fromkeys(row["visualKeywords"]))
        keyword_counts.update(keywords)
        for keyword in keywords:
            if len(keyword_titles[keyword]) < 4:
                keyword_titles[keyword].append(row["title"])

        for i, source in enumerate(keywords):
            for target in keywords[i + 1 :]:
                pair = tuple(sorted((source, target)))
                pair_counts[pair] += 1
                adjacency[source].add(target)
                adjacency[target].add(source)

    return keyword_counts, pair_counts, adjacency, keyword_titles


def build_top_keyword_cards(
    keyword_counts: Counter,
    pair_counts: Counter,
    keyword_titles: dict[str, list[str]],
) -> list[dict[str, Any]]:
    cards = []
    for keyword, count in keyword_counts.most_common(6):
        related = []
        for (left, right), pair_count in pair_counts.items():
            if left == keyword:
                related.append((right, pair_count))
            elif right == keyword:
                related.append((left, pair_count))
        related.sort(key=lambda item: (-item[1], item[0]))
        cards.append(
            {
                "keyword": keyword,
                "count": count,
                "related": [{"keyword": label, "count": pair_count} for label, pair_count in related[:3]],
                "samples": keyword_titles.get(keyword, [])[:4],
            }
        )
    return cards


def build_longtail(keyword_counts: Counter) -> list[dict[str, Any]]:
    total = sum(keyword_counts.values()) or 1
    cumulative = 0
    series = []
    for rank, (keyword, count) in enumerate(keyword_counts.most_common(), start=1):
        cumulative += count
        series.append(
            {
                "rank": rank,
                "keyword": keyword,
                "count": count,
                "cumulativeShare": round(cumulative / total, 4),
            }
        )
    return series


def build_treemap(keyword_counts: Counter) -> list[dict[str, Any]]:
    top_items = keyword_counts.most_common(18)
    tree = []
    for keyword, count in top_items:
        cluster = keyword_cluster_rule(keyword)
        tree.append(
            {
                "name": keyword,
                "size": count,
                "category": cluster["name"],
                "color": cluster["color"],
            }
        )
    other = sum(keyword_counts.values()) - sum(count for _, count in top_items)
    if other > 0:
        tree.append(
            {
                "name": "Others",
                "size": other,
                "category": "Other keywords",
                "color": "#9aa8b3",
            }
        )
    return tree


def build_bubble_series(keyword_counts: Counter, pair_counts: Counter, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    total_presentations = len(rows) or 1
    per_keyword_companions: dict[str, list[int]] = defaultdict(list)
    edge_weight_sum: Counter = Counter()

    for row in rows:
        unique_keywords = list(dict.fromkeys(row["visualKeywords"]))
        companions = max(len(unique_keywords) - 1, 0)
        for keyword in unique_keywords:
            per_keyword_companions[keyword].append(companions)

    for (left, right), count in pair_counts.items():
        edge_weight_sum[left] += count
        edge_weight_sum[right] += count

    bubbles = []
    for keyword, count in keyword_counts.most_common(28):
        avg_companions = 0.0
        if per_keyword_companions[keyword]:
            avg_companions = sum(per_keyword_companions[keyword]) / len(per_keyword_companions[keyword])
        bubbles.append(
            {
                "keyword": keyword,
                "x": count,
                "y": round(avg_companions, 2),
                "z": count,
                "connectionScore": edge_weight_sum[keyword],
                "share": round(count / total_presentations, 4),
            }
        )
    return bubbles


def build_heatmap(keyword_counts: Counter, pair_counts: Counter) -> dict[str, Any]:
    labels = [keyword for keyword, _ in keyword_counts.most_common(18)]
    matrix = []
    max_value = 0
    for source in labels:
        row = []
        for target in labels:
            if source == target:
                value = keyword_counts[source]
            else:
                value = pair_counts[tuple(sorted((source, target)))]
            row.append(value)
            max_value = max(max_value, value)
        matrix.append(row)
    return {"labels": labels, "matrix": matrix, "max": max_value or 1}


def build_network(keyword_counts: Counter, pair_counts: Counter) -> dict[str, Any]:
    top_keywords = [keyword for keyword, _ in keyword_counts.most_common(26)]
    nodes = [{"id": keyword, "keyword": keyword, "count": keyword_counts[keyword]} for keyword in top_keywords]
    links = []
    for (left, right), count in pair_counts.most_common():
        if count < 2:
            continue
        if left in top_keywords and right in top_keywords:
            links.append({"source": left, "target": right, "count": count})
    return {"nodes": nodes, "links": links}


def keyword_cluster_rule(keyword: str) -> dict[str, Any]:
    lowered = keyword.lower()
    for rule in SEMANTIC_CLUSTER_RULES:
        if any(re.search(pattern, lowered) for pattern in rule["patterns"]):
            return rule
    return {
        "id": "domain-signals",
        "name": "Domain Signals",
        "color": "#c48a29",
    }


def compute_clusters(keyword_counts: Counter, pair_counts: Counter) -> list[dict[str, Any]]:
    top_keywords = [keyword for keyword, _ in keyword_counts.most_common(42)]
    grouped: dict[str, dict[str, Any]] = {}

    for keyword in top_keywords:
        rule = keyword_cluster_rule(keyword)
        cluster = grouped.setdefault(
            rule["id"],
            {
                "id": rule["id"],
                "name": rule["name"],
                "color": rule["color"],
                "keywords": [],
            },
        )
        cluster["keywords"].append({"keyword": keyword, "count": keyword_counts[keyword]})

    clusters = []
    for cluster in grouped.values():
        cluster["keywords"].sort(key=lambda item: (-item["count"], item["keyword"]))
        cluster["total"] = sum(item["count"] for item in cluster["keywords"])
        clusters.append(cluster)

    clusters.sort(key=lambda item: (-item["total"], item["name"]))
    return clusters


def build_explorer_rows(rows: list[dict[str, Any]], keyword_counts: Counter) -> list[dict[str, Any]]:
    priority_keywords = {keyword for keyword, _ in keyword_counts.most_common(30)}
    explorer_rows = []
    for row in rows:
        display_keywords = row["visualKeywords"] or row["keywords"]
        highlighted = [keyword for keyword in display_keywords if keyword in priority_keywords]
        explorer_rows.append(
            {
                "id": row["id"],
                "page": row["page"],
                "title": row["title"],
                "abstractSnippet": row["abstractSnippet"],
                "keywords": display_keywords,
                "highlightedKeywords": highlighted[:6],
            }
        )
    return explorer_rows


def build_dashboard_payload(root: Path) -> dict[str, Any]:
    rows, source_name = read_rows(root)
    keyword_counts, pair_counts, adjacency, keyword_titles = compute_keyword_stats(rows)

    total_keywords = sum(keyword_counts.values())
    avg_keywords = round(total_keywords / len(rows), 2) if rows else 0
    network = build_network(keyword_counts, pair_counts)
    clusters = compute_clusters(keyword_counts, pair_counts)

    node_cluster_lookup: dict[str, str] = {}
    for cluster in clusters:
        for keyword in cluster["keywords"]:
            node_cluster_lookup[keyword["keyword"]] = cluster["id"]

    for node in network["nodes"]:
        node["cluster"] = node_cluster_lookup.get(node["id"], "")
        node["degree"] = len(adjacency.get(node["id"], set()))

    top_keywords = [{"keyword": keyword, "count": count} for keyword, count in keyword_counts.most_common(100)]

    return {
        "meta": {
            "sourceWorkbook": source_name,
            "totalPresentations": len(rows),
            "uniqueKeywords": len(keyword_counts),
            "totalKeywordMentions": total_keywords,
            "averageKeywordsPerPresentation": avg_keywords,
            "excludedKeywords": sorted(EXCLUDED_VISUALIZATION_KEYWORDS),
        },
        "overview": {
            "cards": build_top_keyword_cards(keyword_counts, pair_counts, keyword_titles),
            "topKeywords": top_keywords,
            "wordCloud": [{"keyword": keyword, "count": count} for keyword, count in keyword_counts.most_common(80)],
        },
        "distribution": {
            "longtail": build_longtail(keyword_counts),
            "bubble": build_bubble_series(keyword_counts, pair_counts, rows),
            "treemap": build_treemap(keyword_counts),
        },
        "relationships": {
            "network": network,
            "heatmap": build_heatmap(keyword_counts, pair_counts),
            "clusters": clusters,
            "topPairs": [
                {"source": left, "target": right, "count": count}
                for (left, right), count in pair_counts.most_common(60)
            ],
        },
        "explorer": {
            "presentations": build_explorer_rows(rows, keyword_counts),
        },
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    output_path = root / "src" / "data" / "dashboard-data.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = build_dashboard_payload(root)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Created: {output_path}")


if __name__ == "__main__":
    main()
