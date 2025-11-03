#!/usr/bin/env python3
"""
Extract idioms/sayings from a text file using a large public list.

Default source (downloaded on first run and cached):
- IdiomKB English idioms JSON: en_idiom_meaning.json (AAAI'24 dataset)
  Repo: https://github.com/lishuang-w/IdiomKB
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Iterable, List, Set, Tuple

try:
    import requests
except ImportError:
    print("This script requires the 'requests' package. Install with:\n  pip install requests")
    sys.exit(1)

# ---------- Config ----------
IDIOMKB_RAW_URL = (
    "https://raw.githubusercontent.com/lishuang-w/IdiomKB/main/data/en_idiom_meaning.json"
)
CACHE_DIR = Path.home() / ".idiom_extractor"
CACHE_FILE = CACHE_DIR / "en_idiom_meaning.json"


# ---------- Helpers ----------
def ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def download_idiomkb_json(force: bool = False) -> Path:
    """
    Download (or reuse cached) English idioms JSON from IdiomKB.
    Returns path to the cached JSON file.
    """
    ensure_cache_dir()
    if CACHE_FILE.exists() and not force:
        return CACHE_FILE

    print("Downloading idioms list (IdiomKB)…")
    resp = requests.get(IDIOMKB_RAW_URL, timeout=30)
    resp.raise_for_status()
    # Basic sanity check: must be JSON list with objects containing "idiom"
    data = resp.json()
    if not isinstance(data, list):
        raise RuntimeError("Unexpected IdiomKB format (expected list).")
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    return CACHE_FILE


def load_idioms_from_idiomkb(cache_path: Path) -> List[str]:
    """
    Load idioms (strings) from IdiomKB's en_idiom_meaning.json.
    """
    with open(cache_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    idioms = []
    for row in data:
        idiom = (row.get("idiom") or "").strip()
        if idiom:
            idioms.append(idiom)
    return idioms


def normalize_space(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())


def compile_phrase_regex(idiom: str) -> re.Pattern:
    """
    Build a robust, case-insensitive regex for a multi-word idiom:
    - Ignore extra internal whitespace (\\s+)
    - Match optional commas/quotes/hyphens between words
    - Use word boundaries at ends where sensible
    """
    # Split on whitespace to get tokens, then allow light punctuation between them.
    tokens = re.split(r"\s+", idiom.strip())
    # Escape each token for literal match
    parts = [re.escape(t) for t in tokens if t]
    if not parts:
        # Fallback: match nothing
        return re.compile(r"(?!x)x")

    # Allow common punctuation or whitespace between tokens
    # e.g., "let the cat out of the bag" will match across newlines, commas, quotes
    sep = r"[ \t\r\n\-–—'\"“”‘’,.]*"
    pattern = r"\b" + sep.join(parts) + r"\b"
    return re.compile(pattern, flags=re.IGNORECASE)


def build_matchers(idioms: Iterable[str]) -> List[Tuple[str, re.Pattern]]:
    """
    Precompile regexes. Longer idioms first to avoid shorter ones swallowing matches.
    """
    unique_normed = {normalize_space(i) for i in idioms if i.strip()}
    sorted_idioms = sorted(unique_normed, key=lambda s: (-len(s), s))
    return [(idiom, compile_phrase_regex(idiom)) for idiom in sorted_idioms]


def find_idioms_in_text(text: str, matchers: List[Tuple[str, re.Pattern]]) -> Set[str]:
    found: Set[str] = set()
    for idiom, rx in matchers:
        if rx.search(text):
            found.add(idiom)
    return found


def read_text_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


# ---------- CLI ----------
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Extract idioms/sayings from a .txt file using a large open dataset."
    )
    p.add_argument("file", type=Path, help="Path to the input .txt file")
    p.add_argument(
        "--force-refresh",
        action="store_true",
        help="Re-download the idiom dataset even if cached.",
    )
    p.add_argument(
        "--print-lines",
        action="store_true",
        help="Also print the line(s) where each idiom occurs.",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of a human-readable list.",
    )
    return p.parse_args()


def main():
    args = parse_args()
    if not args.file.exists():
        print(f"Input not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    cache_path = download_idiomkb_json(force=args.force_refresh)
    idioms = load_idioms_from_idiomkb(cache_path)
    if not idioms:
        print("Loaded zero idioms from dataset — aborting.", file=sys.stderr)
        sys.exit(2)

    text = read_text_file(args.file)
    matchers = build_matchers(idioms)
    found = find_idioms_in_text(text, matchers)

    if args.json:
        out = {
            "source": "IdiomKB en_idiom_meaning.json",
            "input_file": str(args.file),
            "count": len(found),
            "idioms": sorted(found),
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        if not found:
            print("No idioms/sayings found.")
            return

        print(f"Found {len(found)} idiom(s):")
        for i, idiom in enumerate(sorted(found), 1):
            print(f"{i}. {idiom}")

        if args.print_lines:
            print("\n— Matches by line —")
            lines = text.splitlines()
            # Build one big combined regex for speed
            # (keep it simple: scan each idiom per line to show where it appears)
            for n, line in enumerate(lines, 1):
                hits = [idiom for idiom, rx in matchers if rx.search(line)]
                if hits:
                    print(f"[Line {n}] {line.strip()}")
                    for h in sorted(set(hits)):
                        print(f"   ↳ {h}")

if __name__ == "__main__":
    main()
