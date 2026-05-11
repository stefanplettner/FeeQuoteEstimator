"""Load, save, and look up per-form fees stored in fee_schedule.json."""
import json
from pathlib import Path

_PATH = Path("fee_schedule.json")


def load() -> dict[str, dict]:
    """Return {form_code: entry} indexed by code."""
    if not _PATH.exists():
        return {}
    with _PATH.open(encoding="utf-8") as f:
        raw = json.load(f)
    return {entry["code"]: entry for entry in raw.get("forms", [])}


def save(by_code: dict[str, dict]) -> None:
    """Write the fee schedule back to fee_schedule.json."""
    data = {"forms": list(by_code.values())}
    with _PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_fee(form_code: str) -> float:
    """Return the stored fee for a form code, or 0.0 if not found."""
    schedule = load()
    entry = schedule.get(form_code) or schedule.get(form_code.upper())
    return float(entry.get("fee", 0)) if entry else 0.0
