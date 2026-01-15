from typing import Optional

from .main import FinancingType, PropertyInvestment


class PropertyInvestmentReporter:
    """Handles all reporting and output formatting for property investments"""

    def __init__(self, investment: PropertyInvestment):
        self.investment = investment
        self.acquisition = investment.acquisition_costs
        self.financing = investment.financing
        self.operating = investment.operating
        self.strategy = investment.strategy

    def print_full_report(self) -> None:
        """Print the complete investment analysis report"""
        self._print_header()
        self._print_property_details()
        self._print_financing_details()
        self._print_operating_details()
        self._print_investment_strategy()
        self._print_monthly_analysis()
        self._print_annual_analysis()

    def _print_header(self) -> None:
        """Print the report header"""
        print("=" * 60)
        print("PROPERTY INVESTMENT ANALYSIS")
        print("=" * 60)

    def _print_property_details(self) -> None:
        """Print property acquisition details"""
        print("\n📍 PROPERTY DETAILS:")
        print(
            f"   Purchase Price:              R{self.acquisition.purchase_price:,.0f}"
        )
        print(f"   Transfer Duty:               R{self.acquisition.transfer_duty:,.0f}")
        print(
            f"   Conveyancing Fees:           R{self.acquisition.conveyancing_fees:,.0f}"
        )
        print(
            f"   Bond Registration:           R{self.acquisition.bond_registration:,.0f}"
        )
        print(
            f"   Furnishing Cost:             R{self.acquisition.furnishing_cost:,.0f}"
        )
        print(
            f"   Total Cost (Unfurnished):    R{self.acquisition.total_unfurnished_cost:,.0f}"
        )
        print(
            f"   Total Cost (Furnished):      R{self.acquisition.total_furnished_cost:,.0f}"
        )

    def _print_financing_details(self) -> None:
        """Print financing and loan details"""
        print("\n💰 FINANCING DETAILS:")
        print(
            f"   Financing Type:              {self.financing.financing_type.value.title()}"
        )
        print(f"   LTV Ratio:                   {self.financing.ltv_ratio:.1%}")

        if self.financing.interest_rate:
            print(f"   Interest Rate:               {self.financing.interest_rate:.1%}")
        else:
            print("   Interest Rate:               N/A (Cash)")

        if self.financing.loan_term_years:
            print(
                f"   Loan Term:                   {self.financing.loan_term_years} years"
            )
        else:
            print("   Loan Term:                   N/A (Cash)")

        print(f"   Property Appreciation Rate:  {self.financing.appreciation_rate:.1%}")
        print(
            f"   Initial Cash Required:       R{self.investment.initial_cash_required:,.0f}"
        )

    def _print_operating_details(self) -> None:
        """Print operating income and expense details"""
        print("\n🏠 OPERATING DETAILS:")
        print(
            f"   Monthly Rental Income:       R{self.operating.monthly_rental_income:,.0f}"
        )
        print(f"   Vacancy Rate:                {self.operating.vacancy_rate:.1%}")
        print(
            f"   Property Management Fee:     {self.operating.property_management_fee_rate:.1%}"
        )
        print(f"   Monthly Levies:              R{self.operating.monthly_levies:,.0f}")
        print(
            f"   Monthly Insurance:           R{self.operating.monthly_insurance:,.0f}"
        )
        print(
            f"   Monthly Maintenance:         R{self.operating.monthly_maintenance_reserve:,.0f}"
        )
        print(
            f"   Monthly Furnishing Repairs:  R{self.operating.monthly_furnishing_repair_costs:,.0f}"
        )

    def _print_investment_strategy(self) -> None:
        """Print investment strategy details"""
        print("\n📈 INVESTMENT STRATEGY:")
        print(
            f"   Available Investment:        R{self.strategy.available_investment_amount:,.0f}"
        )
        print(
            f"   Reinvest Cashflow:           {'Yes' if self.strategy.reinvest_cashflow else 'No'}"
        )
        print(
            f"   Refinancing Enabled:         {'Yes' if self.strategy.enable_refinancing else 'No'}"
        )

        if self.strategy.enable_refinancing:
            print(
                f"   Refinance Frequency:         {self.strategy.refinance_frequency.value.replace('_', ' ').title()}"
            )
            print(
                f"   Target Refinance LTV:        {self.strategy.target_refinance_ltv:.1%}"
            )

    def _print_monthly_analysis(self) -> None:
        """Print monthly income, expense, and cash flow analysis"""
        print("\n" + "=" * 60)
        print("MONTHLY INCOME & EXPENSE ANALYSIS")
        print("=" * 60)

        # Monthly Income
        print("\n📊 MONTHLY INCOME:")
        print(
            f"   Gross Rental Income:         R{self.operating.monthly_rental_income:,.0f}"
        )
        vacancy_amount = (
            self.operating.monthly_rental_income * self.operating.vacancy_rate
        )
        print(
            f"   Less: Vacancy ({self.operating.vacancy_rate:.1%}):        -R{vacancy_amount:,.0f}"
        )
        print(
            f"   Effective Rental Income:     R{self.operating.effective_monthly_rental:,.0f}"
        )

        # Monthly Expenses
        print("\n📊 MONTHLY EXPENSES:")
        print(f"   Levies:                      R{self.operating.monthly_levies:,.0f}")
        print(
            f"   Property Management Fee:     R{self.operating.monthly_management_fee:,.0f}"
        )
        print(
            f"   Insurance:                   R{self.operating.monthly_insurance:,.0f}"
        )
        print(
            f"   Maintenance Reserve:         R{self.operating.monthly_maintenance_reserve:,.0f}"
        )
        print(
            f"   Furnishing Repairs:          R{self.operating.monthly_furnishing_repair_costs:,.0f}"
        )

        if self.investment.monthly_bond_payment:
            print(
                f"   Bond Payment:                R{self.investment.monthly_bond_payment:,.0f}"
            )

        total_monthly_expenses = self.operating.total_monthly_expenses + (
            self.investment.monthly_bond_payment or 0
        )
        print(f"   Total Monthly Expenses:      R{total_monthly_expenses:,.0f}")

        # Monthly Cash Flow
        print("\n📊 MONTHLY CASH FLOW:")
        print(
            f"   Net Monthly Cash Flow:       R{self.investment.monthly_cashflow:,.0f}"
        )

        # Cash on Cash Return
        print("\n📊 CASH ON CASH RETURN:")
        annual_cashflow = self.investment.monthly_cashflow * 12
        cash_on_cash_return = self._calculate_cash_on_cash_return(annual_cashflow)
        print(f"   Annual Cash Flow:            R{annual_cashflow:,.0f}")
        print(
            f"   Initial Cash Investment:     R{self.investment.initial_cash_required:,.0f}"
        )
        print(f"   Cash on Cash Return:         {cash_on_cash_return:.2f}%")

    def _print_annual_analysis(self) -> None:
        """Print annual data summary and key metrics"""
        print("\n" + "=" * 60)
        print("ANNUAL DATA SUMMARY")
        print("=" * 60)

        annual_cashflow = self.investment.monthly_cashflow * 12

        # Annual Income & Expenses
        print("\n📈 ANNUAL INCOME & EXPENSES:")
        print(
            f"   Annual Gross Rental:         R{self.operating.monthly_rental_income * 12:,.0f}"
        )
        print(
            f"   Annual Effective Rental:     R{self.operating.effective_monthly_rental * 12:,.0f}"
        )
        print(
            f"   Annual Operating Expenses:   R{self.operating.total_monthly_expenses * 12:,.0f}"
        )

        if self.investment.monthly_bond_payment:
            annual_bond_payments = self.investment.monthly_bond_payment * 12
            print(f"   Annual Bond Payments:        R{annual_bond_payments:,.0f}")
            total_annual_expenses = (
                self.operating.total_monthly_expenses
                + self.investment.monthly_bond_payment
            ) * 12
            print(f"   Annual Total Expenses:       R{total_annual_expenses:,.0f}")
        else:
            print(
                f"   Annual Total Expenses:       R{self.operating.total_monthly_expenses * 12:,.0f}"
            )

        print(f"   Annual Net Cash Flow:        R{annual_cashflow:,.0f}")

        # Annual Returns
        print("\n📈 ANNUAL RETURNS:")
        cash_on_cash_return = self._calculate_cash_on_cash_return(annual_cashflow)
        print(f"   Cash on Cash Return:         {cash_on_cash_return:.2f}%")
        print(f"   Property Appreciation:       {self.financing.appreciation_rate:.1%}")

        annual_appreciation = (
            self.acquisition.purchase_price * self.financing.appreciation_rate
        )
        print(f"   Annual Appreciation Value:   R{annual_appreciation:,.0f}")

        total_annual_return = annual_cashflow + annual_appreciation
        total_return_percentage = self._calculate_total_return_percentage(
            total_annual_return
        )
        print(f"   Total Annual Return:         R{total_annual_return:,.0f}")
        print(f"   Total Return on Investment:  {total_return_percentage:.2f}%")

        # Key Metrics
        print("\n📈 KEY METRICS:")
        gross_yield = (
            self.operating.monthly_rental_income * 12 / self.acquisition.purchase_price
        ) * 100
        net_yield = (annual_cashflow / self.acquisition.purchase_price) * 100
        print(f"   Gross Rental Yield:          {gross_yield:.2f}%")
        print(f"   Net Rental Yield:            {net_yield:.2f}%")

        if self.investment.monthly_bond_payment:
            loan_amount = self.acquisition.purchase_price * self.financing.ltv_ratio
            debt_service_coverage = (
                self.operating.effective_monthly_rental
                / self.investment.monthly_bond_payment
            )
            print(f"   Loan Amount:                 R{loan_amount:,.0f}")
            print(f"   Debt Service Coverage:       {debt_service_coverage:.2f}x")

    def _calculate_cash_on_cash_return(self, annual_cashflow: float) -> float:
        """Calculate cash on cash return percentage"""
        if self.investment.initial_cash_required > 0:
            return (annual_cashflow / self.investment.initial_cash_required) * 100
        return 0

    def _calculate_total_return_percentage(self, total_annual_return: float) -> float:
        """Calculate total return on investment percentage"""
        if self.investment.initial_cash_required > 0:
            return (total_annual_return / self.investment.initial_cash_required) * 100
        return 0

    def print_summary_only(self) -> None:
        """Print only key summary metrics"""
        print("=" * 40)
        print("INVESTMENT SUMMARY")
        print("=" * 40)

        annual_cashflow = self.investment.monthly_cashflow * 12
        cash_on_cash = self._calculate_cash_on_cash_return(annual_cashflow)
        annual_appreciation = (
            self.acquisition.purchase_price * self.financing.appreciation_rate
        )
        total_return = annual_cashflow + annual_appreciation
        total_return_pct = self._calculate_total_return_percentage(total_return)

        print(f"Purchase Price:       R{self.acquisition.purchase_price:,.0f}")
        print(f"Initial Cash:         R{self.investment.initial_cash_required:,.0f}")
        print(f"Monthly Cash Flow:    R{self.investment.monthly_cashflow:,.0f}")
        print(f"Cash on Cash Return:  {cash_on_cash:.2f}%")
        print(f"Total Annual Return:  {total_return_pct:.2f}%")
