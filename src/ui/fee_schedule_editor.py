"""Modal dialog to edit per-form fees stored in fee_schedule.json."""
import tkinter as tk
from tkinter import ttk, messagebox

from src import fee_schedule as fs
from src.form_registry import CATEGORY_LABELS

_CATEGORY_ORDER = ["core_1120", "federal_schedule", "consolidated_group", "state_return"]


class FeeScheduleDialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc):
        super().__init__(parent)
        self.title("Fee Schedule Settings")
        self.geometry("700x520")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        self._entries: dict[str, tk.StringVar] = {}
        self._schedule = fs.load()
        self._build()
        self.wait_window(self)

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Scrollable canvas
        container = ttk.Frame(self)
        container.grid(row=0, column=0, sticky="nsew", padx=12, pady=(12, 4))
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        canvas = tk.Canvas(container, borderwidth=0, highlightthickness=0)
        vsb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        container.columnconfigure(0, weight=1)

        inner = ttk.Frame(canvas, padding=(4, 0))
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
        def _on_mousewheel(e):
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1 * e.delta / 120), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        # Remove the global binding when this dialog closes so it doesn't
        # fire against the destroyed canvas after the window is gone.
        self.bind("<Destroy>", lambda e: self.unbind_all("<MouseWheel>") if e.widget is self else None)

        # Column headers
        inner.columnconfigure(1, weight=1)
        ttk.Label(inner, text="Code",        font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=2)
        ttk.Label(inner, text="Description", font=("Segoe UI", 9, "bold")).grid(row=0, column=1, sticky="w", padx=(0, 8), pady=2)
        ttk.Label(inner, text="Fee ($)",     font=("Segoe UI", 9, "bold")).grid(row=0, column=2, sticky="e", pady=2)
        ttk.Separator(inner, orient="horizontal").grid(row=1, column=0, columnspan=3, sticky="ew", pady=4)

        # Sort entries by category order
        def cat_key(kv):
            cat = kv[1].get("category", "")
            try:
                return _CATEGORY_ORDER.index(cat)
            except ValueError:
                return 99

        row = 2
        last_cat = None
        for code, entry in sorted(self._schedule.items(), key=cat_key):
            cat = entry.get("category", "")
            if cat != last_cat:
                label = CATEGORY_LABELS.get(cat, cat)
                ttk.Label(inner, text=label, font=("Segoe UI", 9, "bold"),
                          foreground="#444").grid(
                    row=row, column=0, columnspan=3, sticky="w",
                    pady=(10 if row > 2 else 0, 2))
                row += 1
                last_cat = cat

            ttk.Label(inner, text=code, width=14).grid(row=row, column=0, sticky="w", padx=(0, 8))
            desc = entry.get("description", "")
            if len(desc) > 65:
                desc = desc[:62] + "…"
            ttk.Label(inner, text=desc, anchor="w").grid(row=row, column=1, sticky="ew", padx=(0, 8))

            var = tk.StringVar(value=str(int(entry.get("fee", 0)) if float(entry.get("fee", 0)).is_integer()
                                         else entry.get("fee", 0)))
            self._entries[code] = var
            ttk.Entry(inner, textvariable=var, width=10, justify="right").grid(
                row=row, column=2, sticky="e", pady=1)
            row += 1

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=8)
        ttk.Label(btn_frame, text="Enter 0 to exclude a form from default pricing.",
                  foreground="#888", font=("Segoe UI", 8)).pack(side="left")
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right", padx=(4, 0))
        ttk.Button(btn_frame, text="Save", command=self._save).pack(side="right")

    def _save(self) -> None:
        for code, var in self._entries.items():
            try:
                self._schedule[code]["fee"] = float(var.get())
            except ValueError:
                messagebox.showerror("Invalid Fee",
                                     f"Fee for {code} must be a number.", parent=self)
                return
        fs.save(self._schedule)
        self.destroy()
