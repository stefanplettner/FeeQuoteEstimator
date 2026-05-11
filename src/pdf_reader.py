from dataclasses import dataclass, field
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError as exc:
    raise ImportError("PyMuPDF is required: pip install pymupdf") from exc


@dataclass
class PageText:
    page_number: int  # 1-based
    text: str


@dataclass
class PDFDocument:
    path: Path
    pages: list[PageText] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        return "\n\n".join(
            f"--- Page {p.page_number} ---\n{p.text}" for p in self.pages
        )

    @property
    def page_count(self) -> int:
        return len(self.pages)


def read(pdf_path: str | Path) -> PDFDocument:
    """Extract text from every page of a PDF and return a PDFDocument."""
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a .pdf file, got: {path.suffix}")

    doc = PDFDocument(path=path)

    with fitz.open(str(path)) as pdf:
        for i, page in enumerate(pdf, start=1):
            text = page.get_text("text")
            doc.pages.append(PageText(page_number=i, text=text.strip()))

    return doc


def read_chunked(pdf_path: str | Path, pages_per_chunk: int = 10) -> list[str]:
    """
    Return the PDF text split into chunks of N pages each.
    Useful for long returns that exceed a single LLM context window.
    """
    doc = read(pdf_path)
    chunks = []
    for start in range(0, doc.page_count, pages_per_chunk):
        chunk_pages = doc.pages[start : start + pages_per_chunk]
        chunk_text = "\n\n".join(
            f"--- Page {p.page_number} ---\n{p.text}" for p in chunk_pages
        )
        chunks.append(chunk_text)
    return chunks
