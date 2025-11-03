#!/usr/bin/env python3
"""
EPUB Builder – single‑file Tkinter app for Windows/macOS/Linux

Features
- Enter ebook metadata (title, author, language, identifier/ISBN, publisher, description)
- Add, edit, reorder, and remove chapters (rich HTML supported)
- Optional cover image (.jpg/.png)
- Save/Load project as JSON
- Export to EPUB (via ebooklib)

Dependencies
    pip install ebooklib lxml pillow

Run
    python epub_builder.py

Notes
- Generates EPUB 3 (includes NCX + NAV).
- Chapter content should be valid HTML fragments (we add minimal wrappers).
"""
from __future__ import annotations

import io
import json
import os
import sys
from dataclasses import dataclass, asdict
from typing import List, Optional

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    from tkinter.scrolledtext import ScrolledText
except Exception as e:
    print("Tkinter is required to run this app.")
    raise

# Optional libs checked at export time
try:
    from PIL import Image
except Exception:
    Image = None  # type: ignore

@dataclass
class Chapter:
    title: str
    content_html: str

    def to_dict(self):
        return {"title": self.title, "content_html": self.content_html}

    @staticmethod
    def from_dict(d: dict) -> "Chapter":
        return Chapter(title=d.get("title", "Untitled"), content_html=d.get("content_html", ""))


class EpubProject:
    def __init__(self):
        self.title: str = "Untitled Book"
        self.author: str = ""
        self.language: str = "en"
        self.identifier: str = "id-12345"
        self.publisher: str = ""
        self.description: str = ""
        self.cover_path: Optional[str] = None
        self.chapters: List[Chapter] = []

    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "language": self.language,
            "identifier": self.identifier,
            "publisher": self.publisher,
            "description": self.description,
            "cover_path": self.cover_path,
            "chapters": [c.to_dict() for c in self.chapters],
        }

    @staticmethod
    def from_dict(d: dict) -> "EpubProject":
        p = EpubProject()
        p.title = d.get("title", p.title)
        p.author = d.get("author", p.author)
        p.language = d.get("language", p.language)
        p.identifier = d.get("identifier", p.identifier)
        p.publisher = d.get("publisher", p.publisher)
        p.description = d.get("description", p.description)
        p.cover_path = d.get("cover_path")
        p.chapters = [Chapter.from_dict(x) for x in d.get("chapters", [])]
        return p


class EpubBuilderApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master.title("EPUB Builder")
        self.master.geometry("1100x680")
        self.pack(fill=tk.BOTH, expand=True)

        # Project state
        self.project = EpubProject()
        self.current_project_path: Optional[str] = None
        self._dirty = False

        self._build_menu()
        self._build_ui()
        self._bind_events()
        self._refresh_titlebar()

    # ---------------- UI ----------------
    def _build_menu(self):
        menubar = tk.Menu(self.master)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Project", command=self.new_project, accelerator="Ctrl+N")
        file_menu.add_command(label="Open Project…", command=self.open_project, accelerator="Ctrl+O")
        file_menu.add_command(label="Save Project", command=self.save_project, accelerator="Ctrl+S")
        file_menu.add_command(label="Save Project As…", command=self.save_project_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export EPUB…", command=self.export_epub, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_exit)

        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Choose Cover Image…", command=self.choose_cover)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)

        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.master.config(menu=menubar)

    def _build_ui(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Left panel: Chapters list & controls
        left = ttk.Frame(self)
        left.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        left.rowconfigure(1, weight=1)

        ttk.Label(left, text="Chapters").grid(row=0, column=0, sticky="w")

        self.chapter_list = tk.Listbox(left, activestyle="dotbox")
        self.chapter_list.grid(row=1, column=0, sticky="nsew")

        btns = ttk.Frame(left)
        btns.grid(row=2, column=0, sticky="ew", pady=(6,0))
        for i in range(5):
            btns.columnconfigure(i, weight=1)

        ttk.Button(btns, text="Add", command=self.add_chapter).grid(row=0, column=0, sticky="ew", padx=2)
        ttk.Button(btns, text="Duplicate", command=self.duplicate_chapter).grid(row=0, column=1, sticky="ew", padx=2)
        ttk.Button(btns, text="Delete", command=self.delete_chapter).grid(row=0, column=2, sticky="ew", padx=2)
        ttk.Button(btns, text="Up", command=lambda: self.move_chapter(-1)).grid(row=0, column=3, sticky="ew", padx=2)
        ttk.Button(btns, text="Down", command=lambda: self.move_chapter(1)).grid(row=0, column=4, sticky="ew", padx=2)

        # Right panel: Tabs for Metadata & Editor
        right = ttk.Notebook(self)
        right.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)

        # Metadata tab
        meta_frame = ttk.Frame(right)
        meta_frame.columnconfigure(1, weight=1)

        self.var_title = tk.StringVar()
        self.var_author = tk.StringVar()
        self.var_lang = tk.StringVar(value="en")
        self.var_identifier = tk.StringVar(value="id-12345")
        self.var_publisher = tk.StringVar()
        self.var_cover = tk.StringVar()

        row = 0
        ttk.Label(meta_frame, text="Title:").grid(row=row, column=0, sticky="e", padx=6, pady=4)
        ttk.Entry(meta_frame, textvariable=self.var_title).grid(row=row, column=1, sticky="ew", pady=4)
        row += 1
        ttk.Label(meta_frame, text="Author:").grid(row=row, column=0, sticky="e", padx=6, pady=4)
        ttk.Entry(meta_frame, textvariable=self.var_author).grid(row=row, column=1, sticky="ew", pady=4)
        row += 1
        ttk.Label(meta_frame, text="Language (BCP47):").grid(row=row, column=0, sticky="e", padx=6, pady=4)
        ttk.Entry(meta_frame, width=12, textvariable=self.var_lang).grid(row=row, column=1, sticky="w", pady=4)
        row += 1
        ttk.Label(meta_frame, text="Identifier/ISBN:").grid(row=row, column=0, sticky="e", padx=6, pady=4)
        ttk.Entry(meta_frame, textvariable=self.var_identifier).grid(row=row, column=1, sticky="ew", pady=4)
        row += 1
        ttk.Label(meta_frame, text="Publisher:").grid(row=row, column=0, sticky="e", padx=6, pady=4)
        ttk.Entry(meta_frame, textvariable=self.var_publisher).grid(row=row, column=1, sticky="ew", pady=4)
        row += 1
        ttk.Label(meta_frame, text="Description:").grid(row=row, column=0, sticky="ne", padx=6, pady=4)
        self.txt_description = ScrolledText(meta_frame, height=6, wrap=tk.WORD)
        self.txt_description.grid(row=row, column=1, sticky="nsew", pady=4)
        meta_frame.rowconfigure(row, weight=1)
        row += 1

        ttk.Label(meta_frame, text="Cover:").grid(row=row, column=0, sticky="e", padx=6, pady=4)
        cover_row = ttk.Frame(meta_frame)
        cover_row.grid(row=row, column=1, sticky="ew")
        cover_row.columnconfigure(0, weight=1)
        ttk.Entry(cover_row, textvariable=self.var_cover, state="readonly").grid(row=0, column=0, sticky="ew")
        ttk.Button(cover_row, text="Browse…", command=self.choose_cover).grid(row=0, column=1, padx=6)

        right.add(meta_frame, text="Metadata")

        # Editor tab
        edit_frame = ttk.Frame(right)
        edit_frame.rowconfigure(3, weight=1)
        edit_frame.columnconfigure(1, weight=1)

        self.var_ch_title = tk.StringVar()
        ttk.Label(edit_frame, text="Chapter Title:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.entry_ch_title = ttk.Entry(edit_frame, textvariable=self.var_ch_title)
        self.entry_ch_title.grid(row=0, column=1, sticky="ew", padx=0, pady=6)

        self.txt_chapter = ScrolledText(edit_frame, wrap=tk.WORD)
        self.txt_chapter.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)

        save_row = ttk.Frame(edit_frame)
        save_row.grid(row=2, column=0, columnspan=2, sticky="ew")
        ttk.Button(save_row, text="Save Changes to Selected Chapter", command=self.save_current_chapter).pack(side=tk.RIGHT)

        tips = ttk.Label(edit_frame, foreground="#555",
            text=("Tip: write valid HTML fragments for chapters (e.g., <h2>…</h2><p>…</p>).\n"
                  "You can paste from a word processor and tidy later if needed."))
        tips.grid(row=3, column=0, columnspan=2, sticky="w", padx=6)

        right.add(edit_frame, text="Chapter Editor")

    def _bind_events(self):
        self.master.bind("<Control-n>", lambda e: self.new_project())
        self.master.bind("<Control-o>", lambda e: self.open_project())
        self.master.bind("<Control-s>", lambda e: self.save_project())
        self.master.bind("<Control-e>", lambda e: self.export_epub())
        self.chapter_list.bind("<<ListboxSelect>>", lambda e: self.load_selected_chapter_into_editor())

    # ------------- Project Ops -------------
    def new_project(self):
        if not self._confirm_discard_changes():
            return
        self.project = EpubProject()
        self.current_project_path = None
        self._dirty = False
        self._refresh_all()

    def open_project(self):
        if not self._confirm_discard_changes():
            return
        path = filedialog.askopenfilename(
            title="Open Project JSON",
            filetypes=[("EPUB Builder Project", "*.epubproj.json"), ("JSON", "*.json"), ("All Files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.project = EpubProject.from_dict(data)
            self.current_project_path = path
            self._dirty = False
            self._refresh_all()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open project:\n{e}")

    def save_project_as(self):
        path = filedialog.asksaveasfilename(
            title="Save Project As",
            defaultextension=".epubproj.json",
            filetypes=[("EPUB Builder Project", "*.epubproj.json"), ("JSON", "*.json"), ("All Files", "*.*")],
        )
        if not path:
            return
        self.current_project_path = path
        self._write_project_to_path(path)

    def save_project(self):
        if self.current_project_path is None:
            return self.save_project_as()
        self._write_project_to_path(self.current_project_path)

    def _write_project_to_path(self, path: str):
        try:
            self._sync_meta_from_ui()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.project.to_dict(), f, ensure_ascii=False, indent=2)
            self._dirty = False
            self._refresh_titlebar()
            messagebox.showinfo("Saved", f"Project saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save project:\n{e}")

    # ------------- Metadata -------------
    def _sync_meta_from_ui(self):
        self.project.title = self.var_title.get().strip() or "Untitled Book"
        self.project.author = self.var_author.get().strip()
        self.project.language = self.var_lang.get().strip() or "en"
        self.project.identifier = self.var_identifier.get().strip() or "id-12345"
        self.project.publisher = self.var_publisher.get().strip()
        self.project.description = self.txt_description.get("1.0", tk.END).strip()
        self.project.cover_path = self.var_cover.get() or None

    def _load_meta_into_ui(self):
        self.var_title.set(self.project.title)
        self.var_author.set(self.project.author)
        self.var_lang.set(self.project.language)
        self.var_identifier.set(self.project.identifier)
        self.var_publisher.set(self.project.publisher)
        self.txt_description.delete("1.0", tk.END)
        self.txt_description.insert("1.0", self.project.description)
        self.var_cover.set(self.project.cover_path or "")

    # ------------- Chapters -------------
    def add_chapter(self):
        new = Chapter(title=f"Chapter {len(self.project.chapters)+1}", content_html="<h2>New Chapter</h2>\n<p>Start writing…</p>")
        self.project.chapters.append(new)
        self._dirty = True
        self._refresh_chapter_list()
        self.chapter_list.selection_clear(0, tk.END)
        idx = len(self.project.chapters) - 1
        self.chapter_list.selection_set(idx)
        self.chapter_list.activate(idx)
        self.load_selected_chapter_into_editor()

    def duplicate_chapter(self):
        idx = self._selected_index()
        if idx is None:
            return
        c = self.project.chapters[idx]
        self.project.chapters.insert(idx + 1, Chapter(title=c.title + " (Copy)", content_html=c.content_html))
        self._dirty = True
        self._refresh_chapter_list()
        self.chapter_list.selection_clear(0, tk.END)
        self.chapter_list.selection_set(idx + 1)
        self.load_selected_chapter_into_editor()

    def delete_chapter(self):
        idx = self._selected_index()
        if idx is None:
            return
        if not messagebox.askyesno("Delete Chapter", "Delete the selected chapter?"):
            return
        del self.project.chapters[idx]
        self._dirty = True
        self._refresh_chapter_list()
        if self.project.chapters:
            sel = min(idx, len(self.project.chapters) - 1)
            self.chapter_list.selection_set(sel)
            self.load_selected_chapter_into_editor()
        else:
            self.var_ch_title.set("")
            self.txt_chapter.delete("1.0", tk.END)

    def move_chapter(self, delta: int):
        idx = self._selected_index()
        if idx is None:
            return
        new_idx = idx + delta
        if not (0 <= new_idx < len(self.project.chapters)):
            return
        self.project.chapters[idx], self.project.chapters[new_idx] = (
            self.project.chapters[new_idx],
            self.project.chapters[idx],
        )
        self._dirty = True
        self._refresh_chapter_list()
        self.chapter_list.selection_clear(0, tk.END)
        self.chapter_list.selection_set(new_idx)
        self.chapter_list.activate(new_idx)
        self.load_selected_chapter_into_editor()

    def _selected_index(self) -> Optional[int]:
        sel = self.chapter_list.curselection()
        if not sel:
            return None
        return int(sel[0])

    def load_selected_chapter_into_editor(self):
        idx = self._selected_index()
        if idx is None:
            return
        c = self.project.chapters[idx]
        self.var_ch_title.set(c.title)
        self.txt_chapter.delete("1.0", tk.END)
        self.txt_chapter.insert("1.0", c.content_html)

    def save_current_chapter(self):
        idx = self._selected_index()
        if idx is None:
            messagebox.showwarning("No selection", "Select a chapter first.")
            return
        title = self.var_ch_title.get().strip() or f"Chapter {idx+1}"
        html = self.txt_chapter.get("1.0", tk.END).strip()
        self.project.chapters[idx].title = title
        self.project.chapters[idx].content_html = html
        self._dirty = True
        self._refresh_chapter_list()
        self.chapter_list.selection_clear(0, tk.END)
        self.chapter_list.selection_set(idx)
        self.chapter_list.activate(idx)
        messagebox.showinfo("Saved", "Chapter updated.")

    def _refresh_chapter_list(self):
        self.chapter_list.delete(0, tk.END)
        for i, c in enumerate(self.project.chapters, start=1):
            self.chapter_list.insert(tk.END, f"{i:02d}. {c.title}")
        self._refresh_titlebar()

    def choose_cover(self):
        path = filedialog.askopenfilename(title="Choose Cover Image", filetypes=[
            ("Images", "*.jpg;*.jpeg;*.png"),
            ("JPEG", "*.jpg;*.jpeg"),
            ("PNG", "*.png"),
            ("All Files", "*.*"),
        ])
        if not path:
            return
        self.var_cover.set(path)
        self.project.cover_path = path
        self._dirty = True

    # ------------- Export EPUB -------------
    def export_epub(self):
        # Lazy import to allow UI to run without deps until export
        try:
            from ebooklib import epub
        except Exception:
            messagebox.showerror(
                "Missing dependency",
                "The 'ebooklib' package is required to export.\nRun: pip install ebooklib lxml pillow",
            )
            return

        self._sync_meta_from_ui()
        if not self.project.title or not self.project.author:
            messagebox.showwarning("Missing metadata", "Please provide at least Title and Author in Metadata tab.")
            return
        if not self.project.chapters:
            messagebox.showwarning("No chapters", "Add at least one chapter before exporting.")
            return

        out_path = filedialog.asksaveasfilename(
            title="Export EPUB",
            defaultextension=".epub",
            filetypes=[("EPUB", "*.epub"), ("All Files", "*.*")],
            initialfile=f"{self._slug(self.project.title)}.epub",
        )
        if not out_path:
            return

        try:
            book = epub.EpubBook()
            book.set_identifier(self.project.identifier or "id-12345")
            book.set_title(self.project.title)
            book.set_language(self.project.language or "en")
            if self.project.author:
                # Multiple authors can be added with repeated calls
                book.add_author(self.project.author)
            if self.project.publisher:
                book.add_metadata("DC", "publisher", self.project.publisher)
            if self.project.description:
                book.add_metadata("DC", "description", self.project.description)

            # Cover image
            if self.project.cover_path:
                try:
                    with open(self.project.cover_path, "rb") as f:
                        cover_bytes = f.read()
                    # ebooklib will set up the cover xhtml automatically
                    book.set_cover(os.path.basename(self.project.cover_path), cover_bytes)
                except Exception as ce:
                    messagebox.showwarning("Cover error", f"Could not embed cover image:\n{ce}\nContinuing without cover.")

            # Chapters
            spine = ["nav"]
            toc = []
            chapter_items = []
            for idx, ch in enumerate(self.project.chapters, start=1):
                file_name = f"chap_{idx:03d}.xhtml"
                item = epub.EpubHtml(title=ch.title, file_name=file_name, lang=self.project.language or "en")
                # Wrap fragment into full xhtml
                item.content = self._wrap_xhtml(ch.title, ch.content_html).encode("utf-8")
                book.add_item(item)
                chapter_items.append(item)
                spine.append(item)
                toc.append(item)

            # TOC & spine
            book.toc = tuple(toc)
            book.spine = spine

            # Required nav/NCX
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())

            # Basic CSS to ensure pleasant defaults
            style = """
            body{font-family: serif; line-height:1.4;}
            h1,h2,h3{font-weight:bold;}
            img{max-width:100%;}
            """
            nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
            book.add_item(nav_css)

            # Write out
            epub.write_epub(out_path, book, {})
            messagebox.showinfo("Exported", f"EPUB saved to:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Export failed", f"Could not export EPUB:\n{e}")

    # ------------- Helpers -------------
    def _wrap_xhtml(self, title: str, body_fragment: str) -> str:
        return f"""<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE html>
<html xmlns='http://www.w3.org/1999/xhtml' lang='{self.project.language or 'en'}'>
<head>
  <meta charset='utf-8'/>
  <title>{self._xml_escape(title)}</title>
</head>
<body>
{body_fragment}
</body>
</html>
"""

    def _xml_escape(self, s: str) -> str:
        return (
            s.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

    def _slug(self, s: str) -> str:
        import re
        s = s.strip().lower()
        s = re.sub(r"[^a-z0-9]+", "-", s)
        s = re.sub(r"-+", "-", s).strip("-")
        return s or "book"

    def _refresh_all(self):
        self._load_meta_into_ui()
        self._refresh_chapter_list()

    def _refresh_titlebar(self):
        star = "*" if self._dirty else ""
        name = os.path.basename(self.current_project_path) if self.current_project_path else "(unsaved)"
        self.master.title(f"EPUB Builder {star} – {name}")

    def _confirm_discard_changes(self) -> bool:
        if not self._dirty:
            return True
        return messagebox.askyesno("Discard changes?", "You have unsaved changes. Discard them?")

    def show_about(self):
        messagebox.showinfo(
            "About",
            "EPUB Builder\n\nA simple GUI to assemble eBooks and export EPUB files.\nBuilt with Tkinter + ebooklib.",
        )

    def on_exit(self):
        if self._confirm_discard_changes():
            self.master.destroy()


def main():
    root = tk.Tk()
    # ttk theme tweaks for nicer look on Windows
    try:
        style = ttk.Style(root)
        if sys.platform.startswith("win"):
            style.theme_use("vista")
    except Exception:
        pass
    app = EpubBuilderApp(root)
    app.mainloop()


if __name__ == "__main__":
    main()
