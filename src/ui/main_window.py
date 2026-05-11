import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path

from src.pdf_reader import read as read_pdf
from src.ai_parser import parse as ai_parse, ParseResult
from src.form_registry import CATEGORY_LABELS
from src import fee_schedule as fs
from src.quote import Quote, QuoteItem, list_quotes
from src.ui.quote_editor import QuoteEditor
from src.ui.fee_schedule_editor import FeeScheduleDialog
from src.exporter import export_pdf, export_excel


class MainWindow:
    def __init__(self, root: tk.Tk, config: dict):
        self._root = root
        self._config = config
        self._pdf_path: Path | None = None
        self._doc = None
        self._current_quote: Quote | None = None
        self._setup_window()
        self._build_ui()

    def _setup_window(self):
        firm = self._config.get("firm_name") or "Fee Quote Estimator"
        self._root.title(firm)
        self._root.geometry("980x660")
        self._root.resizable(True, True)
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(1, weight=1)

    def _build_ui(self):
        # ── Toolbar ───────────────────────────────────────────────────
        toolbar = ttk.Frame(self._root, padding=(8, 6))
        toolbar.grid(row=0, column=0, sticky="ew")

        ttk.Button(toolbar, text="Open PDF…", command=self._open_pdf).pack(side="left", padx=(0, 4))
        self._analyze_btn = ttk.Button(
            toolbar, text="Analyze Return", command=self._run_analysis, state="disabled"
        )
        self._analyze_btn.pack(side="left", padx=(0, 6))

        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=4, pady=2)

        ttk.Button(toolbar, text="Open Quote…", command=self._open_quote).pack(side="left", padx=(6, 4))
        self._save_quote_btn = ttk.Button(
            toolbar, text="Save Quote", command=self._save_quote, state="disabled"
        )
        self._save_quote_btn.pack(side="left", padx=(0, 6))

        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=4, pady=2)

        ttk.Button(toolbar, text="Fee Schedule…", command=self._open_fee_schedule).pack(side="left", padx=6)

        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=4, pady=2)

        self._export_pdf_btn = ttk.Button(
            toolbar, text="Export PDF", command=self._export_pdf, state="disabled"
        )
        self._export_pdf_btn.pack(side="left", padx=(6, 4))
        self._export_xlsx_btn = ttk.Button(
            toolbar, text="Export Excel", command=self._export_excel, state="disabled"
        )
        self._export_xlsx_btn.pack(side="left", padx=(0, 6))

        firm_label = self._config.get("firm_name", "")
        if firm_label:
            ttk.Label(toolbar, text=firm_label, foreground="#555").pack(side="right")

        # ── Content area ──────────────────────────────────────────────
        content = ttk.Frame(self._root, padding=(12, 8))
        content.grid(row=1, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)

        self._status_var = tk.StringVar(value="Open a client 1120 PDF to begin.")
        ttk.Label(
            content,
            textvariable=self._status_var,
            foreground="#555",
            font=("Segoe UI", 10),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", pady=(0, 6))

        # Notebook with two tabs
        self._notebook = ttk.Notebook(content)
        self._notebook.grid(row=1, column=0, sticky="nsew")

        forms_tab = ttk.Frame(self._notebook, padding=4)
        self._notebook.add(forms_tab, text="Detected Forms")
        self._build_forms_tab(forms_tab)

        quote_tab = ttk.Frame(self._notebook, padding=4)
        self._notebook.add(quote_tab, text="Quote")
        self._quote_editor = QuoteEditor(quote_tab)
        self._quote_editor.pack(fill="both", expand=True)

        # ── Status bar ────────────────────────────────────────────────
        self._statusbar = ttk.Label(
            self._root, text="Ready", relief="sunken", anchor="w", padding=(4, 2)
        )
        self._statusbar.grid(row=2, column=0, sticky="ew")

    def _build_forms_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        cols = ("form", "name", "category", "why")
        self._tree = ttk.Treeview(parent, columns=cols, show="headings", selectmode="browse")
        self._tree.heading("form",     text="Form Code")
        self._tree.heading("name",     text="Form Name")
        self._tree.heading("category", text="Category")
        self._tree.heading("why",      text="Why Present")
        self._tree.column("form",     width=110, stretch=False)
        self._tree.column("name",     width=220)
        self._tree.column("category", width=160, stretch=False)
        self._tree.column("why",      width=340)

        vsb = ttk.Scrollbar(parent, orient="vertical",   command=self._tree.yview)
        hsb = ttk.Scrollbar(parent, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self._tree.tag_configure("group", background="#e8eaf0", font=("Segoe UI", 9, "bold"))

    # ── PDF loading ───────────────────────────────────────────────────────────

    def _open_pdf(self):
        path = filedialog.askopenfilename(
            title="Select Form 1120 PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if not path:
            return

        self._set_status(f"Reading {Path(path).name}…")
        self._root.update_idletasks()

        try:
            self._doc = read_pdf(path)
        except Exception as e:
            messagebox.showerror("PDF Error", str(e))
            self._set_status("Open a client 1120 PDF to begin.")
            return

        self._pdf_path = Path(path)
        self._status_var.set(
            f"Loaded: {self._pdf_path.name}  ({self._doc.page_count} pages) — "
            "click Analyze Return to identify forms."
        )
        self._analyze_btn.config(state="normal")
        self._clear_tree()

    # ── Analysis ──────────────────────────────────────────────────────────────

    def _run_analysis(self):
        self._analyze_btn.config(state="disabled")
        self._clear_tree()
        self._set_status("Starting analysis…")

        api_key = self._config.get("api_key", "")
        doc = self._doc

        def worker():
            result = ai_parse(doc, api_key, on_progress=self._thread_status)
            self._root.after(0, lambda: self._on_analysis_done(result))

        threading.Thread(target=worker, daemon=True).start()

    def _thread_status(self, msg: str) -> None:
        self._root.after(0, lambda m=msg: self._set_status(m))

    def _on_analysis_done(self, result: ParseResult) -> None:
        self._analyze_btn.config(state="normal")

        if not result.success:
            messagebox.showerror("Analysis Error", result.error)
            self._set_status("Analysis failed. See error message.")
            return

        self._populate_tree(result)
        self._build_quote(result)

        summary = f"Found {len(result.forms)} forms"
        if result.warnings:
            summary += f"  |  {len(result.warnings)} warning(s)"
        self._status_var.set(summary)
        self._set_status("Analysis complete — review the Quote tab.")

        if result.warnings:
            messagebox.showwarning(
                "Parser Warnings",
                "\n".join(f"• {w}" for w in result.warnings),
            )

    # ── Quote building ────────────────────────────────────────────────────────

    def _build_quote(self, result: ParseResult) -> None:
        """Create a Quote from detected forms and load it into the editor."""
        schedule = fs.load()
        items = []
        for f in result.forms:
            entry = schedule.get(f.form_code, {})
            fee = float(entry.get("fee", 0)) if entry else 0.0
            items.append(QuoteItem(
                form_code=f.form_code,
                form_name=f.form_name,
                category=f.category,
                fee=fee,
                notes="",
                included=True,
            ))

        pdf_name = self._pdf_path.name if self._pdf_path else ""
        self._current_quote = Quote(client_name="", pdf_name=pdf_name, items=items)
        self._quote_editor.load_quote(self._current_quote)
        self._save_quote_btn.config(state="normal")
        self._export_pdf_btn.config(state="normal")
        self._export_xlsx_btn.config(state="normal")
        self._notebook.select(1)  # switch to Quote tab

    # ── Quote save / load ─────────────────────────────────────────────────────

    def _save_quote(self) -> None:
        quote = self._quote_editor.get_quote()
        if quote is None:
            return
        name = simpledialog.askstring(
            "Save Quote", "Client name:",
            parent=self._root,
            initialvalue=quote.client_name or "",
        )
        if not name:
            return
        quote.client_name = name.strip()
        path = quote.save()
        self._set_status(f"Quote saved: {path.name}")
        messagebox.showinfo("Saved", f"Quote saved:\n{path}")

    def _open_quote(self) -> None:
        quotes = list_quotes()
        init_dir = str(quotes[0].parent) if quotes else None
        kwargs = {"initialdir": init_dir} if init_dir else {}
        path = filedialog.askopenfilename(
            title="Open Saved Quote",
            filetypes=[("Quote files", "*.json"), ("All files", "*.*")],
            **kwargs,
        )
        if not path:
            return
        try:
            self._current_quote = Quote.load(Path(path))
        except Exception as e:
            messagebox.showerror("Load Error", str(e))
            return
        self._quote_editor.load_quote(self._current_quote)
        self._save_quote_btn.config(state="normal")
        self._export_pdf_btn.config(state="normal")
        self._export_xlsx_btn.config(state="normal")
        self._notebook.select(1)
        self._status_var.set(
            f"Loaded quote: {self._current_quote.client_name} ({self._current_quote.created})"
        )
        self._set_status("Quote loaded.")

    # ── Fee schedule ──────────────────────────────────────────────────────────

    def _open_fee_schedule(self) -> None:
        FeeScheduleDialog(self._root)

    # ── Export ────────────────────────────────────────────────────────────────

    def _export_pdf(self) -> None:
        quote = self._quote_editor.get_quote()
        if not quote:
            return
        default = f"{quote.client_name or 'quote'}_{quote.created}.pdf" if quote.client_name else "quote.pdf"
        path = filedialog.asksaveasfilename(
            title="Export PDF Quote",
            defaultextension=".pdf",
            initialfile=default,
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            export_pdf(quote, self._config, Path(path))
            self._set_status(f"PDF exported: {Path(path).name}")
            messagebox.showinfo("Exported", f"PDF saved:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def _export_excel(self) -> None:
        quote = self._quote_editor.get_quote()
        if not quote:
            return
        default = f"{quote.client_name or 'quote'}_{quote.created}.xlsx" if quote.client_name else "quote.xlsx"
        path = filedialog.asksaveasfilename(
            title="Export Excel Quote",
            defaultextension=".xlsx",
            initialfile=default,
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            export_excel(quote, self._config, Path(path))
            self._set_status(f"Excel exported: {Path(path).name}")
            messagebox.showinfo("Exported", f"Excel file saved:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    # ── Detected forms tree ───────────────────────────────────────────────────

    def _clear_tree(self):
        for row in self._tree.get_children():
            self._tree.delete(row)

    def _populate_tree(self, result: ParseResult) -> None:
        self._clear_tree()
        categories = ["core_1120", "consolidated_group", "federal_schedule", "state_return"]
        by_cat: dict[str, list] = {c: [] for c in categories}
        for f in result.forms:
            cat = f.category if f.category in by_cat else "federal_schedule"
            by_cat[cat].append(f)

        for cat in categories:
            forms = by_cat[cat]
            if not forms:
                continue
            label = CATEGORY_LABELS.get(cat, cat)
            group = self._tree.insert("", "end", text=label,
                                      values=(label, "", "", ""), open=True, tags=("group",))
            for f in forms:
                self._tree.insert(group, "end",
                                  values=(f.form_code, f.form_name, label, f.why_present))

    # ── Utility ───────────────────────────────────────────────────────────────

    def _set_status(self, msg: str) -> None:
        self._statusbar.config(text=msg)

    def run(self):
        self._root.mainloop()
