#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from collections import OrderedDict
from pathlib import Path
from typing import Iterable

from foss4g_csv import (
    ABSTRACT_COLUMN,
    APPLICATION_AREA_COLUMN,
    CATEGORY_CSV_CANDIDATES,
    MAIN_THEME_COLUMN,
    SOURCE_CSV_CANDIDATES,
    TECH_TOOLS_COLUMN,
    TITLE_COLUMN,
    build_output_fieldnames,
    read_csv_rows,
    resolve_input_path,
    write_csv_rows,
)


OUTPUT_HEADERS = (
    MAIN_THEME_COLUMN,
    TECH_TOOLS_COLUMN,
    APPLICATION_AREA_COLUMN,
)
DEFAULT_INPUT_CANDIDATES = SOURCE_CSV_CANDIDATES
DEFAULT_OUTPUT = CATEGORY_CSV_CANDIDATES[0]

NORMALIZATION_REPLACEMENTS = [
    (r"open[- ]source", "open source"),
    (r"openstreetmap", "openstreetmap osm"),
    (r"map libre", "maplibre"),
    (r"open layers", "openlayers"),
    (r"geo server", "geoserver"),
    (r"geo node", "geonode"),
    (r"geo network", "geonetwork"),
    (r"post gis", "postgis"),
    (r"geo parquet", "geoparquet"),
    (r"geo arrow", "geoarrow"),
    (r"open drone map", "opendronemap"),
    (r"q field", "qfield"),
    (r"re:earth", "reearth"),
    (r"webgis", "web gis"),
    (r"geoai", "geo ai"),
    (r"geollm", "geo llm"),
    (r"llms", "llm"),
    (r"apis", "api"),
    (r"ai/ml", "ai ml"),
    (r"machine-learning", "machine learning"),
    (r"deep-learning", "deep learning"),
    (r"digital-twin", "digital twin"),
    (r"earth-observation", "earth observation"),
    (r"remote-sensing", "remote sensing"),
    (r"point-cloud", "point cloud"),
    (r"vector-tiles", "vector tiles"),
    (r"3d-tiles", "3d tiles"),
    (r"city gml", "citygml"),
]

MAIN_THEME_RULES = OrderedDict(
    [
        (
            "AI·ML·GeoAI",
            [
                r"\bai\b",
                r"\bllm\b",
                r"\bml\b",
                r"machine learning",
                r"deep learning",
                r"computer vision",
                r"natural language",
                r"graph rag",
                r"graph neural",
                r"geo ai",
                r"geo llm",
                r"opencv",
                r"pytorch",
                r"prompt",
            ],
        ),
        (
            "3D·디지털 트윈·시각화",
            [
                r"\b3d\b",
                r"digital twin",
                r"cesium",
                r"webgl",
                r"citygml",
                r"3d tiles",
                r"point cloud",
                r"immersive",
                r"\bxr\b",
                r"visuali[sz]ation",
                r"hillshading",
                r"rendering",
                r"motion design",
            ],
        ),
        (
            "원격탐사·지구관측",
            [
                r"remote sensing",
                r"earth observation",
                r"\beo\b",
                r"\bsar\b",
                r"satellite",
                r"imagery",
                r"lidar",
                r"hyperspectral",
                r"multispectral",
                r"nisar",
                r"ndvi",
                r"\bcog\b",
            ],
        ),
        (
            "측량·GNSS·포토그래메트리",
            [
                r"\bgnss\b",
                r"\brtk\b",
                r"\bsurvey",
                r"surveying",
                r"photogrammetr",
                r"\buav\b",
                r"\bdrone\b",
                r"\bdem\b",
                r"orthophoto",
                r"geodes",
                r"dji",
                r"earthwork volume",
                r"field data",
            ],
        ),
        (
            "웹 매핑·인터랙티브 지도",
            [
                r"web map",
                r"web mapping",
                r"web gis",
                r"maplibre",
                r"leaflet",
                r"openlayers",
                r"vector tiles?",
                r"\bmvt\b",
                r"pmtiles",
                r"terriajs",
                r"mapstore",
                r"titiler",
                r"maplat",
                r"raster tiles",
                r"map engine",
            ],
        ),
        (
            "공간데이터 인프라·표준",
            [
                r"\bogc\b",
                r"\bstac\b",
                r"geoparquet",
                r"flatgeobuf",
                r"geoarrow",
                r"\bsdi\b",
                r"metadata",
                r"catalog",
                r"interoperab",
                r"standard",
                r"schema",
                r"\bapi\b",
                r"\bjson\b",
                r"\bxml\b",
                r"\brdf\b",
                r"\bcrs\b",
                r"pygeoapi",
                r"pycsw",
                r"dggs",
                r"discrete global grid",
                r"format",
                r"data tooling",
            ],
        ),
        (
            "클라우드·데이터 엔지니어링",
            [
                r"\bcloud\b",
                r"\baws\b",
                r"\bazure\b",
                r"\bgcp\b",
                r"kubernetes",
                r"docker",
                r"pipeline",
                r"\betl\b",
                r"lakehouse",
                r"duckdb",
                r"streaming",
                r"scalab",
                r"postgresql",
                r"postgres ",
                r"\bpostgre\b",
                r"database",
                r"\bsql\b",
                r"data gateway",
            ],
        ),
        (
            "오픈소스 GIS·플랫폼",
            [
                r"open source",
                r"\bfoss4g\b",
                r"\bosgeo\b",
                r"\bqgis\b",
                r"geoserver",
                r"postgis",
                r"geonode",
                r"geonetwork",
                r"\bgdal\b",
                r"\bproj\b",
                r"\bgrass\b",
                r"\bqfield\b",
                r"reearth",
                r"opendronemap",
                r"geoplegma",
                r"ouranos gex",
                r"opensource gis",
                r"openstreetmap",
                r"\bosm\b",
            ],
        ),
        (
            "공간분석·모델링",
            [
                r"spatial analysis",
                r"geospatial analysis",
                r"network analysis",
                r"spatial statist",
                r"interpolation",
                r"simulation",
                r"optimization",
                r"routing",
                r"heatmap",
                r"indexing method",
                r"zone delineation",
                r"model",
                r"decision analysis",
                r"multi criteria",
                r"census",
                r"eurostat",
            ],
        ),
        (
            "카토그래피·UX·스토리텔링",
            [
                r"cartograph",
                r"spatial narrative",
                r"mental maps",
                r"font rendering",
                r"hillshading",
                r"colorblind",
                r"inclusive experiences",
                r"map perception",
                r"rendering effect",
                r"making maps readable",
                r"projection",
                r"you are here",
                r"guitar map",
            ],
        ),
        (
            "앱 개발·클라이언트",
            [
                r"\bapp\b",
                r"web application",
                r"dashboard",
                r"web client",
                r"desktop gui",
                r"\bgui\b",
                r"devtools",
                r"frontend",
                r"front end",
                r"client",
                r"platform",
            ],
        ),
        (
            "성능·품질·운영",
            [
                r"performance",
                r"testing",
                r"\bci\b",
                r"tuning",
                r"autovacuum",
                r"quality",
                r"valid\b",
                r"optimization",
                r"speeding up",
                r"project status",
                r"state of",
                r"current status",
                r"lessons",
                r"latest features",
                r"maintaining",
            ],
        ),
        (
            "오픈데이터·커뮤니티·교육",
            [
                r"open data",
                r"community",
                r"education",
                r"teaching",
                r"training",
                r"workshop",
                r"youthmappers",
                r"participatory",
                r"citizen",
                r"volunteer",
                r"archive",
                r"open schools",
                r"social impact",
                r"localization",
                r"sustaining open source",
                r"\bhot\b",
                r"\bclubs\b",
            ],
        ),
    ]
)

TECH_RULES = OrderedDict(
    [
        ("QGIS", [r"\bqgis\b"]),
        ("QField", [r"\bqfield\b"]),
        ("GRASS GIS", [r"\bgrass\b"]),
        ("GeoServer", [r"geoserver"]),
        ("GeoNode", [r"geonode"]),
        ("GeoNetwork", [r"geonetwork"]),
        ("MapLibre", [r"maplibre"]),
        ("Leaflet", [r"leaflet"]),
        ("OpenLayers", [r"openlayers"]),
        ("MapStore", [r"mapstore"]),
        ("TerriaJS", [r"terriajs"]),
        ("Maplat", [r"maplat"]),
        ("Re:Earth", [r"reearth"]),
        ("OpenStreetMap", [r"openstreetmap", r"\bosm\b"]),
        ("PostGIS", [r"postgis"]),
        ("PostgreSQL", [r"postgresql", r"postgres 18", r"\bpostgre\b"]),
        ("GDAL/OGR", [r"\bgdal\b", r"\bogr\b"]),
        ("PROJ", [r"\bproj\b"]),
        ("DGGS", [r"dggs", r"discrete global grid"]),
        ("STAC", [r"\bstac\b"]),
        ("OGC API", [r"ogc api", r"\bogc\b"]),
        ("pygeoapi", [r"pygeoapi"]),
        ("pycsw", [r"pycsw"]),
        ("GeoParquet", [r"geoparquet"]),
        ("FlatGeobuf", [r"flatgeobuf"]),
        ("GeoArrow", [r"geoarrow"]),
        ("PMTiles", [r"pmtiles"]),
        ("Raster Tiles", [r"raster tiles"]),
        ("Vector Tiles", [r"vector tiles?", r"\bmvt\b"]),
        ("CesiumJS", [r"cesiumjs", r"\bcesium\b"]),
        ("WebGL", [r"webgl"]),
        ("Point Cloud", [r"point cloud"]),
        ("LiDAR", [r"lidar"]),
        ("UAV/Drone", [r"\buav\b", r"\bdrone\b"]),
        ("GNSS/RTK", [r"\bgnss\b", r"\brtk\b"]),
        ("Photogrammetry", [r"photogrammetr"]),
        ("DEM", [r"\bdem\b"]),
        ("Satellite Imagery", [r"satellite imagery", r"\bsatellite\b"]),
        ("SAR", [r"\bsar\b", r"nisar"]),
        ("COG", [r"\bcog\b"]),
        ("Remote Sensing", [r"remote sensing"]),
        ("Earth Observation", [r"earth observation"]),
        ("Digital Twin", [r"digital twin"]),
        ("BIM/CityGML", [r"\bbim\b", r"citygml"]),
        ("AI", [r"\bai\b", r"geo ai"]),
        ("LLM", [r"\bllm\b", r"geo llm"]),
        ("Machine Learning", [r"\bml\b", r"machine learning", r"deep learning"]),
        ("Graph Neural Networks", [r"graph neural"]),
        ("Computer Vision", [r"computer vision", r"opencv"]),
        ("Natural Language Interface", [r"natural language"]),
        ("Python", [r"\bpython\b"]),
        ("R", [r"\br package\b", r"\br\b"]),
        ("Julia", [r"\bjulia\b"]),
        ("Java", [r"\bjava\b"]),
        ("JavaScript/TypeScript", [r"javascript", r"typescript", r"\bjs\b"]),
        ("Rust/WASM", [r"\brust\b", r"\bwasm\b"]),
        ("DuckDB", [r"duckdb"]),
        ("SQL/Database", [r"\bsql\b", r"database"]),
        ("API/Web Services", [r"\bapi\b", r"web service", r"web services"]),
        ("Cloud", [r"\bcloud\b", r"\baws\b", r"\bazure\b", r"\bgcp\b"]),
        ("Docker/Kubernetes", [r"docker", r"kubernetes"]),
        ("Dashboard/Web App", [r"web application", r"dashboard", r"\bapp\b"]),
        ("GUI/Client", [r"web client", r"desktop gui", r"\bgui\b", r"client"]),
        ("Plugin Development", [r"plugin", r"devtools"]),
        ("CI/Testing", [r"testing", r"\bci\b"]),
        ("Performance Tuning", [r"performance", r"tuning", r"autovacuum", r"speeding up"]),
        ("Cartography/Rendering", [r"cartograph", r"font rendering", r"hillshading", r"rendering", r"mental maps", r"projection"]),
        ("Spatial Analysis", [r"spatial analysis", r"network analysis", r"routing", r"geospatial analysis", r"heatmap", r"decision analysis"]),
        ("Open Data", [r"open data"]),
        ("Spectral Indices", [r"spectral indices", r"\bndvi\b"]),
        ("Git/Version Control", [r"\bgit\b"]),
    ]
)

APPLICATION_RULES = OrderedDict(
    [
        ("도시·스마트시티", [r"\burban\b", r"\bcity\b", r"cities", r"smart city", r"urban planning", r"built environment", r"neighborhood"]),
        ("모빌리티·교통·내비게이션", [r"\bmobility\b", r"transport", r"traffic", r"transit", r"route", r"routing", r"navigation", r"commuting", r"railway", r"road"]),
        ("기후·기상", [r"\bclimate\b", r"\bweather\b", r"meteorolog", r"atmospher"]),
        ("재난·위험관리", [r"disaster", r"hazard", r"\brisk\b", r"flood", r"wildfire", r"earthquake", r"emergency", r"resilience", r"evacuat"]),
        ("농업·토양", [r"agri", r"crop", r"farm", r"farmland", r"soil", r"irrigation", r"coffee farmers"]),
        ("산림·생태·생물다양성", [r"forest", r"forestry", r"\btree\b", r"canopy", r"ecolog", r"biodiversity", r"habitat", r"species", r"wildlife", r"conservation", r"bear interactions", r"freshwater biodiversity"]),
        ("수자원·해양·연안", [r"\bwater\b", r"hydrolog", r"\briver\b", r"\bbasin\b", r"watershed", r"ocean", r"marine", r"coastal", r"\bsea\b", r"tides"]),
        ("에너지·유틸리티", [r"\benergy\b", r"electric", r"\bpower\b", r"\bgrid\b", r"utility", r"\bsolar\b", r"\bwind\b", r"renewable"]),
        ("문화유산·역사·교육", [r"heritage", r"archive", r"history", r"historical", r"museum", r"cultural", r"education", r"teaching", r"classroom", r"students", r"peace", r"open schools"]),
        ("공공행정·정책", [r"government", r"public sector", r"policy", r"administration", r"municipal", r"municipality", r"governance", r"national spatial data", r"national mapping"]),
        ("토지행정·지적", [r"cadastre", r"cadastral", r"land administration", r"parcel", r"property", r"land tenure", r"polygon actually valid"]),
        ("보건·인도주의", [r"health", r"disease", r"epidemi", r"humanitarian", r"refugee"]),
        ("건설·건축·BIM", [r"\bbim\b", r"building", r"construction", r"\baec\b", r"architecture", r"indoor", r"infrastructure", r"earthwork"]),
        ("국방·안보", [r"defen", r"military", r"\bsecurity\b"]),
        ("저널리즘·미디어", [r"journalism", r"newsroom", r"nikkei", r"media"]),
        ("개발자 도구·운영", [r"plugin", r"devtools", r"testing", r"\bci\b", r"project status", r"state of", r"current status", r"maintaining", r"support", r"localization", r"tuning", r"autovacuum", r"performance"]),
        ("플랫폼·서비스 구축", [r"platform", r"web application", r"dashboard", r"web client", r"gateway", r"data publishing", r"client", r"portal", r"serving", r"access"]),
        ("커뮤니티·사회적 영향", [r"community", r"volunteer", r"social impact", r"open source", r"\bhot\b", r"youthmappers", r"\bclubs\b"]),
        ("지도 디자인·스토리텔링", [r"cartograph", r"spatial narrative", r"mental maps", r"font rendering", r"hillshading", r"colorblind", r"rendering", r"readable", r"projection", r"visualization"]),
        ("현장조사·모니터링", [r"field data", r"field collection", r"\bsurvey", r"accuracy assessment", r"monitoring", r"sensors"]),
        ("환경·오염 모니터링", [r"pollution", r"emission", r"environmental monitoring", r"air quality", r"contamin"]),
    ]
)

TECH_FALLBACK_BY_THEME = {
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

APPLICATION_FALLBACK_BY_THEME = {
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

def normalize_text(text: str) -> str:
    normalized = text.lower()
    for pattern, replacement in NORMALIZATION_REPLACEMENTS:
        normalized = re.sub(pattern, replacement, normalized)
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return f" {normalized} "


def dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value and value not in seen:
            ordered.append(value)
            seen.add(value)
    return ordered


def match_labels(normalized_text: str, rules: OrderedDict[str, list[str]]) -> list[str]:
    labels: list[str] = []
    for label, patterns in rules.items():
        if any(re.search(pattern, normalized_text) for pattern in patterns):
            labels.append(label)
    return labels


def classify_submission(title: str, abstract: str) -> tuple[list[str], list[str], list[str]]:
    normalized_text = normalize_text(f"{title} {abstract}")

    main_themes = match_labels(normalized_text, MAIN_THEME_RULES)
    if not main_themes:
        main_themes = ["일반 GIS·공간정보"]

    tech_tools = match_labels(normalized_text, TECH_RULES)
    if not tech_tools:
        tech_tools = dedupe_preserve_order(
            TECH_FALLBACK_BY_THEME[theme]
            for theme in main_themes
            if theme in TECH_FALLBACK_BY_THEME
        )
    if not tech_tools:
        tech_tools = ["일반 GIS 워크플로우"]

    application_areas = match_labels(normalized_text, APPLICATION_RULES)
    if not application_areas:
        application_areas = dedupe_preserve_order(
            APPLICATION_FALLBACK_BY_THEME[theme]
            for theme in main_themes
            if theme in APPLICATION_FALLBACK_BY_THEME
        )
    if not application_areas:
        application_areas = ["범용·크로스도메인"]

    return main_themes, tech_tools, application_areas

def create_output_csv(input_path: Path, output_path: Path) -> None:
    rows, fieldnames = read_csv_rows(input_path)
    output_rows: list[dict[str, str]] = []

    for row in rows:
        title = row.get(TITLE_COLUMN, "")
        abstract = row.get(ABSTRACT_COLUMN, "")
        main_themes, tech_tools, application_areas = classify_submission(title, abstract)

        updated_row = dict(row)
        updated_row[MAIN_THEME_COLUMN] = ", ".join(main_themes)
        updated_row[TECH_TOOLS_COLUMN] = ", ".join(tech_tools)
        updated_row[APPLICATION_AREA_COLUMN] = ", ".join(application_areas)
        output_rows.append(updated_row)

    output_fieldnames = build_output_fieldnames(fieldnames, OUTPUT_HEADERS)
    write_csv_rows(output_path, output_fieldnames, output_rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add categorized columns to the FOSS4G 2026 submissions CSV.")
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
