import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import { v4 as uuidv4 } from "uuid";
import { ZipFile } from "yazl";
import { Readable } from "stream";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(express.static(path.join(__dirname, "public")));
app.use(express.json({ limit: "5mb" }));

app.get("/", (_req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

/**
 * POST /export
 * Body: {
 *  metadata: { title, author, language, identifier, publisher, date },
 *  chapters: [ { id, title, contentHtml } ]
 * }
 * Returns: application/epub+zip stream
 */
app.post("/export", async (req, res) => {
  try {
    const { metadata, chapters } = req.body || {};
    if (!metadata || !chapters || !Array.isArray(chapters) || chapters.length === 0) {
      return res.status(400).json({ error: "Missing metadata or chapters." });
    }

    // sensible defaults
    const nowISO = new Date().toISOString().slice(0, 10);
    const meta = {
      title: (metadata.title || "Untitled").trim(),
      author: (metadata.author || "Unknown Author").trim(),
      language: (metadata.language || "en").trim(),
      identifier: (metadata.identifier || `urn:uuid:${uuidv4()}`).trim(),
      publisher: (metadata.publisher || "").trim(),
      date: (metadata.date || nowISO).trim()
    };

    // ensure each chapter has an id
    const chaps = chapters.map((c, i) => ({
      id: c.id || `chap${i + 1}`,
      title: (c.title || `Chapter ${i + 1}`).trim(),
      contentHtml: (c.contentHtml || "<p>(empty)</p>").trim()
    }));

    // Build required EPUB files in memory
    // 1) mimetype (must be first, uncompressed)
    const mimetype = "application/epub+zip";

    // 2) META-INF/container.xml
    const containerXml = `<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>`;

    // 3) OEBPS/xhtml for each chapter
    const xhtmls = chaps.map(c => ({
      path: `OEBPS/${c.id}.xhtml`,
      xml: xhtmlForChapter(meta.title, c.title, c.contentHtml)
    }));

    // 4) OEBPS/nav.xhtml (EPUB3 navigation)
    const navXhtml = navForChapters(meta.title, chaps);

    // 5) OEBPS/content.opf (manifest + spine + metadata)
    const contentOpf = opfForBook(meta, chaps);

    // Create zip stream with correct order/flags
    const zip = new ZipFile();

    // Headers for download
    const safeTitle = meta.title.replace(/[^\w\-]+/g, "_");
    res.setHeader("Content-Type", "application/epub+zip");
    res.setHeader("Content-Disposition", `attachment; filename="${safeTitle}.epub"`);

    // **Order matters**: 'mimetype' MUST be the first entry and uncompressed (store)
    zip.addBuffer(Buffer.from(mimetype, "utf8"), "mimetype", { compress: false });

    // Then the rest (compressed is fine)
    zip.addBuffer(Buffer.from(containerXml, "utf8"), "META-INF/container.xml");
    xhtmls.forEach(x => zip.addBuffer(Buffer.from(x.xml, "utf8"), x.path));
    zip.addBuffer(Buffer.from(navXhtml, "utf8"), "OEBPS/nav.xhtml");
    zip.addBuffer(Buffer.from(contentOpf, "utf8"), "OEBPS/content.opf");

    // Pipe zip to response
    zip.end();
    const zipStream = zip.outputStream;
    Readable.from(zipStream).pipe(res);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to build EPUB." });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`📚 EPUB Maker running at http://localhost:${PORT}`));

/* ---------- helpers ---------- */

function xhtmlForChapter(bookTitle, chapterTitle, htmlBody) {
  return `<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
  <meta charset="utf-8"/>
  <title>${escapeXml(chapterTitle)} — ${escapeXml(bookTitle)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <style>
    body{font-family: serif; line-height:1.5; margin: 1em auto; max-width: 40rem;}
    h1{font-size:1.6em; margin: 0 0 .6em}
    p{margin:.6em 0}
  </style>
</head>
<body>
  <h1>${escapeXml(chapterTitle)}</h1>
  ${sanitizeParagraphs(htmlBody)}
</body>
</html>`;
}

function navForChapters(bookTitle, chapters) {
  const lis = chapters.map(c =>
    `<li><a href="${c.id}.xhtml">${escapeXml(c.title)}</a></li>`
  ).join("\n");
  return `<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:epub="http://www.idpf.org/2007/ops" lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Navigation — ${escapeXml(bookTitle)}</title>
</head>
<body>
  <nav epub:type="toc" id="toc">
    <h2>Contents</h2>
    <ol>
      ${lis}
    </ol>
  </nav>
</body>
</html>`;
}

function opfForBook(meta, chapters) {
  const manifestItems = chapters.map(c =>
    `<item id="${c.id}" href="${c.id}.xhtml" media-type="application/xhtml+xml"/>`
  ).join("\n      ");
  const spineItems = chapters.map(c =>
    `<itemref idref="${c.id}"/>`
  ).join("\n      ");

  return `<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">${escapeXml(meta.identifier)}</dc:identifier>
    <dc:title>${escapeXml(meta.title)}</dc:title>
    <dc:language>${escapeXml(meta.language)}</dc:language>
    <dc:creator>${escapeXml(meta.author)}</dc:creator>
    ${meta.publisher ? `<dc:publisher>${escapeXml(meta.publisher)}</dc:publisher>` : ""}
    <meta property="dcterms:modified">${meta.date}T00:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" properties="nav" media-type="application/xhtml+xml"/>
    ${manifestItems ? "      " + manifestItems : ""}
  </manifest>
  <spine>
    <itemref idref="nav" linear="no"/>
    ${spineItems ? "      " + spineItems : ""}
  </spine>
</package>`;
}

function escapeXml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// very small sanitizer: wrap plain text into <p>, keep basic inline tags
function sanitizeParagraphs(html) {
  // If the user pasted plain text, convert blank-line-separated paragraphs
  if (!/<[a-z]/i.test(html)) {
    return html
      .split(/\n{2,}/)
      .map(p => `<p>${escapeXml(p.trim())}</p>`)
      .join("\n");
  }
  return html;
}
