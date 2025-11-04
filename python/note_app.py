import tkinter as tk
from tkinter import ttk, messagebox
from tkhtmlview import HTMLLabel
from tkcalendar import DateEntry
import json, os
from datetime import date
import markdown

NOTES_FILE = "notes.json"

def load_notes():
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_notes(notes):
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=4)

class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notes App")

        # Title
        tk.Label(root, text="Title:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.title_entry = tk.Entry(root, width=50)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        # Date
        tk.Label(root, text="Date:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.date_entry = DateEntry(root, width=20, background="darkblue",
                                    foreground="white", borderwidth=2)
        self.date_entry.set_date(date.today())
        self.date_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Categories
        tk.Label(root, text="Categories (comma-separated):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.categories_entry = tk.Entry(root, width=50)
        self.categories_entry.grid(row=2, column=1, padx=5, pady=5)

        # Note content
        tk.Label(root, text="Content:").grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        self.text_area = tk.Text(root, width=60, height=15)
        self.text_area.grid(row=3, column=1, padx=5, pady=5)

        # Save button
        save_btn = tk.Button(root, text="Save Note", command=self.save_note)
        save_btn.grid(row=4, column=1, sticky="e", pady=5)

        # Category filter
        tk.Label(root, text="Filter by Category:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.category_filter = ttk.Combobox(root, values=["All"], state="readonly", width=47)
        self.category_filter.set("All")
        self.category_filter.grid(row=5, column=1, sticky="w", padx=5, pady=5)
        self.category_filter.bind("<<ComboboxSelected>>", self.refresh_notes)

        # Notes list
        tk.Label(root, text="Your Notes:").grid(row=6, column=0, sticky="nw", padx=5, pady=5)
        self.notes_list = tk.Listbox(root, width=50, height=10)
        self.notes_list.grid(row=6, column=1, padx=5, pady=5)
        self.notes_list.bind("<<ListboxSelect>>", self.display_note)

        # Markdown preview
        self.preview_label = HTMLLabel(root, html="", width=60, height=15)
        self.preview_label.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

        self.refresh_notes()

    def save_note(self):
        title = self.title_entry.get().strip()
        note_date = self.date_entry.get_date().isoformat()
        categories = [c.strip() for c in self.categories_entry.get().split(",") if c.strip()]
        content = self.text_area.get("1.0", "end").strip()

        if not title or not content:
            messagebox.showerror("Error", "Title and Content cannot be empty.")
            return

        notes = load_notes()
        notes.append({
            "title": title,
            "date": note_date,
            "categories": categories,
            "content": content
        })
        save_notes(notes)

        self.refresh_notes()
        self.clear_inputs()
        messagebox.showinfo("Saved", "Note saved successfully!")

    def refresh_notes(self, event=None):
        self.notes_list.delete(0, tk.END)
        notes = load_notes()

        # Update category filter values
        all_categories = set()
        for note in notes:
            all_categories.update(note["categories"])
        self.category_filter["values"] = ["All"] + sorted(all_categories)

        selected_filter = self.category_filter.get()

        for i, note in enumerate(notes):
            if selected_filter != "All" and selected_filter not in note["categories"]:
                continue
            cats = ", ".join(note["categories"]) if note["categories"] else "No Category"
            self.notes_list.insert(tk.END, f"{note['title']} ({note['date']}) [{cats}]")

    def clear_inputs(self):
        self.title_entry.delete(0, tk.END)
        self.text_area.delete("1.0", "end")
        self.categories_entry.delete(0, tk.END)
        self.date_entry.set_date(date.today())

    def display_note(self, event):
        selection = self.notes_list.curselection()
        if not selection:
            return
        index = selection[0]

        notes = load_notes()
        selected_filter = self.category_filter.get()

        # Build filtered notes list
        filtered_notes = []
        for note in notes:
            if selected_filter != "All" and selected_filter not in note["categories"]:
                continue
            filtered_notes.append(note)

        if index >= len(filtered_notes):
            return

        note = filtered_notes[index]

        html_content = markdown.markdown(note["content"])
        self.preview_label.set_html(
            f"<h3>{note['title']}</h3>"
            f"<p><i>{note['date']}</i></p>"
            f"<p><b>Categories:</b> {', '.join(note['categories'])}</p>"
            f"{html_content}"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()
