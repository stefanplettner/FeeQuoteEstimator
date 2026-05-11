"""Quote data model and persistence."""
import json
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

QUOTES_DIR = Path("quotes")


@dataclass
class QuoteItem:
    form_code: str
    form_name: str
    category: str
    fee: float
    notes: str = ""
    included: bool = True


@dataclass
class Quote:
    client_name: str
    pdf_name: str
    created: str = field(default_factory=lambda: date.today().isoformat())
    items: list[QuoteItem] = field(default_factory=list)

    @property
    def total(self) -> float:
        return sum(i.fee for i in self.items if i.included)

    def save(self) -> Path:
        QUOTES_DIR.mkdir(exist_ok=True)
        safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in self.client_name)
        path = QUOTES_DIR / f"{self.created}_{safe}.json"
        data = {
            "client_name": self.client_name,
            "pdf_name": self.pdf_name,
            "created": self.created,
            "items": [asdict(i) for i in self.items],
        }
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return path

    @classmethod
    def load(cls, path: Path) -> "Quote":
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        items = [QuoteItem(**i) for i in data.get("items", [])]
        return cls(
            client_name=data["client_name"],
            pdf_name=data.get("pdf_name", ""),
            created=data.get("created", ""),
            items=items,
        )


def list_quotes() -> list[Path]:
    """Return all saved quote files, newest first."""
    if not QUOTES_DIR.exists():
        return []
    return sorted(QUOTES_DIR.glob("*.json"), reverse=True)
