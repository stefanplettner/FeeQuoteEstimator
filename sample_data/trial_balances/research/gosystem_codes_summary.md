# GoSystem Tax RS trial balance codes for Form 1120: summary

## Definitions (verified)
- **TRC = Tax Return Code.** Thomson Reuters assigns it, and every account needs one. The format is `NN-NNN`, and it ties a trial balance account to a return line.
  An account with no TRC is left out of the trial balance totals. It does not stand for "Tax Reconciliation Code".
- **TCC = Tax Combination Code.** It is optional, user-defined and up to 3 characters long. It is used together with a TRC to group or itemize the accounts on one line, for example the line 26 Other Deductions statement.
  It is required for cross-tie printing on 1120 consolidated returns. Its descriptions are edited under TCC/PC/MCC Descriptions. It does not stand for "Tax Code Category".
- **MRC = M-3 Return Code** (related). It uses I-series and E-series codes and is allowed only on accounts with a 30-range or 40-range TRC.

## TRC ranges
| Range | Section |
|---|---|
| 10-xxx / 11-xxx | Sch L assets (current / noncurrent) |
| 20-xxx / 21-xxx / 22-xxx | Sch L current liabilities / long-term liabilities / equity |
| 30-xxx / 31-xxx | Page 1 income (gross receipts / other income items) |
| 40-xxx | COGS (Form 1125-A) |
| 41-xxx | Page 1 deductions |
| 60-xxx | Schedule M-1 |
| 62-xxx | Schedule M-2 |

## Key codes (verified from excerpts of the official TR/RIA TRC sheets)
- Sch L: 10-100 Cash; 10-200/10-205 AR and allowance; 10-300 Inventory; 10-400 US govt obligations; 10-500 Tax-exempt securities; 10-900 Other current assets.
- Sch L: 11-100 Loans to shareholders; 11-500/11-505 Buildings and accumulated depreciation; 11-700 Land; 11-800..11-835 Intangibles and amortization; 11-900 Other assets.
- Sch L: 20-100 AP; 20-200 Short-term notes; 21-100 Shareholder loans; 21-200 Long-term notes; 21-300 Other liabilities.
- Sch L: 22-100/22-110 Preferred/common stock; 22-200 APIC; 22-300/22-310 Retained earnings; 22-400 Adjustments; 22-440 Treasury stock.
- Income: 30-100 Gross receipts; 30-105 Returns; 31-110..31-180 Dividends; 31-340/31-380 Interest; 31-420 Rents; 31-520 Royalties.
- Income: 31-620 Capital gains; 31-660 Form 4797 gain; 31-900 Other income.
- COGS: 40-110 Beginning inventory; 40-120 Purchases; 40-130 Labor; 40-140 Sec. 263A costs; 40-155 Other costs; 40-190 Ending inventory.
- Deductions: 41-210 Officer compensation; 41-220 Wages; 41-260 Repairs; 41-300 Bad debts; 41-350 Rents; 41-400 Federal income tax (book); 41-420 Taxes and licenses.
- Deductions: 41-500 Interest; 41-520 Contributions; 41-530 Insurance; 41-540 Depreciation; 41-560 Depletion; 41-580 Advertising; 41-600 Pension; 41-620 Employee benefits.
- Deductions: 41-810 Meals and entertainment; 41-812 Travel; 41-900 Other deductions.
- M-1: 60-110 Federal income tax; 60-150 Taxable income not on the books; 60-210 Depreciation, book over tax; 60-213 Contributions, book over tax; 60-216 Travel and entertainment; 60-240 Other nondeductible book expenses.
- M-1: 60-410 Tax-exempt interest; 60-450 Other book income; 60-510 Depreciation, tax over book.
- M-2: 62-300 Other increases; 62-302 Other decreases; 62-306/62-308/62-310 Distributions (property / cash / stock).
- M-3 MRCs: E550 Current federal income tax expense; E650 Meals; E660 Fines; E700 Pension; E730 Contributions; I160 Dividends; I220.05 Interest.

## Gaps and inferences (verified:false)
- The line 26 detail (utilities, professional fees, office expense, fines, officer life insurance) has no confirmed dedicated TRC.
  The documented convention is TRC 41-900, or the closest 41-xxx code, subdivided by firm-defined TCCs. Nondeductible items are added back through 60-240.
- 11-605 accumulated depletion, 40-150, 60-130 capital loss excess, 60-520 M-1 L8b and 31-300 tax-exempt interest income are inferred.
- All TCC entries are illustrative, because TCCs are defined by each firm and have no canonical list.

## How the codes were verified
- The Thomson Reuters and riahelp.com hosts were blocked in this sandbox, so the full PDFs could not be downloaded.
  Values come from search-engine excerpts of the official PDFs, chiefly 1120_TRC_MRC.pdf, 1125A_TRC.pdf, 1120_MRC.pdf and TRC_All.pdf.
- Several codes were seen only on the 1120-C, 1120S, 1120-RIC or 1120-REIT sheets. The `note` field on each code says which sheet it came from.
- The line numbers were mapped to the current Form 1120 layout, which should be checked.
- Workpapers CS, Accounting CS and UltraTax use a different numeric scheme (for example 100 for gross receipts and 101 for returns), so do not mix it with GoSystem codes.
- Before production use, confirm the codes against 1120_TRC_MRC.pdf for the target tax year.

Data: gosystem_codes.json (107 codes, 92 marked verified).
