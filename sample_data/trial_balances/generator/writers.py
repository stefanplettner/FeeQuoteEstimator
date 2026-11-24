"""Package-specific trial balance export writers (layouts per tb_formats research).

Each writer returns rows (list of lists) for one fiscal year; the caller saves
them as CSV.  Account numbers are generated from the package's numbering scheme.
"""
from catalog import ACCOUNTS

# number ranges per class: (start, step) per digit-width
CLASS_BLOCK = {"A": 1, "CA": 1, "L": 2, "E": 3, "ED": 3, "R": 4, "CR": 4, "C": 5, "X": 6, "O": 8, "OX": 8, "T": 9}

# Xero three-digit code bands (default chart style)
XERO_BAND = {"A": 600, "CA": 600, "L": 800, "E": 950, "ED": 950, "R": 200, "CR": 200, "C": 310, "X": 400, "O": 260, "OX": 260, "T": 505}


def assign_numbers(keys, software):
    """Return {key: account number string or ''} following the package convention."""
    nums, counters = {}, {}
    if software in ("QuickBooks Online", "Zoho Books"):
        # default chart has no numbers; QBO users often turn on 4-digit numbers.
        pass
    for k in keys:
        cls = ACCOUNTS[k][1]
        blk = CLASS_BLOCK[cls]
        if k in ("federal_tax_current", "federal_tax_deferred"):
            blk = 9
        if software == "Xero":
            base = XERO_BAND[cls]
            if k.startswith("cash") or k == "petty_cash":
                base = 90
            elif cls in ("A", "CA") and k in ("land", "buildings", "machinery", "furniture", "vehicles", "computers",
                                              "leasehold", "accum_depr", "goodwill", "intangibles", "software_cap", "accum_amort"):
                base = 710
            elif k in ("retained_earnings",):
                base = 960
            n = counters.get(base, 0)
            counters[base] = n + 1
            nums[k] = f"{base + n * (1 if base in (90, 960, 505) else 2):03d}"
            continue
        width = {"QuickBooks Online": 4, "Oracle NetSuite": 4, "Zoho Books": 0}.get(software, 5)
        if width == 0:
            nums[k] = ""
            continue
        step = 10 if width == 4 else 100
        start = blk * 10 ** (width - 1) + (step if blk != 6 else 0)
        n = counters.get(blk, 0)
        counters[blk] = n + 1
        nums[k] = str(start + n * step)
    return nums


def _amt(c):
    return f"{c / 100:,.2f}" if c else ""


def _dc(bal):
    return (_amt(bal), "") if bal > 0 else ("", _amt(-bal))


def write_rows(co, year, nums):
    sw = co.software
    bal = co.bal[year]
    keys = [k for k in co.keys() if bal.get(k, 0) != 0]
    asof_long = f"As of December 31, {year}"
    tot_dr = sum(v for v in bal.values() if v > 0)
    tot_cr = -sum(v for v in bal.values() if v < 0)
    name = co.account_name
    rows = []
    if sw == "QuickBooks Online":
        use_nums = co.rng_fmt.random() < 0.5
        rows += [[co.name], ["Trial Balance"], [asof_long], [], ["", "Debit", "Credit"]]
        for k in keys:
            label = f"{nums[k]} {name(k)}" if use_nums else name(k)
            rows.append([label, *_dc(bal[k])])
        rows += [["TOTAL", f"${tot_dr / 100:,.2f}", f"${tot_cr / 100:,.2f}"], [], [],
                 [f"Accrual Basis Tuesday, January {14 + (year - 2024) * 6}, {year + 1} 09:42 AM GMT-05:00"]]
    elif sw == "QuickBooks Desktop":
        rows += [["", "", co.name], ["", "", "Trial Balance"], ["", "", asof_long],
                 ["Accrual Basis"], ["", f"Dec 31, {str(year)[2:]}", ""], ["", "Debit", "Credit"]]
        for k in keys:
            rows.append([f"{nums[k]} · {name(k)}", *_dc(bal[k])])
        rows.append(["TOTAL", _amt(tot_dr), _amt(tot_cr)])
    elif sw == "Xero":
        rows += [["Trial Balance"], [co.name], [asof_long], [],
                 ["Account Code", "Account", "Account Type", "Debit", "Credit", "Debit - Year to date", "Credit - Year to date"]]
        sections = [("Revenue", {"R", "CR", "O", "OX"}), ("Expenses", {"C", "X", "T"}), ("Assets", {"A", "CA"}),
                    ("Liabilities", {"L"}), ("Equity", {"E", "ED"})]
        xtype = {"A": "Current Asset", "CA": "Fixed Asset", "L": "Current Liability", "E": "Equity", "ED": "Equity",
                 "R": "Revenue", "CR": "Revenue", "O": "Other Income", "OX": "Other Income", "C": "Direct Costs", "X": "Expense", "T": "Expense"}
        for title, classes in sections:
            sk = [k for k in keys if ACCOUNTS[k][1] in classes]
            if not sk:
                continue
            rows.append([title])
            sdr = scr = 0
            for k in sk:
                d, c = _dc(bal[k])
                t = xtype[ACCOUNTS[k][1]]
                if k in ("land", "buildings", "machinery", "furniture", "vehicles", "computers", "leasehold", "goodwill", "intangibles", "software_cap"):
                    t = "Fixed Asset"
                elif k in ("note_bank", "mortgage", "equipment_loan", "lease_liability", "dtl", "due_to_sh"):
                    t = "Non-current Liability"
                elif k.startswith("cash") or k == "petty_cash":
                    t = "Bank"
                rows.append([nums[k], name(k), t, d, c, d, c])
                sdr += max(bal[k], 0)
                scr += max(-bal[k], 0)
            rows.append([f"Total {title}", "", "", _amt(sdr), _amt(scr), _amt(sdr), _amt(scr)])
            rows.append([])
        rows.append(["Total", "", "", _amt(tot_dr), _amt(tot_cr), _amt(tot_dr), _amt(tot_cr)])
    elif sw == "Sage Intacct":
        prior = co.bal.get(year - 1, {})
        rows += [[co.name], ["Trial Balance"], [f"For the period January 1, {year} to December 31, {year}"],
                 ["Reporting book: Accrual"], [],
                 ["Account", "Account title", "Opening balance", "Debit", "Credit", "Closing balance"]]
        t_open = t_dr = t_cr = 0
        for k in keys:
            close = bal[k]
            cls = ACCOUNTS[k][1]
            if cls in ("A", "CA", "L", "E", "ED") and k != "retained_earnings":
                opening = prior.get(k, 0) if prior else int(close * co.rng_fmt.uniform(0.85, 1.1))
            else:
                opening = 0 if k != "retained_earnings" else close
            if k == "retained_earnings":
                opening = close
            move = close - opening
            dr = max(move, 0) + abs(close) * (0 if cls not in ("A", "L") else 3)
            cr = dr - move
            rows.append([nums[k], name(k), f"{opening / 100:.2f}", f"{dr / 100:.2f}", f"{cr / 100:.2f}", f"{close / 100:.2f}"])
            t_open += opening
            t_dr += dr
            t_cr += cr
        rows.append(["Total", "", f"{t_open / 100:.2f}", f"{t_dr / 100:.2f}", f"{t_cr / 100:.2f}", f"{tot_dr / 100 - tot_cr / 100:.2f}"])
    elif sw == "Oracle NetSuite":
        rows += [[co.name], ["Trial Balance"], [f"End of Dec {year}"], ["Account", "Debit", "Credit"]]
        for k in keys:
            rows.append([f"{nums[k]} {name(k)}", *_dc(bal[k])])
        rows.append(["Total", _amt(tot_dr), _amt(tot_cr)])
    elif sw == "Microsoft Dynamics 365 Business Central":
        rows += [["Trial Balance"], [f"Period: 01/01/{str(year)[2:]}..12/31/{str(year)[2:]}"], [co.name],
                 [f"G/L Account: Date Filter: 01/01/{str(year)[2:]}..12/31/{str(year)[2:]}"], [],
                 ["No.", "Name", "Net Change Debit", "Net Change Credit", "Balance Debit", "Balance Credit"]]
        prior = co.bal.get(year - 1, {})
        for k in keys:
            cls = ACCOUNTS[k][1]
            closing = bal[k]
            if cls in ("A", "CA", "L", "E", "ED"):
                opening = prior.get(k, 0) if prior else int(closing * co.rng_fmt.uniform(0.85, 1.1))
                if k == "retained_earnings":
                    opening = closing
                net = closing - opening
            else:
                net = closing
            rows.append([nums[k], name(k), *_dc(net), *_dc(closing)])
        rows.append(["", "Total", "", "", _amt(tot_dr), _amt(tot_cr)])
    elif sw == "Sage 50":
        rows += [[co.name], ["General Ledger Trial Balance"], [f"As of Dec 31, {year}"],
                 ["Filter Criteria includes: Report order is by ID. Report is printed in Detail Format."], [],
                 ["Account ID", "Account Description", "Debit Amt", "Credit Amt"]]
        for k in keys:
            rows.append([nums[k], name(k), *_dc(bal[k])])
        rows.append(["", "Total:", _amt(tot_dr), _amt(tot_cr)])
    elif sw == "Zoho Books":
        rows += [[co.name], ["Trial Balance"], ["Basis: Accrual"], [f"As of 12/31/{year}"], [],
                 ["Account", "Account Code", "Net Debit", "Net Credit"]]
        sections = [("Assets", {"A", "CA"}), ("Liabilities", {"L"}), ("Equities", {"E", "ED"}),
                    ("Income", {"R", "CR", "O", "OX"}), ("Expense", {"C", "X", "T"})]
        for title, classes in sections:
            sk = [k for k in keys if ACCOUNTS[k][1] in classes]
            if not sk:
                continue
            rows.append([title])
            sdr = scr = 0
            for k in sk:
                rows.append([name(k), nums[k], *_dc(bal[k])])
                sdr += max(bal[k], 0)
                scr += max(-bal[k], 0)
            rows.append([f"Total for {title}", "", _amt(sdr), _amt(scr)])
        rows.append(["Total", "", _amt(tot_dr), _amt(tot_cr)])
    else:
        raise ValueError(sw)
    return rows
