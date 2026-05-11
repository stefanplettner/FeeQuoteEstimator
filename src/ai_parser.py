"""
Claude API parser for Form 1120 PDFs.

Sends extracted PDF text to claude-opus-4-7 and gets back a structured list
of every form and filing requirement detected in the return.
"""
import json
import ssl
from dataclasses import dataclass, field
from typing import Callable

import anthropic
import httpx

try:
    import truststore
    _TRUST_CTX = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
except Exception:
    _TRUST_CTX = None  # fall back to default cert bundle

from src.pdf_reader import PDFDocument


def _make_http_client() -> httpx.Client:
    """Return an httpx client that trusts the Windows certificate store.

    Needed in corporate environments where a proxy (Zscaler etc.) performs
    SSL inspection using a company-issued CA certificate.
    """
    if _TRUST_CTX is not None:
        return httpx.Client(verify=_TRUST_CTX)
    return httpx.Client()

MODEL = "claude-opus-4-7"

# Cached system prompt — same for every 1120 call, so we mark it for caching.
_SYSTEM_PROMPT = """\
You are an expert U.S. tax professional specializing in corporate income tax returns \
(Form 1120). Your task is to read the text extracted from a completed Form 1120 PDF \
and identify every form, schedule, and state return that is ACTUALLY PRESENT in the \
document — not forms that are merely referenced in instructions or mentioned in passing.

RULES
1. Only list forms whose pages or data are actually included in this return.
2. State returns: list only state tax return forms with actual pages present \
(e.g. "CA Form 100", "NY CT-3"). Do NOT infer or guess state filings from \
apportionment schedules alone.
3. Consolidated groups: include Form 851, 1120-PC, 1120-L sub-returns only if \
they have pages present.
4. Be comprehensive — include every federal schedule attached to the base 1120.

CATEGORIES (use exactly one per form):
- core_1120          : Base Form 1120 pages 1-6 and standard schedules C/D/G/H/J/K/L/M-1/M-2/M-3
- federal_schedule   : Federal forms attached to the 1120 (4562, 4797, 5471, 5472, 8858, 8990-8993, 1118, etc.)
- state_return       : State tax returns with actual pages in this return
- consolidated_group : Consolidated group forms (851, 1122, 1120-PC, 1120-L)

OUTPUT: Return ONLY a valid JSON object matching this schema — no preamble, \
no markdown, no explanation outside the JSON:

{
  "forms": [
    {
      "form_code": "<short code, e.g. '5471', '1120-SCH-M3', 'CA-100'>",
      "form_name": "<full name, e.g. 'Form 5471', 'Schedule M-3', 'California Form 100'>",
      "description": "<one sentence: what this form covers>",
      "category": "<core_1120 | federal_schedule | state_return | consolidated_group>",
      "why_present": "<one sentence: what triggered this form in this specific return>",
      "state_code": "<two-letter code e.g. 'CA' — only for state_return, otherwise empty string>"
    }
  ],
  "warnings": ["<any concern about legibility, missing pages, or ambiguity>"]
}
"""

# JSON schema for output_config.format — guarantees parseable output
_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "forms": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "form_code":   {"type": "string"},
                    "form_name":   {"type": "string"},
                    "description": {"type": "string"},
                    "category":    {
                        "type": "string",
                        "enum": ["core_1120", "federal_schedule", "state_return", "consolidated_group"],
                    },
                    "why_present": {"type": "string"},
                    "state_code":  {"type": "string"},
                },
                "required": ["form_code", "form_name", "description", "category", "why_present", "state_code"],
                "additionalProperties": False,
            },
        },
        "warnings": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["forms", "warnings"],
    "additionalProperties": False,
}


@dataclass
class DetectedForm:
    form_code: str
    form_name: str
    description: str
    category: str
    why_present: str
    state_code: str = ""


@dataclass
class ParseResult:
    forms: list[DetectedForm] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    error: str = ""

    @property
    def success(self) -> bool:
        return not self.error


def parse(
    doc: PDFDocument,
    api_key: str,
    on_progress: Callable[[str], None] | None = None,
) -> ParseResult:
    """
    Analyze a Form 1120 PDFDocument with Claude and return every detected form.

    Args:
        doc:          PDFDocument produced by pdf_reader.read()
        api_key:      Anthropic API key
        on_progress:  Optional callback(message: str) for status updates
    """

    def progress(msg: str) -> None:
        if on_progress:
            on_progress(msg)

    client = anthropic.Anthropic(api_key=api_key, http_client=_make_http_client())

    progress(f"Preparing {doc.page_count}-page return for analysis…")

    # Build the user message with the extracted PDF text
    user_content = (
        f"Below is the full text extracted from a {doc.page_count}-page Form 1120 "
        f"corporate tax return PDF. Identify every form and filing requirement present.\n\n"
        f"{doc.full_text}"
    )

    progress("Sending to Claude for analysis (this may take 20–60 seconds)…")

    try:
        with client.messages.stream(
            model=MODEL,
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=[
                {
                    "type": "text",
                    "text": _SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},  # cache the system prompt
                }
            ],
            output_config={"format": {"type": "json_schema", "schema": _OUTPUT_SCHEMA}},
            messages=[{"role": "user", "content": user_content}],
        ) as stream:
            progress("Claude is reading the return…")
            final = stream.get_final_message()

    except anthropic.AuthenticationError:
        return ParseResult(error="Invalid API key. Please check your key in config.json.")
    except anthropic.RateLimitError:
        return ParseResult(error="API rate limit reached. Please wait a moment and try again.")
    except anthropic.BadRequestError as e:
        return ParseResult(error=f"API request error: {e.message}")
    except anthropic.APIConnectionError:
        return ParseResult(error="Network error — check your internet connection and try again.")
    except Exception as e:
        return ParseResult(error=f"Unexpected error: {e}")

    # Extract the JSON text from the first text block
    text_block = next((b for b in final.content if b.type == "text"), None)
    if not text_block:
        return ParseResult(error="Claude returned no text content.")

    progress("Parsing results…")
    try:
        data = json.loads(text_block.text)
    except json.JSONDecodeError as e:
        return ParseResult(error=f"Could not parse Claude's response as JSON: {e}")

    forms = [
        DetectedForm(
            form_code=f.get("form_code", ""),
            form_name=f.get("form_name", ""),
            description=f.get("description", ""),
            category=f.get("category", "federal_schedule"),
            why_present=f.get("why_present", ""),
            state_code=f.get("state_code", ""),
        )
        for f in data.get("forms", [])
    ]

    progress(f"Analysis complete — {len(forms)} forms identified.")
    return ParseResult(forms=forms, warnings=data.get("warnings", []))
