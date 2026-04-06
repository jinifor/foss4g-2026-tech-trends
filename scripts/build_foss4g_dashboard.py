#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
from collections import Counter, OrderedDict, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from foss4g_csv import (
    ABSTRACT_COLUMN,
    APPLICATION_AREA_COLUMN,
    CATEGORY_CSV_CANDIDATES,
    ID_COLUMN,
    PAGE_COLUMN,
    SOURCE_CSV_CANDIDATES,
    TECH_TOOLS_COLUMN,
    TITLE_COLUMN,
    find_existing_path,
    split_csv_list,
    MAIN_THEME_COLUMN,
)

GENERIC_THEME = "일반 GIS·공간정보"
GENERIC_TECH = "일반 GIS 워크플로우"
GENERIC_APP = "범용·크로스도메인"
DEFAULT_INPUT = CATEGORY_CSV_CANDIDATES[0]

KEYWORD_PATTERNS = OrderedDict(
    [
        ("Open Source GIS", {"group": "theme", "patterns": [r"open source", r"\bosgeo\b", r"\bfoss4g\b"]}),
        ("QGIS", {"group": "tech", "patterns": [r"\bqgis\b"]}),
        ("Geospatial Data", {"group": "theme", "patterns": [r"geospatial data", r"spatial data"]}),
        ("Web Mapping", {"group": "theme", "patterns": [r"web map", r"web mapping", r"maplibre", r"leaflet", r"openlayers"]}),
        ("MapLibre", {"group": "tech", "patterns": [r"maplibre"]}),
        ("OpenStreetMap", {"group": "tech", "patterns": [r"openstreetmap", r"\bosm\b"]}),
        ("GeoServer", {"group": "tech", "patterns": [r"geoserver"]}),
        ("PostGIS", {"group": "tech", "patterns": [r"postgis"]}),
        ("OGC API", {"group": "tech", "patterns": [r"ogc api", r"\bogc\b"]}),
        ("STAC", {"group": "tech", "patterns": [r"\bstac\b"]}),
        ("GeoParquet", {"group": "tech", "patterns": [r"geoparquet"]}),
        ("Cloud", {"group": "theme", "patterns": [r"\bcloud\b", r"\baws\b", r"\bazure\b", r"\bgcp\b"]}),
        ("AI", {"group": "theme", "patterns": [r"\bai\b", r"geo ai"]}),
        ("LLM", {"group": "theme", "patterns": [r"\bllm\b", r"geo llm"]}),
        ("Machine Learning", {"group": "theme", "patterns": [r"\bml\b", r"machine learning", r"deep learning"]}),
        ("3D", {"group": "theme", "patterns": [r"\b3d\b"]}),
        ("Digital Twin", {"group": "theme", "patterns": [r"digital twin"]}),
        ("Earth Observation", {"group": "theme", "patterns": [r"earth observation"]}),
        ("Remote Sensing", {"group": "theme", "patterns": [r"remote sensing"]}),
        ("Satellite Imagery", {"group": "tech", "patterns": [r"\bsatellite\b"]}),
        ("LiDAR", {"group": "tech", "patterns": [r"lidar"]}),
        ("Point Cloud", {"group": "tech", "patterns": [r"point cloud"]}),
        ("UAV/Drone", {"group": "tech", "patterns": [r"\buav\b", r"\bdrone\b"]}),
        ("Photogrammetry", {"group": "tech", "patterns": [r"photogrammetr"]}),
        ("GNSS", {"group": "tech", "patterns": [r"\bgnss\b", r"\brtk\b"]}),
        ("Vector Tiles", {"group": "tech", "patterns": [r"vector tiles?", r"\bmvt\b", r"pmtiles"]}),
        ("Cartography", {"group": "theme", "patterns": [r"cartograph", r"projection", r"hillshading"]}),
        ("Spatial Analysis", {"group": "theme", "patterns": [r"spatial analysis", r"geospatial analysis", r"network analysis", r"heatmap"]}),
        ("Open Data", {"group": "theme", "patterns": [r"open data"]}),
        ("Community", {"group": "domain", "patterns": [r"community", r"volunteer", r"youthmappers"]}),
        ("Urban", {"group": "domain", "patterns": [r"\burban\b", r"\bcity\b", r"cities"]}),
        ("Mobility", {"group": "domain", "patterns": [r"\bmobility\b", r"transport", r"traffic", r"commuting", r"railway"]}),
        ("Climate", {"group": "domain", "patterns": [r"\bclimate\b", r"\bweather\b", r"meteorolog"]}),
        ("Disaster", {"group": "domain", "patterns": [r"disaster", r"flood", r"wildfire", r"hazard", r"resilience"]}),
        ("Water", {"group": "domain", "patterns": [r"\bwater\b", r"river", r"basin", r"watershed", r"marine", r"ocean", r"coastal"]}),
        ("Forest", {"group": "domain", "patterns": [r"forest", r"forestry", r"canopy", r"biodiversity", r"ecolog", r"wildlife"]}),
        ("Agriculture", {"group": "domain", "patterns": [r"agri", r"crop", r"farm", r"soil", r"irrigation"]}),
        ("Energy", {"group": "domain", "patterns": [r"energy", r"electric", r"grid", r"solar", r"wind", r"renewable"]}),
        ("Heritage", {"group": "domain", "patterns": [r"heritage", r"archive", r"history", r"cultural", r"museum", r"peace"]}),
    ]
)

THEME_TO_TECH_HINT = {
    "AI·ML·GeoAI": "AI/ML",
    "3D·디지털 트윈·시각화": "3D Visualization",
    "원격탐사·지구관측": "Remote Sensing",
    "측량·GNSS·포토그래메트리": "Surveying/Photogrammetry",
    "웹 매핑·인터랙티브 지도": "Web Mapping",
    "공간데이터 인프라·표준": "Spatial Data Standards",
    "클라우드·데이터 엔지니어링": "Data Engineering",
    "오픈소스 GIS·플랫폼": "Open Source GIS",
    "공간분석·모델링": "Spatial Analysis",
    "카토그래피·UX·스토리텔링": "Cartography/UX",
    "앱 개발·클라이언트": "Dashboard/Web App",
    "성능·품질·운영": "Performance/Operations",
    "오픈데이터·커뮤니티·교육": "Open Data/Community",
}

THEME_TO_APP_HINT = {
    "측량·GNSS·포토그래메트리": "현장조사·모니터링",
    "웹 매핑·인터랙티브 지도": "지도 디자인·스토리텔링",
    "카토그래피·UX·스토리텔링": "지도 디자인·스토리텔링",
    "앱 개발·클라이언트": "플랫폼·서비스 구축",
    "공간데이터 인프라·표준": "플랫폼·서비스 구축",
    "클라우드·데이터 엔지니어링": "개발자 도구·운영",
    "성능·품질·운영": "개발자 도구·운영",
    "오픈데이터·커뮤니티·교육": "커뮤니티·사회적 영향",
    "오픈소스 GIS·플랫폼": "플랫폼·서비스 구축",
    "원격탐사·지구관측": "환경·오염 모니터링",
    "3D·디지털 트윈·시각화": "지도 디자인·스토리텔링",
    "공간분석·모델링": "범용·크로스도메인",
    "AI·ML·GeoAI": "범용·크로스도메인",
}


def load_classifier_module(script_path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("classifier", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import classifier script: {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def split_labels(value: str) -> list[str]:
    return split_csv_list(value)


def read_rows(csv_path: Path, classifier_module: Any) -> list[dict[str, Any]]:
    rows_out: list[dict[str, Any]] = []
    with csv_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            title = row.get(TITLE_COLUMN, "")
            abstract = row.get(ABSTRACT_COLUMN, "")
            themes = split_labels(row.get(MAIN_THEME_COLUMN, ""))
            techs = split_labels(row.get(TECH_TOOLS_COLUMN, ""))
            apps = split_labels(row.get(APPLICATION_AREA_COLUMN, ""))

            if not themes or not techs or not apps:
                inferred_themes, inferred_techs, inferred_apps = classifier_module.classify_submission(title, abstract)
                themes = themes or inferred_themes
                techs = techs or inferred_techs
                apps = apps or inferred_apps

            rows_out.append(
                {
                    "no": row.get(ID_COLUMN, ""),
                    "page": row.get(PAGE_COLUMN, ""),
                    "title": title,
                    "abstract": abstract,
                    "themes": themes,
                    "techs": techs,
                    "apps": apps,
                    "normalized": classifier_module.normalize_text(f"{title} {abstract}"),
                }
            )
    return rows_out


def count_labels(rows: list[dict[str, Any]], key: str, exclude: set[str] | None = None) -> Counter:
    counter: Counter = Counter()
    exclude = exclude or set()
    for row in rows:
        for label in row[key]:
            if label not in exclude:
                counter[label] += 1
    return counter


def build_keyword_counts(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter = Counter()
    for row in rows:
        matched_labels: list[str] = []
        normalized = row["normalized"]
        for label, rule in KEYWORD_PATTERNS.items():
            if any(re.search(pattern, normalized) for pattern in rule["patterns"]):
                matched_labels.append(label)
        for label in dict.fromkeys(matched_labels):
            counts[label] += 1

    results = []
    for label, count in counts.most_common():
        results.append(
            {
                "label": label,
                "count": count,
                "group": KEYWORD_PATTERNS[label]["group"],
            }
        )
    return results


def build_heatmap(tech_counts: Counter, app_counts: Counter, rows: list[dict[str, Any]]) -> dict[str, Any]:
    tech_labels = [label for label, _ in tech_counts.most_common(12)]
    app_labels = [label for label, _ in app_counts.most_common(10)]

    matrix_counter: Counter = Counter()
    for row in rows:
        row_techs = [label for label in row["techs"] if label in tech_labels]
        row_apps = [label for label in row["apps"] if label in app_labels]
        for tech in row_techs:
            for app in row_apps:
                matrix_counter[(tech, app)] += 1

    values: list[list[int]] = []
    max_value = 0
    for tech in tech_labels:
        row_values: list[int] = []
        for app in app_labels:
            count = matrix_counter[(tech, app)]
            row_values.append(count)
            if count > max_value:
                max_value = count
        values.append(row_values)

    return {
        "rows": tech_labels,
        "cols": app_labels,
        "values": values,
        "max": max_value or 1,
    }


def pick_top_related(counter: Counter, limit: int, minimum: int = 2) -> list[tuple[str, int]]:
    return [(label, count) for label, count in counter.most_common() if count >= minimum][:limit]


def build_network(rows: list[dict[str, Any]], theme_counts: Counter, tech_counts: Counter, app_counts: Counter) -> dict[str, Any]:
    theme_nodes = [label for label, _ in theme_counts.most_common(7) if label != GENERIC_THEME]
    tech_nodes = [label for label, _ in tech_counts.most_common(10) if label != GENERIC_TECH]
    app_nodes = [label for label, _ in app_counts.most_common(10) if label != GENERIC_APP]

    tech_theme_counter: Counter = Counter()
    theme_app_counter: Counter = Counter()
    tech_app_counter: Counter = Counter()

    for row in rows:
        themes = [label for label in row["themes"] if label in theme_nodes]
        techs = [label for label in row["techs"] if label in tech_nodes]
        apps = [label for label in row["apps"] if label in app_nodes]

        for tech in techs:
            for theme in themes:
                tech_theme_counter[(tech, theme)] += 1
        for theme in themes:
            for app in apps:
                theme_app_counter[(theme, app)] += 1
        for tech in techs:
            for app in apps:
                tech_app_counter[(tech, app)] += 1

    nodes = []
    for label in tech_nodes:
        nodes.append({"id": label, "label": label, "type": "tech", "count": tech_counts[label]})
    for label in theme_nodes:
        nodes.append({"id": label, "label": label, "type": "theme", "count": theme_counts[label]})
    for label in app_nodes:
        nodes.append({"id": label, "label": label, "type": "app", "count": app_counts[label]})

    edges = []
    for tech in tech_nodes:
        related = Counter({theme: tech_theme_counter[(tech, theme)] for theme in theme_nodes})
        for theme, count in pick_top_related(related, 2):
            edges.append(
                {
                    "source": tech,
                    "target": theme,
                    "count": count,
                    "type": "ontology",
                    "label": "기술 -> 대주제",
                }
            )

    for app in app_nodes:
        related = Counter({theme: theme_app_counter[(theme, app)] for theme in theme_nodes})
        for theme, count in pick_top_related(related, 2):
            edges.append(
                {
                    "source": theme,
                    "target": app,
                    "count": count,
                    "type": "ontology",
                    "label": "대주제 -> 활용 분야",
                }
            )

    co_edges = [
        {
            "source": tech,
            "target": app,
            "count": count,
            "type": "cooccurrence",
            "label": "기술 <-> 활용 분야 공동출현",
        }
        for (tech, app), count in tech_app_counter.most_common(18)
        if count >= 3 and tech in tech_nodes and app in app_nodes
    ]
    edges.extend(co_edges)

    return {"nodes": nodes, "edges": edges}


def build_top_pairs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pair_counter: Counter = Counter()
    for row in rows:
        techs = [label for label in row["techs"] if label != GENERIC_TECH]
        apps = [label for label in row["apps"] if label != GENERIC_APP]
        for tech in techs:
            for app in apps:
                pair_counter[(tech, app)] += 1

    results = []
    for (tech, app), count in pair_counter.most_common(30):
        results.append({"tech": tech, "app": app, "count": count})
    return results


def build_summary_tables(
    keyword_counts: list[dict[str, Any]],
    theme_counts: Counter,
    tech_counts: Counter,
    app_counts: Counter,
    top_pairs: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "keywords": keyword_counts[:30],
        "themes": [{"label": label, "count": count} for label, count in theme_counts.most_common()],
        "techs": [{"label": label, "count": count} for label, count in tech_counts.most_common()],
        "applications": [{"label": label, "count": count} for label, count in app_counts.most_common()],
        "pairs": top_pairs,
    }


def build_csv_rows(
    keyword_counts: list[dict[str, Any]],
    theme_counts: Counter,
    tech_counts: Counter,
    app_counts: Counter,
    top_pairs: list[dict[str, Any]],
) -> list[list[Any]]:
    csv_rows: list[list[Any]] = [["section", "label", "sub_label", "count"]]

    for item in keyword_counts:
        csv_rows.append(["keyword_count", item["label"], "", item["count"]])
    for label, count in theme_counts.most_common():
        csv_rows.append(["theme_count", label, "", count])
    for label, count in tech_counts.most_common():
        csv_rows.append(["tech_count", label, "", count])
    for label, count in app_counts.most_common():
        csv_rows.append(["application_count", label, "", count])
    for item in top_pairs:
        csv_rows.append(["tech_application", item["tech"], item["app"], item["count"]])

    return csv_rows


def write_csv(path: Path, rows: list[list[Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as output:
        writer = csv.writer(output)
        writer.writerows(rows)


def render_html(data: dict[str, Any], csv_filename: str) -> str:
    template = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>FOSS4G 2026 Tech Trend Atlas</title>
  <style>
    :root {
      --bg: #f6f1e8;
      --panel: rgba(255, 251, 245, 0.86);
      --panel-strong: rgba(255, 252, 247, 0.94);
      --line: rgba(27, 62, 74, 0.12);
      --text: #173640;
      --muted: #617d87;
      --accent: #177e89;
      --accent-2: #d96c3d;
      --accent-3: #e8b84c;
      --theme: #177e89;
      --tech: #d96c3d;
      --domain: #7a8f3c;
      --shadow: 0 20px 60px rgba(23, 54, 64, 0.12);
      --radius: 26px;
    }

    * { box-sizing: border-box; }
    html, body { margin: 0; padding: 0; }
    body {
      background:
        radial-gradient(circle at top left, rgba(23, 126, 137, 0.18), transparent 34%),
        radial-gradient(circle at 80% 10%, rgba(217, 108, 61, 0.18), transparent 30%),
        linear-gradient(180deg, #f9f4ec 0%, #f2ece2 100%);
      color: var(--text);
      font-family: "Avenir Next", "Segoe UI", "Noto Sans KR", sans-serif;
      line-height: 1.5;
    }

    .page {
      width: min(1320px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 28px 0 48px;
    }

    .hero,
    .panel {
      background: var(--panel);
      backdrop-filter: blur(16px);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }

    .hero {
      position: relative;
      overflow: hidden;
      padding: 34px;
      margin-bottom: 20px;
    }

    .hero::before,
    .hero::after {
      content: "";
      position: absolute;
      border-radius: 999px;
      filter: blur(10px);
      opacity: 0.48;
    }

    .hero::before {
      width: 220px;
      height: 220px;
      right: -40px;
      top: -50px;
      background: radial-gradient(circle, rgba(217, 108, 61, 0.42), transparent 68%);
    }

    .hero::after {
      width: 240px;
      height: 240px;
      left: -70px;
      bottom: -90px;
      background: radial-gradient(circle, rgba(23, 126, 137, 0.34), transparent 70%);
    }

    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 8px 14px;
      border-radius: 999px;
      background: rgba(23, 126, 137, 0.1);
      color: var(--accent);
      font-size: 0.86rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }

    h1, h2, h3 {
      font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
      letter-spacing: -0.02em;
      margin: 0;
    }

    h1 {
      font-size: clamp(2.2rem, 4.4vw, 4.5rem);
      line-height: 0.98;
      margin-top: 18px;
      max-width: 11ch;
    }

    .hero p {
      margin: 18px 0 0;
      max-width: 76ch;
      color: var(--muted);
      font-size: 1.02rem;
    }

    .stats {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-top: 26px;
    }

    .stat {
      padding: 16px 18px;
      border-radius: 20px;
      background: rgba(255, 255, 255, 0.65);
      border: 1px solid rgba(23, 54, 64, 0.08);
      animation: rise 0.8s ease both;
    }

    .stat:nth-child(2) { animation-delay: 0.08s; }
    .stat:nth-child(3) { animation-delay: 0.16s; }
    .stat:nth-child(4) { animation-delay: 0.24s; }

    .stat .value {
      font-size: clamp(1.7rem, 3vw, 2.7rem);
      font-weight: 800;
      line-height: 1;
      margin-bottom: 8px;
    }

    .stat .label {
      color: var(--muted);
      font-size: 0.95rem;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(12, minmax(0, 1fr));
      gap: 18px;
    }

    .panel {
      padding: 22px;
      position: relative;
      overflow: hidden;
    }

    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 16px;
      margin-bottom: 18px;
    }

    .panel-header p,
    .section-note,
    .legend-note {
      margin: 8px 0 0;
      color: var(--muted);
      font-size: 0.94rem;
    }

    .span-5 { grid-column: span 5; }
    .span-7 { grid-column: span 7; }
    .span-12 { grid-column: 1 / -1; }

    .cloud-wrap {
      position: relative;
      min-height: 480px;
      border-radius: 24px;
      background:
        radial-gradient(circle at 15% 20%, rgba(23, 126, 137, 0.08), transparent 28%),
        radial-gradient(circle at 78% 24%, rgba(217, 108, 61, 0.09), transparent 22%),
        rgba(255, 255, 255, 0.58);
      overflow: hidden;
      border: 1px solid rgba(23, 54, 64, 0.07);
    }

    .cloud-token {
      position: absolute;
      white-space: nowrap;
      font-weight: 750;
      padding: 2px 6px;
      border-radius: 999px;
      opacity: 0;
      transform-origin: center center;
      transition: transform 0.28s ease, opacity 0.5s ease;
      cursor: default;
      mix-blend-mode: multiply;
    }

    .cloud-token:hover {
      transform: scale(1.08) rotate(0deg) !important;
      z-index: 4;
    }

    .bars {
      display: grid;
      gap: 9px;
    }

    .bar-row {
      display: grid;
      grid-template-columns: minmax(110px, 170px) minmax(0, 1fr) 48px;
      gap: 12px;
      align-items: center;
    }

    .bar-label {
      font-size: 0.95rem;
      font-weight: 700;
    }

    .bar-track {
      height: 16px;
      background: rgba(23, 54, 64, 0.08);
      border-radius: 999px;
      overflow: hidden;
      position: relative;
    }

    .bar-fill {
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(90deg, var(--accent), var(--accent-2));
      transform-origin: left center;
      animation: grow 1.2s ease both;
    }

    .bar-count {
      text-align: right;
      font-variant-numeric: tabular-nums;
      font-weight: 700;
      color: var(--muted);
    }

    .heatmap-shell {
      overflow: auto;
      border-radius: 22px;
      border: 1px solid rgba(23, 54, 64, 0.07);
      background: rgba(255, 255, 255, 0.6);
    }

    table {
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      min-width: 980px;
    }

    th, td {
      padding: 10px 12px;
      text-align: center;
      border-bottom: 1px solid rgba(23, 54, 64, 0.06);
      border-right: 1px solid rgba(23, 54, 64, 0.06);
      font-size: 0.93rem;
    }

    thead th {
      position: sticky;
      top: 0;
      background: rgba(250, 248, 243, 0.96);
      z-index: 2;
      font-weight: 800;
    }

    tbody th {
      position: sticky;
      left: 0;
      background: rgba(250, 248, 243, 0.96);
      z-index: 1;
      text-align: left;
      font-weight: 700;
    }

    .heat-cell {
      font-variant-numeric: tabular-nums;
      font-weight: 700;
      color: #12313c;
    }

    .heat-legend {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-top: 14px;
      color: var(--muted);
      font-size: 0.9rem;
    }

    .legend-gradient {
      width: 180px;
      height: 12px;
      border-radius: 999px;
      background: linear-gradient(90deg, rgba(23, 126, 137, 0.05), rgba(23, 126, 137, 0.2), rgba(23, 126, 137, 0.9));
    }

    .network-shell {
      position: relative;
      min-height: 760px;
      border-radius: 24px;
      background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.72), rgba(255, 255, 255, 0.56)),
        radial-gradient(circle at center, rgba(23, 126, 137, 0.08), transparent 42%);
      border: 1px solid rgba(23, 54, 64, 0.07);
      overflow: hidden;
    }

    .network-shell svg {
      width: 100%;
      height: 100%;
      display: block;
    }

    .network-caption {
      display: flex;
      gap: 18px;
      flex-wrap: wrap;
      margin-top: 12px;
      color: var(--muted);
      font-size: 0.9rem;
    }

    .network-caption span {
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }

    .swatch {
      width: 12px;
      height: 12px;
      border-radius: 999px;
      display: inline-block;
    }

    .tabs {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-bottom: 16px;
    }

    .tab {
      border: 1px solid rgba(23, 54, 64, 0.1);
      background: rgba(255, 255, 255, 0.7);
      color: var(--text);
      padding: 10px 14px;
      border-radius: 999px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .tab.active {
      background: linear-gradient(135deg, rgba(23, 126, 137, 0.16), rgba(217, 108, 61, 0.12));
      border-color: rgba(23, 126, 137, 0.28);
    }

    .summary-table {
      display: none;
      overflow: auto;
      border-radius: 22px;
      border: 1px solid rgba(23, 54, 64, 0.07);
      background: rgba(255, 255, 255, 0.62);
    }

    .summary-table.active {
      display: block;
      animation: fadeIn 0.35s ease;
    }

    .summary-actions {
      display: flex;
      justify-content: flex-end;
      margin-top: 14px;
    }

    .download {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 12px 16px;
      border-radius: 999px;
      text-decoration: none;
      color: var(--text);
      font-weight: 800;
      background: rgba(255, 255, 255, 0.76);
      border: 1px solid rgba(23, 54, 64, 0.1);
    }

    .tooltip {
      position: fixed;
      pointer-events: none;
      background: rgba(23, 54, 64, 0.94);
      color: #fffaf5;
      padding: 10px 12px;
      border-radius: 12px;
      font-size: 0.84rem;
      line-height: 1.35;
      box-shadow: 0 18px 44px rgba(0, 0, 0, 0.18);
      opacity: 0;
      transform: translateY(8px);
      transition: opacity 0.16s ease, transform 0.16s ease;
      z-index: 20;
      max-width: 260px;
    }

    .tooltip.visible {
      opacity: 1;
      transform: translateY(0);
    }

    .footer-note {
      margin-top: 18px;
      color: var(--muted);
      font-size: 0.88rem;
    }

    @keyframes grow {
      from { transform: scaleX(0); }
      to { transform: scaleX(1); }
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @keyframes rise {
      from { opacity: 0; transform: translateY(12px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @media (max-width: 1100px) {
      .stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .span-5, .span-7 { grid-column: 1 / -1; }
    }

    @media (max-width: 720px) {
      .page { width: min(100vw - 18px, 1320px); padding: 16px 0 34px; }
      .hero, .panel { padding: 18px; border-radius: 20px; }
      .stats { grid-template-columns: 1fr; }
      .cloud-wrap { min-height: 420px; }
      .network-shell { min-height: 620px; }
      .bar-row { grid-template-columns: 100px minmax(0, 1fr) 42px; gap: 8px; }
      th, td { padding: 8px 10px; font-size: 0.88rem; }
    }
  </style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <div class="eyebrow">FOSS4G 2026 Trend Atlas</div>
      <h1>376개 발표에서 읽어낸 공간정보 기술 흐름</h1>
      <p>
        제목과 초록을 정규화한 뒤, 대주제·기술/도구·활용 분야 분류 결과와 키워드 문서 빈도를 함께 묶어 시각화했습니다.
        워드 클라우드와 Top 20는 발표 건수 기준의 정규화 키워드이며, 히트맵과 네트워크는 분류된 카테고리의 공동출현 구조를 보여줍니다.
      </p>
      <div class="stats" id="stats"></div>
    </section>

    <div class="grid">
      <section class="panel span-5">
        <div class="panel-header">
          <div>
            <h2>워드 클라우드</h2>
            <p>정규화 키워드가 몇 개 발표에서 등장했는지 문서 빈도로 계산했습니다.</p>
          </div>
        </div>
        <div class="cloud-wrap" id="word-cloud"></div>
      </section>

      <section class="panel span-7">
        <div class="panel-header">
          <div>
            <h2>트렌드 Top 20</h2>
            <p>중복 언급 수가 아니라, 해당 키워드를 언급한 발표 건수 기준입니다.</p>
          </div>
        </div>
        <div class="bars" id="top-bars"></div>
      </section>

      <section class="panel span-12">
        <div class="panel-header">
          <div>
            <h2>기술 x 활용분야 히트맵</h2>
            <p>분류된 기술/도구와 활용 분야가 같은 발표 안에서 함께 등장한 건수를 보여줍니다.</p>
          </div>
        </div>
        <div class="heatmap-shell" id="heatmap"></div>
        <div class="heat-legend">
          <span>낮음</span>
          <span class="legend-gradient"></span>
          <span>높음</span>
        </div>
      </section>

      <section class="panel span-12">
        <div class="panel-header">
          <div>
            <h2>키워드 공동출현 네트워크</h2>
            <p>좌측은 기술/도구, 중앙은 대주제, 우측은 활용 분야입니다. 실선은 온톨로지형 분류 링크, 점선은 실제 공동출현 링크입니다.</p>
          </div>
        </div>
        <div class="network-shell" id="network"></div>
        <div class="network-caption">
          <span><i class="swatch" style="background: var(--tech)"></i>기술/도구 노드</span>
          <span><i class="swatch" style="background: var(--theme)"></i>대주제 노드</span>
          <span><i class="swatch" style="background: var(--domain)"></i>활용 분야 노드</span>
        </div>
      </section>

      <section class="panel span-12">
        <div class="panel-header">
          <div>
            <h2>발표 건수 기준 차트용 요약 시트</h2>
            <p>바로 차트에 넣을 수 있도록 집계 결과를 표 형태로 정리했습니다. 같은 데이터는 CSV로도 내려받을 수 있습니다.</p>
          </div>
        </div>
        <div class="tabs" id="summary-tabs"></div>
        <div id="summary-panels"></div>
        <div class="summary-actions">
          <a class="download" href="__CSV_FILE__" download>요약 CSV 다운로드</a>
        </div>
        <p class="footer-note">
          생성 시각: <span id="generated-at"></span> · 데이터 소스: <span id="source-name"></span>
        </p>
      </section>
    </div>
  </div>

  <div class="tooltip" id="tooltip"></div>
  <script id="dashboard-data" type="application/json">__DATA__</script>
  <script>
    const dashboard = JSON.parse(document.getElementById('dashboard-data').textContent);
    const tooltip = document.getElementById('tooltip');
    const numberFormat = new Intl.NumberFormat('ko-KR');

    const colorByGroup = {
      theme: 'var(--theme)',
      tech: 'var(--tech)',
      domain: 'var(--domain)'
    };

    function showTooltip(event, html) {
      tooltip.innerHTML = html;
      tooltip.style.left = event.clientX + 16 + 'px';
      tooltip.style.top = event.clientY + 16 + 'px';
      tooltip.classList.add('visible');
    }

    function moveTooltip(event) {
      tooltip.style.left = event.clientX + 16 + 'px';
      tooltip.style.top = event.clientY + 16 + 'px';
    }

    function hideTooltip() {
      tooltip.classList.remove('visible');
    }

    function makeHoverable(node, htmlFactory) {
      node.addEventListener('mouseenter', event => showTooltip(event, htmlFactory()));
      node.addEventListener('mousemove', moveTooltip);
      node.addEventListener('mouseleave', hideTooltip);
    }

    function renderStats() {
      const statsEl = document.getElementById('stats');
      const items = [
        ['총 발표 수', dashboard.meta.submissionCount],
        ['정규화 키워드', dashboard.meta.keywordCount],
        ['기술/도구 라벨', dashboard.meta.techLabelCount],
        ['활용 분야 라벨', dashboard.meta.appLabelCount]
      ];
      statsEl.innerHTML = items.map(([label, value]) => `
        <div class="stat">
          <div class="value">${numberFormat.format(value)}</div>
          <div class="label">${label}</div>
        </div>
      `).join('');
      document.getElementById('generated-at').textContent = dashboard.meta.generatedAt;
      document.getElementById('source-name').textContent = dashboard.meta.sourceWorkbook;
    }

    function renderWordCloud() {
      const host = document.getElementById('word-cloud');
      const words = dashboard.wordCloudTerms;
      if (!words.length) {
        host.textContent = '표시할 키워드가 없습니다.';
        return;
      }

      const placeWords = () => {
        host.innerHTML = '';
        const rect = host.getBoundingClientRect();
        const width = Math.max(rect.width, 320);
        const height = Math.max(rect.height, 360);
        const maxCount = Math.max(...words.map(word => word.count));
        const minCount = Math.min(...words.map(word => word.count));
        const placed = [];

        const measure = document.createElement('span');
        measure.className = 'cloud-token';
        measure.style.visibility = 'hidden';
        host.appendChild(measure);

        words.forEach((word, index) => {
          const scale = maxCount === minCount ? 1 : (word.count - minCount) / (maxCount - minCount);
          const fontSize = 15 + scale * 36;
          const rotation = ((index % 6) - 2) * 5;

          measure.textContent = word.label;
          measure.style.fontSize = fontSize + 'px';
          measure.style.fontWeight = String(620 + Math.round(scale * 180));
          const wordWidth = Math.ceil(measure.offsetWidth + 18);
          const wordHeight = Math.ceil(measure.offsetHeight + 10);

          let placedRect = null;
          for (let step = 0; step < 1200; step += 1) {
            const angle = step * 0.48;
            const radius = 2.8 * Math.sqrt(step) * 4.8;
            const x = width / 2 + Math.cos(angle) * radius - wordWidth / 2;
            const y = height / 2 + Math.sin(angle) * radius - wordHeight / 2;

            if (x < 0 || y < 0 || x + wordWidth > width || y + wordHeight > height) {
              continue;
            }

            const candidate = { x, y, w: wordWidth, h: wordHeight };
            const collision = placed.some(box =>
              !(candidate.x + candidate.w + 4 < box.x ||
                candidate.x - 4 > box.x + box.w ||
                candidate.y + candidate.h + 4 < box.y ||
                candidate.y - 4 > box.y + box.h)
            );

            if (!collision) {
              placedRect = candidate;
              break;
            }
          }

          if (!placedRect) {
            const row = Math.floor(index / 5);
            const col = index % 5;
            placedRect = {
              x: 18 + col * (width - 36) / 5,
              y: 18 + row * 44,
              w: wordWidth,
              h: wordHeight
            };
          }

          placed.push(placedRect);
          const token = document.createElement('span');
          token.className = 'cloud-token';
          token.textContent = word.label;
          token.style.left = placedRect.x + 'px';
          token.style.top = placedRect.y + 'px';
          token.style.fontSize = fontSize + 'px';
          token.style.fontWeight = String(620 + Math.round(scale * 180));
          token.style.color = colorByGroup[word.group];
          token.style.background = word.group === 'theme'
            ? 'rgba(23, 126, 137, 0.08)'
            : word.group === 'tech'
              ? 'rgba(217, 108, 61, 0.08)'
              : 'rgba(122, 143, 60, 0.08)';
          token.style.transform = `rotate(${rotation}deg)`;
          token.style.opacity = '1';
          makeHoverable(token, () => `<strong>${word.label}</strong><br/>발표 ${numberFormat.format(word.count)}건`);
          host.appendChild(token);
        });

        measure.remove();
      };

      placeWords();
      let resizeTimer = null;
      window.addEventListener('resize', () => {
        window.clearTimeout(resizeTimer);
        resizeTimer = window.setTimeout(placeWords, 150);
      });
    }

    function renderTopBars() {
      const host = document.getElementById('top-bars');
      const maxCount = dashboard.topKeywords[0]?.count || 1;
      host.innerHTML = dashboard.topKeywords.map((item, index) => `
        <div class="bar-row">
          <div class="bar-label">${index + 1}. ${item.label}</div>
          <div class="bar-track">
            <div class="bar-fill" style="width: ${(item.count / maxCount) * 100}%; animation-delay: ${index * 0.03}s;"></div>
          </div>
          <div class="bar-count">${numberFormat.format(item.count)}</div>
        </div>
      `).join('');
    }

    function heatColor(value, maxValue) {
      const ratio = maxValue === 0 ? 0 : value / maxValue;
      const alpha = 0.08 + ratio * 0.9;
      return `rgba(23, 126, 137, ${alpha})`;
    }

    function renderHeatmap() {
      const host = document.getElementById('heatmap');
      const heatmap = dashboard.heatmap;
      const header = `
        <thead>
          <tr>
            <th>기술/도구</th>
            ${heatmap.cols.map(label => `<th>${label}</th>`).join('')}
          </tr>
        </thead>
      `;
      const body = `
        <tbody>
          ${heatmap.rows.map((rowLabel, rowIndex) => `
            <tr>
              <th>${rowLabel}</th>
              ${heatmap.values[rowIndex].map((value, colIndex) => `
                <td class="heat-cell" data-row="${rowLabel}" data-col="${heatmap.cols[colIndex]}" data-value="${value}"
                  style="background:${heatColor(value, heatmap.max)}; color:${value > heatmap.max * 0.52 ? '#fffaf5' : '#12313c'};">
                  ${value}
                </td>
              `).join('')}
            </tr>
          `).join('')}
        </tbody>
      `;
      host.innerHTML = `<table>${header}${body}</table>`;

      host.querySelectorAll('.heat-cell').forEach(cell => {
        makeHoverable(cell, () => `
          <strong>${cell.dataset.row}</strong><br/>
          ${cell.dataset.col}<br/>
          공동출현 ${numberFormat.format(Number(cell.dataset.value))}건
        `);
      });
    }

    function positionGroup(nodes, x, yStart, yEnd) {
      if (!nodes.length) return {};
      const spacing = nodes.length === 1 ? 0 : (yEnd - yStart) / (nodes.length - 1);
      const positions = {};
      nodes.forEach((node, index) => {
        positions[node.id] = { x, y: yStart + spacing * index };
      });
      return positions;
    }

    function renderNetwork() {
      const host = document.getElementById('network');
      const width = 1260;
      const height = 760;
      const nodes = dashboard.network.nodes;
      const edges = dashboard.network.edges;
      const techNodes = nodes.filter(node => node.type === 'tech');
      const themeNodes = nodes.filter(node => node.type === 'theme');
      const appNodes = nodes.filter(node => node.type === 'app');

      const positions = {
        ...positionGroup(techNodes, 220, 90, height - 90),
        ...positionGroup(themeNodes, width / 2, 130, height - 130),
        ...positionGroup(appNodes, width - 220, 90, height - 90)
      };

      const maxNode = Math.max(...nodes.map(node => node.count), 1);
      const maxEdge = Math.max(...edges.map(edge => edge.count), 1);
      const nodeRadius = count => 10 + (count / maxNode) * 18;
      const edgeWidth = count => 1.5 + (count / maxEdge) * 4.5;

      const edgeMarkup = edges.map((edge, index) => {
        const source = positions[edge.source];
        const target = positions[edge.target];
        if (!source || !target) return '';
        const midPull = edge.type === 'cooccurrence' ? 0.24 : 0.18;
        const c1x = source.x + (target.x - source.x) * midPull;
        const c2x = target.x - (target.x - source.x) * midPull;
        const offset = edge.type === 'cooccurrence' ? ((index % 5) - 2) * 18 : 0;
        const path = `M ${source.x} ${source.y} C ${c1x} ${source.y + offset}, ${c2x} ${target.y - offset}, ${target.x} ${target.y}`;
        const stroke = edge.type === 'cooccurrence' ? 'rgba(217, 108, 61, 0.32)' : 'rgba(23, 126, 137, 0.32)';
        const dash = edge.type === 'cooccurrence' ? '8 6' : '';
        return `
          <path class="network-edge"
            d="${path}"
            fill="none"
            stroke="${stroke}"
            stroke-width="${edgeWidth(edge.count)}"
            stroke-linecap="round"
            stroke-dasharray="${dash}"
            data-tip="${edge.label}: ${edge.source} / ${edge.target} / ${numberFormat.format(edge.count)}건" />
        `;
      }).join('');

      const nodeMarkup = nodes.map(node => {
        const pos = positions[node.id];
        const radius = nodeRadius(node.count);
        const fill = node.type === 'theme' ? 'var(--theme)' : node.type === 'tech' ? 'var(--tech)' : 'var(--domain)';
        const textAnchor = node.type === 'tech' ? 'end' : node.type === 'app' ? 'start' : 'middle';
        const textX = node.type === 'tech' ? pos.x - radius - 10 : node.type === 'app' ? pos.x + radius + 10 : pos.x;
        const dy = node.type === 'theme' ? -(radius + 12) : 5;
        return `
          <g class="network-node" data-tip="${node.label}: 발표 ${numberFormat.format(node.count)}건">
            <circle cx="${pos.x}" cy="${pos.y}" r="${radius}" fill="${fill}" fill-opacity="0.92"></circle>
            <circle cx="${pos.x}" cy="${pos.y}" r="${radius + 8}" fill="none" stroke="${fill}" stroke-opacity="0.18"></circle>
            <text x="${textX}" y="${pos.y + dy}" text-anchor="${textAnchor}" font-size="14" font-weight="700" fill="#173640">${node.label}</text>
          </g>
        `;
      }).join('');

      host.innerHTML = `
        <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="키워드 공동출현 네트워크">
          <text x="170" y="44" font-size="16" font-weight="800" fill="#173640">기술/도구</text>
          <text x="${width / 2}" y="44" font-size="16" font-weight="800" fill="#173640" text-anchor="middle">대주제</text>
          <text x="${width - 170}" y="44" font-size="16" font-weight="800" fill="#173640" text-anchor="end">활용 분야</text>
          ${edgeMarkup}
          ${nodeMarkup}
        </svg>
      `;

      host.querySelectorAll('[data-tip]').forEach(element => {
        makeHoverable(element, () => element.dataset.tip.replaceAll(' / ', '<br/>'));
      });
    }

    function renderSummaryTables() {
      const tabsHost = document.getElementById('summary-tabs');
      const panelsHost = document.getElementById('summary-panels');
      const sections = [
        ['keywords', '정규화 키워드'],
        ['themes', '대주제'],
        ['techs', '기술/도구'],
        ['applications', '활용 분야'],
        ['pairs', '기술 x 활용분야 조합']
      ];

      tabsHost.innerHTML = sections.map(([key, label], index) => `
        <button class="tab ${index === 0 ? 'active' : ''}" data-target="${key}">${label}</button>
      `).join('');

      panelsHost.innerHTML = sections.map(([key, label], index) => {
        const active = index === 0 ? 'active' : '';
        if (key === 'pairs') {
          const rows = dashboard.summaryTables[key].map((item, rowIndex) => `
            <tr>
              <td>${rowIndex + 1}</td>
              <td>${item.tech}</td>
              <td>${item.app}</td>
              <td>${numberFormat.format(item.count)}</td>
            </tr>
          `).join('');
          return `
            <div class="summary-table ${active}" data-panel="${key}">
              <table>
                <thead><tr><th>순위</th><th>기술/도구</th><th>활용 분야</th><th>발표 건수</th></tr></thead>
                <tbody>${rows}</tbody>
              </table>
            </div>
          `;
        }

        const rows = dashboard.summaryTables[key].map((item, rowIndex) => `
          <tr>
            <td>${rowIndex + 1}</td>
            <td>${item.label}</td>
            <td>${numberFormat.format(item.count)}</td>
          </tr>
        `).join('');
        return `
          <div class="summary-table ${active}" data-panel="${key}">
            <table>
              <thead><tr><th>순위</th><th>${label}</th><th>발표 건수</th></tr></thead>
              <tbody>${rows}</tbody>
            </table>
          </div>
        `;
      }).join('');

      tabsHost.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
          tabsHost.querySelectorAll('.tab').forEach(item => item.classList.remove('active'));
          panelsHost.querySelectorAll('.summary-table').forEach(item => item.classList.remove('active'));
          tab.classList.add('active');
          panelsHost.querySelector(`[data-panel="${tab.dataset.target}"]`).classList.add('active');
        });
      });
    }

    renderStats();
    renderWordCloud();
    renderTopBars();
    renderHeatmap();
    renderNetwork();
    renderSummaryTables();
  </script>
</body>
</html>
"""

    return (
        template.replace("__DATA__", json.dumps(data, ensure_ascii=False))
        .replace("__CSV_FILE__", csv_filename)
    )


def write_html(path: Path, html: str) -> None:
    path.write_text(html, encoding="utf-8")


def build_dashboard_data(rows: list[dict[str, Any]], source_workbook: str) -> tuple[dict[str, Any], list[list[Any]]]:
    theme_counts = count_labels(rows, "themes")
    tech_counts = count_labels(rows, "techs")
    app_counts = count_labels(rows, "apps")

    keyword_counts = build_keyword_counts(rows)

    filtered_theme_counts = Counter({label: count for label, count in theme_counts.items() if label != GENERIC_THEME})
    filtered_tech_counts = Counter({label: count for label, count in tech_counts.items() if label != GENERIC_TECH})
    filtered_app_counts = Counter({label: count for label, count in app_counts.items() if label != GENERIC_APP})

    heatmap = build_heatmap(filtered_tech_counts, filtered_app_counts, rows)
    top_pairs = build_top_pairs(rows)
    network = build_network(rows, filtered_theme_counts, filtered_tech_counts, filtered_app_counts)
    summary_tables = build_summary_tables(keyword_counts, filtered_theme_counts, filtered_tech_counts, filtered_app_counts, top_pairs)

    data = {
        "meta": {
            "submissionCount": len(rows),
            "keywordCount": len(keyword_counts),
            "techLabelCount": len(filtered_tech_counts),
            "appLabelCount": len(filtered_app_counts),
            "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "sourceWorkbook": source_workbook,
        },
        "wordCloudTerms": keyword_counts[:60],
        "topKeywords": keyword_counts[:20],
        "heatmap": heatmap,
        "network": network,
        "summaryTables": summary_tables,
    }

    csv_rows = build_csv_rows(keyword_counts, filtered_theme_counts, filtered_tech_counts, filtered_app_counts, top_pairs)
    return data, csv_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a self-contained FOSS4G trend dashboard HTML page.")
    parser.add_argument(
        "--input",
        default=DEFAULT_INPUT,
        help="Path to the classified CSV.",
    )
    parser.add_argument(
        "--output-dir",
        default="dist",
        help="Directory where the dashboard HTML and CSV will be written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path.cwd()
    input_path = (root / args.input).resolve()
    output_dir = (root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists() and args.input == DEFAULT_INPUT:
        input_path = find_existing_path(CATEGORY_CSV_CANDIDATES, root) or find_existing_path(SOURCE_CSV_CANDIDATES, root)
        if input_path is None:
            raise SystemExit(f"Input CSV not found. Checked: {CATEGORY_CSV_CANDIDATES + SOURCE_CSV_CANDIDATES}")

    if input_path is None or not input_path.exists():
        raise SystemExit(f"Input CSV not found: {args.input}")

    classifier_path = root / "scripts" / "classify_foss4g_submissions.py"
    classifier_module = load_classifier_module(classifier_path)
    rows = read_rows(input_path, classifier_module)

    data, csv_rows = build_dashboard_data(rows, input_path.name)
    csv_path = output_dir / "foss4g_2026_chart_summary.csv"
    html_path = output_dir / "foss4g_2026_trend_dashboard.html"

    write_csv(csv_path, csv_rows)
    write_html(html_path, render_html(data, csv_path.name))

    print(f"Created: {html_path}")
    print(f"Created: {csv_path}")


if __name__ == "__main__":
    main()
