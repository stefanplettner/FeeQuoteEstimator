"""GoSystem Tax RS trial balance mapping for Form 1120.

TRC = Tax Return Code (Thomson Reuters-defined, required, format NN-NNN).
TCC = Tax Combination Code (optional, FIRM-DEFINED, up to 3 characters) used
      with a TRC to itemize/group accounts within a single return line.
MRC = Schedule M-3 Return Code (I/E series), only on 30- and 40-range TRCs
      per GoSystem rules; listed for reference on income/expense items.

TRC values come from excerpts of Thomson Reuters' 1120 TRC/MRC code lists (see
../research/gosystem_codes.json).  Every value should be confirmed against the
current-year 1120_TRC_MRC list before it is used on a live return.  The TCC
scheme below is an illustrative firm standard, not a Thomson Reuters list.
"""

TRC_DESC = {
    "10-100": "Cash", "10-200": "Trade notes and accounts receivable", "10-205": "Less allowance for bad debts",
    "10-300": "Inventories", "10-500": "Tax-exempt securities", "10-900": "Other current assets",
    "11-100": "Loans to shareholders", "11-400": "Other investments", "11-500": "Buildings and other depreciable assets",
    "11-505": "Less accumulated depreciation", "11-700": "Land", "11-800": "Intangible assets - goodwill",
    "11-830": "Intangible assets - other", "11-835": "Less accumulated amortization", "11-900": "Other assets",
    "20-100": "Accounts payable", "20-200": "Mortgages, notes, bonds payable in less than 1 year",
    "20-300": "Other current liabilities", "21-100": "Loans from shareholders",
    "21-200": "Mortgages, notes, bonds payable in 1 year or more", "21-300": "Other liabilities",
    "22-100": "Capital stock - preferred", "22-110": "Capital stock - common", "22-200": "Additional paid-in capital",
    "22-310": "Retained earnings - unappropriated", "22-440": "Cost of treasury stock",
    "30-100": "Gross receipts or sales", "30-105": "Returns and allowances",
    "31-110": "Dividends", "31-380": "Other interest income", "31-420": "Gross rents",
    "31-660": "Ordinary gain (loss) - Form 4797", "31-900": "Other income",
    "40-120": "COGS - purchases", "40-130": "COGS - cost of labor", "40-155": "COGS - other costs",
    "41-210": "Compensation of officers", "41-220": "Salaries and wages", "41-260": "Repairs and maintenance",
    "41-300": "Bad debts", "41-350": "Rents", "41-400": "Federal income tax (book)", "41-420": "Taxes and licenses",
    "41-500": "Interest", "41-520": "Charitable contributions", "41-530": "Insurance", "41-540": "Depreciation",
    "41-580": "Advertising", "41-600": "Pension, profit-sharing, etc. plans", "41-620": "Employee benefit programs",
    "41-810": "Meals (50% limit)", "41-812": "Travel", "41-900": "Other deductions",
    "60-216": "M-1: Travel and entertainment not deductible", "60-240": "M-1: Other book expenses not deducted",
    "60-410": "M-1: Tax-exempt interest", "60-450": "M-1: Other book income not on return",
    "62-308": "M-2: Distributions - cash",
}

TRC_LINE = {
    "10-100": "Sch L L1", "10-200": "Sch L L2a", "10-205": "Sch L L2b", "10-300": "Sch L L3", "10-500": "Sch L L5",
    "10-900": "Sch L L6", "11-100": "Sch L L7", "11-400": "Sch L L9", "11-500": "Sch L L10a", "11-505": "Sch L L10b",
    "11-700": "Sch L L12", "11-800": "Sch L L13a", "11-830": "Sch L L13a", "11-835": "Sch L L13b", "11-900": "Sch L L14",
    "20-100": "Sch L L16", "20-200": "Sch L L17", "20-300": "Sch L L18", "21-100": "Sch L L19", "21-200": "Sch L L20",
    "21-300": "Sch L L21", "22-100": "Sch L L22a", "22-110": "Sch L L22b", "22-200": "Sch L L23", "22-310": "Sch L L25",
    "22-440": "Sch L L27", "30-100": "p1 L1a", "30-105": "p1 L1b", "31-110": "p1 L4 / Sch C", "31-380": "p1 L5",
    "31-420": "p1 L6", "31-660": "p1 L9 / Form 4797", "31-900": "p1 L10", "40-120": "1125-A L2", "40-130": "1125-A L3",
    "40-155": "1125-A L5", "41-210": "p1 L12 / 1125-E", "41-220": "p1 L13", "41-260": "p1 L14", "41-300": "p1 L15",
    "41-350": "p1 L16", "41-400": "Sch M-1 L2", "41-420": "p1 L17", "41-500": "p1 L18", "41-520": "p1 L19",
    "41-530": "p1 L26", "41-540": "p1 L20 / 4562", "41-580": "p1 L22", "41-600": "p1 L23", "41-620": "p1 L24",
    "41-810": "p1 L26 + M-1 L5c", "41-812": "p1 L26", "41-900": "p1 L26", "60-216": "Sch M-1 L5c",
    "60-240": "Sch M-1 L5", "60-410": "Sch M-1 L7", "60-450": "Sch M-1 L7", "62-308": "Sch M-2 L5a",
}

# Source confidence for each TRC used (from ../research/gosystem_codes.json).
#  "1120 list"   - seen in excerpts of the Form 1120 TRC list
#  "1120 family" - seen only on a related-form list (1120S/1120-C/F/RIC/PC/REIT);
#                  numbering appears shared but confirm on the 1120 list
#  "snippet"     - seen only in search-result snippets
TRC_SOURCE_FAMILY = {"11-100", "11-400", "11-500", "11-505", "20-300", "22-310", "31-380", "31-420",
                     "41-810", "41-812", "41-900", "62-308"}
TRC_SOURCE_SNIPPET = {"60-216", "60-240", "60-450"}


def trc_confidence(trc):
    if trc in TRC_SOURCE_SNIPPET:
        return "snippet - verify"
    if trc in TRC_SOURCE_FAMILY:
        return "1120 family - verify"
    return "1120 list"

# Firm-defined TCC scheme (illustrative).
TCC_DESC = {
    "CHK": "Checking accounts", "SAV": "Savings / money market", "PTY": "Petty cash",
    "PPD": "Prepaid expenses", "PPI": "Prepaid insurance", "PFT": "Prepaid federal income tax",
    "ADV": "Employee advances", "CIE": "Costs in excess of billings", "RET": "Retainage",
    "BLD": "Buildings", "MAE": "Machinery & equipment", "FFX": "Furniture & fixtures", "VEH": "Vehicles",
    "CMP": "Computer equipment", "LHI": "Leasehold improvements", "CUS": "Customer list (Sec. 197)",
    "SFW": "Capitalized software", "DEP": "Deposits", "ROU": "Operating lease ROU asset (ASC 842)",
    "CSV": "Cash surrender value - life insurance", "DTA": "Deferred tax asset",
    "CCP": "Credit cards payable", "ACW": "Accrued wages", "PRT": "Payroll taxes payable",
    "STX": "Sales tax payable", "ACE": "Accrued expenses", "DRV": "Deferred revenue",
    "BIE": "Billings in excess of costs", "CDP": "Customer deposits", "FIT": "Federal income tax payable",
    "SIT": "State income tax payable", "LOC": "Line of credit", "CPD": "Current portion LTD",
    "LSL": "Operating lease liability (ASC 842)", "DTL": "Deferred tax liability",
    "RTN": "Returns & allowances", "DSC": "Sales discounts", "PAY": "Payroll taxes", "STT": "State income tax",
    "PRP": "Property taxes", "LIC": "Licenses & franchise taxes", "AMR": "Amortization", "AUT": "Auto & truck",
    "BNK": "Bank & merchant fees", "DUE": "Dues & subscriptions", "SUP": "Office supplies & postage",
    "PRO": "Legal & professional fees", "CON": "Contract labor", "SOF": "Software", "TEL": "Telephone & internet",
    "UTL": "Utilities", "TRN": "Training", "UNI": "Uniforms", "JAN": "Janitorial", "R&D": "Research & experimental (Sec. 174/174A)",
    "FRT": "Freight-out & shipping", "MSC": "Miscellaneous", "CUR": "Current provision", "DEF": "Deferred provision",
    "ENT": "Entertainment (Sec. 274(a))", "FIN": "Fines & penalties (Sec. 162(f))", "OLI": "Officer life insurance (Sec. 264)",
    "LOB": "Lobbying & political (Sec. 162(e))", "CLB": "Club dues (Sec. 274(a)(3))", "UGL": "Unrealized gain/loss on securities",
    "WCI": "Workers' compensation", "GLI": "General liability insurance", "FDS": "Food & beverage purchases",
    "FUL": "Fuel", "SUB": "Subcontractors", "OVH": "Overhead", "FRI": "Freight-in", "HST": "Hosting", "SHR": "Shrinkage",
    "EQR": "Equipment rental", "MED": "Medical supplies",
}

# semantic key -> (TRC, TCC or "", MRC or "", note)
MAP = {
    "cash_operating": ("10-100", "CHK", "", ""), "cash_payroll": ("10-100", "CHK", "", ""),
    "cash_savings": ("10-100", "SAV", "", ""), "petty_cash": ("10-100", "PTY", "", ""),
    "ar": ("10-200", "", "", ""), "ar_retainage": ("10-200", "RET", "", ""),
    "allowance": ("10-205", "", "", "Bad debt reserve not deductible; Sec. 166 specific charge-off - M-1 on change in reserve"),
    "costs_in_excess": ("10-900", "CIE", "", ""),
    "inventory": ("10-300", "", "", "Ending inventory also feeds 1125-A L1/L7"), "inventory_raw": ("10-300", "", "", ""),
    "inventory_wip": ("10-300", "", "", ""), "inventory_fg": ("10-300", "", "", ""),
    "prepaid": ("10-900", "PPD", "", ""), "prepaid_insurance": ("10-900", "PPI", "", ""),
    "prepaid_tax": ("10-900", "PFT", "", ""), "employee_adv": ("10-900", "ADV", "", ""),
    "invest_muni": ("10-500", "", "", ""), "invest_securities": ("11-400", "", "", ""),
    "land": ("11-700", "", "", ""), "buildings": ("11-500", "BLD", "", ""), "machinery": ("11-500", "MAE", "", ""),
    "furniture": ("11-500", "FFX", "", ""), "vehicles": ("11-500", "VEH", "", ""), "computers": ("11-500", "CMP", "", ""),
    "leasehold": ("11-500", "LHI", "", ""), "accum_depr": ("11-505", "", "", "Book accumulated depreciation; tax basis tracked in fixed asset module"),
    "goodwill": ("11-800", "", "", "Book goodwill; tax Sec. 197 15-yr amortization if acquired in asset deal"),
    "intangibles": ("11-830", "CUS", "", ""), "software_cap": ("11-830", "SFW", "", ""),
    "accum_amort": ("11-835", "", "", ""), "deposits": ("11-900", "DEP", "", ""),
    "loan_to_sh": ("11-100", "", "", "Review for constructive dividend; Sec. 7872 below-market interest"),
    "rou_asset": ("11-900", "ROU", "", "ASC 842 - tax treats as operating rent; M-1/M-3 difference"),
    "csv_life": ("11-900", "CSV", "", ""), "dta": ("11-900", "DTA", "", ""),
    "ap": ("20-100", "", "", ""), "credit_card": ("20-300", "CCP", "", ""), "accrued_payroll": ("20-300", "ACW", "", "Sec. 404(a)(5) - related-party accruals"),
    "payroll_liab": ("20-300", "PRT", "", ""), "sales_tax": ("20-300", "STX", "", ""), "accrued_exp": ("20-300", "ACE", "", "Sec. 461(h) economic performance"),
    "deferred_rev": ("20-300", "DRV", "", "Sec. 451(c) one-year deferral"), "billings_in_excess": ("20-300", "BIE", "", ""),
    "customer_deposits": ("20-300", "CDP", "", ""), "retainage_payable": ("20-300", "RET", "", ""),
    "income_tax_payable": ("20-300", "FIT", "", ""), "state_tax_payable": ("20-300", "SIT", "", ""),
    "loc": ("20-200", "LOC", "", ""), "current_ltd": ("20-200", "CPD", "", ""),
    "note_bank": ("21-200", "", "", ""), "mortgage": ("21-200", "", "", ""), "equipment_loan": ("21-200", "", "", ""),
    "due_to_sh": ("21-100", "", "", ""), "lease_liability": ("21-300", "LSL", "", "Current portion may be reclassed to 20-300"),
    "dtl": ("21-300", "DTL", "", ""),
    "common_stock": ("22-110", "", "", ""), "preferred_stock": ("22-100", "", "", ""), "apic": ("22-200", "", "", ""),
    "retained_earnings": ("22-310", "", "", "Beginning-of-year balance (pre-closing TB)"),
    "dividends": ("62-308", "", "", "M-2 L5a cash distributions; E&P review"), "treasury_stock": ("22-440", "", "", ""),
    "sales": ("30-100", "", "", ""), "sales_wholesale": ("30-100", "", "", ""), "sales_online": ("30-100", "", "", ""),
    "service_rev": ("30-100", "", "", ""), "contract_rev": ("30-100", "", "", "Sec. 460 PCM vs. small-contractor exception"),
    "subscription_rev": ("30-100", "", "", ""), "consulting_rev": ("30-100", "", "", ""), "patient_rev": ("30-100", "", "", ""),
    "food_sales": ("30-100", "", "", ""), "beverage_sales": ("30-100", "", "", ""), "freight_rev": ("30-100", "", "", ""),
    "rental_rev": ("31-420", "", "", "Gross rents - p1 L6"),
    "sales_returns": ("30-105", "RTN", "", ""), "sales_discounts": ("30-105", "DSC", "", ""),
    "cogs": ("40-120", "", "", "COGS expense mapped to purchases; 1125-A L1/L7 from Sch L inventory"),
    "cogs_materials": ("40-120", "", "", ""), "cogs_food": ("40-120", "FDS", "", ""), "cogs_beverage": ("40-120", "FDS", "", ""),
    "cogs_medical_supplies": ("40-120", "MED", "", ""),
    "cogs_labor": ("40-130", "", "", ""), "cogs_overhead": ("40-155", "OVH", "", "Sec. 263A UNICAP review"),
    "cogs_subs": ("40-155", "SUB", "", ""), "cogs_freight_in": ("40-155", "FRI", "", ""), "cogs_fuel": ("40-155", "FUL", "", ""),
    "cogs_hosting": ("40-155", "HST", "", ""), "cogs_equipment_rental": ("40-155", "EQR", "", ""),
    "inventory_adj": ("40-155", "SHR", "", ""),
    "officer_comp": ("41-210", "", "", "Form 1125-E if total receipts >= $500,000"), "salaries": ("41-220", "", "", ""),
    "payroll_taxes": ("41-420", "PAY", "", ""), "health_ins": ("41-620", "", "", ""), "retirement": ("41-600", "", "E700", ""),
    "rent": ("41-350", "", "", ""), "repairs": ("41-260", "", "", ""), "bad_debt": ("41-300", "", "", "Book = reserve method; tax = specific charge-off"),
    "taxes_licenses": ("41-420", "LIC", "", ""), "property_tax": ("41-420", "PRP", "", ""),
    "state_income_tax": ("41-420", "STT", "", "Deductible; check accrual vs. paid (Sec. 461)"),
    "interest_exp": ("41-500", "", "", "Sec. 163(j) if avg receipts > small-business threshold"),
    "depreciation": ("41-540", "", "", "Book depreciation; tax per Form 4562, difference to M-1 L5a/L8a"),
    "amortization": ("41-900", "AMR", "", "Book amortization; tax per Form 4562 Part VI"),
    "advertising": ("41-580", "", "", ""), "auto": ("41-900", "AUT", "", ""), "bank_fees": ("41-900", "BNK", "", ""),
    "merchant_fees": ("41-900", "BNK", "", ""), "charitable": ("41-520", "", "E730", "10% of taxable income limit"),
    "dues_subs": ("41-900", "DUE", "", ""), "insurance": ("41-530", "GLI", "", ""), "workers_comp": ("41-530", "WCI", "", ""),
    "officer_life": ("60-240", "OLI", "", "Nondeductible Sec. 264 - M-1 L5"),
    "meals": ("41-810", "", "E650", "50% auto-limit; nondeductible half to M-1 L5c"),
    "entertainment": ("60-216", "ENT", "", "Nondeductible Sec. 274(a) - M-1 L5c"),
    "office_supplies": ("41-900", "SUP", "", ""), "postage": ("41-900", "SUP", "", ""), "freight_out": ("41-900", "FRT", "", ""),
    "professional_fees": ("41-900", "PRO", "", ""), "legal_fees": ("41-900", "PRO", "", ""), "consulting_fees": ("41-900", "PRO", "", ""),
    "contract_labor": ("41-900", "CON", "", "Form 1099-NEC compliance"), "software": ("41-900", "SOF", "", ""),
    "telephone": ("41-900", "TEL", "", ""), "travel": ("41-812", "", "", ""), "utilities": ("41-900", "UTL", "", ""),
    "training": ("41-900", "TRN", "", ""), "uniforms": ("41-900", "UNI", "", ""), "janitorial": ("41-900", "JAN", "", ""),
    "research": ("41-900", "R&D", "", "2024: Sec. 174 capitalization (domestic 5-yr); 2025: Sec. 174A domestic expensing - confirm treatment"),
    "penalties": ("60-240", "FIN", "", "Nondeductible Sec. 162(f) - M-1 L5"),
    "political": ("60-240", "LOB", "", "Nondeductible Sec. 162(e) - M-1 L5"),
    "club_dues": ("60-240", "CLB", "", "Nondeductible Sec. 274(a)(3) - M-1 L5"),
    "misc_exp": ("41-900", "MSC", "", ""),
    "interest_income": ("31-380", "", "I220.05", ""), "muni_interest": ("60-410", "", "", "Tax-exempt - M-1 L7; Sch K L9"),
    "dividend_income": ("31-110", "", "I160", "Confirm ownership % for DRD (Sch C)"),
    "gain_asset_sale": ("31-660", "", "", "Book gain; recompute tax gain/recapture on Form 4797"),
    "other_income": ("31-900", "", "", ""),
    "unrealized_gain": ("60-450", "UGL", "", "Book-only mark-to-market gain - M-1 L7"),
    "unrealized_loss": ("60-240", "UGL", "", "Book-only mark-to-market loss - M-1 L5"),
    "federal_tax_current": ("41-400", "CUR", "E550", "Nondeductible - M-1 L2"),
    "federal_tax_deferred": ("41-400", "DEF", "", "Nondeductible - M-1 L2 (M-3 deferred line)"),
}
