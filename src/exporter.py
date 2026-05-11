"""PDF and Excel export for fee quotes.

PDF uses reportlab; Excel uses openpyxl — both already in requirements.txt.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from src.quote import Quote, QuoteItem
from src.form_registry import CATEGORY_LABELS

_CATEGORY_ORDER = ["core_1120", "consolidated_group", "federal_schedule", "state_return"]


def _included_by_category(quote: Quote) -> dict[str, list[QuoteItem]]:
    by_cat: dict[str, list[QuoteItem]] = {c: [] for c in _CATEGORY_ORDER}
    for item in quote.items:
        if item.included:
            bucket = item.category if item.category in by_cat else "federal_schedule"
            by_cat[bucket].append(item)
    return by_cat


# ── PDF export ────────────────────────────────────────────────────────────────

def export_pdf(quote: Quote, config: dict, dest: Path) -> None:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
    )

    DARK   = colors.HexColor("#1a1a6e")
    LGREY  = colors.HexColor("#f4f4f4")
    LBLUE  = colors.HexColor("#e8eaf0")
    MGREY  = colors.HexColor("#cccccc")
    DGREY  = colors.HexColor("#555555")

    doc = SimpleDocTemplate(
        str(dest), pagesize=letter,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.75 * inch,  bottomMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()

    def style(name, base="Normal", **kw):
        return ParagraphStyle(name, parent=styles[base], **kw)

    firm_st   = style("Firm",  fontSize=16, fontName="Helvetica-Bold", spaceAfter=2)
    sub_st    = style("Sub",   fontSize=9,  textColor=DGREY, spaceAfter=0)
    title_st  = style("Title", fontSize=13, fontName="Helvetica-Bold",
                      spaceBefore=12, spaceAfter=4)
    meta_st   = style("Meta",  fontSize=9,  textColor=colors.HexColor("#444444"), spaceAfter=2)
    footer_st = style("Foot",  fontSize=8,  textColor=DGREY, spaceBefore=12)

    story = []

    # Firm header
    firm_name = config.get("firm_name") or "Fee Quote Estimator"
    story.append(Paragraph(firm_name, firm_st))
    sub_parts = [p for p in [
        config.get("firm_address", ""), config.get("firm_phone", ""), config.get("firm_email", ""),
    ] if p]
    if sub_parts:
        story.append(Paragraph("  •  ".join(sub_parts), sub_st))
    story.append(HRFlowable(width="100%", thickness=1, color=MGREY, spaceAfter=6))

    # Quote meta
    story.append(Paragraph("FEE QUOTE ESTIMATE", title_st))
    story.append(Paragraph(f"<b>Client:</b>  {quote.client_name or '—'}", meta_st))
    story.append(Paragraph(f"<b>Return:</b>  {quote.pdf_name or '—'}", meta_st))
    story.append(Paragraph(f"<b>Date:</b>    {quote.created or date.today().isoformat()}", meta_st))
    story.append(Spacer(1, 10))

    # Build table data + styles
    COL_W = [1.05 * inch, 3.4 * inch, 1.1 * inch]
    rows: list[list] = []
    cmds: list[tuple] = []
    r = 0

    rows.append(["Form Code", "Description", "Fee"])
    cmds += [
        ("BACKGROUND",    (0, r), (-1, r), DARK),
        ("TEXTCOLOR",     (0, r), (-1, r), colors.white),
        ("FONTNAME",      (0, r), (-1, r), "Helvetica-Bold"),
        ("FONTSIZE",      (0, r), (-1, r), 9),
        ("ALIGN",         (2, r), (2, r),  "RIGHT"),
        ("TOPPADDING",    (0, r), (-1, r), 5),
        ("BOTTOMPADDING", (0, r), (-1, r), 5),
    ]
    r += 1

    grand_total = 0.0
    by_cat = _included_by_category(quote)

    for cat in _CATEGORY_ORDER:
        items = by_cat[cat]
        if not items:
            continue

        label = CATEGORY_LABELS.get(cat, cat)
        rows.append([label, "", ""])
        cmds += [
            ("BACKGROUND",    (0, r), (-1, r), LBLUE),
            ("FONTNAME",      (0, r), (-1, r), "Helvetica-Bold"),
            ("FONTSIZE",      (0, r), (-1, r), 9),
            ("SPAN",          (0, r), (1, r)),
            ("TOPPADDING",    (0, r), (-1, r), 4),
            ("BOTTOMPADDING", (0, r), (-1, r), 4),
        ]
        r += 1

        subtotal = 0.0
        for qi in items:
            rows.append([qi.form_code, qi.form_name, f"${qi.fee:,.2f}"])
            cmds += [
                ("FONTSIZE",      (0, r), (-1, r), 9),
                ("ALIGN",         (2, r), (2, r),  "RIGHT"),
                ("TOPPADDING",    (0, r), (-1, r), 3),
                ("BOTTOMPADDING", (0, r), (-1, r), 3),
            ]
            subtotal    += qi.fee
            grand_total += qi.fee
            r += 1

        rows.append(["", "Subtotal", f"${subtotal:,.2f}"])
        cmds += [
            ("BACKGROUND",    (0, r), (-1, r), LGREY),
            ("FONTNAME",      (1, r), (-1, r), "Helvetica-Bold"),
            ("FONTSIZE",      (0, r), (-1, r), 9),
            ("ALIGN",         (2, r), (2, r),  "RIGHT"),
            ("TOPPADDING",    (0, r), (-1, r), 3),
            ("BOTTOMPADDING", (0, r), (-1, r), 3),
        ]
        r += 1

    rows.append(["", "TOTAL ESTIMATED FEE", f"${grand_total:,.2f}"])
    cmds += [
        ("BACKGROUND",    (0, r), (-1, r), DARK),
        ("TEXTCOLOR",     (0, r), (-1, r), colors.white),
        ("FONTNAME",      (0, r), (-1, r), "Helvetica-Bold"),
        ("FONTSIZE",      (0, r), (-1, r), 10),
        ("ALIGN",         (2, r), (2, r),  "RIGHT"),
        ("TOPPADDING",    (0, r), (-1, r), 6),
        ("BOTTOMPADDING", (0, r), (-1, r), 6),
    ]

    cmds += [
        ("GRID",          (0, 0), (-1, -1), 0.25, MGREY),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
    ]

    table = Table(rows, colWidths=COL_W, repeatRows=1)
    table.setStyle(TableStyle(cmds))
    story.append(table)

    story.append(Paragraph(
        "This estimate is based on forms identified in the provided return. "
        "Actual fees may vary depending on complexity and additional information required.",
        footer_st,
    ))
    doc.build(story)


# ── Excel export ──────────────────────────────────────────────────────────────

def export_excel(quote: Quote, config: dict, dest: Path) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    DARK_HEX  = "1A1A6E"
    LBLUE_HEX = "E8EAF0"
    LGREY_HEX = "F4F4F4"
    WHITE_HEX = "FFFFFF"

    def _side(color="CCCCCC"):
        return Side(style="thin", color=color)

    def _border():
        s = _side()
        return Border(left=s, right=s, top=s, bottom=s)

    def _fill(hex_color: str) -> PatternFill:
        return PatternFill("solid", fgColor=hex_color)

    def _font(bold=False, size=10, color="000000"):
        return Font(name="Calibri", size=size, bold=bold, color=color)

    wb = Workbook()
    ws = wb.active
    ws.title = "Fee Quote"

    ws.column_dimensions["A"].width = 16
    ws.column_dimensions["B"].width = 44
    ws.column_dimensions["C"].width = 28
    ws.column_dimensions["D"].width = 14
    ws.column_dimensions["E"].width = 32

    r = 1

    # Firm name
    ws.merge_cells(f"A{r}:E{r}")
    c = ws[f"A{r}"]
    c.value = config.get("firm_name") or "Fee Quote Estimator"
    c.font  = _font(bold=True, size=16, color=DARK_HEX)
    r += 1

    sub_parts = [p for p in [
        config.get("firm_address", ""), config.get("firm_phone", ""), config.get("firm_email", ""),
    ] if p]
    if sub_parts:
        ws.merge_cells(f"A{r}:E{r}")
        ws[f"A{r}"].value = "  •  ".join(sub_parts)
        ws[f"A{r}"].font  = _font(size=9, color="666666")
        r += 1

    r += 1  # blank row

    # Title
    ws.merge_cells(f"A{r}:E{r}")
    c = ws[f"A{r}"]
    c.value = "FEE QUOTE ESTIMATE"
    c.font  = _font(bold=True, size=13, color=DARK_HEX)
    r += 1

    for label, value in [
        ("Client:", quote.client_name or "—"),
        ("Return:", quote.pdf_name or "—"),
        ("Date:",   quote.created or date.today().isoformat()),
    ]:
        ws.cell(r, 1, label).font = _font(bold=True)
        ws.cell(r, 2, value).font = _font()
        r += 1

    r += 1  # blank row

    # Table header
    header_row = r
    for col, h in enumerate(["Form Code", "Form Name", "Category", "Fee", "Notes"], 1):
        c = ws.cell(r, col, h)
        c.font      = _font(bold=True, size=10, color=WHITE_HEX)
        c.fill      = _fill(DARK_HEX)
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border    = _border()
    ws.row_dimensions[r].height = 18
    r += 1

    by_cat      = _included_by_category(quote)
    grand_total = 0.0

    for cat in _CATEGORY_ORDER:
        items = by_cat[cat]
        if not items:
            continue

        # Category header
        label = CATEGORY_LABELS.get(cat, cat)
        ws.merge_cells(f"A{r}:E{r}")
        c = ws[f"A{r}"]
        c.value     = label
        c.font      = _font(bold=True, size=10, color=DARK_HEX)
        c.fill      = _fill(LBLUE_HEX)
        c.alignment = Alignment(vertical="center")
        c.border    = _border()
        # apply fill/border to merged cells
        for col in range(2, 6):
            mc = ws.cell(r, col)
            mc.fill   = _fill(LBLUE_HEX)
            mc.border = _border()
        ws.row_dimensions[r].height = 16
        r += 1

        subtotal = 0.0
        for qi in items:
            cat_label = CATEGORY_LABELS.get(qi.category, qi.category)
            for col, val in enumerate([qi.form_code, qi.form_name, cat_label, qi.fee, qi.notes], 1):
                c = ws.cell(r, col, val)
                c.font   = _font(size=9)
                c.border = _border()
                c.alignment = Alignment(
                    vertical="center",
                    horizontal="right" if col == 4 else "left",
                )
                if col == 4:
                    c.number_format = '"$"#,##0.00'
            ws.row_dimensions[r].height = 15
            subtotal    += qi.fee
            grand_total += qi.fee
            r += 1

        # Subtotal row
        for col in range(1, 6):
            c = ws.cell(r, col)
            c.fill   = _fill(LGREY_HEX)
            c.border = _border()
            c.font   = _font(size=9)
        ws.cell(r, 3).value     = "Subtotal"
        ws.cell(r, 3).font      = _font(bold=True, size=9)
        ws.cell(r, 3).alignment = Alignment(horizontal="right")
        ws.cell(r, 4).value         = subtotal
        ws.cell(r, 4).font          = _font(bold=True, size=9)
        ws.cell(r, 4).number_format = '"$"#,##0.00'
        ws.cell(r, 4).alignment     = Alignment(horizontal="right")
        ws.row_dimensions[r].height = 15
        r += 1

    r += 1  # blank row before total

    # Grand total row
    for col in range(1, 6):
        c = ws.cell(r, col)
        c.fill   = _fill(DARK_HEX)
        c.border = _border()
        c.font   = _font(bold=True, size=11, color=WHITE_HEX)
    ws.cell(r, 3).value     = "TOTAL ESTIMATED FEE"
    ws.cell(r, 3).alignment = Alignment(horizontal="right")
    ws.cell(r, 4).value         = grand_total
    ws.cell(r, 4).number_format = '"$"#,##0.00'
    ws.cell(r, 4).alignment     = Alignment(horizontal="right")
    ws.row_dimensions[r].height = 22

    ws.freeze_panes = ws.cell(row=header_row + 1, column=1)

    wb.save(str(dest))
