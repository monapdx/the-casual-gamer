import React, { useEffect, useMemo, useRef, useState } from "react";
import cloud from "d3-cloud";
import seedrandom from "seedrandom";
import { Download, Plus, RefreshCw, Trash2, Upload } from "lucide-react";

/* === Minimal UI shim (no shadcn needed) ======================= */
const cn = (...c) => c.filter(Boolean).join(" ");

function Card({ className, children }) {
  return <div className={cn("rounded-2xl border shadow-sm bg-white", className)}>{children}</div>;
}
function CardContent({ className, children }) {
  return <div className={cn("p-4", className)}>{children}</div>;
}
function Button({ children, className, variant, ...props }) {
  const base = "inline-flex items-center justify-center rounded-2xl px-3 py-2 text-sm border";
  const styles = {
    default: "bg-black text-white border-black hover:opacity-90",
    secondary: "bg-white text-black border-neutral-300 hover:bg-neutral-50",
    ghost: "bg-transparent border-transparent hover:bg-neutral-100",
    destructive: "bg-red-600 text-white border-red-600 hover:opacity-90",
  };
  return (
    <button className={cn(base, styles[variant || "default"], className)} {...props}>
      {children}
    </button>
  );
}
function Input({ className, ...props }) {
  return <input className={cn("border rounded-xl px-2 py-2 text-sm w-full", className)} {...props} />;
}
function Label({ className, children }) {
  return <label className={cn("block text-sm mb-1", className)}>{children}</label>;
}
function Slider({ value, min = 0, max = 100, step = 1, onValueChange }) {
  return (
    <input
      type="range"
      className="w-full"
      min={min}
      max={max}
      step={step}
      value={value?.[0] ?? 0}
      onChange={(e) => onValueChange([Number(e.target.value)])}
    />
  );
}
function Switch({ checked, onCheckedChange }) {
  return (
    <label className="inline-flex items-center gap-2 cursor-pointer">
      <input type="checkbox" checked={checked} onChange={(e) => onCheckedChange(e.target.checked)} />
    </label>
  );
}
function Select({ value, onValueChange, children }) {
  return (
    <select className="border rounded-xl px-2 py-2 w-full" value={value} onChange={(e) => onValueChange(e.target.value)}>
      {children}
    </select>
  );
}
function SelectTrigger({ children }) { return <>{children}</>; }
function SelectValue() { return null; }
function SelectContent({ children }) { return <>{children}</>; }
function SelectItem({ value, children }) { return <option value={value}>{children}</option>; }
/* =============================================================== */

const defaultWords = [
  { text: "design", weight: 40 },
  { text: "react", weight: 34 },
  { text: "javascript", weight: 30 },
  { text: "ui", weight: 28 },
  { text: "frontend", weight: 26 },
  { text: "tailwind", weight: 22 },
  { text: "visualization", weight: 20 },
  { text: "d3", weight: 18 },
  { text: "cloud", weight: 16 },
  { text: "canvas", weight: 15 },
  { text: "svg", weight: 14 },
  { text: "open-source", weight: 12 },
  { text: "accessibility", weight: 10 },
];

const palettes = {
  "Gray scale": (i) => `hsl(0 0% ${80 - (i % 6) * 10}% )`,
  Vibrant: (i) => `hsl(${(i * 47) % 360} 90% 55%)`,
  Cool: (i) => `hsl(${200 + ((i * 17) % 120)} 70% 55%)`,
  Warm: (i) => `hsl(${(i * 19) % 60} 80% 55%)`,
  Monochrome: (i) => `hsl(260 80% ${65 - (i % 6) * 6}% )`,
};

const fontFamilies = [
  "Inter, system-ui, sans-serif",
  "'Fjalla One', sans-serif",
  "'Bebas Neue', sans-serif",
  "'Oswald', sans-serif",
  "'Merriweather', serif",
  "'Lobster', cursive",
];

function useResize(ref) {
  const [rect, setRect] = useState({ width: 800, height: 500 });
  useEffect(() => {
    if (!ref.current) return;
    const ro = new ResizeObserver((entries) => {
      for (const e of entries) {
        const cr = e.contentRect;
        setRect({ width: cr.width, height: cr.height });
      }
    });
    ro.observe(ref.current);
    return () => ro.disconnect();
  }, [ref]);
  return rect;
}

function escapeXml(unsafe) {
  return String(unsafe)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

export default function App() {
  const [items, setItems] = useState(defaultWords);
  const [textInput, setTextInput] = useState("");
  const [weightInput, setWeightInput] = useState(20);
  const [minFont, setMinFont] = useState(14);
  const [maxFont, setMaxFont] = useState(64);
  const [padding, setPadding] = useState(2);
  const [rotate, setRotate] = useState(true);
  const [rotationAngles, setRotationAngles] = useState([-90, -60, -30, 0, 30, 60, 90]);
  const [spiral, setSpiral] = useState("archimedean");
  const [palette, setPalette] = useState("Vibrant");
  const [fontFamily, setFontFamily] = useState(fontFamilies[0]);
  const [seed, setSeed] = useState("tag-cloud");
  const [caseFold, setCaseFold] = useState(true);
  const [removeDuplicates, setRemoveDuplicates] = useState(true);
  const [svgMarkup, setSvgMarkup] = useState("");

  const boardRef = useRef(null);
  const { width, height } = useResize(boardRef);

  // Derived words
  const words = useMemo(() => {
    let list = items
      .filter((d) => d.text && String(d.text).trim().length > 0)
      .map((d) => ({
        ...d,
        text: caseFold ? String(d.text).trim().toLowerCase() : String(d.text).trim(),
      }));
    if (removeDuplicates) {
      const map = new Map();
      for (const w of list) {
        const key = w.text;
        if (!map.has(key)) map.set(key, { text: key, weight: Number(w.weight) || 1 });
        else map.get(key).weight += Number(w.weight) || 1;
      }
      list = [...map.values()];
    }
    return list;
  }, [items, caseFold, removeDuplicates]);

  // Layout with d3-cloud
  useEffect(() => {
    if (!width || !height || words.length === 0) return;

    const rng = seedrandom(seed || "tag-cloud"); // function like Math.random
    const minW = Math.min(...words.map((w) => w.weight));
    const maxW = Math.max(...words.map((w) => w.weight));
    const scale = (v) => {
      if (minW === maxW) return (minFont + maxFont) / 2;
      const t = (v - minW) / (maxW - minW);
      return minFont + t * (maxFont - minFont);
    };

    const rotations = rotationAngles.filter((a) => !isNaN(a));
    const rotFn = () => (rotate && rotations.length ? rotations[Math.floor(rng() * rotations.length)] : 0);

    const layout = cloud()
      .size([width, height])
      .words(words.map((w) => ({ ...w, size: scale(w.weight) })))
      .padding(padding)
      .rotate(rotFn)
      .font("inherit")
      .fontSize((d) => d.size)
      .random(rng) // d3-cloud expects a Math.random-like function
      .spiral(spiral);

    layout.on("end", (placed) => {
      const paletteFn = palettes[palette] || palettes["Vibrant"];
      const svg = [
        `<svg xmlns='http://www.w3.org/2000/svg' width='${width}' height='${height}' viewBox='0 0 ${width} ${height}'>`,
        `<style>text{font-family:${fontFamily}} .w{dominant-baseline:middle;text-anchor:middle;}</style>`,
        `<rect width='100%' height='100%' fill='white'/>`,
      ];
      placed.forEach((d, i) => {
        const x = d.x + width / 2;
        const y = d.y + height / 2;
        const fill = paletteFn(i);
        svg.push(
          `<text class='w' fill='${fill}' font-size='${d.size.toFixed(
            2
          )}' transform='translate(${x.toFixed(2)},${y.toFixed(2)}) rotate(${d.rotate || 0})'>${escapeXml(
            d.text
          )}</text>`
        );
      });
      svg.push("</svg>");
      setSvgMarkup(svg.join(""));
    });

    layout.start();
  }, [width, height, words, minFont, maxFont, padding, rotate, spiral, rotationAngles, palette, fontFamily, seed]);

  const addItem = () => {
    if (!textInput.trim()) return;
    setItems((prev) => [...prev, { text: textInput.trim(), weight: Number(weightInput) || 1 }]);
    setTextInput("");
    setWeightInput(20);
  };

  const importText = (text) => {
    const tokens = text.toLowerCase().match(/[\p{L}']+/gu) || [];
    const freq = new Map();
    for (const t of tokens) freq.set(t, (freq.get(t) || 0) + 1);
    const next = [...freq.entries()].map(([text, weight]) => ({ text, weight }));
    setItems(next);
  };

  const downloadSVG = () => {
    if (!svgMarkup) return;
    const blob = new Blob([svgMarkup], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "tag-cloud.svg";
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadPNG = () => {
    if (!svgMarkup) return;
    const svgBlob = new Blob([svgMarkup], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(svgBlob);
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = Math.ceil(boardRef.current.clientWidth);
      canvas.height = Math.ceil(boardRef.current.clientHeight);
      const ctx = canvas.getContext("2d");
      ctx.fillStyle = "#fff";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0);
      canvas.toBlob((blob) => {
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "tag-cloud.png";
        a.click();
      });
      URL.revokeObjectURL(url);
    };
    img.src = url;
  };

  const removeIndex = (idx) => setItems((prev) => prev.filter((_, i) => i !== idx));
  const clearAll = () => setItems([]);

  return (
    <div className="min-h-screen w-full bg-white text-neutral-900 p-4 md:p-6 lg:p-8">
      <div className="mx-auto max-w-7xl grid grid-cols-1 lg:grid-cols-[380px,1fr] gap-6">
        {/* Left: Controls */}
        <div className="space-y-4">
          <h1 className="text-2xl md:text-3xl font-bold">Tag Cloud Studio</h1>
          <Card className="rounded-2xl shadow-sm">
            <CardContent className="p-4 space-y-3">
              <div className="flex gap-2">
                <Input placeholder="Add a word" value={textInput} onChange={(e) => setTextInput(e.target.value)} />
                <div className="w-28">
                  <Label className="text-xs">Weight</Label>
                  <Input
                    type="number"
                    value={weightInput}
                    onChange={(e) => setWeightInput(parseInt(e.target.value || 1))}
                  />
                </div>
                <Button className="shrink-0" onClick={addItem}>
                  <Plus className="h-4 w-4 mr-1" />
                  Add
                </Button>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="file"
                  accept=".txt"
                  onChange={async (e) => {
                    const f = e.target.files?.[0];
                    if (!f) return;
                    const text = await f.text();
                    importText(text);
                  }}
                />
                <Upload className="h-4 w-4" />
                <span className="text-sm text-neutral-600">Import .txt to auto-generate from frequencies</span>
              </div>

              {/* Settings */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label>Font (min/max px)</Label>
                  <div className="flex gap-2 items-center">
                    <Input
                      type="number"
                      className="w-20"
                      value={minFont}
                      onChange={(e) => setMinFont(parseInt(e.target.value || 12))}
                    />
                    <span className="opacity-50">→</span>
                    <Input
                      type="number"
                      className="w-20"
                      value={maxFont}
                      onChange={(e) => setMaxFont(parseInt(e.target.value || 64))}
                    />
                  </div>
                </div>
                <div>
                  <Label>Padding</Label>
                  <Slider value={[padding]} min={0} max={12} step={1} onValueChange={(v) => setPadding(v[0])} />
                </div>
                <div>
                  <Label>Spiral</Label>
                  <Select value={spiral} onValueChange={setSpiral}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="archimedean">Archimedean</SelectItem>
                      <SelectItem value="rectangular">Rectangular</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Palette</Label>
                  <Select value={palette} onValueChange={setPalette}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.keys(palettes).map((p) => (
                        <SelectItem key={p} value={p}>
                          {p}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Font Family</Label>
                  <Select value={fontFamily} onValueChange={setFontFamily}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                      <SelectContent>
                        {fontFamilies.map((f) => (
                          <SelectItem key={f} value={f}>
                            {f}
                          </SelectItem>
                        ))}
                      </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Seed</Label>
                  <Input value={seed} onChange={(e) => setSeed(e.target.value)} />
                </div>
                <div className="flex items-center gap-2">
                  <Switch checked={rotate} onCheckedChange={setRotate} />
                  <Label>Allow rotation</Label>
                </div>
                <div>
                  <Label>Angles (comma-separated)</Label>
                  <Input
                    value={rotationAngles.join(", ")}
                    onChange={(e) =>
                      setRotationAngles(
                        e.target.value
                          .split(/[, \s]+/)
                          .map((n) => parseFloat(n))
                          .filter((x) => !isNaN(x))
                      )
                    }
                  />
                </div>
                <div className="flex items-center gap-2">
                  <Switch checked={caseFold} onCheckedChange={setCaseFold} />
                  <Label>Lowercase words</Label>
                </div>
                <div className="flex items-center gap-2">
                  <Switch checked={removeDuplicates} onCheckedChange={setRemoveDuplicates} />
                  <Label>Merge duplicates</Label>
                </div>
              </div>

              <div className="flex gap-2 pt-2">
                <Button variant="secondary" onClick={() => setSeed(String(Math.random()).slice(2))}>
                  <RefreshCw className="h-4 w-4 mr-1" />
                  Shuffle
                </Button>
                <Button onClick={downloadSVG}>
                  <Download className="h-4 w-4 mr-1" />
                  SVG
                </Button>
                <Button onClick={downloadPNG}>
                  <Download className="h-4 w-4 mr-1" />
                  PNG
                </Button>
                <Button variant="destructive" onClick={clearAll}>
                  <Trash2 className="h-4 w-4 mr-1" />
                  Clear
                </Button>
              </div>

              {/* Words list */}
              <div className="max-h-48 overflow-auto border rounded-xl p-2">
                {items.length === 0 ? (
                  <p className="text-sm text-neutral-500">No words yet. Add words above or import a .txt file.</p>
                ) : (
                  <ul className="space-y-1">
                    {items.map((w, i) => (
                      <li key={i} className="grid grid-cols-[1fr,88px,32px] gap-2 items-center">
                        <Input
                          value={w.text}
                          onChange={(e) => {
                            const v = e.target.value;
                            setItems((prev) => prev.map((x, idx) => (idx === i ? { ...x, text: v } : x)));
                          }}
                        />
                        <Input
                          type="number"
                          value={w.weight}
                          onChange={(e) => {
                            const v = parseInt(e.target.value || 1);
                            setItems((prev) => prev.map((x, idx) => (idx === i ? { ...x, weight: v } : x)));
                          }}
                        />
                        <Button variant="ghost" onClick={() => removeIndex(i)}>
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </CardContent>
          </Card>
          <p className="text-xs text-neutral-500">
            Tip: Import a block of text to auto-generate weights by word frequency. Use the Seed to create deterministic
            layouts.
          </p>
        </div>

        {/* Right: Preview */}
        <Card className="rounded-2xl shadow-sm">
          <CardContent className="p-2 h-[520px] md:h-[640px] lg:h-[720px]">
            <div ref={boardRef} className="w-full h-full bg-white rounded-xl overflow-hidden border relative">
              {svgMarkup ? (
                <div className="absolute inset-0">
                  <div className="w-full h-full" dangerouslySetInnerHTML={{ __html: svgMarkup }} />
                </div>
              ) : (
                <div className="w-full h-full grid place-items-center text-neutral-400">Generating…</div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Helpful fonts */}
      <link
        href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Fjalla+One&family=Lobster&family=Merriweather:ital,wght@0,300;0,400;0,700;1,300;1,400&family=Oswald:wght@300;400;500;600;700&display=swap"
        rel="stylesheet"
      />
    </div>
  );
}
