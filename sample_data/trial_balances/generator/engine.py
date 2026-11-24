"""Builds balanced 2024 and 2025 year-end (pre-closing) trial balances.

Balances are integer cents, signed debit-positive.  Income-statement accounts
carry the full-year activity; Retained Earnings carries the *beginning* of year
balance, exactly as an unadjusted pre-closing trial balance does, so that
2025 beginning RE = 2024 beginning RE + 2024 net income - 2024 dividends.
"""
import random

from catalog import ACCOUNTS, BS_CLASSES, normal_side
from industries import COMMON_X, INDUSTRIES

YEARS = (2024, 2025)


def _c(dollars, rng, whole=False):
    """dollars -> cents with realistic odd cents."""
    if whole:
        return int(round(dollars)) * 100
    return int(round(dollars * 100)) + rng.randint(0, 99)


class Company:
    def __init__(self, cid, name, industry, state, revenue, growth, features, software, seed):
        self.cid, self.name, self.industry, self.state = cid, name, industry, state
        self.revenue, self.growth, self.features, self.software = revenue, growth, set(features), software
        self.rng = random.Random(seed)
        self.ind = INDUSTRIES[industry]
        self.bal = {y: {} for y in YEARS}     # key -> signed cents (debit +)
        self.names = {}
        self.ein = f"{self.rng.randint(20, 99)}-{self.rng.randint(1000000, 9999999)}"
        self.incorporated = self.rng.randint(1978, 2016)
        self.build()

    # ------------------------------------------------------------ helpers
    def set(self, year, key, cents_natural):
        """store an amount given in its *natural* sign (positive = normal balance)."""
        if cents_natural == 0:
            return
        cls = ACCOUNTS[key][1]
        self.bal[year][key] = self.bal[year].get(key, 0) + normal_side(cls) * cents_natural

    def nat(self, year, key):
        cls = ACCOUNTS[key][1]
        return normal_side(cls) * self.bal[year].get(key, 0)

    def u(self, lo, hi):
        return self.rng.uniform(lo, hi)

    # ------------------------------------------------------------ build
    def build(self):
        r, ind, f = self.rng, self.ind, self.features
        rev = {2024: self.revenue, 2025: self.revenue * self.growth * self.u(0.985, 1.015)}
        target_margin = {2024: self.u(-0.02, 0.11), 2025: self.u(-0.03, 0.12)}
        if r.random() < 0.75:  # most companies profitable both years
            target_margin = {y: abs(m) + 0.01 for y, m in target_margin.items()}
        scale_x = ind.get("scale_x", 1.0)

        # ratios fixed per company, drift modestly between years
        ratios = {}
        for k, (lo, hi) in {**ind["contra"], **ind["cogs"]}.items():
            ratios[k] = self.u(lo, hi)
        xr = {k: (lo * scale_x, hi * scale_x) for k, (lo, hi) in COMMON_X.items()}
        xr.update(ind.get("extra_x", {}))
        for k, (lo, hi) in xr.items():
            ratios[k] = self.u(lo, hi)
        if ind["revenue"].get("rental_rev"):
            for k in ("officer_comp", "salaries", "health_ins", "retirement", "rent", "workers_comp", "travel"):
                ratios[k] *= 0.35
            ratios["rent"] = 0
        optional = {"entertainment": (0.0005, 0.002), "club": (0.0003, 0.001), "penalties": (0.0001, 0.0006), "political": (0.0002, 0.0008)}
        for feat, rng_ in optional.items():
            if feat in f:
                ratios["club_dues" if feat == "club" else feat] = self.u(*rng_)

        # ----------------------------------------- fixed assets (2024 base)
        fixed_keys = ind["fixed_keys"]
        gross_total = self.revenue * self.u(*ind["fixed"])
        weights = {k: r.uniform(0.5, 1.5) * (3 if k in ("buildings", "machinery", "vehicles") else 1) for k in fixed_keys}
        if "land" in weights:
            weights["land"] *= 0.5
        wsum = sum(weights.values())
        gross = {2024: {k: gross_total * w / wsum for k, w in weights.items()}}
        depr_rate = 0.03 if self.industry == "real_estate" else self.u(0.08, 0.13)
        depreciable = lambda g: sum(v for k, v in g.items() if k != "land")
        accum = {2024: depreciable(gross[2024]) * self.u(0.30, 0.55)}
        depr = {2024: depreciable(gross[2024]) * depr_rate}
        capex = depreciable(gross[2024]) * self.u(0.05, 0.16)
        g25 = dict(gross[2024])
        disposal_gain = {2024: 0, 2025: 0}
        disposed_accum = 0
        if "gain" in f:
            dk = "vehicles" if "vehicles" in g25 else "machinery" if "machinery" in g25 else fixed_keys[0]
            cost = g25[dk] * self.u(0.06, 0.12)
            g25[dk] -= cost
            disposed_accum = cost * self.u(0.75, 0.95)
            disposal_gain[2025] = (cost - disposed_accum) * self.u(0.6, 1.8)
            disposal_gain[2024] = self.revenue * self.u(0.0005, 0.002)
        bump = r.choice([k for k in fixed_keys if k != "land"])
        g25[bump] += capex
        gross[2025] = g25
        depr[2025] = depreciable(g25) * depr_rate
        accum[2025] = accum[2024] + depr[2025] - disposed_accum

        # ----------------------------------------- intangibles
        has_gw = self.revenue > 15_000_000 and r.random() < 0.6 or self.cid in ("C18",)
        gw = self.revenue * self.u(0.04, 0.10) if has_gw else 0
        cust = gw * self.u(0.3, 0.6) if has_gw else 0
        sw = self.revenue * self.u(0.15, 0.30) if ind.get("software_cap") else 0
        amort_base = cust + sw
        amort = {2024: cust / 15 + sw / 3, 2025: cust / 15 + sw * 1.25 / 3}
        accum_amort = {2024: amort_base * self.u(0.2, 0.45)}
        accum_amort[2025] = accum_amort[2024] + amort[2025]

        # ----------------------------------------- debt
        net_fixed24 = sum(gross[2024].values()) - accum[2024]
        debt = {}
        if ind.get("mortgage"):
            debt["mortgage"] = net_fixed24 * self.u(0.45, 0.65)
        elif net_fixed24 > 0.12 * self.revenue:
            debt["note_bank"] = net_fixed24 * self.u(0.25, 0.5)
        if self.industry in ("trucking", "construction"):
            debt["equipment_loan"] = net_fixed24 * self.u(0.15, 0.3)
        amort_years = 25 if ind.get("mortgage") else 7
        debt_by_year = {2024: {k: v for k, v in debt.items()},
                        2025: {k: v * (1 - 1 / amort_years) for k, v in debt.items()}}
        has_loc = r.random() < 0.55

        for y in YEARS:
            R = rev[y]
            drift = (lambda: self.u(0.93, 1.07)) if y == 2025 else (lambda: 1.0)
            yr = {k: v * drift() for k, v in ratios.items()}
            # ------------------- revenue
            for k, share in ind["revenue"].items():
                self.set(y, k, _c(R * share, r))
            for k in ind["contra"]:
                self.set(y, k, _c(R * yr[k], r))
            net_rev = R * (1 - sum(yr[k] for k in ind["contra"]))
            for k in ind["cogs"]:
                self.set(y, k, _c(net_rev * yr[k], r))
            # ------------------- expenses (salaries is the balancing item)
            exp = {}
            for k in xr:
                if k in ("depreciation", "amortization", "interest_exp", "state_income_tax", "salaries"):
                    continue
                exp[k] = net_rev * yr[k]
            if "officer_comp" in exp:
                exp["officer_comp"] = min(exp["officer_comp"], self.u(240_000, 1_150_000) * (1 if y == 2024 else 1.04))
            for k in ("entertainment", "club_dues", "penalties", "political"):
                if k in yr:
                    exp[k] = net_rev * yr[k]
            if "life" in f:
                exp["officer_life"] = self.u(6_000, 28_000)
            if "bad_debt" not in exp and r.random() < 0.7 and ind["ar_days"][0] > 20:
                exp["bad_debt"] = net_rev * self.u(0.001, 0.004)
            if ind.get("rou"):
                exp["rent"] = exp.get("rent", net_rev * 0.03)
            exp["depreciation"] = depr[y]
            if amort[y]:
                exp["amortization"] = amort[y]
            total_debt = sum(debt_by_year[y].values())
            exp["interest_exp"] = total_debt * self.u(0.055, 0.08) + (self.revenue * 0.004 if has_loc else 0)
            # other income
            oth = {"interest_income": R * self.u(0.0002, 0.0012)}
            if "muni" in f:
                muni_bal = self.revenue * self.u(0.04, 0.08) * (1 if y == 2024 else 1.05)
                oth["muni_interest"] = muni_bal * self.u(0.025, 0.035)
            if "securities" in f:
                oth["dividend_income"] = self.revenue * self.u(0.002, 0.006)
                oth["unrealized_gain"] = self.revenue * self.u(-0.003, 0.006)
            if disposal_gain[y]:
                oth["gain_asset_sale"] = disposal_gain[y]
            if r.random() < 0.4:
                oth["other_income"] = R * self.u(0.0005, 0.003)
            cogs_total = sum(net_rev * yr[k] for k in ind["cogs"])
            pretax_wo_sal = net_rev - cogs_total - sum(exp.values()) + sum(oth.values())
            salaries = pretax_wo_sal - target_margin[y] * net_rev
            floor = net_rev * 0.06 * scale_x
            if salaries < floor:
                salaries = floor
            exp["salaries"] = salaries
            exp["payroll_taxes"] = (salaries + exp.get("officer_comp", 0) + net_rev * yr.get("cogs_labor", 0)) * self.u(0.072, 0.082)
            pretax = net_rev - cogs_total - sum(exp.values()) + sum(oth.values())
            state_tax = max(pretax, 0) * self.u(0.035, 0.065)
            exp["state_income_tax"] = state_tax
            pretax -= state_tax
            for k, v in exp.items():
                self.set(y, k, _c(v, r))
            for k, v in oth.items():
                if k == "unrealized_gain" and v < 0:
                    self.bal[y][k] = self.bal[y].get(k, 0) + _c(-v, r)  # debit = loss
                else:
                    self.set(y, k, _c(v, r))
            # federal provision (book): current on approx. taxable, deferred from DTL movement
            perm = exp.get("penalties", 0) + exp.get("political", 0) + exp.get("entertainment", 0) + exp.get("meals", 0) * 0.5 \
                + exp.get("officer_life", 0) + exp.get("club_dues", 0) - oth.get("muni_interest", 0)
            temp = depr[y] * self.u(-0.6, 0.1)  # bonus/179 accelerates tax depreciation
            fed_current = max(0.0, (pretax + perm + temp) * 0.21)
            fed_deferred = -temp * 0.21 if pretax > 0 else 0
            self.set(y, "federal_tax_current", _c(fed_current, r))
            if abs(fed_deferred) > 100:
                cents = _c(abs(fed_deferred), r)
                self.bal[y]["federal_tax_deferred"] = cents if fed_deferred > 0 else -cents
            ni = pretax - fed_current - fed_deferred
            self._store_ni(y, ni)
            self._fed = getattr(self, "_fed", {})
            self._fed[y] = (fed_current, fed_deferred)

            # ------------------- balance sheet
            g = gross[y]
            for k, v in g.items():
                self.set(y, k, _c(v, r, whole=True))
            self.set(y, "accum_depr", _c(accum[y], r))
            if gw:
                self.set(y, "goodwill", _c(gw, r, whole=True))
            if cust:
                self.set(y, "intangibles", _c(cust, r, whole=True))
            if sw:
                self.set(y, "software_cap", _c(sw * (1 if y == 2024 else 1.25), r))
            if amort_base:
                self.set(y, "accum_amort", _c(accum_amort[y], r))
            cogs_b = cogs_total if cogs_total else net_rev * 0.3
            ar = net_rev * self.u(*ind["ar_days"]) / 365
            if ind.get("construction"):
                self.set(y, "ar", _c(ar * 0.85, r))
                self.set(y, "ar_retainage", _c(ar * 0.15, r))
                self.set(y, "costs_in_excess", _c(net_rev * self.u(0.01, 0.03), r))
                self.set(y, "billings_in_excess", _c(net_rev * self.u(0.03, 0.06), r))
                self.set(y, "retainage_payable", _c(net_rev * self.u(0.02, 0.04), r))
            else:
                self.set(y, "ar", _c(ar, r))
            if ind["ar_days"][0] > 20:
                self.set(y, "allowance", _c(ar * self.u(0.01, 0.03), r))
            inv = cogs_b * self.u(*ind["inv_days"]) / 365 if ind["inv_days"][1] else 0
            if inv:
                if ind.get("inventory_split"):
                    self.set(y, "inventory_raw", _c(inv * 0.45, r))
                    self.set(y, "inventory_wip", _c(inv * 0.2, r))
                    self.set(y, "inventory_fg", _c(inv * 0.35, r))
                else:
                    self.set(y, "inventory", _c(inv, r))
            self.set(y, "prepaid", _c(net_rev * self.u(0.003, 0.01), r))
            self.set(y, "prepaid_insurance", _c(exp.get("insurance", 0) * self.u(0.2, 0.5), r))
            if r.random() < 0.3:
                self.set(y, "employee_adv", _c(self.u(800, 6000), r))
            self.set(y, "deposits", _c(net_rev * self.u(0.001, 0.004), r, whole=True))
            if "muni" in f:
                self.set(y, "invest_muni", _c(oth["muni_interest"] / 0.03, r, whole=True))
            if "securities" in f:
                self.set(y, "invest_securities", _c(self.revenue * self.u(0.05, 0.12) * (1 if y == 2024 else 1.04), r))
            if "life" in f:
                self.set(y, "csv_life", _c(self.u(40_000, 160_000) * (1 if y == 2024 else 1.08), r))
            if "loan_to_sh" in f:
                self.set(y, "loan_to_sh", _c(self.u(25_000, 120_000), r, whole=True))
            if ind.get("rou"):
                rou = exp["rent"] * self.u(2.5, 4.5)
                self.set(y, "rou_asset", _c(rou, r))
                self.set(y, "lease_liability", _c(rou * self.u(1.02, 1.08), r))
            # liabilities
            self.set(y, "ap", _c(cogs_b * self.u(*ind["ap_days"]) / 365 + net_rev * 0.01, r))
            self.set(y, "credit_card", _c(net_rev * self.u(0.001, 0.004), r))
            self.set(y, "accrued_payroll", _c(salaries * self.u(1.0, 2.5) / 52, r))
            self.set(y, "payroll_liab", _c(exp["payroll_taxes"] * self.u(0.03, 0.06), r))
            if ind.get("sales_tax"):
                self.set(y, "sales_tax", _c(net_rev * self.u(0.004, 0.009), r))
            self.set(y, "accrued_exp", _c(net_rev * self.u(0.004, 0.012), r))
            if ind.get("deferred_rev"):
                self.set(y, "deferred_rev", _c(net_rev * self.u(*ind["deferred_rev"]), r))
            if self.industry in ("manufacturing", "wholesale") and r.random() < 0.5:
                self.set(y, "customer_deposits", _c(net_rev * self.u(0.005, 0.015), r))
            # income taxes payable / prepaid
            paid_frac = self.u(0.75, 1.15)
            bal_due = fed_current * (1 - paid_frac)
            if bal_due >= 0:
                self.set(y, "income_tax_payable", _c(bal_due, r))
            else:
                self.set(y, "prepaid_tax", _c(-bal_due, r))
            if state_tax:
                self.set(y, "state_tax_payable", _c(state_tax * self.u(0.05, 0.25), r))
            for k, v in debt_by_year[y].items():
                cur = v / amort_years if k != "mortgage" else v / amort_years * 0.8
                self.set(y, k, _c(v - cur, r))
                self.bal[y]["current_ltd"] = self.bal[y].get("current_ltd", 0) - _c(cur, r)
            if "due_to_sh" in f:
                self.set(y, "due_to_sh", _c(self.u(40_000, 180_000), r, whole=True))
            dtl_base = (sum(gross[y].values()) - accum[y]) * 0.21 * 0.25
            if dtl_base > 20_000:
                self.set(y, "dtl", _c(dtl_base, r))
            # equity
            if y == 2024:
                self.cs = self.rng.choice([1_000, 10_000, 25_000, 100_000, 500_000])
                self.apic = self.revenue * self.u(0.0, 0.08) if r.random() < 0.6 else 0
                self.pref = self.revenue * self.u(0.15, 0.4) if "preferred" in f else 0
                self.treasury = self.revenue * self.u(0.005, 0.015) if "treasury" in f else 0
                if self.industry == "real_estate":
                    self.re_begin = {2024: sum(gross[2024].values()) * self.u(0.15, 0.35)}
                else:
                    self.re_begin = {2024: self.revenue * self.u(0.10, 0.35)}
                if self.industry == "saas":
                    self.re_begin[2024] = -self.revenue * self.u(0.1, 0.4)
            else:
                if self.industry == "saas":
                    self.apic *= 1.0
                    self.pref *= 1.5 if self.pref else 1
            self.set(y, "common_stock", _c(self.cs, r, whole=True))
            if self.apic:
                self.set(y, "apic", _c(self.apic, r, whole=True))
            if self.pref:
                self.set(y, "preferred_stock", _c(self.pref, r, whole=True))
            if self.treasury:
                self.set(y, "treasury_stock", _c(self.treasury, r, whole=True))
            div = 0
            if "dividends" in f and ni > 0:
                div = ni * self.u(0.25, 0.6)
                self.set(y, "dividends", _c(div, r, whole=True))
            if y == 2025:
                re24 = self.bal[2024]["retained_earnings"]  # signed (credit negative)
                ni24 = -sum(v for k, v in self.bal[2024].items() if ACCOUNTS[k][1] not in BS_CLASSES)
                div24 = self.bal[2024].get("dividends", 0)
                self.bal[y]["retained_earnings"] = re24 - ni24 + div24
            else:
                self.bal[y]["retained_earnings"] = -_c(self.re_begin[2024], r, whole=True)
            # ------------------- cash plug and line of credit
            self._plug_cash(y, net_rev, has_loc)

    def _store_ni(self, y, ni):
        self.ni = getattr(self, "ni", {})
        self.ni[y] = ni

    def _plug_cash(self, y, net_rev, has_loc):
        r = self.rng
        b = self.bal[y]
        imbalance = sum(b.values())  # debits - credits, must become 0
        cash_needed = -imbalance
        min_cash = net_rev * self.u(0.02, 0.06)
        if cash_needed < min_cash * 100:
            draw = int(min_cash * 100 - cash_needed)
            draw = (draw // 100_000 + 1) * 100_000  # round $1,000
            b["loc"] = b.get("loc", 0) - draw
            cash_needed += draw
        elif has_loc and y == 2025 and r.random() < 0.5:
            draw = int(net_rev * self.u(0.01, 0.03)) * 100
            b["loc"] = b.get("loc", 0) - draw
            cash_needed += draw
        petty = 50_000 if self.industry in ("restaurant", "retail", "auto_dealer_service") else 0
        payroll = int(cash_needed * self.u(0.04, 0.10))
        savings = int(cash_needed * self.u(0.10, 0.30)) if net_rev > 4_000_000 else 0
        b["petty_cash"] = petty if petty else 0
        b["cash_payroll"] = payroll
        if savings:
            b["cash_savings"] = savings
        b["cash_operating"] = cash_needed - petty - payroll - savings
        for k in [k for k, v in b.items() if v == 0]:
            del b[k]
        assert sum(b.values()) == 0, (self.cid, y, sum(b.values()))

    # ------------------------------------------------------------ outputs
    def keys(self):
        ks = set(self.bal[2024]) | set(self.bal[2025])
        order = list(ACCOUNTS)
        return sorted(ks, key=order.index)

    def account_name(self, key):
        return ACCOUNTS[key][0]

    def net_income(self, y):
        return -sum(v for k, v in self.bal[y].items() if ACCOUNTS[k][1] not in BS_CLASSES)
