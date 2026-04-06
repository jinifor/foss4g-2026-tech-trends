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
    PAGE_COLUMN,
    SOURCE_CSV_CANDIDATES,
    THREE_D_CSV_CANDIDATES,
    THREE_D_KEYWORDS_COLUMN,
    TITLE_COLUMN,
    find_existing_path,
    resolve_existing_path,
    split_csv_list,
)


THREE_D_FILE_CANDIDATES = THREE_D_CSV_CANDIDATES
SOURCE_FILE_CANDIDATES = SOURCE_CSV_CANDIDATES

THREE_D_CATEGORY_RULES = [
    {
        "id": "three-d-models-twins",
        "name": "3D Models & Twins",
        "color": "#177e89",
        "patterns": [r"^3d$", r"digital twin", r"3d city model"],
    },
    {
        "id": "three-d-platforms-standards",
        "name": "3D Platforms & Standards",
        "color": "#7c5cff",
        "patterns": [r"plateau", r"citygml", r"cityjson", r"\bbim\b"],
    },
    {
        "id": "point-clouds-reconstruction",
        "name": "Point Clouds & Reconstruction",
        "color": "#d96c3d",
        "patterns": [r"point cloud", r"photogrammetry", r"point tiler", r"lidar"],
    },
    {
        "id": "web-rendering-streaming",
        "name": "Web Rendering & Streaming",
        "color": "#7a8f3c",
        "patterns": [r"3d tiles", r"cesiumjs", r"webgl", r"webgpu", r"deck\.gl", r"gltf / glb"],
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


def classify_three_d_category(keyword: str) -> dict[str, str]:
    lowered = keyword.lower()
    for rule in THREE_D_CATEGORY_RULES:
        if any(re.search(pattern, lowered) for pattern in rule["patterns"]):
            return {
                "id": rule["id"],
                "category": rule["name"],
                "color": rule["color"],
            }
    return {
        "id": "general-three-d-signals",
        "category": "General 3D Signals",
        "color": "#3f7cac",
    }


def compute_clusters(keyword_counts: dict[str, int]) -> list[dict[str, Any]]:
    top_keywords = [keyword for keyword, _ in keyword_counts.most_common(42)]
    grouped: dict[str, dict[str, Any]] = {}

    for keyword in top_keywords:
        rule = classify_three_d_category(keyword)
        cluster = grouped.setdefault(
            rule["id"],
            {
                "id": rule["id"],
                "name": rule["category"],
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


def build_treemap(keyword_counts: dict[str, int]) -> list[dict[str, Any]]:
    tree = []
    top_items = keyword_counts.most_common(18)
    for keyword, count in top_items:
        category = classify_three_d_category(keyword)
        tree.append(
            {
                "name": keyword,
                "size": count,
                "category": category["category"],
                "color": category["color"],
            }
        )

    other = sum(keyword_counts.values()) - sum(item["size"] for item in tree)
    if other > 0:
        tree.append(
            {
                "name": "Others",
                "size": other,
                "category": "General 3D Signals",
                "color": "#9aa8b3",
            }
        )
    return tree


def read_rows(root: Path, three_d_extractor: Any) -> tuple[list[dict[str, Any]], str, int]:
    source_path = find_existing_path(THREE_D_FILE_CANDIDATES, root) or resolve_existing_path(SOURCE_FILE_CANDIDATES, root)
    rows_out: list[dict[str, Any]] = []
    total_rows = 0

    with source_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            total_rows += 1
            title = row[TITLE_COLUMN].strip()
            abstract = row[ABSTRACT_COLUMN].strip()
            keywords = split_keywords(row.get(THREE_D_KEYWORDS_COLUMN, ""))
            if not keywords:
                keywords = three_d_extractor.extract_three_d_keywords(title, abstract)
            if not keywords:
                continue

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

    return rows_out, source_path.name, total_rows


def build_dashboard_payload(root: Path) -> dict[str, Any]:
    base = load_module(root / "scripts" / "build_keyword_dashboard_data.py", "keyword_dashboard_builder")
    three_d_extractor = load_module(root / "scripts" / "extract_foss4g_3d_keywords.py", "three_d_extractor")

    rows, source_name, source_total = read_rows(root, three_d_extractor)
    keyword_counts, pair_counts, adjacency, keyword_titles = base.compute_keyword_stats(rows)

    total_keywords = sum(keyword_counts.values())
    avg_keywords = round(total_keywords / len(rows), 2) if rows else 0
    presentation_share = round(len(rows) / source_total, 4) if source_total else 0
    network = base.build_network(keyword_counts, pair_counts)
    clusters = compute_clusters(keyword_counts)

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
            "excludedKeywords": [],
            "presentationShare": presentation_share,
            "sourcePresentationCount": source_total,
        },
        "overview": {
            "cards": base.build_top_keyword_cards(keyword_counts, pair_counts, keyword_titles),
            "topKeywords": top_keywords,
            "wordCloud": [{"keyword": keyword, "count": count} for keyword, count in keyword_counts.most_common(80)],
        },
        "distribution": {
            "longtail": base.build_longtail(keyword_counts),
            "bubble": base.build_bubble_series(keyword_counts, pair_counts, rows),
            "treemap": build_treemap(keyword_counts),
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
    output_path = root / "src" / "data" / "three-d-dashboard-data.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = build_dashboard_payload(root)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Created: {output_path}")


if __name__ == "__main__":
    main()
