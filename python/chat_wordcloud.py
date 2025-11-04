#!/usr/bin/env python3
import argparse
import json
import math
import os
import re
import sys
from collections import Counter, deque
from itertools import islice
from typing import Any, Dict, Iterable, List, Set, Tuple

# Try to import matplotlib; required for charts/visuals
import matplotlib.pyplot as plt

# Optional wordcloud dependency
try:
    from wordcloud import WordCloud  # type: ignore
    HAS_WORDCLOUD = True
except Exception:
    HAS_WORDCLOUD = False

# -------------------------------
# Stopwords
# -------------------------------

BASIC_STOPWORDS = {
    # generic English stopwords (trimmed list, can expand as needed)
    "a","an","and","are","as","at","be","but","by","for","if","in","into","is","it","no","not","of",
    "on","or","such","that","the","their","then","there","these","they","this","to","was","will","with",
    "you","your","yours","i","me","my","we","our","ours","he","she","him","her","his","hers","them",
    "their","theirs","what","which","who","whom","been","being","from","were","am","do","does","did",
    "doing","than","too","very","can","just","should","now","so","own","same","s","t","don","ll","re","ve",
    "m","d",
    # common chat-specific filler
    "yeah","yep","ok","okay","right","uh","um","like","got","thanks","thank","hi","hey",
    # Chat roles & meta
    "assistant","user","system","tool","message","content","role",
    # common code/data words to de-bias tech-heavy chats
    "code","function","file","json","http","https","www","com"
}

URL_RE = re.compile(r'https?://\S+|www\.\S+', re.IGNORECASE)
CODEBLOCK_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`]*`")
NON_ALPHA_RE = re.compile(r"[^a-z\s]")  # keep letters & spaces
WHITESPACE_RE = re.compile(r"\s+")

def load_extra_stopwords(path: str) -> Set[str]:
    words: Set[str] = set()
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                w = line.strip().lower()
                if w:
                    words.add(w)
    return words

# -------------------------------
# JSON text extraction
# -------------------------------

LIKELY_TEXT_KEYS = {"content", "text", "body", "value"}

def extract_texts(obj: Any) -> Iterable[str]:
    """
    Recursively traverse an arbitrary JSON structure and yield text fields.
    Heuristics:
      - If we see dicts with keys in LIKELY_TEXT_KEYS, yield their string values
      - If dict has "author" or "role", prefer only "user"/"assistant" (skip "system"/"tool")
    """
    queue = deque([obj])
    while queue:
        current = queue.popleft()
        if isinstance(current, dict):
            # Skip system/tool if role present
            role = str(current.get("role", "")).lower()
            author = str(current.get("author", ""))
            author_name = ""
            if isinstance(author, dict):
                author_name = str(author.get("role", ""))
            elif isinstance(author, str):
                author_name = author.lower()

            if role in {"system", "tool"} or author_name in {"system", "tool"}:
                # still traverse children (content might contain useful info), but de-prioritize
                pass

            # Simple "parts" array common in some exports
            parts = current.get("parts")
            if isinstance(parts, list):
                for p in parts:
                    if isinstance(p, str):
                        yield p
                    elif isinstance(p, dict):
                        # OpenAI export sometimes uses {"content":[{"text": "..."}]}
                        if "text" in p and isinstance(p["text"], str):
                            yield p["text"]
                        else:
                            queue.append(p)

            # Capture likely text keys
            for k, v in current.items():
                if k in LIKELY_TEXT_KEYS and isinstance(v, str):
                    yield v
                elif isinstance(v, (dict, list)):
                    queue.append(v)

        elif isinstance(current, list):
            queue.extend(current)
        elif isinstance(current, str):
            # Some exports can have strings directly in arrays
            yield current

# -------------------------------
# Text cleaning & tokenization
# -------------------------------

def clean_text(s: str) -> str:
    s = CODEBLOCK_RE.sub(" ", s)
    s = INLINE_CODE_RE.sub(" ", s)
    s = URL_RE.sub(" ", s)
    s = s.lower()
    s = NON_ALPHA_RE.sub(" ", s)
    s = WHITESPACE_RE.sub(" ", s).strip()
    return s

def tokenize(s: str) -> List[str]:
    if not s:
        return []
    return s.split()

def generate_bigrams(tokens: List[str]) -> Iterable[Tuple[str, str]]:
    for i in range(len(tokens) - 1):
        yield (tokens[i], tokens[i+1])

# -------------------------------
# Visualization helpers
# -------------------------------

def save_top_words_bar(top_items: List[Tuple[str, int]], outpath: str, title: str = "Top Words"):
    words = [w for w,_ in top_items]
    freqs = [c for _,c in top_items]

    plt.figure(figsize=(10, 6))
    y_pos = range(len(words))
    plt.barh(y_pos, freqs)
    plt.yticks(y_pos, words)
    plt.xlabel("Frequency")
    plt.title(title)
    plt.gca().invert_yaxis()  # largest on top
    plt.tight_layout()
    plt.savefig(outpath, dpi=200)
    plt.close()

def save_fallback_wordcloud(freqs: Dict[str,int], outpath: str, max_words: int = 150):
    # Simple scatter of words sized by frequency; not as pretty as WordCloud
    items = sorted(freqs.items(), key=lambda x: x[1], reverse=True)[:max_words]

    # Arrange in a grid-ish layout
    cols = int(math.sqrt(len(items))) or 1
    rows = math.ceil(len(items)/cols)
    plt.figure(figsize=(14, 8))
    plt.axis('off')

    # Normalize font sizes between 8 and 52
    counts = [c for _, c in items]
    cmin, cmax = min(counts), max(counts)
    def scale(c):
        if cmax == cmin:
            return 20
        return 8 + (c - cmin) * (52 - 8) / (cmax - cmin)

    # Position words roughly in grid
    x_step = 1.0/(cols+1)
    y_step = 1.0/(rows+1)
    x_positions = [x_step*(i+1) for i in range(cols)]
    y_positions = [1 - y_step*(j+1) for j in range(rows)]

    idx = 0
    for j, y in enumerate(y_positions):
        for i, x in enumerate(x_positions):
            if idx >= len(items):
                break
            w, c = items[idx]
            plt.text(x, y, w, fontsize=scale(c), ha='center', va='center')
            idx += 1

    plt.tight_layout()
    plt.savefig(outpath, dpi=200, bbox_inches='tight')
    plt.close()

# -------------------------------
# Main processing
# -------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate word cloud & frequency tables from a ChatGPT JSON export.")
    parser.add_argument("json_path", help="Path to your exported conversations JSON file")
    parser.add_argument("--outdir", default="chat_wordcloud_output", help="Output directory")
    parser.add_argument("--min_len", type=int, default=3, help="Minimum token length to keep (default: 3)")
    parser.add_argument("--top_n", type=int, default=200, help="How many top unigrams to save to CSV (default: 200)")
    parser.add_argument("--top_n_bi", type=int, default=150, help="How many top bigrams to save to CSV (default: 150)")
    parser.add_argument("--min_freq", type=int, default=3, help="Drop tokens that occur fewer than this many times (default: 3)")
    parser.add_argument("--min_freq_bi", type=int, default=3, help="Drop bigrams that occur fewer than this many times (default: 3)")
    parser.add_argument("--stopwords-file", default="", help="Optional path to a newline-delimited extra stopwords file")
    parser.add_argument("--add-stopwords", default="", help="Optional extra stopwords as a comma-separated list")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    # Load JSON (supports large files)
    try:
        with open(args.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to read JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Collect raw texts
    texts = list(extract_texts(data))
    if not texts:
        print("No text found in the JSON. You may need to adjust extract_texts heuristics.", file=sys.stderr)
        sys.exit(2)

    # Build stopwords
    stopwords = set(BASIC_STOPWORDS)
    if args.stopwords_file:
        stopwords |= load_extra_stopwords(args.stopwords_file)
    if args.add_stopwords.strip():
        stopwords |= {w.strip().lower() for w in args.add_stopwords.split(",") if w.strip()}

    # Tokenize & count
    unigram_counter: Counter[str] = Counter()
    bigram_counter: Counter[Tuple[str, str]] = Counter()

    for t in texts:
        cleaned = clean_text(t)
        tokens = [tok for tok in tokenize(cleaned) if len(tok) >= args.min_len and tok not in stopwords]
        unigram_counter.update(tokens)
        bigram_counter.update(generate_bigrams(tokens))

    # Apply frequency thresholds
    unigram_counter = Counter({w:c for w,c in unigram_counter.items() if c >= args.min_freq})
    bigram_counter = Counter({b:c for b,c in bigram_counter.items() if c >= args.min_freq_bi})

    # Save CSVs
    import csv
    top_uni = unigram_counter.most_common(args.top_n)
    with open(os.path.join(args.outdir, "word_frequencies.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["word","count"])
        for w, c in top_uni:
            writer.writerow([w, c])

    top_bi = bigram_counter.most_common(args.top_n_bi)
    with open(os.path.join(args.outdir, "bigram_frequencies.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["bigram","count"])
        for (w1,w2), c in top_bi:
            writer.writerow([f"{w1} {w2}", c])

    # Bar chart of top words
    if top_uni:
        top_for_plot = top_uni[:30]
        save_top_words_bar(top_for_plot, os.path.join(args.outdir, "top_words.png"), title="Top Words")

    # Word cloud
    if top_uni:
        freqs = dict(top_uni)
        if HAS_WORDCLOUD:
            wc = WordCloud(width=1600, height=900, background_color="white")
            wc.generate_from_frequencies(freqs)
            wc.to_file(os.path.join(args.outdir, "wordcloud.png"))
        else:
            save_fallback_wordcloud(freqs, os.path.join(args.outdir, "fallback_wordcloud.png"))

    print(f"Done. Outputs saved to: {args.outdir}")
    if HAS_WORDCLOUD:
        print("Created: wordcloud.png, top_words.png, word_frequencies.csv, bigram_frequencies.csv")
    else:
        print("Created: fallback_wordcloud.png, top_words.png, word_frequencies.csv, bigram_frequencies.csv")
    
if __name__ == "__main__":
    main()
