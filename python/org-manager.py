import sqlite3
import csv
import os
import re
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

DB_FILE = "organizations.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS orgs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    website TEXT,
    phone TEXT,
    hours TEXT,
    services TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
"""

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute(SCHEMA)

def normalize_phone(raw: str) -> str:
    # keep digits and +; format lightly if US-ish (10 digits)
    s = re.sub(r"[^\d+]", "", raw or "")
    digits = re.sub(r"\D", "", s)
    if len(digits) == 10:
        return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
    return raw.strip()

class OrgApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Organization Manager")
        self.geometry("1100x600")
        self.minsize(1000, 560)
        self.configure(padx=12, pady=12)

        self.selected_id = None
        self._build_style()
        self._build_ui()
        self.refresh_table()

    def _build_style(self):
        style = ttk.Style(self)
        try:
            self.call('tk', 'scaling', 1.2)  # slightly larger UI on Windows
        except Exception:
            pass
        if "vista" in style.theme_names():
            style.theme_use("vista")
        elif "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TButton", padding=8)
        style.configure("TEntry", padding=4)
        style.configure("Treeview.Heading", font=("", 10, "bold"))

    def _build_ui(self):
        # Layout: left form | right table
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=0, minsize=420)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

        # LEFT: form
        form = ttk.LabelFrame(container, text="Add / Edit Organization", padding=12)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        # Inputs
        self.var_name = tk.StringVar()
        self.var_website = tk.StringVar()
        self.var_phone = tk.StringVar()
        self.var_hours = tk.StringVar()

        r = 0
        ttk.Label(form, text="Company Name *").grid(row=r, column=0, sticky="w")
        self.ent_name = ttk.Entry(form, textvariable=self.var_name, width=46)
        self.ent_name.grid(row=r, column=1, sticky="ew", pady=4)
        r += 1

        ttk.Label(form, text="Website").grid(row=r, column=0, sticky="w")
        self.ent_website = ttk.Entry(form, textvariable=self.var_website, width=46)
        self.ent_website.grid(row=r, column=1, sticky="ew", pady=4)
        r += 1

        ttk.Label(form, text="Phone").grid(row=r, column=0, sticky="w")
        self.ent_phone = ttk.Entry(form, textvariable=self.var_phone, width=46)
        self.ent_phone.grid(row=r, column=1, sticky="ew", pady=4)
        r += 1

        ttk.Label(form, text="Days/Hours Available").grid(row=r, column=0, sticky="w")
        self.ent_hours = ttk.Entry(form, textvariable=self.var_hours, width=46)
        self.ent_hours.grid(row=r, column=1, sticky="ew", pady=4)
        r += 1

        ttk.Label(form, text="Services").grid(row=r, column=0, sticky="nw")
        self.txt_services = tk.Text(form, height=8, width=44, wrap="word")
        self.txt_services.grid(row=r, column=1, sticky="ew", pady=4)
        r += 1

        for c in range(2):
            form.columnconfigure(c, weight=1)

        # Buttons row
        btns = ttk.Frame(form)
        btns.grid(row=r, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        btns.columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.btn_new = ttk.Button(btns, text="New / Clear", command=self.clear_form)
        self.btn_save = ttk.Button(btns, text="Save", command=self.save_record)
        self.btn_update = ttk.Button(btns, text="Update", command=self.update_record, state="disabled")
        self.btn_delete = ttk.Button(btns, text="Delete", command=self.delete_record, state="disabled")
        self.btn_export = ttk.Button(btns, text="Export CSV", command=self.export_csv)

        self.btn_new.grid(row=0, column=0, sticky="ew", padx=3)
        self.btn_save.grid(row=0, column=1, sticky="ew", padx=3)
        self.btn_update.grid(row=0, column=2, sticky="ew", padx=3)
        self.btn_delete.grid(row=0, column=3, sticky="ew", padx=3)
        self.btn_export.grid(row=0, column=4, sticky="ew", padx=3)

        # RIGHT: table + search
        right = ttk.Frame(container)
        right.grid(row=0, column=1, sticky="nsew")

        search_row = ttk.Frame(right)
        search_row.pack(fill="x", pady=(0, 8))
        ttk.Label(search_row, text="Search:").pack(side="left")
        self.var_search = tk.StringVar()
        self.ent_search = ttk.Entry(search_row, textvariable=self.var_search)
        self.ent_search.pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(search_row, text="Go", command=self.refresh_table).pack(side="left")
        ttk.Button(search_row, text="Clear", command=self.clear_search).pack(side="left", padx=(6, 0))

        cols = ("name", "phone", "website", "hours", "services", "updated_at", "id")
        self.tree = ttk.Treeview(right, columns=cols, show="headings", height=18)
        self.tree.heading("name", text="Company Name")
        self.tree.heading("phone", text="Phone")
        self.tree.heading("website", text="Website")
        self.tree.heading("hours", text="Days/Hours")
        self.tree.heading("services", text="Services")
        self.tree.heading("updated_at", text="Updated")
        self.tree.heading("id", text="ID")

        self.tree.column("name", width=220, anchor="w")
        self.tree.column("phone", width=120, anchor="center")
        self.tree.column("website", width=200, anchor="w")
        self.tree.column("hours", width=160, anchor="w")
        self.tree.column("services", width=260, anchor="w")
        self.tree.column("updated_at", width=130, anchor="center")
        self.tree.column("id", width=60, anchor="center")

        vsb = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="left", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Enter to search convenience
        self.ent_search.bind("<Return>", lambda e: self.refresh_table())

    def clear_search(self):
        self.var_search.set("")
        self.refresh_table()

    def get_services_text(self) -> str:
        return self.txt_services.get("1.0", "end-1c").strip()

    def set_services_text(self, text: str):
        self.txt_services.delete("1.0", "end")
        self.txt_services.insert("1.0", text or "")

    def clear_form(self):
        self.selected_id = None
        self.var_name.set("")
        self.var_website.set("")
        self.var_phone.set("")
        self.var_hours.set("")
        self.set_services_text("")
        self.btn_update.config(state="disabled")
        self.btn_delete.config(state="disabled")
        self.btn_save.config(state="normal")
        self.ent_name.focus_set()
        self.tree.selection_remove(self.tree.selection())

    def validate_form(self) -> bool:
        if not self.var_name.get().strip():
            messagebox.showwarning("Missing Name", "Company Name is required.")
            self.ent_name.focus_set()
            return False
        return True

    def save_record(self):
        if not self.validate_form():
            return
        name = self.var_name.get().strip()
        website = self.var_website.get().strip()
        phone = normalize_phone(self.var_phone.get().strip())
        hours = self.var_hours.get().strip()
        services = self.get_services_text()

        with get_conn() as conn:
            conn.execute(
                """INSERT INTO orgs(name, website, phone, hours, services, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (name, website, phone, hours, services, datetime.utcnow().isoformat(timespec="seconds"),
                 datetime.utcnow().isoformat(timespec="seconds"))
            )
        self.clear_form()
        self.refresh_table()
        messagebox.showinfo("Saved", "Organization saved.")

    def update_record(self):
        if self.selected_id is None:
            messagebox.showwarning("No selection", "Select a record to update.")
            return
        if not self.validate_form():
            return
        oid = self.selected_id
        name = self.var_name.get().strip()
        website = self.var_website.get().strip()
        phone = normalize_phone(self.var_phone.get().strip())
        hours = self.var_hours.get().strip()
        services = self.get_services_text()

        with get_conn() as conn:
            conn.execute(
                """UPDATE orgs
                   SET name=?, website=?, phone=?, hours=?, services=?, updated_at=?
                   WHERE id=?""",
                (name, website, phone, hours, services, datetime.utcnow().isoformat(timespec="seconds"), oid)
            )
        self.refresh_table()
        messagebox.showinfo("Updated", "Organization updated.")

    def delete_record(self):
        if self.selected_id is None:
            messagebox.showwarning("No selection", "Select a record to delete.")
            return
        if messagebox.askyesno("Confirm Delete", "Delete the selected organization? This cannot be undone."):
            with get_conn() as conn:
                conn.execute("DELETE FROM orgs WHERE id=?", (self.selected_id,))
            self.clear_form()
            self.refresh_table()
            messagebox.showinfo("Deleted", "Organization deleted.")

    def on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        item_id = sel[0]
        values = self.tree.item(item_id, "values")
        # values order matches columns tuple
        name, phone, website, hours, services, updated_at, oid = values
        self.selected_id = int(oid)
        self.var_name.set(name)
        self.var_website.set(website)
        self.var_phone.set(phone)
        self.var_hours.set(hours)
        self.set_services_text(services)

        self.btn_update.config(state="normal")
        self.btn_delete.config(state="normal")
        self.btn_save.config(state="disabled")

    def refresh_table(self):
        query = self.var_search.get().strip()
        for row in self.tree.get_children():
            self.tree.delete(row)

        with get_conn() as conn:
            if query:
                like = f"%{query}%"
                cur = conn.execute(
                    """SELECT name, phone, website, hours, services, updated_at, id
                       FROM orgs
                       WHERE name LIKE ? OR website LIKE ? OR phone LIKE ? OR hours LIKE ? OR services LIKE ?
                       ORDER BY updated_at DESC""",
                    (like, like, like, like, like)
                )
            else:
                cur = conn.execute(
                    """SELECT name, phone, website, hours, services, updated_at, id
                       FROM orgs
                       ORDER BY updated_at DESC"""
                )
            for row in cur.fetchall():
                self.tree.insert("", "end", values=row)

    def export_csv(self):
        with get_conn() as conn:
            cur = conn.execute(
                "SELECT id, name, website, phone, hours, services, created_at, updated_at FROM orgs ORDER BY id ASC"
            )
            rows = cur.fetchall()
        if not rows:
            messagebox.showinfo("No data", "There are no records to export.")
            return

        default_name = f"organizations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=default_name,
            title="Save CSV"
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "name", "website", "phone", "hours", "services", "created_at", "updated_at"])
                for r in rows:
                    writer.writerow(r)
            messagebox.showinfo("Exported", f"Exported {len(rows)} records to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export failed", f"Could not write file:\n{e}")

if __name__ == "__main__":
    init_db()
    app = OrgApp()
    app.mainloop()
