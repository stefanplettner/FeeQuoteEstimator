"""25 fictitious US C corporations.  All names, EINs and figures are invented.

revenue_2024 is gross revenue in dollars.  growth is the 2025/2024 revenue
multiple.  features toggle optional accounts that create book-tax differences.
"""

COMPANIES = [
    # id, name, industry, state, revenue_2024, growth, features
    ("C01", "Ironbridge Precision Components, Inc.", "manufacturing", "OH", 18_400_000, 1.06, {"muni", "life", "penalties", "dividends"}),
    ("C02", "Bluewater Industrial Supply Corp.", "wholesale", "TX", 32_750_000, 1.04, {"dividends", "entertainment"}),
    ("C03", "Maple & Thread Home Goods, Inc.", "retail", "VT", 4_120_000, 0.97, {"loan_to_sh"}),
    ("C04", "Granite Peak Builders, Inc.", "construction", "CO", 27_900_000, 1.12, {"penalties", "gain"}),
    ("C05", "Nimbus Ledger Software, Inc.", "saas", "CA", 9_650_000, 1.28, {"securities", "preferred"}),
    ("C06", "Halvorsen Structural Engineering, P.C.", "prof_services", "MN", 6_300_000, 1.05, {"life", "club"}),
    ("C07", "Copper Kettle Hospitality Group, Inc.", "restaurant", "GA", 5_480_000, 1.03, {"entertainment", "due_to_sh"}),
    ("C08", "Prairie Line Logistics, Inc.", "trucking", "NE", 21_300_000, 0.94, {"gain", "penalties"}),
    ("C09", "Riverbend Family Medicine, P.C.", "healthcare", "NC", 7_850_000, 1.07, {"life", "dividends"}),
    ("C10", "Sterling Commons Properties, Inc.", "real_estate", "AZ", 3_260_000, 1.03, {"muni", "dividends"}),
    ("C11", "Fernwood Outdoor Co.", "ecommerce", "OR", 12_900_000, 1.15, {"securities"}),
    ("C12", "Keystone Auto Care, Inc.", "auto_dealer_service", "PA", 3_740_000, 1.02, {"loan_to_sh", "entertainment"}),
    ("C13", "Atlas Forge & Fabrication Co.", "manufacturing", "MI", 44_600_000, 0.98, {"muni", "political", "dividends", "treasury"}),
    ("C14", "Silverline Medical Distributors, Inc.", "wholesale", "NJ", 58_200_000, 1.09, {"securities", "life", "political"}),
    ("C15", "Harborview Market & Deli, Inc.", "retail", "MA", 2_350_000, 1.01, {"due_to_sh"}),
    ("C16", "Redstone Civil Contractors, Inc.", "construction", "UT", 15_700_000, 0.91, {"gain", "club"}),
    ("C17", "Quantum Orchard Analytics, Inc.", "saas", "WA", 3_180_000, 1.45, {"preferred"}),
    ("C18", "Pemberton & Vale Consulting Group, Inc.", "prof_services", "VA", 11_200_000, 1.08, {"life", "entertainment", "dividends"}),
    ("C19", "Saguaro Grill Concepts, Inc.", "restaurant", "NM", 9_300_000, 1.06, {"penalties"}),
    ("C20", "Lakeshore Cold Chain Transport, Inc.", "trucking", "WI", 8_450_000, 1.10, {"gain", "loan_to_sh"}),
    ("C21", "Tidewater Pediatric Associates, P.A.", "healthcare", "FL", 5_100_000, 1.04, {"dividends", "club"}),
    ("C22", "Old Mill Plaza Holdings, Inc.", "real_estate", "IN", 1_980_000, 1.02, {"securities"}),
    ("C23", "Brightpath Pet Supply, Inc.", "ecommerce", "TN", 6_750_000, 0.92, {"penalties"}),
    ("C24", "Summit Ridge Collision & Repair, Inc.", "auto_dealer_service", "ID", 2_890_000, 1.05, {"due_to_sh", "life"}),
    ("C25", "Cedar Hollow Millwork, Inc.", "manufacturing", "KY", 7_400_000, 1.03, {"gain", "muni", "club"}),
]

# Accounting packages whose trial-balance export layouts are reproduced.
SOFTWARE = [
    "QuickBooks Online",
    "QuickBooks Desktop",
    "Xero",
    "Sage Intacct",
    "Oracle NetSuite",
    "Microsoft Dynamics 365 Business Central",
    "Sage 50",
    "Zoho Books",
]
