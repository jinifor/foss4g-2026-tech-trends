#!/usr/bin/env python3

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


SOURCE_CSV = "docs/foss4g_2026_talks.csv"

CLOUD_RULES: list[tuple[str, list[str]]] = [
    ("Cloud Native", [r"\bcloud[- ]nativ(?:e|ely)\b"]),
    (
        "Cloud Infrastructure",
        [
            r"\bcloud[- ]based\b",
            r"\bcloud infrastructure\b",
            r"\bcloud computing\b",
            r"\bcloud ai services\b",
            r"\bcloud[- ]optimized architecture[s]?\b",
            r"across any cloud provider",
            r"cloud-native apis",
        ],
    ),
    ("AWS", [r"\baws\b", r"amazon web services", r"bedrock"]),
    ("Kubernetes", [r"\bkubernetes\b", r"\bk8s\b"]),
    ("Docker", [r"\bdocker\b"]),
    ("Containers", [r"\bmulti-container\b", r"\bcontainerized\b", r"\bcontainers\b"]),
    ("Serverless", [r"\bserverless\b", r"scale-to-zero"]),
    ("Auto-scaling", [r"auto-?scal", r"horizontally scalable"]),
    ("S3-Compatible Storage", [r"s3-compatible", r"s3-compliant", r"\bs3 gateway\b"]),
    ("Object Storage", [r"object storage", r"cloud storage"]),
    ("COG", [r"cloud optimized geotiff[s]?", r"cloud-optimized geotiff[s]?", r"\bcog\b", r"\bcogs\b"]),
    ("Zarr", [r"\bzarr\b"]),
    ("PMTiles", [r"\bpmtiles\b"]),
    ("STAC", [r"\bstac\b"]),
    ("TiTiler", [r"\btitiler\b"]),
    ("QFieldCloud", [r"\bqfieldcloud\b"]),
    ("Observability", [r"\bobservability\b", r"opentelemetry", r"prometheus", r"grafana", r"\bloki\b", r"\bslo\b", r"\bslos\b"]),
    ("Deployment", [r"\bdeploying\b", r"deployment strategies", r"deployment gap", r"production-grade", r"production-ready"]),
    ("Workflow Orchestration", [r"\bairflow\b"]),
    ("Browser Runtime", [r"duckdb-wasm", r"\bwebassembly\b", r"\bwasm\b", r"\bwebgpu\b", r"browser-native"]),
    ("Distributed Workers", [r"\bworkers\b", r"\bscheduler\b", r"distributed web rendering"]),
    ("Offline-First", [r"offline-first"]),
    ("Data Gateway", [r"data proxy", r"\bgateway\b"]),
]

SUPPRESSION_RULES: dict[str, set[str]] = {
    "Cloud Native": {"Cloud Infrastructure"},
    "S3-Compatible Storage": {"Object Storage"},
    "Kubernetes": {"Containers"},
    "Docker": {"Containers"},
}

TRIGGER_KEYWORDS = {
    "Cloud Native",
    "Cloud Infrastructure",
    "AWS",
    "Kubernetes",
    "Docker",
    "Containers",
    "Serverless",
    "Auto-scaling",
    "S3-Compatible Storage",
    "Object Storage",
    "COG",
    "Zarr",
    "PMTiles",
    "STAC",
    "TiTiler",
    "QFieldCloud",
    "Observability",
    "Deployment",
    "Workflow Orchestration",
}

CLUSTER_RULES = [
    {
        "id": "cloud-platforms",
        "name": "Cloud Platforms & Architecture",
        "color": "#177e89",
        "patterns": [
            r"cloud native",
            r"cloud infrastructure",
            r"\baws\b",
            r"deployment",
            r"qfieldcloud",
            r"data gateway",
        ],
    },
    {
        "id": "cloud-storage",
        "name": "Cloud Storage & Delivery",
        "color": "#d96c3d",
        "patterns": [
            r"s3-compatible storage",
            r"object storage",
            r"\bcog\b",
            r"\bzarr\b",
            r"\bpmtiles\b",
            r"\bstac\b",
        ],
    },
    {
        "id": "orchestration-ops",
        "name": "Orchestration & Operations",
        "color": "#7a8f3c",
        "patterns": [
            r"kubernetes",
            r"docker",
            r"containers",
            r"auto-scaling",
            r"workflow orchestration",
            r"observability",
        ],
    },
    {
        "id": "runtime-processing",
        "name": "Runtime & Scalable Processing",
        "color": "#7c5cff",
        "patterns": [
            r"serverless",
            r"browser runtime",
            r"distributed workers",
            r"offline-first",
        ],
    },
    {
        "id": "cloud-tooling",
        "name": "Cloud Tooling",
        "color": "#b74f6f",
        "patterns": [
            r"titiler",
        ],
    },
]


def normalize_text(text: str) -> str:
    lowered = text.lower()
    replacements = [
        ("cloud natively", "cloud-native"),
        ("cloud native", "cloud-native"),
        ("cloud optimized", "cloud-optimized"),
        ("s3 compliant", "s3-compliant"),
        ("s3 compatible", "s3-compatible"),
        ("duckdb wasm", "duckdb-wasm"),
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


def extract_cloud_keywords(title: str, abstract: str) -> list[str]:
    normalized = normalize_text(f"{title} {abstract}")
    matches: list[tuple[int, int, str]] = []

    for index, (label, patterns) in enumerate(CLOUD_RULES):
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


def is_cloud_related(keywords: list[str]) -> bool:
    return bool(set(keywords) & TRIGGER_KEYWORDS)


def read_rows(root: Path) -> tuple[list[dict[str, Any]], str, int]:
    csv_path = root / SOURCE_CSV
    rows_out: list[dict[str, Any]] = []
    total_rows = 0

    with csv_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            total_rows += 1
            title = row["발표 제목 (Title)"].strip()
            abstract = row["초록 (Abstract)"].strip()
            keywords = extract_cloud_keywords(title, abstract)
            if not is_cloud_related(keywords):
                continue

            rows_out.append(
                {
                    "id": row["No."].strip(),
                    "page": row["Page"].strip(),
                    "title": title,
                    "abstractSnippet": abstract[:240] + ("..." if len(abstract) > 240 else ""),
                    "keywords": keywords,
                }
            )

    return rows_out, csv_path.name, total_rows


def compute_keyword_stats(rows: list[dict[str, Any]]) -> tuple[Counter, Counter, dict[str, set[str]], dict[str, list[str]]]:
    keyword_counts: Counter = Counter()
    pair_counts: Counter = Counter()
    adjacency: dict[str, set[str]] = defaultdict(set)
    keyword_titles: dict[str, list[str]] = defaultdict(list)

    for row in rows:
        keywords = list(dict.fromkeys(row["keywords"]))
        keyword_counts.update(keywords)
        for keyword in keywords:
            if len(keyword_titles[keyword]) < 4:
                keyword_titles[keyword].append(row["title"])

        for index, source in enumerate(keywords):
            for target in keywords[index + 1 :]:
                pair = tuple(sorted((source, target)))
                pair_counts[pair] += 1
                adjacency[source].add(target)
                adjacency[target].add(source)

    return keyword_counts, pair_counts, adjacency, keyword_titles


def build_top_keyword_cards(keyword_counts: Counter, pair_counts: Counter, keyword_titles: dict[str, list[str]]) -> list[dict[str, Any]]:
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


def cloud_cluster_rule(keyword: str) -> dict[str, Any]:
    lowered = keyword.lower()
    for rule in CLUSTER_RULES:
        if any(re.search(pattern, lowered) for pattern in rule["patterns"]):
            return rule
    return {
        "id": "other-cloud-signals",
        "name": "Other Cloud Signals",
        "color": "#3f7cac",
    }


def build_treemap(keyword_counts: Counter) -> list[dict[str, Any]]:
    top_items = keyword_counts.most_common(18)
    tree = []
    for keyword, count in top_items:
        cluster = cloud_cluster_rule(keyword)
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
                "category": "Other Cloud Signals",
                "color": "#9aa8b3",
            }
        )
    return tree


def build_bubble_series(keyword_counts: Counter, pair_counts: Counter, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    total_presentations = len(rows) or 1
    per_keyword_companions: dict[str, list[int]] = defaultdict(list)
    edge_weight_sum: Counter = Counter()

    for row in rows:
        unique_keywords = list(dict.fromkeys(row["keywords"]))
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


def compute_clusters(keyword_counts: Counter) -> list[dict[str, Any]]:
    top_keywords = [keyword for keyword, _ in keyword_counts.most_common(42)]
    grouped: dict[str, dict[str, Any]] = {}

    for keyword in top_keywords:
        rule = cloud_cluster_rule(keyword)
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
        highlighted = [keyword for keyword in row["keywords"] if keyword in priority_keywords]
        explorer_rows.append(
            {
                "id": row["id"],
                "page": row["page"],
                "title": row["title"],
                "abstractSnippet": row["abstractSnippet"],
                "keywords": row["keywords"],
                "highlightedKeywords": highlighted[:6],
            }
        )
    return explorer_rows


def build_dashboard_payload(root: Path) -> dict[str, Any]:
    rows, source_name, source_total = read_rows(root)
    keyword_counts, pair_counts, adjacency, keyword_titles = compute_keyword_stats(rows)

    total_keywords = sum(keyword_counts.values())
    avg_keywords = round(total_keywords / len(rows), 2) if rows else 0
    presentation_share = round(len(rows) / source_total, 4) if source_total else 0
    network = build_network(keyword_counts, pair_counts)
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
            "topPairs": [{"source": left, "target": right, "count": count} for (left, right), count in pair_counts.most_common(60)],
        },
        "explorer": {
            "presentations": build_explorer_rows(rows, keyword_counts),
        },
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    output_path = root / "src" / "data" / "cloud-dashboard-data.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = build_dashboard_payload(root)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Created: {output_path}")


if __name__ == "__main__":
    main()
