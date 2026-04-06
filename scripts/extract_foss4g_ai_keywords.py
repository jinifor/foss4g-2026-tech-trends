#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import re
from pathlib import Path
from typing import Any, Iterable

from foss4g_csv import (
    ABSTRACT_COLUMN,
    AI_CONTEXT_KEYWORDS_COLUMN,
    AI_CSV_CANDIDATES,
    AI_KEYWORDS_COLUMN,
    SOURCE_CSV_CANDIDATES,
    TITLE_COLUMN,
    build_output_fieldnames,
    read_csv_rows,
    resolve_input_path,
    write_csv_rows,
)


DEFAULT_INPUT_CANDIDATES = SOURCE_CSV_CANDIDATES
DEFAULT_OUTPUT = AI_CSV_CANDIDATES[0]

AI_RULES: list[tuple[str, list[str]]] = [
    ("AI", [r"\bartificial intelligence\b", r"\bai\b"]),
    ("GeoAI", [r"\bgeoai\b", r"\bgeo ai\b", r"\bgeospatial ai\b"]),
    ("LLM", [r"\bllm\b", r"\bllms\b", r"large language model"]),
    ("GPT", [r"\bgpt\b", r"chatgpt"]),
    ("Machine Learning", [r"machine learning", r"\bml\b"]),
    ("Deep Learning", [r"deep learning"]),
    ("Neural Network", [r"neural network", r"neural networks"]),
    ("Graph Neural Networks", [r"graph neural network", r"graph neural networks"]),
    ("Computer Vision", [r"computer vision"]),
    ("Natural Language Processing", [r"natural language processing", r"\bnlp\b"]),
    ("Natural Language Interface", [r"natural language"]),
    ("Conversational AI", [r"conversational"]),
    ("RAG", [r"\brag\b", r"retrieval augmented generation"]),
    ("GraphRAG", [r"graphrag", r"graph rag"]),
    ("Agent", [r"\bagent\b", r"ai agent"]),
    ("GeoLLM", [r"\bgeollm\b", r"\bgeo llm\b"]),
    ("Transformer", [r"\btransformer\b", r"\btransformers\b"]),
    ("Embeddings", [r"\bembedding\b", r"\bembeddings\b"]),
    ("Prompt Engineering", [r"\bprompt\b", r"prompt engineering"]),
    ("Model Context Protocol", [r"model context protocol", r"\bmcp\b"]),
    ("Inference", [r"\binference\b"]),
    ("Random Forest", [r"random forest"]),
    ("PyTorch", [r"pytorch"]),
    ("OpenCV", [r"opencv"]),
    ("Vision Language Model", [r"vision language model", r"\bvlm\b"]),
]

SUPPRESSION_RULES: dict[str, set[str]] = {
    "GeoAI": {"AI"},
    "GeoLLM": {"LLM", "AI"},
    "GPT": {"LLM"},
    "GraphRAG": {"RAG"},
    "Natural Language Processing": {"Natural Language Interface"},
    "Graph Neural Networks": {"Neural Network", "Machine Learning"},
    "Deep Learning": {"Machine Learning"},
    "Random Forest": {"Machine Learning"},
    "Computer Vision": {"AI"},
    "Vision Language Model": {"Computer Vision", "LLM"},
}

def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize_text(text: str) -> str:
    lowered = text.lower()
    replacements = [
        ("geo llm", "geollm"),
        ("geo ai", "geoai"),
        ("graph rag", "graphrag"),
        ("large language models", "large language model"),
        ("large-language-model", "large language model"),
        ("machine-learning", "machine learning"),
        ("deep-learning", "deep learning"),
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


def extract_ai_keywords(title: str, abstract: str) -> list[str]:
    normalized = normalize_text(f"{title} {abstract}")
    matches: list[tuple[int, int, str]] = []

    for index, (label, patterns) in enumerate(AI_RULES):
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


def extract_context_keywords(
    title: str,
    abstract: str,
    general_extractor: Any,
    ai_keywords: list[str] | None = None,
) -> list[str]:
    ai_keywords = ai_keywords or extract_ai_keywords(title, abstract)
    general_keywords = general_extractor.extract_keywords(title, abstract)
    return [keyword for keyword in general_keywords if keyword not in ai_keywords]


def create_output_csv(input_path: Path, output_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    general_extractor = load_module(root / "scripts" / "extract_foss4g_keywords.py", "general_keyword_extractor")
    rows, fieldnames = read_csv_rows(input_path)
    output_rows: list[dict[str, str]] = []

    for row in rows:
        title = row.get(TITLE_COLUMN, "").strip()
        abstract = row.get(ABSTRACT_COLUMN, "").strip()
        ai_keywords = extract_ai_keywords(title, abstract)
        context_keywords = extract_context_keywords(title, abstract, general_extractor, ai_keywords) if ai_keywords else []

        updated_row = dict(row)
        updated_row[AI_KEYWORDS_COLUMN] = ", ".join(ai_keywords)
        updated_row[AI_CONTEXT_KEYWORDS_COLUMN] = ", ".join(context_keywords)
        output_rows.append(updated_row)

    output_fieldnames = build_output_fieldnames(
        fieldnames,
        [AI_KEYWORDS_COLUMN, AI_CONTEXT_KEYWORDS_COLUMN],
    )
    write_csv_rows(output_path, output_fieldnames, output_rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract AI-related keywords and AI talk context keywords from the FOSS4G submissions CSV.")
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
