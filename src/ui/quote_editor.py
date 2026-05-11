"""Editable quote table widget."""
import tkinter as tk
from tkinter import ttk, simpledialog

from src.quote import Quote, QuoteItem
from src.form_registry import CATEGORY_LABELS

_CATEGORY_ORDER = ["core_1120", "consolidated_group", "federal_schedule", "state_return"]


class QuoteEditor(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._quote: Quote | None = None
        self._iid_to_item: dict[str, QuoteItem] = {}
        self._edit_widget: tk.Widget | None = None
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Toolbar
        tb = ttk.Frame(self, padding=(0, 0, 0, 4))
        tb.grid(row=0, column=0, columnspan=2, sticky="ew")
        ttk.Button(tb, text="Add Form…", command=self._add_form).pack(side="left", padx=(0, 4))
        ttk.Button(tb, text="Remove Selected", command=self._remove_selected).pack(side="left")
        ttk.Label(tb, text="  Double-click Fee or Notes to edit • Click ✓ to toggle inclusion",
                  foreground="#888", font=("Segoe UI", 8)).pack(side="left", padx=12)

        # Treeview
        cols = ("included", "form", "name", "fee", "notes")
        self._tree = ttk.Treeview(self, columns=cols, show="headings", selectmode="browse")
        self._tree.heading("included", text="✓")
        self._tree.heading("form",     text="Form Code")
        self._tree.heading("name",     text="Form Name")
        self._tree.heading("fee",      text="Fee ($)")
        self._tree.heading("notes",    text="Notes")
        self._tree.column("included", width=32,  stretch=False, anchor="center")
        self._tree.column("form",     width=120, stretch=False)
        self._tree.column("name",     width=240)
        self._tree.column("fee",      width=90,  stretch=False, anchor="e")
        self._tree.column("notes",    width=260)

        vsb = ttk.Scrollbar(self, orient="vertical",   command=self._tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._tree.grid(row=1, column=0, sticky="nsew")
        vsb.grid(row=1, column=1, sticky="ns")
        hsb.grid(row=2, column=0, sticky="ew")

        # Footer: total
        footer = ttk.Frame(self, padding=(0, 8, 0, 0))
        footer.grid(row=3, column=0, columnspan=2, sticky="ew")
        ttk.Label(footer, text="Estimated Total:", font=("Segoe UI", 10)).pack(side="left")
        self._total_var = tk.StringVar(value="$0.00")
        ttk.Label(footer, textvariable=self._total_var,
                  font=("Segoe UI", 12, "bold"), foreground="#1a6e1a").pack(side="left", padx=8)

        self._tree.tag_configure("group", background="#e8eaf0", font=("Segoe UI", 9, "bold"))

        self._tree.bind("<Button-1>",       self._on_single_click)
        self._tree.bind("<Double-Button-1>", self._on_double_click)

    # ── Public API ────────────────────────────────────────────────────────────

    def load_quote(self, quote: Quote) -> None:
        self._quote = quote
        self._refresh_tree()

    def get_quote(self) -> Quote | None:
        if self._quote is None:
            return None
        self._sync_items()
        return self._quote

    # ── Tree management ───────────────────────────────────────────────────────

    def _refresh_tree(self) -> None:
        self._dismiss_edit()
        for row in self._tree.get_children():
            self._tree.delete(row)
        self._iid_to_item.clear()

        if self._quote is None:
            return

        by_cat: dict[str, list[QuoteItem]] = {c: [] for c in _CATEGORY_ORDER}
        for item in self._quote.items:
            bucket = item.category if item.category in by_cat else "federal_schedule"
            by_cat[bucket].append(item)

        counter = 0
        for cat in _CATEGORY_ORDER:
            items = by_cat[cat]
            if not items:
                continue
            label = CATEGORY_LABELS.get(cat, cat)
            group = self._tree.insert("", "end", values=(label, "", "", "", ""),
                                      tags=("group",), open=True)
            for qi in items:
                iid = f"qi_{counter}_{qi.form_code}"
                counter += 1
                self._iid_to_item[iid] = qi
                check = "✓" if qi.included else ""
                fee_str = f"{qi.fee:.2f}"
                self._tree.insert(group, "end", iid=iid,
                                  values=(check, qi.form_code, qi.form_name, fee_str, qi.notes),
                                  tags=("item",))
        self._update_total()

    def _sync_items(self) -> None:
        """Write tree values back into the QuoteItem objects."""
        for iid, qi in self._iid_to_item.items():
            if not self._tree.exists(iid):
                continue
            vals = self._tree.item(iid, "values")
            qi.included = (vals[0] == "✓")
            try:
                qi.fee = float(vals[3])
            except ValueError:
                qi.fee = 0.0
            qi.notes = str(vals[4])

    def _update_total(self) -> None:
        total = 0.0
        for iid, qi in self._iid_to_item.items():
            if not self._tree.exists(iid):
                continue
            vals = self._tree.item(iid, "values")
            if vals[0] == "✓":
                try:
                    total += float(vals[3])
                except (ValueError, IndexError):
                    pass
        self._total_var.set(f"${total:,.2f}")

    # ── Event handlers ────────────────────────────────────────────────────────

    def _on_single_click(self, event: tk.Event) -> None:
        self._dismiss_edit()
        if self._tree.identify_region(event.x, event.y) != "cell":
            return
        if self._tree.identify_column(event.x) != "#1":
            return
        iid = self._tree.identify_row(event.y)
        if not iid or "group" in self._tree.item(iid, "tags"):
            return
        vals = list(self._tree.item(iid, "values"))
        vals[0] = "" if vals[0] == "✓" else "✓"
        self._tree.item(iid, values=vals)
        self._update_total()

    def _on_double_click(self, event: tk.Event) -> None:
        self._dismiss_edit()
        if self._tree.identify_region(event.x, event.y) != "cell":
            return
        col = self._tree.identify_column(event.x)
        iid = self._tree.identify_row(event.y)
        if not iid or "group" in self._tree.item(iid, "tags"):
            return
        if col not in ("#4", "#5"):  # fee and notes only
            return
        bbox = self._tree.bbox(iid, col)
        if not bbox:
            return
        x, y, w, h = bbox
        col_idx = int(col[1:]) - 1
        current = str(self._tree.item(iid, "values")[col_idx])

        entry = ttk.Entry(self._tree)
        entry.place(x=x, y=y, width=w, height=h)
        entry.insert(0, current)
        entry.select_range(0, tk.END)
        entry.focus_set()
        self._edit_widget = entry

        def commit(e=None):
            new_val = entry.get()
            if col == "#4":
                try:
                    new_val = f"{float(new_val):.2f}"
                except ValueError:
                    new_val = current
            vals = list(self._tree.item(iid, "values"))
            vals[col_idx] = new_val
            self._tree.item(iid, values=vals)
            self._dismiss_edit()
            self._update_total()

        entry.bind("<Return>",   commit)
        entry.bind("<Tab>",      commit)
        entry.bind("<FocusOut>", commit)
        entry.bind("<Escape>",   lambda e: self._dismiss_edit())

    def _dismiss_edit(self) -> None:
        if self._edit_widget and self._edit_widget.winfo_exists():
            self._edit_widget.destroy()
        self._edit_widget = None

    # ── Add / Remove ──────────────────────────────────────────────────────────

    def _add_form(self) -> None:
        code = simpledialog.askstring("Add Form", "Form code (e.g. '4562'):", parent=self)
        if not code:
            return
        code = code.strip()
        name = simpledialog.askstring("Add Form", f"Description for {code}:", parent=self)
        if name is None:
            return
        name = name.strip() or code
        fee_str = simpledialog.askstring("Add Form", "Fee ($):", parent=self, initialvalue="0")
        try:
            fee = float(fee_str or "0")
        except ValueError:
            fee = 0.0

        new_item = QuoteItem(
            form_code=code, form_name=name, category="federal_schedule",
            fee=fee, notes="", included=True,
        )
        if self._quote:
            self._quote.items.append(new_item)
        self._refresh_tree()

    def _remove_selected(self) -> None:
        sel = self._tree.selection()
        if not sel:
            return
        iid = sel[0]
        if "group" in self._tree.item(iid, "tags"):
            return
        qi = self._iid_to_item.pop(iid, None)
        if qi and self._quote:
            self._quote.items = [i for i in self._quote.items if i is not qi]
        self._tree.delete(iid)
        self._update_total()
