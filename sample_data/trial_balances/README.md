# Fictitious C-Corporation Trial Balances: GoSystem TRC/TCC Mapping

This folder holds 25 **fictitious** US C corporations. Each has a year-end, pre-closing trial balance for
**12/31/2024 and 12/31/2025**, exported in the layout of a popular accounting package, and every account is mapped to
**Thomson Reuters GoSystem Tax RS** Form 1120 trial balance codes. All names, EINs and amounts are invented.

## What's here

| Path | Contents |
|---|---|
| `index.xlsx` | Company list (industry, NAICS, state, source software, revenue, net income, total assets, M-3 flag), plus the TRC and TCC reference tables |
| `all_accounts_mapped.csv` | Every account at all 25 companies in one long table, with signed balances, TRC, TCC, MRC and Form 1120 line |
| `companies/Cxx_*/Cxx_TB_2024_<software>.csv` | Native trial balance export, 2024 |
| `companies/Cxx_*/Cxx_TB_2025_<software>.csv` | Native trial balance export, 2025 |
| `companies/Cxx_*/Cxx_GoSystem_TRC_TCC_Mapping.xlsx` | Mapping workbook. Tabs: **Mapping** (each account with Dr/Cr for both years, TRC, TCC, MRC, 1120 line and tax review notes), **1120 Rollup by TRC**, **TCC Detail** (line 26 and other itemizations), **GoSystem Import** (account / TRC / TCC / prior-year / current-year layout), **Proposed Tax AJEs** (1125-A inventory tie and bad debt reserve M-1 memo) and **Checks** (TB balance, RE roll-forward, M-3 flag, §448(c) receipts, NOL carryforward) |
| `research/` | Agent research: `gosystem_codes.json` (107 GoSystem codes, each flagged verified or not, with sources), `gosystem_codes_summary.md`, and `tb_formats.json` (export layouts for 8 packages) |
| `generator/` | Deterministic Python generator. Run `python build.py` (fixed seed) to rebuild everything |

## Companies

| ID | Company | State | Activity | TB source software | Net revenue 2024 | M-3 in 2025 (assets ≥ $10M) |
|---|---|---|---|---|---:|---|
| C01 | Ironbridge Precision Components, Inc. | OH | Machine shop / precision parts manufacturing | QuickBooks Online | 18,178,275 | Yes |
| C02 | Bluewater Industrial Supply Corp. | TX | Wholesale distribution of industrial supplies | QuickBooks Desktop | 32,154,751 | Yes |
| C03 | Maple & Thread Home Goods, Inc. | VT | Retail gift, novelty and home goods stores | QuickBooks Desktop | 3,967,163 | No |
| C04 | Granite Peak Builders, Inc. | CO | Commercial building general contractor | Xero | 27,900,001 | Yes |
| C05 | Nimbus Ledger Software, Inc. | CA | Software publisher - cloud subscription software | QuickBooks Desktop | 9,650,001 | No |
| C06 | Halvorsen Structural Engineering, P.C. | MN | Engineering services | Zoho Books | 6,300,001 | No |
| C07 | Copper Kettle Hospitality Group, Inc. | GA | Full-service restaurants | Oracle NetSuite | 5,424,851 | No |
| C08 | Prairie Line Logistics, Inc. | NE | General freight trucking, long-distance, truckload | Zoho Books | 21,300,000 | Yes |
| C09 | Riverbend Family Medicine, P.C. | NC | Offices of physicians | QuickBooks Online | 7,614,810 | No |
| C10 | Sterling Commons Properties, Inc. | AZ | Lessors of nonresidential buildings | QuickBooks Desktop | 3,260,000 | Yes |
| C11 | Fernwood Outdoor Co. | OR | Electronic shopping - consumer products | QuickBooks Online | 12,278,707 | No |
| C12 | Keystone Auto Care, Inc. | PA | General automotive repair | Sage 50 | 3,716,217 | No |
| C13 | Atlas Forge & Fabrication Co. | MI | Machine shop / precision parts manufacturing | Sage 50 | 44,044,126 | Yes |
| C14 | Silverline Medical Distributors, Inc. | NJ | Wholesale distribution of industrial supplies | Microsoft Dynamics 365 Business Central | 57,234,150 | Yes |
| C15 | Harborview Market & Deli, Inc. | MA | Retail gift, novelty and home goods stores | Sage 50 | 2,279,173 | No |
| C16 | Redstone Civil Contractors, Inc. | UT | Commercial building general contractor | Sage 50 | 15,700,001 | No |
| C17 | Quantum Orchard Analytics, Inc. | WA | Software publisher - cloud subscription software | Sage Intacct | 3,180,001 | No |
| C18 | Pemberton & Vale Consulting Group, Inc. | VA | Engineering services | Oracle NetSuite | 11,200,000 | No |
| C19 | Saguaro Grill Concepts, Inc. | NM | Full-service restaurants | Oracle NetSuite | 9,202,092 | No |
| C20 | Lakeshore Cold Chain Transport, Inc. | WI | General freight trucking, long-distance, truckload | Zoho Books | 8,450,000 | No |
| C21 | Tidewater Pediatric Associates, P.A. | FL | Offices of physicians | Sage Intacct | 4,952,460 | No |
| C22 | Old Mill Plaza Holdings, Inc. | IN | Lessors of nonresidential buildings | Microsoft Dynamics 365 Business Central | 1,980,000 | No |
| C23 | Brightpath Pet Supply, Inc. | TN | Electronic shopping - consumer products | Microsoft Dynamics 365 Business Central | 6,412,027 | No |
| C24 | Summit Ridge Collision & Repair, Inc. | ID | General automotive repair | Zoho Books | 2,862,074 | No |
| C25 | Cedar Hollow Millwork, Inc. | KY | Machine shop / precision parts manufacturing | Sage Intacct | 7,293,502 | No |

The source software was assigned at random with a fixed seed, and each of the 8 packages is used at least once.

## GoSystem code definitions

- **TRC: Tax Return Code.** Required for every account. Thomson Reuters defines these codes in the form `NN-NNN`, and each
  one ties an account to a return line. Ranges for the 1120: `10-`/`11-` Sch L assets, `20-`/`21-`/`22-` Sch L liabilities
  and equity, `30-`/`31-` page 1 income, `40-` Form 1125-A COGS, `41-` page 1 deductions, `60-` Sch M-1, `62-` Sch M-2.
- **TCC: Tax Combination Code.** Optional and defined by the firm (up to 3 characters). It is used with a TRC to group or
  itemize accounts within one line, for example the line 26 Other Deductions statement or the Sch L line 6, 14 and 18
  statements. The TCCs here (`UTL`, `PRO`, `FIN`, `OLI`, ...) are an **illustrative firm scheme**. Thomson Reuters
  publishes no standard TCC list.
- **MRC: M-3 Return Code** (I/E series). GoSystem allows these only on 30- and 40-range TRCs, so they are shown only
  there, as a partial reference. M-3 filers (7 companies) still need their full M-3 coding reviewed.

### Mapping conventions worth knowing

- **Retained earnings** in a pre-closing TB is the *beginning* balance (`22-310`). Each workbook's Checks tab proves that
  2025 beginning RE = 2024 beginning RE + 2024 net income − 2024 dividends.
- **Dividends paid** map to `62-308` (Sch M-2 line 5a).
- **Nondeductible items** map straight to M-1 codes so they stay off page 1: fines and penalties, officer life insurance,
  lobbying, club dues, and unrealized losses go to `60-240`; entertainment goes to `60-216`; unrealized gains go to `60-450`. Meals go to `41-810`, where GoSystem applies the
  50% limit itself. Federal income tax expense goes to `41-400` (M-1 line 2), and tax-exempt interest goes to `60-410`.
- **COGS expense accounts** map to 1125-A purchases, labor and other costs (`40-120`, `40-130`, `40-155`). Book COGS is
  already net of the inventory change, so each workbook's **Proposed Tax AJEs** tab gives the entry that makes 1125-A tie
  to book COGS: beginning inventory `40-110`, ending inventory `40-190`, and an EI − BI adjustment to purchases.
- **Book depreciation and amortization** are mapped as booked (`41-540`; `41-900`/`AMR`). Tax amounts come from the fixed
  asset module, and the difference flows to the M-1.
- Items to review are noted per account: §174/§174A R&E (2024 capitalization vs. 2025 domestic expensing), §163(j),
  §460, the bad debt reserve, ASC 842 ROU and lease liability, shareholder loans, and the DRD.

## Caveats

- Each Mapping row has a **TRC Source Confidence** column. "1120 list" means the code was seen on the 1120 list.
  "1120 family" means it was seen only on a related form's list (for example `41-900` and `62-308`). "snippet" means it
  was seen only in search snippets (`60-216`, `60-240`, `60-450`).
- **Verify the codes before using them on a live return.** Thomson Reuters' help sites were blocked from this
  environment, so the TRC values come from excerpts of the official GoSystem `1120_TRC_MRC` lists found by search, not
  the full PDFs. Every TRC used in the mappings was found in those excerpts. Confirm them against the current-year list.
- **Export layouts are best-effort.** Each package's layout (title rows, column headers, account display, total and footer
  wording) follows vendor documentation where it could be reached. Some header strings are inferred and are flagged in
  `research/tb_formats.json`.
- The book tax provisions are simplified but internally consistent. The federal provision uses 21% with NOL
  carryforwards (80% limit). It treats §174 R&E as capitalized in 2024 and expensed under §174A in 2025, and the
  deferred tax liability or asset rolls forward each year. State tax uses approximate statutory rates, with 100%
  apportioned to the home state. OH, TX and WA have no corporate income tax, so CAT, franchise (margin) and B&O tax is
  booked to Taxes & Licenses instead.
- Federal and state tax provisions, deferred taxes and the 2023 opening balances (used for the Intacct and Business
  Central opening and net-change columns) are simplified so the test data stays plausible. They are not provision-grade.
