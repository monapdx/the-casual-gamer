import os
import re

# --- Hyphen & dash normalization helpers ---
DASHES_TO_HYPHEN = {
    "\u2010": "-",  # hyphen
    "\u2011": "-",  # non-breaking hyphen
    "\u2012": "-",  # figure dash
    "\u2013": "-",  # en dash
    "\u2014": "-",  # em dash
    "\u2212": "-",  # minus sign
    "\u2043": "-",  # hyphen bullet
}
SOFT_HYPHEN = "\u00AD"  # discretionary hyphen

def normalize_hyphens(text: str) -> str:
    text = text.replace(SOFT_HYPHEN, "")
    for ch, repl in DASHES_TO_HYPHEN.items():
        text = text.replace(ch, repl)
    return text

# --- Readers for different file types ---
def read_text_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(path, "r", encoding="windows-1252", errors="ignore") as f:
            return f.read()

def read_pdf_pypdf(path: str) -> str:
    try:
        from pypdf import PdfReader
    except Exception:
        return ""
    try:
        txt = []
        with open(path, "rb") as f:
            reader = PdfReader(f)
            for page in reader.pages:
                txt.append(page.extract_text() or "")
        return "".join(txt)
    except Exception:
        return ""

def read_pdf_pdfminer(path: str) -> str:
    try:
        from pdfminer.high_level import extract_text
    except Exception:
        return ""
    try:
        return extract_text(path) or ""
    except Exception:
        return ""

def read_pdf_file(path: str) -> str:
    text = read_pdf_pypdf(path)
    if not text.strip():
        text = read_pdf_pdfminer(path)
    return text or ""

def read_html_file(path: str) -> str:
    # Parse HTML, remove script/style, return visible text
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        raise SystemExit("❌ BeautifulSoup not found. Run 'pip install beautifulsoup4 lxml' first.")
    try:
        raw = read_text_file(path)  # handles encodings
        soup = BeautifulSoup(raw, "lxml")  # lxml is fast/robust
        # Remove scripts/styles
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        return text
    except Exception as e:
        raise RuntimeError(f"Failed to read HTML: {e}")

# --- Core extraction ---
def extract_hyphenated_words(input_file: str, output_file: str):
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"❌ File not found: {input_file}")

    ext = os.path.splitext(input_file)[1].lower()
    if ext == ".pdf":
        text = read_pdf_file(input_file)
    elif ext in (".txt",):
        text = read_text_file(input_file)
    elif ext in (".html", ".htm"):
        text = read_html_file(input_file)
    else:
        raise ValueError("❌ Unsupported file type. Use .txt, .pdf, .html, or .htm")

    if not text.strip():
        raise RuntimeError(
            "No extractable text found. If this is a scanned PDF or very script-heavy HTML, "
            "you may need OCR (for PDFs) or to load a server-rendered version."
        )

    # Normalize dashes to '-' and remove soft hyphens
    text = normalize_hyphens(text)

    # Remove line-break hyphenation (end-of-line split words)
    text = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "", text)

    # Standardize newlines
    text = text.replace("\r", "\n")

    # Unicode-aware word parts; requires at least one hyphen
    pattern = r"\b[^\W\d_]+(?:-[^\W\d_]+)+\b"
    hyphenated_words = re.findall(pattern, text, flags=re.UNICODE)

    unique_words = sorted(set(hyphenated_words), key=str.lower)

    with open(output_file, "w", encoding="utf-8") as f:
        for w in unique_words:
            f.write(w + "\n")

    print(f"✅ Found {len(unique_words)} unique hyphenated words.")
    print(f"Results saved to '{output_file}'.")

if __name__ == "__main__":
    # Change this to your file path (.txt / .pdf / .html / .htm)
    input_path = r"C:\Users\Ash\Downloads\Exported-Data\chatGPT\October-12\chat.html"
    output_path = "hyphenated_words.txt"
    extract_hyphenated_words(input_path, output_path)
