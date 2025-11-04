#!/usr/bin/env python3
"""
Pack Chat Tree — inline a large conversations export JSON into the HTML viewer.

Usage (preferred flags):
  python pack-chat-tree.py --export-json export.json --template-html chat-tree.html --output-html chat-tree-packed.html

Also supported (positional fallback, in this order):
  python pack-chat-tree.py export.json chat-tree.html chat-tree-packed.html

Notes:
- Escapes JSON safely for <script> embedding.
- Minifies JSON to reduce size.
- If you omit --template-html, a minimal built-in template is used.
"""

import argparse
import json
import sys
from pathlib import Path

def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def write_text(p: Path, s: str):
    p.write_text(s, encoding="utf-8", newline="\n")

def minify_json(obj) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)

def html_escape_json_for_script_tag(s: str) -> str:
    # Prevent accidental </script> termination and < parsing
    s = s.replace("</script>", "<\\/script>")
    s = s.replace("<", "\\u003C")
    return s

BUILTIN_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Chat Thread Tree Browser (Packed)</title>
  <style>
    body{margin:0;background:#0f1116;color:#e6e9ef;font-family:system-ui,-apple-system,Segoe UI,Roboto,Inter,Arial,sans-serif}
    .wrap{max-width:1100px;margin:32px auto;padding:0 16px}
    .panel{background:#0c0f15;border:1px solid #202635;border-radius:14px;box-shadow:0 8px 30px rgba(0,0,0,.35),inset 0 1px 0 rgba(255,255,255,.03)}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Chat Thread Tree Browser (Packed)</h1>
    <p>Open this file locally. Data is embedded below.</p>
    <!-- EMBEDDED_JSON_INSERT_POINT -->
  </div>
  <!-- Minimal loader to display data using the same API as the full app -->
  <script>
    (function(){
      const tag=document.getElementById('embedded-data');
      if(!tag){ document.body.insertAdjacentHTML('beforeend','<p style="color:#aaa">No embedded data found.</p>'); return; }
      const data=JSON.parse(tag.textContent);
      const pre=document.createElement('pre'); pre.textContent=JSON.stringify(data.slice(0,1), null, 2);
      document.body.appendChild(pre);
      // For best experience, use the full chat-tree.html template as input.
    })();
  </script>
</body>
</html>
"""

def inject_json_into_html(html: str, json_str: str) -> str:
    payload = f'<script id="embedded-data" type="application/json">{json_str}</script>'
    if "<!-- EMBEDDED_JSON_INSERT_POINT -->" in html:
        return html.replace("<!-- EMBEDDED_JSON_INSERT_POINT -->", payload)
    # Otherwise, insert before </body>
    idx = html.lower().rfind("</body>")
    if idx == -1:
        return html + "\n" + payload + "\n"
    return html[:idx] + payload + html[idx:]

def parse_args():
    ap = argparse.ArgumentParser()
    # Hyphen-style optional flags
    ap.add_argument("--export-json", dest="export_json", help="Path to conversations export JSON")
    ap.add_argument("--template-html", dest="template_html", help="Path to chat-tree.html template (optional)")
    ap.add_argument("--output-html", dest="output_html", help="Path to write packed HTML (optional)")

    # Positional fallbacks (same order)
    ap.add_argument("pos_export", nargs="?", help="(positional) export.json")
    ap.add_argument("pos_template", nargs="?", help="(positional) chat-tree.html")
    ap.add_argument("pos_output", nargs="?", help="(positional) chat-tree-packed.html")
    args = ap.parse_args()

    # Resolve precedence: flags override positionals
    export_json = args.export_json or args.pos_export
    template_html = args.template_html or args.pos_template
    output_html = args.output_html or args.pos_output

    if not export_json:
        ap.error("You must provide --export-json or a positional export.json path")

    return export_json, template_html, output_html

def main():
    export_json, template_html, output_html = parse_args()

    export_path = Path(export_json)
    if not export_path.exists():
        print(f"Error: {export_path} not found", file=sys.stderr)
        sys.exit(1)

    # Load and validate JSON
    try:
        with export_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            print("Error: Top-level JSON must be an array of conversations", file=sys.stderr)
            sys.exit(2)
    except Exception as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(2)

    # Minify & escape
    mini = minify_json(data)
    safe = html_escape_json_for_script_tag(mini)

    # Load template
    if template_html:
        tpl_path = Path(template_html)
        if not tpl_path.exists():
            print(f"Error: template {tpl_path} not found", file=sys.stderr)
            sys.exit(3)
        html = read_text(tpl_path)
    else:
        html = BUILTIN_TEMPLATE

    # Inject
    out_html = inject_json_into_html(html, safe)

    # Output path
    out_path = Path(output_html) if output_html else Path("chat-tree-packed.html")
    write_text(out_path, out_html)

    # Report
    print(f"Embedded {len(mini):,} bytes of minified JSON into {out_path}")
    print("Open the packed HTML in a browser. If you used the full app template, it will render automatically.")
    print("Tip: For very large files, open from disk (file://) in a modern browser, or serve locally to enable streaming.")

if __name__ == "__main__":
    main()
