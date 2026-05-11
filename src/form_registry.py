"""
Master registry of known Form 1120-related forms.
Maps form_code -> metadata. Used to enrich Claude's output with canonical names
and to seed the fee schedule with all known entries.
"""

FORM_REGISTRY: dict[str, dict] = {
    # ── Core Form 1120 ────────────────────────────────────────────────────────
    "1120": {
        "form_name": "Form 1120",
        "description": "U.S. Corporation Income Tax Return (base form, pages 1–6)",
        "category": "core_1120",
    },
    "1120-SCH-C": {
        "form_name": "Schedule C",
        "description": "Dividends, Inclusions, and Special Deductions",
        "category": "core_1120",
    },
    "1120-SCH-D": {
        "form_name": "Schedule D",
        "description": "Capital Gains and Losses",
        "category": "core_1120",
    },
    "1120-SCH-G": {
        "form_name": "Schedule G",
        "description": "Information on Certain Persons Owning the Corporation's Voting Stock",
        "category": "core_1120",
    },
    "1120-SCH-H": {
        "form_name": "Schedule H",
        "description": "Section 280H Limitations for a Personal Service Corporation",
        "category": "core_1120",
    },
    "1120-SCH-J": {
        "form_name": "Schedule J",
        "description": "Tax Computation and Payment",
        "category": "core_1120",
    },
    "1120-SCH-K": {
        "form_name": "Schedule K",
        "description": "Other Information",
        "category": "core_1120",
    },
    "1120-SCH-L": {
        "form_name": "Schedule L",
        "description": "Balance Sheets per Books",
        "category": "core_1120",
    },
    "1120-SCH-M1": {
        "form_name": "Schedule M-1",
        "description": "Reconciliation of Income per Books with Income per Return",
        "category": "core_1120",
    },
    "1120-SCH-M2": {
        "form_name": "Schedule M-2",
        "description": "Analysis of Unappropriated Retained Earnings per Books",
        "category": "core_1120",
    },
    "1120-SCH-M3": {
        "form_name": "Schedule M-3",
        "description": "Net Income (Loss) Reconciliation for Corporations with Total Assets of $10 Million or More",
        "category": "core_1120",
    },
    # ── Federal Schedules / Attachments ──────────────────────────────────────
    "4562": {
        "form_name": "Form 4562",
        "description": "Depreciation and Amortization",
        "category": "federal_schedule",
    },
    "4797": {
        "form_name": "Form 4797",
        "description": "Sales of Business Property",
        "category": "federal_schedule",
    },
    "8949": {
        "form_name": "Form 8949",
        "description": "Sales and Other Dispositions of Capital Assets",
        "category": "federal_schedule",
    },
    "5471": {
        "form_name": "Form 5471",
        "description": "Information Return of U.S. Persons With Respect to Certain Foreign Corporations",
        "category": "federal_schedule",
    },
    "5472": {
        "form_name": "Form 5472",
        "description": "Information Return of a 25% Foreign-Owned U.S. Corporation or a Foreign Corporation Engaged in a U.S. Trade or Business",
        "category": "federal_schedule",
    },
    "8858": {
        "form_name": "Form 8858",
        "description": "Information Return of U.S. Persons With Respect to Foreign Disregarded Entities and Foreign Branches",
        "category": "federal_schedule",
    },
    "965": {
        "form_name": "Form 965 / Schedule 965-A",
        "description": "Inclusion of Deferred Foreign Income Upon Transition to Participation Exemption System",
        "category": "federal_schedule",
    },
    "8990": {
        "form_name": "Form 8990",
        "description": "Limitation on Business Interest Expense Under Section 163(j)",
        "category": "federal_schedule",
    },
    "8991": {
        "form_name": "Form 8991",
        "description": "Tax on Base Erosion Payments of Taxpayers With Substantial Gross Receipts (BEAT)",
        "category": "federal_schedule",
    },
    "8992": {
        "form_name": "Form 8992",
        "description": "U.S. Shareholder Calculation of Global Intangible Low-Taxed Income (GILTI)",
        "category": "federal_schedule",
    },
    "8993": {
        "form_name": "Form 8993",
        "description": "Section 250 Deduction for Foreign-Derived Intangible Income (FDII) and GILTI",
        "category": "federal_schedule",
    },
    "1118": {
        "form_name": "Form 1118",
        "description": "Foreign Tax Credit — Corporations",
        "category": "federal_schedule",
    },
    "8916": {
        "form_name": "Form 8916",
        "description": "Reconciliation of Schedule M-3 Taxable Income with Tax Return Taxable Income for Mixed Groups",
        "category": "federal_schedule",
    },
    "8916A": {
        "form_name": "Form 8916-A",
        "description": "Supplemental Attachment to Schedule M-3",
        "category": "federal_schedule",
    },
    "4626": {
        "form_name": "Form 4626",
        "description": "Alternative Minimum Tax — Corporations",
        "category": "federal_schedule",
    },
    "8827": {
        "form_name": "Form 8827",
        "description": "Credit for Prior Year Minimum Tax — Corporations",
        "category": "federal_schedule",
    },
    "3800": {
        "form_name": "Form 3800",
        "description": "General Business Credit",
        "category": "federal_schedule",
    },
    "6765": {
        "form_name": "Form 6765",
        "description": "Credit for Increasing Research Activities (R&D Credit)",
        "category": "federal_schedule",
    },
    "8586": {
        "form_name": "Form 8586",
        "description": "Low-Income Housing Credit",
        "category": "federal_schedule",
    },
    "8594": {
        "form_name": "Form 8594",
        "description": "Asset Acquisition Statement Under Section 1060",
        "category": "federal_schedule",
    },
    "8621": {
        "form_name": "Form 8621",
        "description": "Information Return by a Shareholder of a Passive Foreign Investment Company or Qualified Electing Fund",
        "category": "federal_schedule",
    },
    "926": {
        "form_name": "Form 926",
        "description": "Return by a U.S. Transferor of Property to a Foreign Corporation",
        "category": "federal_schedule",
    },
    "8832": {
        "form_name": "Form 8832",
        "description": "Entity Classification Election",
        "category": "federal_schedule",
    },
    "7004": {
        "form_name": "Form 7004",
        "description": "Application for Automatic Extension of Time to File Certain Business Income Tax Returns",
        "category": "federal_schedule",
    },
    "2220": {
        "form_name": "Form 2220",
        "description": "Underpayment of Estimated Tax by Corporations",
        "category": "federal_schedule",
    },
    "8050": {
        "form_name": "Form 8050",
        "description": "Direct Deposit of Corporate Tax Refund",
        "category": "federal_schedule",
    },
    # ── Consolidated Group ────────────────────────────────────────────────────
    "851": {
        "form_name": "Form 851",
        "description": "Affiliations Schedule (required for consolidated returns)",
        "category": "consolidated_group",
    },
    "1122": {
        "form_name": "Form 1122",
        "description": "Authorization and Consent of Subsidiary Corporation to be Included in a Consolidated Income Tax Return",
        "category": "consolidated_group",
    },
    "1120-PC": {
        "form_name": "Form 1120-PC",
        "description": "U.S. Property and Casualty Insurance Company Income Tax Return (subsidiary)",
        "category": "consolidated_group",
    },
    "1120-L": {
        "form_name": "Form 1120-L",
        "description": "U.S. Life Insurance Company Income Tax Return (subsidiary)",
        "category": "consolidated_group",
    },
    # ── State Returns (common) — codes follow pattern STATE-FORM ─────────────
    "CA-100": {
        "form_name": "California Form 100",
        "description": "California Corporation Franchise or Income Tax Return",
        "category": "state_return",
        "state_code": "CA",
    },
    "NY-CT3": {
        "form_name": "New York Form CT-3",
        "description": "New York General Business Corporation Franchise Tax Return",
        "category": "state_return",
        "state_code": "NY",
    },
    "TX-05102": {
        "form_name": "Texas Form 05-102",
        "description": "Texas Franchise Tax Public Information Report",
        "category": "state_return",
        "state_code": "TX",
    },
    "IL-1120": {
        "form_name": "Illinois Form IL-1120",
        "description": "Illinois Corporation Income and Replacement Tax Return",
        "category": "state_return",
        "state_code": "IL",
    },
    "FL-F1120": {
        "form_name": "Florida Form F-1120",
        "description": "Florida Corporate Income/Franchise Tax Return",
        "category": "state_return",
        "state_code": "FL",
    },
    "NJ-CBT100": {
        "form_name": "New Jersey CBT-100",
        "description": "New Jersey Corporation Business Tax Return",
        "category": "state_return",
        "state_code": "NJ",
    },
    "PA-RCT101": {
        "form_name": "Pennsylvania RCT-101",
        "description": "Pennsylvania Corporate Net Income Tax Report",
        "category": "state_return",
        "state_code": "PA",
    },
    "OH-IT4708": {
        "form_name": "Ohio IT 4708",
        "description": "Ohio Pass-Through Entity / Trust Withholding Tax Return",
        "category": "state_return",
        "state_code": "OH",
    },
    "MA-355": {
        "form_name": "Massachusetts Form 355",
        "description": "Massachusetts Business/Manufacturing Corporation Excise Return",
        "category": "state_return",
        "state_code": "MA",
    },
    "GA-600": {
        "form_name": "Georgia Form 600",
        "description": "Georgia Corporation Income Tax Return",
        "category": "state_return",
        "state_code": "GA",
    },
    "VA-500": {
        "form_name": "Virginia Form 500",
        "description": "Virginia Corporation Income Tax Return",
        "category": "state_return",
        "state_code": "VA",
    },
    "WA-EXCISE": {
        "form_name": "Washington Business & Occupation Tax",
        "description": "Washington State Business and Occupation Tax Return",
        "category": "state_return",
        "state_code": "WA",
    },
}


def get_form(code: str) -> dict | None:
    """Look up a form by code (case-insensitive). Returns None if not found."""
    return FORM_REGISTRY.get(code) or FORM_REGISTRY.get(code.upper())


def all_codes() -> list[str]:
    return list(FORM_REGISTRY.keys())


CATEGORY_LABELS = {
    "core_1120": "Core Form 1120",
    "federal_schedule": "Federal Schedules & Attachments",
    "state_return": "State Returns",
    "consolidated_group": "Consolidated Group Forms",
}
