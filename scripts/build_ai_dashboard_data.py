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
    AI_CONTEXT_KEYWORDS_COLUMN,
    AI_CSV_CANDIDATES,
    AI_KEYWORDS_COLUMN,
    ID_COLUMN,
    PAGE_COLUMN,
    SOURCE_CSV_CANDIDATES,
    TITLE_COLUMN,
    find_existing_path,
    resolve_existing_path,
    split_csv_list,
)


AI_FILE_CANDIDATES = AI_CSV_CANDIDATES
SOURCE_FILE_CANDIDATES = SOURCE_CSV_CANDIDATES

AI_FAMILY_RULES = [
    {
        "id": "genai-language",
        "label": "Generative & Language AI",
        "color": "#7c5cff",
        "patterns": [
            r"\bllm\b",
            r"\bgpt\b",
            r"geollm",
            r"rag",
            r"graphrag",
            r"prompt engineering",
            r"embeddings",
            r"conversational ai",
            r"natural language processing",
            r"natural language interface",
            r"model context protocol",
        ],
    },
    {
        "id": "ml-prediction",
        "label": "Machine Learning & Prediction",
        "color": "#177e89",
        "patterns": [
            r"machine learning",
            r"deep learning",
            r"prediction",
            r"classification",
            r"decision support",
            r"automation",
        ],
    },
    {
        "id": "vision-detection",
        "label": "Vision & Detection",
        "color": "#d96c3d",
        "patterns": [
            r"computer vision",
            r"open cv",
            r"opencv",
            r"detection",
            r"vision language model",
        ],
    },
    {
        "id": "graph-neural",
        "label": "Graph & Neural Models",
        "color": "#b74f6f",
        "patterns": [
            r"graph neural networks",
            r"neural network",
            r"transformer",
        ],
    },
    {
        "id": "geoai-agents",
        "label": "GeoAI & Agents",
        "color": "#4f9d69",
        "patterns": [
            r"geoai",
            r"\bagent\b",
            r"\bai\b",
            r"inference",
        ],
    },
    {
        "id": "ai-tooling",
        "label": "AI Tooling",
        "color": "#c48a29",
        "patterns": [
            r"pytorch",
            r"open cv",
            r"opencv",
            r"model context protocol",
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


def ai_family_for(keyword: str) -> dict[str, str]:
    lowered = keyword.lower()
    for rule in AI_FAMILY_RULES:
        if any(re.search(pattern, lowered) for pattern in rule["patterns"]):
            return {
                "id": rule["id"],
                "label": rule["label"],
                "color": rule["color"],
            }
    return {
        "id": "ai-signals",
        "label": "General AI Signals",
        "color": "#3f7cac",
    }


def read_rows(root: Path, ai_extractor: Any, general_extractor: Any) -> tuple[list[dict[str, Any]], str]:
    source_path = find_existing_path(AI_FILE_CANDIDATES, root) or resolve_existing_path(SOURCE_FILE_CANDIDATES, root)
    rows_out: list[dict[str, Any]] = []

    with source_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            title = row[TITLE_COLUMN].strip()
            abstract = row[ABSTRACT_COLUMN].strip()
            ai_keywords = split_keywords(row.get(AI_KEYWORDS_COLUMN, ""))
            context_keywords = split_keywords(row.get(AI_CONTEXT_KEYWORDS_COLUMN, ""))
            if not ai_keywords:
                ai_keywords = ai_extractor.extract_ai_keywords(title, abstract)
            if ai_keywords and not context_keywords:
                context_keywords = ai_extractor.extract_context_keywords(title, abstract, general_extractor, ai_keywords)

            rows_out.append(
                {
                    "id": row[ID_COLUMN].strip(),
                    "page": row[PAGE_COLUMN].strip(),
                    "title": title,
                    "abstractSnippet": abstract[:240] + ("..." if len(abstract) > 240 else ""),
                    "aiKeywords": ai_keywords,
                    "contextKeywords": context_keywords,
                }
            )

    return rows_out, source_path.name


def build_dashboard_payload(root: Path) -> dict[str, Any]:
    ai_extractor = load_module(root / "scripts" / "extract_foss4g_ai_keywords.py", "ai_extractor")
    general_extractor = load_module(root / "scripts" / "extract_foss4g_keywords.py", "general_keyword_extractor")
    rows, source_name = read_rows(root, ai_extractor, general_extractor)
    ai_rows = [row for row in rows if row["aiKeywords"]]

    ai_keyword_counts: Counter = Counter()
    context_keyword_counts: Counter = Counter()
    ai_context_pairs: Counter = Counter()
    family_talk_counts: Counter = Counter()
    family_contexts: dict[str, set[str]] = defaultdict(set)
    family_keywords: dict[str, set[str]] = defaultdict(set)
    keyword_samples: dict[str, list[str]] = defaultdict(list)
    keyword_contexts: dict[str, Counter] = defaultdict(Counter)

    for row in ai_rows:
        ai_keywords = list(dict.fromkeys(row["aiKeywords"]))
        context_keywords = list(dict.fromkeys(row["contextKeywords"]))

        ai_keyword_counts.update(ai_keywords)
        context_keyword_counts.update(context_keywords)

        for keyword in ai_keywords:
            if len(keyword_samples[keyword]) < 3:
                keyword_samples[keyword].append(row["title"])
            keyword_contexts[keyword].update(context_keywords)

        families_in_row = set()
        for keyword in ai_keywords:
            family = ai_family_for(keyword)
            families_in_row.add(family["id"])
            family_contexts[family["id"]].update(context_keywords)
            family_keywords[family["id"]].add(keyword)

        for family_id in families_in_row:
            family_talk_counts[family_id] += 1

        for ai_keyword in ai_keywords:
            for context_keyword in context_keywords:
                ai_context_pairs[(ai_keyword, context_keyword)] += 1

    total_ai_talks = len(ai_rows)
    ai_share = round(total_ai_talks / len(rows), 4) if rows else 0

    scorecards = [
        {"label": "AI-related talks", "value": total_ai_talks, "caption": "Talks with at least one AI signal"},
        {"label": "AI talk share", "value": ai_share, "caption": "Share of the full submission set", "format": "percent"},
        {"label": "Unique AI keywords", "value": len(ai_keyword_counts), "caption": "Normalized AI signal terms"},
        {"label": "Unique context keywords", "value": len(context_keyword_counts), "caption": "Context terms inside AI talks"},
    ]

    family_nodes = []
    for rule in AI_FAMILY_RULES + [{"id": "ai-signals", "label": "General AI Signals", "color": "#3f7cac"}]:
        family_id = rule["id"]
        count = family_talk_counts[family_id]
        if count == 0:
            continue
        family_nodes.append(
            {
                "family": rule["label"],
                "familyId": family_id,
                "count": count,
                "color": rule["color"],
                "share": round(count / total_ai_talks, 4) if total_ai_talks else 0,
                "keywordCount": len(family_keywords[family_id]),
            }
        )

    radar = []
    for family in family_nodes:
        family_id = family["familyId"]
        radar.append(
            {
                "family": family["family"],
                "talks": family["count"],
                "contextBreadth": len(family_contexts[family_id]),
                "keywordBreadth": len(family_keywords[family_id]),
            }
        )

    flow_ai_keywords = [keyword for keyword, _ in ai_keyword_counts.most_common(12)]
    flow_context_keywords = [keyword for keyword, _ in context_keyword_counts.most_common(12)]
    flow_nodes = [{"name": keyword} for keyword in flow_ai_keywords + flow_context_keywords]
    flow_links = [
        {"source": ai_keyword, "target": context_keyword, "value": count}
        for (ai_keyword, context_keyword), count in ai_context_pairs.most_common(40)
        if ai_keyword in flow_ai_keywords and context_keyword in flow_context_keywords and count >= 2
    ]

    signal_briefs = []
    for keyword, count in ai_keyword_counts.most_common(8):
        related_contexts = [{"keyword": context, "count": c} for context, c in keyword_contexts[keyword].most_common(5)]
        signal_briefs.append(
            {
                "keyword": keyword,
                "count": count,
                "family": ai_family_for(keyword)["label"],
                "relatedContexts": related_contexts,
                "samples": keyword_samples[keyword],
            }
        )

    explorer_rows = []
    top_ai_keywords = {keyword for keyword, _ in ai_keyword_counts.most_common(16)}
    for row in ai_rows:
        explorer_rows.append(
            {
                "id": row["id"],
                "page": row["page"],
                "title": row["title"],
                "abstractSnippet": row["abstractSnippet"],
                "keywords": row["aiKeywords"] + row["contextKeywords"],
                "highlightedKeywords": [keyword for keyword in row["aiKeywords"] if keyword in top_ai_keywords],
                "aiKeywords": row["aiKeywords"],
                "contextKeywords": row["contextKeywords"],
            }
        )

    ai_treemap = []
    for keyword, count in ai_keyword_counts.most_common(16):
        family = ai_family_for(keyword)
        ai_treemap.append(
            {
                "name": keyword,
                "size": count,
                "category": family["label"],
                "color": family["color"],
            }
        )
    ai_other = sum(ai_keyword_counts.values()) - sum(item["size"] for item in ai_treemap)
    if ai_other > 0:
        ai_treemap.append(
            {
                "name": "Others",
                "size": ai_other,
                "category": "Other AI Signals",
                "color": "#9aa8b3",
            }
        )

    return {
        "meta": {
            "sourceWorkbook": source_name,
            "totalPresentations": len(rows),
            "aiPresentationCount": total_ai_talks,
            "aiPresentationShare": ai_share,
            "uniqueAiKeywords": len(ai_keyword_counts),
            "uniqueContextKeywords": len(context_keyword_counts),
        },
        "overview": {
            "scorecards": scorecards,
            "signalBriefs": signal_briefs,
            "topAiKeywords": [{"keyword": keyword, "count": count} for keyword, count in ai_keyword_counts.most_common(20)],
            "topContextKeywords": [{"keyword": keyword, "count": count} for keyword, count in context_keyword_counts.most_common(20)],
            "treemap": ai_treemap,
        },
        "families": {
            "radial": family_nodes,
            "radar": radar,
        },
        "flows": {
            "nodes": flow_nodes,
            "links": flow_links,
        },
        "explorer": {
            "presentations": explorer_rows,
        },
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    output_path = root / "src" / "data" / "ai-dashboard-data.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = build_dashboard_payload(root)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Created: {output_path}")


if __name__ == "__main__":
    main()
