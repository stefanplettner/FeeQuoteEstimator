"""Industry templates: which accounts a company uses and how big they are.

Ratios are fractions of net revenue (low, high).  Balance-sheet drivers are
expressed in days (of revenue or COGS) or as fractions of revenue.
"""

# expense keys common to almost every company, with ratio ranges
COMMON_X = {
    "officer_comp": (0.03, 0.08), "salaries": (0.10, 0.20), "payroll_taxes": (0.012, 0.022),
    "health_ins": (0.010, 0.025), "retirement": (0.003, 0.008), "rent": (0.015, 0.04),
    "repairs": (0.002, 0.008), "taxes_licenses": (0.001, 0.003), "state_income_tax": (0.0, 0.0),
    "interest_exp": (0.0, 0.0), "depreciation": (0.0, 0.0), "advertising": (0.004, 0.015),
    "bank_fees": (0.0003, 0.001), "charitable": (0.0005, 0.002), "dues_subs": (0.0005, 0.002),
    "insurance": (0.004, 0.012), "workers_comp": (0.002, 0.006), "meals": (0.001, 0.004),
    "office_supplies": (0.001, 0.004), "professional_fees": (0.002, 0.006), "legal_fees": (0.0005, 0.003),
    "software": (0.002, 0.008), "telephone": (0.001, 0.003), "travel": (0.001, 0.006),
    "utilities": (0.002, 0.008), "misc_exp": (0.0002, 0.001),
}

INDUSTRIES = {
    "manufacturing": dict(
        naics="332700", activity="Machine shop / precision parts manufacturing",
        revenue={"sales": 0.97, "sales_online": 0.03}, contra={"sales_returns": (0.005, 0.012), "sales_discounts": (0.002, 0.006)},
        cogs={"cogs_materials": (0.30, 0.36), "cogs_labor": (0.14, 0.18), "cogs_overhead": (0.07, 0.10), "cogs_freight_in": (0.008, 0.015), "inventory_adj": (0.001, 0.004)},
        extra_x={"freight_out": (0.008, 0.015), "research": (0.004, 0.012), "uniforms": (0.001, 0.002)},
        inventory_split=True, ar_days=(42, 58), inv_days=(60, 95), ap_days=(30, 45), fixed=(0.35, 0.55),
        fixed_keys=["land", "buildings", "machinery", "furniture", "vehicles", "computers"], sales_tax=False),
    "wholesale": dict(
        naics="423400", activity="Wholesale distribution of industrial supplies",
        revenue={"sales_wholesale": 0.92, "sales_online": 0.08}, contra={"sales_returns": (0.008, 0.015), "sales_discounts": (0.004, 0.009)},
        cogs={"cogs": (0.70, 0.76), "cogs_freight_in": (0.01, 0.02), "inventory_adj": (0.001, 0.003)},
        extra_x={"freight_out": (0.012, 0.02), "merchant_fees": (0.002, 0.004)}, scale_x=0.6,
        ar_days=(35, 50), inv_days=(45, 75), ap_days=(30, 50), fixed=(0.06, 0.12),
        fixed_keys=["machinery", "furniture", "vehicles", "computers", "leasehold"], sales_tax=True),
    "retail": dict(
        naics="453220", activity="Retail gift, novelty and home goods stores",
        revenue={"sales": 0.82, "sales_online": 0.18}, contra={"sales_returns": (0.015, 0.03), "sales_discounts": (0.01, 0.02)},
        cogs={"cogs": (0.52, 0.58), "cogs_freight_in": (0.01, 0.02), "inventory_adj": (0.004, 0.01)},
        extra_x={"merchant_fees": (0.018, 0.026), "janitorial": (0.002, 0.004), "postage": (0.004, 0.008)},
        ar_days=(2, 6), inv_days=(75, 120), ap_days=(20, 35), fixed=(0.08, 0.15),
        fixed_keys=["furniture", "computers", "leasehold", "vehicles"], sales_tax=True, rou=True),
    "construction": dict(
        naics="236220", activity="Commercial building general contractor",
        revenue={"contract_rev": 1.0}, contra={},
        cogs={"cogs_subs": (0.42, 0.50), "cogs_materials": (0.16, 0.22), "cogs_labor": (0.10, 0.14), "cogs_equipment_rental": (0.01, 0.025)},
        extra_x={"auto": (0.006, 0.012), "uniforms": (0.0005, 0.001)}, scale_x=0.55,
        ar_days=(45, 70), inv_days=(0, 0), ap_days=(35, 55), fixed=(0.06, 0.14), construction=True,
        fixed_keys=["machinery", "vehicles", "furniture", "computers"], sales_tax=False),
    "saas": dict(
        naics="513210", activity="Software publisher - cloud subscription software",
        revenue={"subscription_rev": 0.85, "consulting_rev": 0.15}, contra={},
        cogs={"cogs_hosting": (0.08, 0.12), "cogs_labor": (0.07, 0.10)},
        extra_x={"research": (0.12, 0.20), "contract_labor": (0.02, 0.05), "consulting_fees": (0.005, 0.015), "amortization": (0, 0)}, scale_x=1.25,
        ar_days=(30, 50), inv_days=(0, 0), ap_days=(20, 35), fixed=(0.03, 0.06), deferred_rev=(0.20, 0.32),
        fixed_keys=["computers", "furniture", "leasehold"], software_cap=True, sales_tax=False, rou=True),
    "prof_services": dict(
        naics="541330", activity="Engineering services",
        revenue={"consulting_rev": 0.94, "service_rev": 0.06}, contra={},
        cogs={}, extra_x={"contract_labor": (0.04, 0.09), "training": (0.002, 0.006), "auto": (0.003, 0.008)}, scale_x=2.2,
        ar_days=(50, 75), inv_days=(0, 0), ap_days=(15, 30), fixed=(0.03, 0.07),
        fixed_keys=["computers", "furniture", "leasehold", "vehicles"], sales_tax=False, rou=True),
    "restaurant": dict(
        naics="722511", activity="Full-service restaurants",
        revenue={"food_sales": 0.74, "beverage_sales": 0.26}, contra={"sales_discounts": (0.005, 0.012)},
        cogs={"cogs_food": (0.27, 0.31), "cogs_beverage": (0.06, 0.08)},
        extra_x={"merchant_fees": (0.022, 0.03), "janitorial": (0.005, 0.01), "uniforms": (0.001, 0.003)}, scale_x=1.35,
        ar_days=(1, 4), inv_days=(6, 12), ap_days=(12, 20), fixed=(0.20, 0.35),
        fixed_keys=["machinery", "furniture", "leasehold", "computers"], sales_tax=True, rou=True),
    "trucking": dict(
        naics="484121", activity="General freight trucking, long-distance, truckload",
        revenue={"freight_rev": 1.0}, contra={},
        cogs={"cogs_fuel": (0.22, 0.28), "cogs_labor": (0.24, 0.30), "cogs_subs": (0.04, 0.09)},
        extra_x={"auto": (0.03, 0.05), "uniforms": (0.0005, 0.001)}, scale_x=0.55,
        ar_days=(28, 40), inv_days=(0, 0), ap_days=(15, 30), fixed=(0.45, 0.70),
        fixed_keys=["land", "buildings", "vehicles", "machinery", "computers"], sales_tax=False),
    "healthcare": dict(
        naics="621111", activity="Offices of physicians",
        revenue={"patient_rev": 1.0}, contra={"sales_discounts": (0.02, 0.04)},
        cogs={"cogs_medical_supplies": (0.05, 0.08)},
        extra_x={"contract_labor": (0.01, 0.03), "training": (0.002, 0.005), "janitorial": (0.003, 0.006)}, scale_x=2.0,
        ar_days=(35, 55), inv_days=(0, 0), ap_days=(15, 25), fixed=(0.10, 0.20),
        fixed_keys=["machinery", "furniture", "computers", "leasehold"], sales_tax=False, rou=True),
    "real_estate": dict(
        naics="531120", activity="Lessors of nonresidential buildings",
        revenue={"rental_rev": 1.0}, contra={},
        cogs={}, extra_x={"property_tax": (0.08, 0.12), "janitorial": (0.02, 0.04)}, scale_x=0.5,
        ar_days=(5, 15), inv_days=(0, 0), ap_days=(10, 20), fixed=(5.0, 7.0),
        fixed_keys=["land", "buildings", "furniture"], sales_tax=False, mortgage=True),
    "ecommerce": dict(
        naics="454110", activity="Electronic shopping - consumer products",
        revenue={"sales_online": 1.0}, contra={"sales_returns": (0.03, 0.06), "sales_discounts": (0.01, 0.02)},
        cogs={"cogs": (0.45, 0.52), "cogs_freight_in": (0.015, 0.025), "inventory_adj": (0.003, 0.008)},
        extra_x={"merchant_fees": (0.025, 0.032), "postage": (0.05, 0.08), "advertising": (0.06, 0.10)}, scale_x=0.8,
        ar_days=(3, 8), inv_days=(60, 100), ap_days=(25, 40), fixed=(0.02, 0.05),
        fixed_keys=["computers", "furniture", "machinery"], sales_tax=True),
    "auto_dealer_service": dict(
        naics="811111", activity="General automotive repair",
        revenue={"service_rev": 0.62, "sales": 0.38}, contra={"sales_discounts": (0.005, 0.01)},
        cogs={"cogs": (0.24, 0.30), "cogs_labor": (0.18, 0.22)},
        extra_x={"uniforms": (0.002, 0.004), "merchant_fees": (0.015, 0.02)}, scale_x=1.1,
        ar_days=(10, 20), inv_days=(30, 50), ap_days=(20, 30), fixed=(0.15, 0.25),
        fixed_keys=["machinery", "vehicles", "furniture", "computers", "leasehold"], sales_tax=True, rou=True),
}
