"""Generate 25 fictitious C-corp trial balances (2024, 2025) + GoSystem mappings.

Run:  python build.py      (deterministic; SEED below)
"""
import csv
import random
import re
import shutil
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from catalog import ACCOUNTS, BS_CLASSES
from companies import COMPANIES, SOFTWARE
from engine import Company
from gosystem_map import MAP, TCC_DESC, TRC_DESC, TRC_LINE, trc_confidence
from writers import assign_numbers, write_rows

SEED = 20241231
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "companies"
CLASS_LABEL = {"A": "Asset", "CA": "Contra-asset", "L": "Liability", "E": "Equity", "ED": "Equity (debit)",
               "R": "Revenue", "CR": "Contra-revenue", "C": "Cost of goods sold", "X": "Expense",
               "O": "Other income", "OX": "Other expense", "T": "Income tax expense"}
HDR = Font(bold=True, color="FFFFFF")
HFILL = PatternFill("solid", fgColor="1F3864")
MONEY = '#,##0.00;(#,##0.00);"-"'


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower().replace("&", "and")).strip("-")


def synth_prior(co):
    """Synthesize 12/31/2023 balance-sheet balances so 2024 opening columns tie."""
    r = co.rng_fmt
    prior = {}
    for k, v in co.bal[2024].items():
        if ACCOUNTS[k][1] in BS_CLASSES and k not in ("cash_operating", "dividends"):
            prior[k] = v if k in ("retained_earnings", "common_stock", "land", "goodwill") else int(v * r.uniform(0.86, 1.08))
    prior["cash_operating"] = -sum(prior.values())
    if prior["cash_operating"] < 0:  # keep cash positive: larger opening payables
        draw = -prior["cash_operating"] + 5_000_000
        prior["ap"] = prior.get("ap", 0) - draw
        prior["cash_operating"] += draw
    assert sum(prior.values()) == 0
    return prior


def style_header(ws, row, ncol):
    for c in range(1, ncol + 1):
        cell = ws.cell(row=row, column=c)
        cell.font, cell.fill = HDR, HFILL
        cell.alignment = Alignment(wrap_text=True, vertical="center")


def mapping_workbook(co, nums, path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Mapping"
    ws.append([f"{co.name}  |  EIN {co.ein}  |  Source: {co.software}  |  GoSystem Tax RS Form 1120 trial balance mapping"])
    ws["A1"].font = Font(bold=True, size=12)
    cols = ["Account No.", "Account Name", "Class", "12/31/2024 Debit", "12/31/2024 Credit", "12/31/2025 Debit",
            "12/31/2025 Credit", "2024 Net (Dr+/Cr-)", "2025 Net (Dr+/Cr-)", "TRC", "TRC Description", "TCC",
            "TCC Description (firm-defined)", "MRC (M-3)", "Form 1120 Line", "TRC Source Confidence", "Tax Review Notes"]
    ws.append(cols)
    style_header(ws, 2, len(cols))
    first = 3
    for k in co.keys():
        trc, tcc, mrc, note = MAP[k]
        b24, b25 = co.bal[2024].get(k, 0) / 100, co.bal[2025].get(k, 0) / 100
        row = ws.max_row + 1
        ws.append([nums[k] or "", co.account_name(k), CLASS_LABEL[ACCOUNTS[k][1]],
                   b24 if b24 > 0 else None, -b24 if b24 < 0 else None, b25 if b25 > 0 else None, -b25 if b25 < 0 else None,
                   f"=N(D{row})-N(E{row})", f"=N(F{row})-N(G{row})", trc, TRC_DESC[trc], tcc, TCC_DESC.get(tcc, ""),
                   mrc, TRC_LINE[trc], trc_confidence(trc), note])
    last = ws.max_row
    tot = last + 1
    ws.append(["", "TOTAL", ""] + [f"=SUM({get_column_letter(c)}{first}:{get_column_letter(c)}{last})" for c in range(4, 10)])
    for c in range(1, 10):
        ws.cell(row=tot, column=c).font = Font(bold=True)
    for r in range(first, tot + 1):
        for c in range(4, 10):
            ws.cell(row=r, column=c).number_format = MONEY
    widths = [11, 42, 17, 15, 15, 15, 15, 16, 16, 8, 40, 6, 32, 9, 18, 20, 60]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "C3"

    # ---------------- rollup by TRC
    ru = wb.create_sheet("1120 Rollup by TRC")
    ru.append(["TRC", "Description", "Form 1120 Line", "2024 Net (Dr+/Cr-)", "2025 Net (Dr+/Cr-)"])
    style_header(ru, 1, 5)
    used = sorted({MAP[k][0] for k in co.keys()})
    for t in used:
        r = ru.max_row + 1
        ru.append([t, TRC_DESC[t], TRC_LINE[t], f"=SUMIF(Mapping!$J${first}:$J${last},A{r},Mapping!$H${first}:$H${last})",
                   f"=SUMIF(Mapping!$J${first}:$J${last},A{r},Mapping!$I${first}:$I${last})"])
    n = ru.max_row
    ru.append(["", "Net (must be zero)", "", f"=SUM(D2:D{n})", f"=SUM(E2:E{n})"])
    for r in range(2, ru.max_row + 1):
        for c in (4, 5):
            ru.cell(row=r, column=c).number_format = MONEY
    for i, w in enumerate([9, 52, 20, 18, 18], 1):
        ru.column_dimensions[get_column_letter(i)].width = w

    # ---------------- TCC detail (other deductions etc.)
    tc = wb.create_sheet("TCC Detail")
    tc.append(["TRC", "TCC", "TCC Description", "2024 Net (Dr+/Cr-)", "2025 Net (Dr+/Cr-)"])
    style_header(tc, 1, 5)
    pairs = sorted({(MAP[k][0], MAP[k][1]) for k in co.keys() if MAP[k][1]})
    for t, c in pairs:
        r = tc.max_row + 1
        tc.append([t, c, TCC_DESC[c],
                   f"=SUMIFS(Mapping!$H${first}:$H${last},Mapping!$J${first}:$J${last},A{r},Mapping!$L${first}:$L${last},B{r})",
                   f"=SUMIFS(Mapping!$I${first}:$I${last},Mapping!$J${first}:$J${last},A{r},Mapping!$L${first}:$L${last},B{r})"])
    for r in range(2, tc.max_row + 1):
        for c in (4, 5):
            tc.cell(row=r, column=c).number_format = MONEY
    for i, w in enumerate([9, 6, 40, 18, 18], 1):
        tc.column_dimensions[get_column_letter(i)].width = w

    # ---------------- GoSystem import layout
    gi = wb.create_sheet("GoSystem Import")
    gi.append(["Account Number", "Account Description", "TRC", "TCC", "Prior Year Balance", "Current Year Balance"])
    style_header(gi, 1, 6)
    for k in co.keys():
        gi.append([nums[k] or co.account_name(k)[:20].upper().replace(" ", ""), co.account_name(k), MAP[k][0], MAP[k][1],
                   co.bal[2024].get(k, 0) / 100, co.bal[2025].get(k, 0) / 100])
    for r in range(2, gi.max_row + 1):
        for c in (5, 6):
            gi.cell(row=r, column=c).number_format = MONEY
    for i, w in enumerate([16, 42, 8, 6, 18, 18], 1):
        gi.column_dimensions[get_column_letter(i)].width = w

    # ---------------- checks
    ck = wb.create_sheet("Checks")
    ck.append(["Check", "2024", "2025"])
    style_header(ck, 1, 3)
    ni = {y: round(co.net_income(y) / 100, 2) for y in (2024, 2025)}
    assets = {y: round(sum(v for k, v in co.bal[y].items() if ACCOUNTS[k][1] in ("A", "CA")) / 100, 2) for y in (2024, 2025)}
    receipts = {y: round(-sum(v for k, v in co.bal[y].items() if ACCOUNTS[k][1] in ("R", "CR", "O")) / 100, 2) for y in (2024, 2025)}
    div = {y: co.bal[y].get("dividends", 0) / 100 for y in (2024, 2025)}
    re_beg = {y: -co.bal[y]["retained_earnings"] / 100 for y in (2024, 2025)}
    rows = [
        ("Trial balance debits - credits (must be 0)", f"=Mapping!H{tot}", f"=Mapping!I{tot}"),
        ("Net income per books", ni[2024], ni[2025]),
        ("Total assets (Sch L L15)", assets[2024], assets[2025]),
        ("Retained earnings - beginning (per TB)", re_beg[2024], re_beg[2025]),
        ("Less: dividends / distributions", div[2024], div[2025]),
        ("Retained earnings - ending (beg + NI - div)", round(re_beg[2024] + ni[2024] - div[2024], 2), round(re_beg[2025] + ni[2025] - div[2025], 2)),
        ("Roll-forward: 2025 beginning RE = 2024 ending RE", "", "=IF(ROUND(C5-B7,2)=0,\"OK\",\"ERROR\")"),
        ("Schedule M-3 required (total assets >= $10M)", "Yes" if assets[2024] >= 10_000_000 else "No",
         "Yes" if assets[2025] >= 10_000_000 else "No"),
        ("Book gross receipts (approx., single year)", receipts[2024], receipts[2025]),
        ("Sec. 448(c) threshold ($30M 2024 / $31M 2025; test uses 3-yr average)", 30_000_000, 31_000_000),
        ("Over 448(c) on single-year receipts? (163(j), 263A, 471 review)", "Yes" if receipts[2024] > 30_000_000 else "No",
         "Yes" if receipts[2025] > 31_000_000 else "No"),
        ("Federal NOL carryforward at year end (simplified)", round(co.nol_hist[2024], 2), round(co.nol_hist[2025], 2)),
    ]
    for row in rows:
        ck.append(list(row))
    for r in range(2, ck.max_row + 1):
        for c in (2, 3):
            ck.cell(row=r, column=c).number_format = MONEY
    ck.column_dimensions["A"].width = 66
    aje_sheet(wb, co)
    ck.column_dimensions["B"].width = 18
    ck.column_dimensions["C"].width = 18
    wb.save(path)
    return ni, assets


def aje_sheet(wb, co):
    """Proposed tax-only adjustments a preparer would post in GoSystem."""
    ws = wb.create_sheet("Proposed Tax AJEs")
    ws.append(["Year", "AJE", "TRC", "Description", "Debit", "Credit", "Explanation"])
    style_header(ws, 1, 7)
    inv_keys = ("inventory", "inventory_raw", "inventory_wip", "inventory_fg")
    for y in (2024, 2025):
        bi = sum(co.bal[y - 1].get(k, 0) for k in inv_keys) / 100
        ei = sum(co.bal[y].get(k, 0) for k in inv_keys) / 100
        if bi or ei:
            n = f"{y}-1"
            ws.append([y, n, "40-110", "COGS - inventory at beginning of year", round(bi, 2), None,
                       "Form 1125-A tie: book COGS accounts are net of the inventory change but are mapped to purchases/labor/other."])
            ws.append([y, n, "40-190", "COGS - inventory at end of year", None, round(ei, 2),
                       "If your template already pulls 1125-A L1/L7 from Sch L 10-300, post only the 40-120 line."])
            chg = round(ei - bi, 2)
            ws.append([y, n, "40-120", "COGS - purchases (book COGS + EI - BI)", chg if chg > 0 else None,
                       -chg if chg < 0 else None, "Net effect on cost of goods sold = 0; 1125-A L8 then equals book COGS."])
        al0 = -co.bal[y - 1].get("allowance", 0) / 100
        al1 = -co.bal[y].get("allowance", 0) / 100
        if al0 or al1:
            chg = round(al1 - al0, 2)
            ws.append([y, f"{y}-M1", "Sch M-1", "Change in allowance for doubtful accounts (memo)", None, None,
                       f"{'Add back increase' if chg > 0 else 'Deduct decrease'} of {abs(chg):,.2f} (M-1 L5 / L8); Sec. 166 specific charge-off method."])
    for r in range(2, ws.max_row + 1):
        for c in (5, 6):
            ws.cell(row=r, column=c).number_format = MONEY
    for i, wd in enumerate([6, 9, 9, 42, 15, 15, 95], 1):
        ws.column_dimensions[get_column_letter(i)].width = wd


def main():
    rng = random.Random(SEED)
    pool = SOFTWARE * 4
    rng.shuffle(pool)
    assignment = pool[:25]
    for sw in SOFTWARE:  # guarantee every package appears at least once
        if sw not in assignment:
            counts = {s: assignment.count(s) for s in assignment}
            idx = max(range(25), key=lambda i: counts[assignment[i]])
            assignment[idx] = sw
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    index, long_rows = [], []
    for i, (cid, name, ind, st, rev, g, feats) in enumerate(COMPANIES):
        co = Company(cid, name, ind, st, rev, g, feats, assignment[i], seed=SEED + i)
        co.rng_fmt = random.Random(SEED * 7 + i)
        co.bal[2023] = synth_prior(co)
        co.qbo_numbers = co.rng_fmt.random() < 0.5
        nums = assign_numbers(co.keys(), co.software)
        if co.software == "QuickBooks Online" and not co.qbo_numbers:
            nums = {k: "" for k in nums}  # QBO default: account numbers turned off
        d = OUT / f"{cid}_{slug(name)}"
        d.mkdir()
        sw_slug = slug(co.software)
        for y in (2024, 2025):
            rows = write_rows(co, y, nums)
            with open(d / f"{cid}_TB_{y}_{sw_slug}.csv", "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
        ni, assets = mapping_workbook(co, nums, d / f"{cid}_GoSystem_TRC_TCC_Mapping.xlsx")
        del co.bal[2023]
        for k in co.keys():
            trc, tcc, mrc, note = MAP[k]
            long_rows.append([cid, name, co.software, nums[k], co.account_name(k), CLASS_LABEL[ACCOUNTS[k][1]],
                              f"{co.bal[2024].get(k, 0) / 100:.2f}", f"{co.bal[2025].get(k, 0) / 100:.2f}", trc, tcc, mrc, TRC_LINE[trc]])
        index.append(dict(cid=cid, name=name, ein=co.ein, state=st, industry=ind, naics=co.ind["naics"],
                          activity=co.ind["activity"], software=co.software, accounts=len(co.keys()),
                          rev24=sum(-v for k, v in co.bal[2024].items() if ACCOUNTS[k][1] in ("R", "CR")) / 100,
                          rev25=sum(-v for k, v in co.bal[2025].items() if ACCOUNTS[k][1] in ("R", "CR")) / 100,
                          ni24=ni[2024], ni25=ni[2025], ta24=assets[2024], ta25=assets[2025], folder=d.name))
    with open(ROOT / "all_accounts_mapped.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Company ID", "Company", "Source Software", "Account No.", "Account Name", "Class",
                    "2024 Net (Dr+/Cr-)", "2025 Net (Dr+/Cr-)", "TRC", "TCC", "MRC", "Form 1120 Line"])
        w.writerows(long_rows)
    write_index(index)
    return index


def write_index(index):
    wb = Workbook()
    ws = wb.active
    ws.title = "Companies"
    cols = ["ID", "Company (fictitious)", "EIN (fictitious)", "State", "Industry", "NAICS", "Business Activity",
            "TB Source Software", "# Accounts", "Net Revenue 2024", "Net Revenue 2025", "Net Income 2024",
            "Net Income 2025", "Total Assets 12/31/2024", "Total Assets 12/31/2025", "M-3 (2025)", "Folder"]
    ws.append(cols)
    style_header(ws, 1, len(cols))
    for c in index:
        ws.append([c["cid"], c["name"], c["ein"], c["state"], c["industry"], c["naics"], c["activity"], c["software"],
                   c["accounts"], c["rev24"], c["rev25"], c["ni24"], c["ni25"], c["ta24"], c["ta25"],
                   "Yes" if c["ta25"] >= 10_000_000 else "No", c["folder"]])
    for r in range(2, ws.max_row + 1):
        for col in range(10, 16):
            ws.cell(row=r, column=col).number_format = '#,##0;(#,##0)'
    for i, w in enumerate([5, 42, 12, 6, 18, 8, 46, 36, 10, 15, 15, 14, 14, 16, 16, 9, 48], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "C2"
    tr = wb.create_sheet("TRC Reference")
    tr.append(["TRC", "Description", "Form 1120 Line"])
    style_header(tr, 1, 3)
    for t in sorted(TRC_DESC):
        tr.append([t, TRC_DESC[t], TRC_LINE[t]])
    tc = wb.create_sheet("TCC Reference")
    tc.append(["TCC", "Description (firm-defined scheme)"])
    style_header(tc, 1, 2)
    for t in sorted(TCC_DESC):
        tc.append([t, TCC_DESC[t]])
    for s in (tr, tc):
        s.column_dimensions["A"].width = 10
        s.column_dimensions["B"].width = 55
        s.column_dimensions["C"].width = 22
    wb.save(ROOT / "index.xlsx")


if __name__ == "__main__":
    idx = main()
    for c in idx:
        print(f'{c["cid"]} {c["software"]:<40} rev24 {c["rev24"]:>14,.0f} NI24 {c["ni24"]:>12,.0f} NI25 {c["ni25"]:>12,.0f} TA25 {c["ta25"]:>14,.0f}')
