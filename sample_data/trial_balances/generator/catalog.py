"""Semantic account catalog used by the fictitious trial balance generator.

Each semantic key describes one general-ledger account independent of the
accounting package.  The package-specific writer decides the account number
and display format; the GoSystem mapping table (gosystem_map.py) assigns the
TRC/TCC tax codes by semantic key.

class codes:
  A  asset (debit)            CA contra-asset (credit)
  L  liability (credit)       E  equity (credit)          ED equity contra (debit)
  R  revenue (credit)         CR contra-revenue (debit)
  C  cost of goods sold       X  operating expense        O  other income (credit)
  OX other expense            T  income tax expense
"""

ACCOUNTS = {
    # ---------------- current assets ----------------
    "cash_operating":      ("Operating Checking", "A"),
    "cash_payroll":        ("Payroll Checking", "A"),
    "cash_savings":        ("Money Market Savings", "A"),
    "petty_cash":          ("Petty Cash", "A"),
    "ar":                  ("Accounts Receivable", "A"),
    "ar_retainage":        ("Retainage Receivable", "A"),
    "allowance":           ("Allowance for Doubtful Accounts", "CA"),
    "costs_in_excess":     ("Costs in Excess of Billings", "A"),
    "inventory":           ("Inventory", "A"),
    "inventory_raw":       ("Inventory - Raw Materials", "A"),
    "inventory_wip":       ("Inventory - Work in Process", "A"),
    "inventory_fg":        ("Inventory - Finished Goods", "A"),
    "prepaid":             ("Prepaid Expenses", "A"),
    "prepaid_insurance":   ("Prepaid Insurance", "A"),
    "prepaid_tax":         ("Prepaid Federal Income Tax", "A"),
    "employee_adv":        ("Employee Advances", "A"),
    "invest_muni":         ("Investments - Municipal Bonds", "A"),
    "invest_securities":   ("Investments - Marketable Securities", "A"),
    # ---------------- fixed / other assets ----------------
    "land":                ("Land", "A"),
    "buildings":           ("Buildings", "A"),
    "machinery":           ("Machinery & Equipment", "A"),
    "furniture":           ("Furniture & Fixtures", "A"),
    "vehicles":            ("Vehicles", "A"),
    "computers":           ("Computer Equipment", "A"),
    "leasehold":           ("Leasehold Improvements", "A"),
    "accum_depr":          ("Accumulated Depreciation", "CA"),
    "goodwill":            ("Goodwill", "A"),
    "intangibles":         ("Customer List", "A"),
    "software_cap":        ("Capitalized Software", "A"),
    "accum_amort":         ("Accumulated Amortization", "CA"),
    "deposits":            ("Security Deposits", "A"),
    "loan_to_sh":          ("Loan Receivable - Shareholder", "A"),
    "rou_asset":           ("Right-of-Use Asset - Operating Lease", "A"),
    "csv_life":            ("Cash Surrender Value - Officer Life Insurance", "A"),
    "dta":                 ("Deferred Tax Asset", "A"),
    # ---------------- liabilities ----------------
    "ap":                  ("Accounts Payable", "L"),
    "credit_card":         ("Corporate Credit Card", "L"),
    "accrued_payroll":     ("Accrued Wages", "L"),
    "payroll_liab":        ("Payroll Taxes Payable", "L"),
    "sales_tax":           ("Sales Tax Payable", "L"),
    "accrued_exp":         ("Accrued Expenses", "L"),
    "deferred_rev":        ("Deferred Revenue", "L"),
    "billings_in_excess":  ("Billings in Excess of Costs", "L"),
    "customer_deposits":   ("Customer Deposits", "L"),
    "retainage_payable":   ("Retainage Payable", "L"),
    "income_tax_payable":  ("Federal Income Tax Payable", "L"),
    "state_tax_payable":   ("State Income Tax Payable", "L"),
    "loc":                 ("Line of Credit", "L"),
    "current_ltd":         ("Current Portion of Long-Term Debt", "L"),
    "note_bank":           ("Note Payable - Bank", "L"),
    "mortgage":            ("Mortgage Payable", "L"),
    "equipment_loan":      ("Equipment Loans Payable", "L"),
    "due_to_sh":           ("Due to Shareholder", "L"),
    "lease_liability":     ("Operating Lease Liability", "L"),
    "dtl":                 ("Deferred Tax Liability", "L"),
    # ---------------- equity ----------------
    "common_stock":        ("Common Stock", "E"),
    "preferred_stock":     ("Preferred Stock", "E"),
    "apic":                ("Additional Paid-In Capital", "E"),
    "retained_earnings":   ("Retained Earnings", "E"),
    "dividends":           ("Dividends Paid", "ED"),
    "treasury_stock":      ("Treasury Stock", "ED"),
    # ---------------- revenue ----------------
    "sales":               ("Sales", "R"),
    "sales_wholesale":     ("Sales - Wholesale", "R"),
    "sales_online":        ("Sales - E-commerce", "R"),
    "service_rev":         ("Service Revenue", "R"),
    "contract_rev":        ("Contract Revenue", "R"),
    "subscription_rev":    ("Subscription Revenue", "R"),
    "consulting_rev":      ("Professional Services Revenue", "R"),
    "patient_rev":         ("Patient Service Revenue", "R"),
    "food_sales":          ("Food Sales", "R"),
    "beverage_sales":      ("Beverage Sales", "R"),
    "freight_rev":         ("Freight Revenue", "R"),
    "rental_rev":          ("Rental Income", "R"),
    "sales_returns":       ("Sales Returns & Allowances", "CR"),
    "sales_discounts":     ("Sales Discounts", "CR"),
    # ---------------- cost of goods sold ----------------
    "cogs":                ("Cost of Goods Sold", "C"),
    "cogs_materials":      ("Materials & Purchases", "C"),
    "cogs_labor":          ("Direct Labor", "C"),
    "cogs_overhead":       ("Manufacturing Overhead", "C"),
    "cogs_subs":           ("Subcontractors", "C"),
    "cogs_freight_in":     ("Freight-In", "C"),
    "cogs_food":           ("Food Cost", "C"),
    "cogs_beverage":       ("Beverage Cost", "C"),
    "cogs_hosting":        ("Hosting & Infrastructure", "C"),
    "cogs_fuel":           ("Fuel", "C"),
    "cogs_medical_supplies": ("Medical Supplies", "C"),
    "cogs_equipment_rental": ("Equipment Rental - Jobs", "C"),
    "inventory_adj":       ("Inventory Shrinkage & Adjustments", "C"),
    # ---------------- operating expenses ----------------
    "officer_comp":        ("Officer Compensation", "X"),
    "salaries":            ("Salaries & Wages", "X"),
    "payroll_taxes":       ("Payroll Tax Expense", "X"),
    "health_ins":          ("Employee Health Insurance", "X"),
    "retirement":          ("401(k) Matching Contributions", "X"),
    "rent":                ("Rent Expense", "X"),
    "repairs":             ("Repairs & Maintenance", "X"),
    "bad_debt":            ("Bad Debt Expense", "X"),
    "taxes_licenses":      ("Taxes & Licenses", "X"),
    "property_tax":        ("Property Taxes", "X"),
    "state_income_tax":    ("State Income Tax Expense", "X"),
    "interest_exp":        ("Interest Expense", "X"),
    "depreciation":        ("Depreciation Expense", "X"),
    "amortization":        ("Amortization Expense", "X"),
    "advertising":         ("Advertising & Marketing", "X"),
    "auto":                ("Auto & Truck Expense", "X"),
    "bank_fees":           ("Bank Service Charges", "X"),
    "merchant_fees":       ("Merchant Processing Fees", "X"),
    "charitable":          ("Charitable Contributions", "X"),
    "dues_subs":           ("Dues & Subscriptions", "X"),
    "insurance":           ("Insurance - General Liability", "X"),
    "workers_comp":        ("Workers' Compensation Insurance", "X"),
    "officer_life":        ("Officer Life Insurance Premiums", "X"),
    "meals":               ("Meals (50%)", "X"),
    "entertainment":       ("Entertainment (Nondeductible)", "X"),
    "office_supplies":     ("Office Supplies", "X"),
    "postage":             ("Postage & Shipping", "X"),
    "freight_out":         ("Freight-Out", "X"),
    "professional_fees":   ("Accounting Fees", "X"),
    "legal_fees":          ("Legal Fees", "X"),
    "consulting_fees":     ("Consulting Fees", "X"),
    "contract_labor":      ("Contract Labor", "X"),
    "software":            ("Software & SaaS Subscriptions", "X"),
    "telephone":           ("Telephone & Internet", "X"),
    "travel":              ("Travel", "X"),
    "utilities":           ("Utilities", "X"),
    "training":            ("Training & Education", "X"),
    "uniforms":            ("Uniforms", "X"),
    "janitorial":          ("Janitorial & Cleaning", "X"),
    "research":            ("Research & Development", "X"),
    "penalties":           ("Penalties & Fines", "X"),
    "political":           ("Lobbying & Political Contributions", "X"),
    "club_dues":           ("Club Dues", "X"),
    "misc_exp":            ("Miscellaneous Expense", "X"),
    # ---------------- other income / expense ----------------
    "interest_income":     ("Interest Income", "O"),
    "muni_interest":       ("Tax-Exempt Interest Income", "O"),
    "dividend_income":     ("Dividend Income", "O"),
    "gain_asset_sale":     ("Gain on Sale of Assets", "O"),
    "other_income":        ("Other Income", "O"),
    "unrealized_gain":     ("Unrealized Gain/Loss on Securities", "O"),
    # ---------------- income tax ----------------
    "federal_tax_current": ("Federal Income Tax Expense - Current", "T"),
    "federal_tax_deferred": ("Federal Income Tax Expense - Deferred", "T"),
}

DEBIT_CLASSES = {"A", "ED", "CR", "C", "X", "OX", "T"}
BS_CLASSES = {"A", "CA", "L", "E", "ED"}


def normal_side(cls: str) -> int:
    """+1 for debit-normal accounts, -1 for credit-normal accounts."""
    return 1 if cls in DEBIT_CLASSES else -1
