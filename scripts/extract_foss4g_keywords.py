#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

from foss4g_csv import (
    ABSTRACT_COLUMN,
    KEYWORDS_COLUMN,
    SOURCE_CSV_CANDIDATES,
    TITLE_COLUMN,
    build_output_fieldnames,
    read_csv_rows,
    resolve_input_path,
    write_csv_rows,
)


DEFAULT_INPUT_CANDIDATES = SOURCE_CSV_CANDIDATES
DEFAULT_OUTPUT = "docs/foss4g_2026_talks_with_keywords.csv"


TERM_RULES: list[tuple[str, list[str]]] = [
    ("Copernicus Urban Atlas", [r"copernicus urban atlas"]),
    ("Open Mobility Data", [r"open mobility data"]),
    ("Open Geospatial Data", [r"open geospatial data"]),
    ("OpenStreetMap", [r"openstreetmap", r"\bosm\b"]),
    ("Open Mapping", [r"open mapping"]),
    ("Open Source", [r"open source", r"opensource"]),
    ("Open Data", [r"open data"]),
    ("Open-access Platform", [r"open-access platform"]),
    ("FOSS4G", [r"\bfoss4g\b"]),
    ("OSGeo", [r"\bosgeo\b"]),
    ("FOSS Stack", [r"foss stack"]),
    ("FOSS Workflows", [r"foss workflows"]),
    ("Localization", [r"localization"]),
    ("Digital Elevation Model", [r"digital elevation model", r"\bdem\b"]),
    ("Digital Terrain Model", [r"digital terrain model", r"\bdtm\b"]),
    ("Differential GNSS", [r"differential gnss"]),
    ("GNSS", [r"\bgnss\b", r"\brtk\b"]),
    ("Photogrammetry", [r"photogrammetr"]),
    ("UAV", [r"\buav\b"]),
    ("Drone", [r"\bdrone\b"]),
    ("Numerical Weather Prediction", [r"numerical weather prediction"]),
    ("3D Visualization", [r"3d visuali[sz]ation", r"3d visuali[sz]ations"]),
    ("3D", [r"\b3d\b"]),
    ("Digital Twin", [r"digital twin"]),
    ("3D Tiles", [r"3d tiles"]),
    ("CityGML", [r"citygml", r"city gml"]),
    ("BIM", [r"\bbim\b"]),
    ("Point Cloud", [r"point cloud"]),
    ("LiDAR", [r"lidar"]),
    ("Remote Sensing", [r"remote sensing"]),
    ("Earth Observation", [r"earth observation"]),
    ("Satellite Imagery", [r"satellite imagery", r"\bsatellite\b imagery"]),
    ("SAR", [r"synthetic aperture radar", r"\bsar\b"]),
    ("NISAR", [r"\bnisar\b"]),
    ("NDVI", [r"\bndvi\b"]),
    ("Spectral Indices", [r"spectral indices"]),
    ("Geospatial Data", [r"geospatial data"]),
    ("Spatial Data", [r"spatial data"]),
    ("Spatial Information", [r"spatial information"]),
    ("Geospatial Platform", [r"geospatial platform"]),
    ("Geospatial Tools", [r"geospatial tools"]),
    ("Spatial Analysis", [r"spatial analysis"]),
    ("Geospatial Analysis", [r"geospatial analysis"]),
    ("Network Analysis", [r"network analysis"]),
    ("Network Modelling", [r"network modelling", r"network modeling"]),
    ("Simulation", [r"simulations?", r"simulation"]),
    ("Geospatial Indexing", [r"geospatial indexing"]),
    ("Spatial Indicators", [r"spatial indicators"]),
    ("Exposure Model", [r"exposure model"]),
    ("Geographic Boundary Features", [r"geographic boundary features"]),
    ("Zone Delineation", [r"zone delineation"]),
    ("Administrative Districts", [r"administrative districts"]),
    ("Digital Archive", [r"digital archive"]),
    ("Interactive Map", [r"interactive map", r"interactive, map-based", r"map-based"]),
    ("Interactive Web Mapping", [r"interactive web mapping"]),
    ("Web Mapping", [r"web mapping", r"web map"]),
    ("WebGIS", [r"webgis", r"web gis"]),
    ("GIS", [r"\bgis\b", r"gis-based"]),
    ("QGIS", [r"\bqgis\b"]),
    ("QField", [r"\bqfield\b", r"q field"]),
    ("GRASS GIS", [r"\bgrass\b"]),
    ("GeoServer", [r"geoserver"]),
    ("GeoNode", [r"geonode"]),
    ("GeoNetwork", [r"geonetwork"]),
    ("PostGIS", [r"postgis"]),
    ("PostgreSQL", [r"postgresql", r"postgres 18", r"\bpostgres\b"]),
    ("MapLibre", [r"maplibre"]),
    ("MapLibre GL JS", [r"maplibre gl js", r"maplibre gl"]),
    ("Leaflet", [r"leaflet"]),
    ("OpenLayers", [r"openlayers", r"open layers"]),
    ("CesiumJS", [r"cesiumjs", r"\bcesium\b"]),
    ("Re:Earth", [r"re:earth", r"\breearth\b"]),
    ("MapStore", [r"mapstore"]),
    ("TerriaJS", [r"terriajs"]),
    ("GeoTools", [r"geotools"]),
    ("GeoPandas", [r"geopandas"]),
    ("GDAL", [r"\bgdal\b"]),
    ("PROJ", [r"\bproj\b"]),
    ("PDAL", [r"\bpdal\b"]),
    ("JTS", [r"\bjts\b"]),
    ("DuckDB", [r"duckdb"]),
    ("SQL", [r"\bsql\b"]),
    ("API", [r"\bapi\b", r"\bapis\b"]),
    ("pgRouting", [r"pgrouting"]),
    ("OGC API EDR", [r"ogc api edr"]),
    ("OGC API", [r"ogc api"]),
    ("OGC", [r"\bogc\b"]),
    ("STAC", [r"\bstac\b"]),
    ("COG", [r"\bcog\b"]),
    ("GeoParquet", [r"geoparquet"]),
    ("GeoArrow", [r"geoarrow"]),
    ("FlatGeobuf", [r"flatgeobuf"]),
    ("GeoJSON", [r"geojson"]),
    ("JSON", [r"\bjson\b"]),
    ("XML", [r"\bxml\b"]),
    ("RDF", [r"\brdf\b"]),
    ("Linked Data", [r"linked data"]),
    ("SensorThings API", [r"sensorthings api"]),
    ("SensorThings", [r"sensorthings"]),
    ("Spatial Data Infrastructure", [r"spatial data infrastructure", r"\bsdi\b"]),
    ("CRS", [r"\bcrs\b"]),
    ("GeoParquet", [r"geo parquet"]),
    ("Vector Tiles", [r"vector tiles?", r"\bmvt\b"]),
    ("Raster Tiles", [r"raster tiles"]),
    ("PMTiles", [r"pmtiles"]),
    ("GeoArrow", [r"geo arrow"]),
    ("DGGS", [r"\bdggs\b", r"discrete global grid"]),
    ("DGGAL", [r"\bdggal\b"]),
    ("GeoAI", [r"geoai", r"geo ai"]),
    ("AI", [r"\bai\b"]),
    ("LLM", [r"\bllm\b", r"\bllms\b", r"large language model"]),
    ("GeoLLM", [r"geollm", r"geo llm"]),
    ("Machine Learning", [r"machine learning", r"\bml\b"]),
    ("Deep Learning", [r"deep learning"]),
    ("Natural Language", [r"natural language"]),
    ("Graph Neural Networks", [r"graph neural network", r"graph neural networks"]),
    ("GraphRAG", [r"graphrag", r"graph rag"]),
    ("Computer Vision", [r"computer vision"]),
    ("OpenCV", [r"opencv"]),
    ("PyTorch", [r"pytorch"]),
    ("Cloud", [r"\bcloud\b"]),
    ("AWS", [r"\baws\b"]),
    ("GPU", [r"\bgpu\b"]),
    ("WebAssembly", [r"webassembly", r"\bwasm\b"]),
    ("MCP", [r"\bmcp\b"]),
    ("ETL", [r"\betl\b"]),
    ("Codecs", [r"\bcodecs?\b"]),
    ("Format Drivers", [r"format drivers?"]),
    ("Storage Drivers", [r"storage drivers?"]),
    ("CI", [r"\bci\b"]),
    ("DevTools", [r"devtools"]),
    ("Database Recovery", [r"database recovery"]),
    ("Disaster Recovery", [r"disaster recovery", r"\bdr\b culture"]),
    ("Dashboard", [r"dashboard"]),
    ("Web App", [r"webapp", r"web app", r"\bwebsite\b"]),
    ("Web Client", [r"web client"]),
    ("Plugin", [r"plugin"]),
    ("GUI", [r"\bgui\b", r"desktop gui"]),
    ("CLI", [r"\bcli\b"]),
    ("SDK", [r"\bsdks?\b"]),
    ("Python", [r"\bpython\b"]),
    ("Java", [r"\bjava\b"]),
    ("JavaScript", [r"\bjavascript\b"]),
    ("TypeScript", [r"typescript"]),
    ("Julia", [r"\bjulia\b"]),
    ("R", [r"\br package\b", r"\br\b"]),
    ("Rust", [r"\brust\b"]),
    ("OpenDroneMap", [r"opendronemap", r"open drone map"]),
    ("TiTiler", [r"titiler"]),
    ("pygeoapi", [r"pygeoapi"]),
    ("pycsw", [r"pycsw"]),
    ("ZOO-Project", [r"zoo-project"]),
    ("QWC", [r"\bqwc\b"]),
    ("ImageN", [r"\bimagen\b"]),
    ("DigiAgriApp", [r"digiagriapp"]),
    ("GeoAgent", [r"geoagent"]),
    ("GeoPlegma", [r"geoplegma"]),
    ("GeoReports", [r"georeports"]),
    ("GeoGirafe", [r"geogirafe"]),
    ("GeoFence", [r"geofence"]),
    ("GeoSampa", [r"geosampa"]),
    ("GeoCat Bridge", [r"geocat bridge"]),
    ("Ouranos GEX", [r"ouranos gex"]),
    ("MapConductor", [r"mapconductor"]),
    ("QMapCompare", [r"qmapcompare"]),
    ("PINOGIO", [r"pinogio"]),
    ("MakeGIS", [r"makegis"]),
    ("ChOWDER", [r"chowder"]),
    ("GIFramework", [r"giframework"]),
    ("TrustChain", [r"trustchain"]),
    ("USE-SVI", [r"use-svi"]),
    ("SLA4GIS", [r"sla4gis"]),
    ("DHIS2", [r"dhis2"]),
    ("SWMM", [r"swmm"]),
    ("ESGF", [r"esgf"]),
    ("YouthMappers", [r"youthmappers"]),
    ("HOT", [r"\bhot\b"]),
    ("PLATEAU", [r"\bplateau\b"]),
    ("NASA-ISRO", [r"nasa-isro"]),
    ("GISTDA", [r"gistda"]),
    ("Overture Maps", [r"overturemaps", r"overture maps"]),
    ("CNES", [r"\bcnes\b"]),
    ("ESA", [r"\besa\b"]),
    ("NASA", [r"\bnasa\b"]),
    ("Eurostat", [r"\beurostat\b"]),
    ("Census", [r"\bcensus\b"]),
    ("Urban Atlas", [r"urban atlas"]),
    ("Cartography", [r"cartograph"]),
    ("Visualization", [r"visuali[sz]ation", r"visuali[sz]ations", r"visuali[sz]ing"]),
    ("Hillshading", [r"hillshading"]),
    ("Projection", [r"\bprojection\b"]),
    ("Font Rendering", [r"font rendering"]),
    ("Map Perception", [r"map perception"]),
    ("Map Design", [r"map designs?"]),
    ("Map Applications", [r"map applications"]),
    ("Map Styles", [r"map styles"]),
    ("Vector Map", [r"vector map"]),
    ("Client Rendering", [r"client rendering"]),
    ("Tile Size", [r"tile size"]),
    ("Infographics", [r"infographics"]),
    ("Spatial Narrative", [r"spatial narrative"]),
    ("Mental Maps", [r"mental maps"]),
    ("Time Series", [r"time series"]),
    ("Metadata", [r"\bmetadata\b"]),
    ("Data Gateway", [r"data gateway"]),
    ("Data Publishing", [r"data publishing"]),
    ("Climate Change", [r"climate change"]),
    ("Industrial Revolution", [r"industrial revolution"]),
    ("Urbanization", [r"urbanization"]),
    ("Renewable Energy", [r"renewable energy"]),
    ("Earthwork Volume", [r"earthwork volume"]),
    ("Rasterization", [r"rasterization"]),
    ("Freshwater Biodiversity Data", [r"freshwater biodiversity data"]),
    ("Policy", [r"\bpolicy\b"]),
    ("Participatory Workflows", [r"participatory .*?workflows", r"community-led workflows"]),
    ("Seagrass Mapping", [r"map seagrass", r"seagrass"]),
    ("Motion UI", [r"motion ui"]),
    ("Smart Agriculture", [r"smart agriculture"]),
    ("Connectivity Indicators", [r"connectivity indicators"]),
    ("Network Measurements", [r"network measurements"]),
    ("Routing Constraints", [r"routing constraints"]),
    ("Polygon Validation", [r"valid polygon", r"valid polygon", r"constitutes a valid polygon", r"polygon actually valid"]),
    ("Geodata", [r"\bgeodata\b"]),
    ("EU Regulation", [r"eu regulation"]),
    ("Pacific Tides App", [r"pacific tides app"]),
]

SUPPRESSION_RULES: dict[str, set[str]] = {
    "Copernicus Urban Atlas": {"Urban Atlas"},
    "3D Visualization": {"Visualization"},
    "Geospatial Analysis": {"Spatial Analysis"},
    "Differential GNSS": {"GNSS"},
    "OGC API EDR": {"OGC API", "OGC"},
    "OGC API": {"OGC", "API"},
    "SensorThings API": {"SensorThings", "API"},
    "MapLibre GL JS": {"MapLibre", "JavaScript"},
    "GeoAI": {"AI"},
    "GeoLLM": {"LLM"},
    "Graph Neural Networks": {"Machine Learning"},
    "Computer Vision": {"AI"},
    "WebAssembly": {"WASM"},
}

def normalize_text(text: str) -> str:
    lowered = text.lower()
    replacements = [
        ("open-source", "open source"),
        ("ai/ml", "ai ml"),
        ("open street map", "openstreetmap"),
        ("re: earth", "re:earth"),
        ("map libre", "maplibre"),
        ("open layers", "openlayers"),
        ("geo server", "geoserver"),
        ("geo node", "geonode"),
        ("geo network", "geonetwork"),
        ("geo parquet", "geoparquet"),
        ("geo arrow", "geoarrow"),
        ("open drone map", "opendronemap"),
        ("q field", "qfield"),
        ("3-d", "3d"),
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


def extract_keywords(title: str, abstract: str) -> list[str]:
    text = f"{title} {abstract}".strip()
    normalized = normalize_text(text)

    matches: list[tuple[int, int, str]] = []
    for index, (label, patterns) in enumerate(TERM_RULES):
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
        updated_row[KEYWORDS_COLUMN] = ", ".join(extract_keywords(title, abstract))
        output_rows.append(updated_row)

    output_fieldnames = build_output_fieldnames(fieldnames, [KEYWORDS_COLUMN])
    write_csv_rows(output_path, output_fieldnames, output_rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract explicit spatial and tech keywords from the FOSS4G submissions CSV.")
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
