import json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.json"

_DEFAULTS = {
    "api_key": "",
    "firm_name": "",
    "firm_address": "",
    "firm_phone": "",
    "firm_email": "",
}


def load() -> dict:
    if not CONFIG_PATH.exists():
        _write(_DEFAULTS.copy())
        return _DEFAULTS.copy()
    with open(CONFIG_PATH) as f:
        data = json.load(f)
    # Merge in any new keys added since last run
    changed = False
    for k, v in _DEFAULTS.items():
        if k not in data:
            data[k] = v
            changed = True
    if changed:
        _write(data)
    return data


def save(data: dict) -> None:
    _write(data)


def _write(data: dict) -> None:
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=4)


def ensure_api_key(parent: tk.Tk | None = None) -> str:
    """Return a valid API key, prompting the user if one is not configured."""
    cfg = load()
    if cfg.get("api_key", "").strip():
        return cfg["api_key"].strip()

    key = _prompt_api_key(parent)
    if not key:
        raise RuntimeError("No API key provided. Application cannot start.")
    cfg["api_key"] = key
    if not cfg.get("firm_name"):
        cfg["firm_name"] = _prompt_firm_name(parent)
    save(cfg)
    return key


def _prompt_api_key(parent) -> str:
    dlg = _Dialog(parent, title="API Key Setup", fields=[
        ("Anthropic API Key", "api_key", True),
    ])
    return dlg.result.get("api_key", "").strip() if dlg.result else ""


def _prompt_firm_name(parent) -> str:
    dlg = _Dialog(parent, title="Firm Setup", fields=[
        ("Firm Name", "firm_name", False),
    ])
    return dlg.result.get("firm_name", "").strip() if dlg.result else ""


class _Dialog(tk.Toplevel):
    """Generic modal dialog for collecting one or more text fields."""

    def __init__(self, parent, title: str, fields: list[tuple[str, str, bool]]):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result: dict | None = None
        self._entries: dict[str, tk.Entry] = {}

        self.grab_set()

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Please complete the following to continue:",
            wraplength=340,
        ).grid(row=0, column=0, columnspan=2, pady=(0, 12), sticky="w")

        for i, (label, key, secret) in enumerate(fields, start=1):
            ttk.Label(frame, text=label + ":").grid(
                row=i, column=0, sticky="w", pady=4, padx=(0, 8)
            )
            show = "*" if secret else ""
            entry = ttk.Entry(frame, width=40, show=show)
            entry.grid(row=i, column=1, sticky="ew", pady=4)
            self._entries[key] = entry

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=len(fields) + 1, column=0, columnspan=2, pady=(16, 0))
        ttk.Button(btn_frame, text="Save", command=self._on_save).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Cancel", command=self._on_cancel).pack(side="left", padx=4)

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.wait_window()

    def _on_save(self):
        values = {k: e.get().strip() for k, e in self._entries.items()}
        if any(v == "" for v in values.values()):
            messagebox.showwarning("Required", "All fields are required.", parent=self)
            return
        self.result = values
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()
