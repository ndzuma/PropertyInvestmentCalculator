from dataclasses import dataclass
from enum import Enum
from typing import Optional

# from tax_integration import PropertyTaxAnalyzer, create_tax_analyzer


class FinancingType(Enum):
    CASH = "cash"
    LEVERAGED = "leveraged"


class RefineFrequency(Enum):
    NEVER = "never"
    ANNUALLY = "annually"
    BI_ANNUALLY = "bi_annually"
    QUARTERLY = "quarterly"


@dataclass
class PropertyAcquisitionCosts:
    """Property acquisition cost parameters"""

    purchase_price: float
    transfer_duty: float
    conveyancing_fees: float
    bond_registration: float  # 0 for cash purchases
    furnishing_cost: Optional[float] = 0.0

    @property
    def total_unfurnished_cost(self) -> float:
        return (
            self.purchase_price
            + self.transfer_duty
            + self.conveyancing_fees
            + self.bond_registration
        )

    @property
    def total_furnished_cost(self) -> float:
        return self.total_unfurnished_cost + (self.furnishing_cost or 0)


@dataclass
class FinancingParameters:
    """Financing and investment parameters"""

    ltv_ratio: float  # Loan-to-value ratio (e.g., 0.5 for 50%)
    financing_type: FinancingType
    appreciation_rate: float  # Annual property appreciation rate
    interest_rate: Optional[float] = (
        None  # Bond interest rate (for leveraged purchases)
    )
    loan_term_years: Optional[int] = 20  # Loan term in years


@dataclass
class OperatingParameters:
    """Property operating income and expense parameters"""

    monthly_rental_income: float
    vacancy_rate: float  # As percentage (e.g., 0.05 for 5%)
    monthly_levies: float
    property_management_fee_rate: float  # As percentage of rental income
    monthly_insurance: float
    monthly_maintenance_reserve: float
    monthly_furnishing_repair_costs: Optional[float] = 0.0

    @property
    def effective_monthly_rental(self) -> float:
        """Monthly rental income adjusted for vacancy"""
        return self.monthly_rental_income * (1 - self.vacancy_rate)

    @property
    def monthly_management_fee(self) -> float:
        """Monthly property management fee"""
        return self.effective_monthly_rental * self.property_management_fee_rate

    @property
    def total_monthly_expenses(self) -> float:
        """Total monthly operating expenses"""
        return (
            self.monthly_levies
            + self.monthly_management_fee
            + self.monthly_insurance
            + self.monthly_maintenance_reserve
            + (self.monthly_furnishing_repair_costs or 0)
        )

    @property
    def annual_rental_income(self) -> float:
        """Annual rental income before vacancy"""
        return self.monthly_rental_income * 12


@dataclass
class InvestmentStrategy:
    """Investment strategy parameters"""

    available_investment_amount: float
    reinvest_cashflow: bool = True
    enable_refinancing: bool = False
    refinance_frequency: RefineFrequency = RefineFrequency.NEVER
    target_refinance_ltv: Optional[float] = None  # LTV to refinance to


@dataclass
class PropertyInvestment:
    """Complete property investment configuration"""

    acquisition_costs: PropertyAcquisitionCosts
    financing: FinancingParameters
    operating: OperatingParameters
    strategy: InvestmentStrategy

    def __post_init__(self):
        """Validate the investment parameters"""
        if self.financing.financing_type == FinancingType.LEVERAGED:
            if self.financing.interest_rate is None:
                raise ValueError("Interest rate required for leveraged financing")
            if self.acquisition_costs.bond_registration == 0:
                raise ValueError(
                    "Bond registration cost should be > 0 for leveraged financing"
                )

        if (
            self.strategy.enable_refinancing
            and self.strategy.target_refinance_ltv is None
        ):
            raise ValueError(
                "Target refinance LTV required when refinancing is enabled"
            )

    @property
    def initial_cash_required(self) -> float:
        """Calculate initial cash required for investment"""
        if self.financing.financing_type == FinancingType.CASH:
            return self.acquisition_costs.total_furnished_cost
        else:
            # Leveraged: down payment + costs not covered by bond
            loan_amount = (
                self.acquisition_costs.purchase_price * self.financing.ltv_ratio
            )
            return self.acquisition_costs.total_furnished_cost - loan_amount

    @property
    def monthly_bond_payment(self) -> Optional[float]:
        """Calculate monthly bond payment for leveraged purchases"""
        if self.financing.financing_type == FinancingType.CASH:
            return None

        loan_amount = self.acquisition_costs.purchase_price * self.financing.ltv_ratio

        # Handle None values for interest rate and loan term
        if (
            self.financing.interest_rate is None
            or self.financing.loan_term_years is None
        ):
            raise ValueError(
                "Interest rate and loan term must be provided for leveraged financing"
            )

        monthly_rate = self.financing.interest_rate / 12
        num_payments = self.financing.loan_term_years * 12

        # Calculate monthly payment using PMT formula
        if monthly_rate == 0:
            return loan_amount / num_payments
        else:
            return (
                loan_amount
                * (monthly_rate * (1 + monthly_rate) ** num_payments)
                / ((1 + monthly_rate) ** num_payments - 1)
            )

    @property
    def monthly_cashflow(self) -> float:
        """Calculate monthly cash flow after all expenses"""
        cashflow = (
            self.operating.effective_monthly_rental
            - self.operating.total_monthly_expenses
        )

        if self.monthly_bond_payment:
            cashflow -= self.monthly_bond_payment

        return cashflow


def main():
    """Main function to demonstrate the property investment calculator"""
    from .reports import PropertyInvestmentReporter

    # Property Acquisition Costs
    acquisition = PropertyAcquisitionCosts(
        purchase_price=1_650_000,
        transfer_duty=13_200,
        conveyancing_fees=32_000,
        bond_registration=22_000,  # Set to 0 for cash purchase
        furnishing_cost=80_000,
    )

    # Financing Parameters
    financing = FinancingParameters(
        ltv_ratio=0.5,  # 50% LTV
        financing_type=FinancingType.LEVERAGED,  # or FinancingType.CASH
        appreciation_rate=0.06,  # 6% annual appreciation
        interest_rate=0.105,  # 10.5% annual interest rate
        loan_term_years=20,
    )

    # Operating Parameters
    operating = OperatingParameters(
        monthly_rental_income=15_000,
        vacancy_rate=0.05,  # 5% vacancy
        monthly_levies=2_500,
        property_management_fee_rate=0.08,  # 8% of rental income
        monthly_insurance=800,
        monthly_maintenance_reserve=1_000,
        monthly_furnishing_repair_costs=500,
    )

    # Investment Strategy
    strategy = InvestmentStrategy(
        available_investment_amount=2_000_000,
        reinvest_cashflow=True,
        enable_refinancing=True,
        refinance_frequency=RefineFrequency.ANNUALLY,
        target_refinance_ltv=0.6,
    )

    # Create Investment Object
    investment = PropertyInvestment(acquisition, financing, operating, strategy)

    # Create reporter and print full analysis
    reporter = PropertyInvestmentReporter(investment)
    reporter.print_full_report()

    # ==============================================
    # STRATEGY SIMULATIONS
    # ==============================================

    from .strategies import (
        AdditionalCapitalFrequency,
        AdditionalCapitalInjection,
        FirstPropertyType,
        PropertyPortfolioSimulator,
        TrackingFrequency,
        compare_strategies,
        create_cash_strategy,
        create_leveraged_strategy,
        create_mixed_strategy,
    )

    print("\n" + "=" * 80)
    print("STRATEGY SIMULATIONS")
    print("=" * 80)

    # Define capital injections for demonstration
    monthly_injection = AdditionalCapitalInjection(
        amount=50_000,
        frequency=AdditionalCapitalFrequency.MONTHLY,
        start_period=1,
        end_period=None,
    )

    quarterly_bonus = AdditionalCapitalInjection(
        amount=200_000,
        frequency=AdditionalCapitalFrequency.QUARTERLY,
        start_period=1,
        end_period=24,  # First 2 years only
    )

    yearly_inheritance = AdditionalCapitalInjection(
        amount=500_000,
        frequency=AdditionalCapitalFrequency.ONE_TIME,
        specific_periods=[3],  # Year 3 only
    )

    # Define different strategies to compare
    strategies = [
        # Strategy 1: Cash only with reinvestment (no additional capital)
        (
            "Cash Only (No Extra Capital)",
            create_cash_strategy(
                reinvestment=True, tracking=TrackingFrequency.YEARLY, years=5
            ),
        ),
        # Strategy 2: Cash only with monthly capital injection
        (
            "Cash Only (Monthly R50K)",
            create_cash_strategy(
                reinvestment=True,
                tracking=TrackingFrequency.YEARLY,
                years=5,
                additional_capital_injections=[monthly_injection],
            ),
        ),
        # Strategy 3: Leverage with quarterly bonus
        (
            "Leverage (Quarterly R200K)",
            create_leveraged_strategy(
                leverage_ratio=0.5,
                refinancing=True,
                refinance_years=1.0,
                reinvestment=True,
                tracking=TrackingFrequency.YEARLY,
                years=5,
                additional_capital_injections=[quarterly_bonus],
            ),
        ),
        # Strategy 4: Mixed strategy with inheritance
        (
            "Mixed + Inheritance Y3",
            create_mixed_strategy(
                leveraged_property_ratio=0.7,
                cash_property_ratio=0.3,
                leverage_ratio=0.5,
                first_property_type=FirstPropertyType.LEVERAGED,
                refinancing=True,
                refinance_years=1.0,
                reinvestment=True,
                tracking=TrackingFrequency.YEARLY,
                years=5,
                additional_capital_injections=[yearly_inheritance],
            ),
        ),
        # Strategy 5: Aggressive - Multiple capital sources
        (
            "Aggressive (Multiple Sources)",
            create_mixed_strategy(
                leveraged_property_ratio=0.6,
                cash_property_ratio=0.4,
                leverage_ratio=0.6,
                first_property_type=FirstPropertyType.CASH,
                refinancing=True,
                refinance_years=1.0,
                reinvestment=True,
                tracking=TrackingFrequency.YEARLY,
                years=5,
                additional_capital_injections=[monthly_injection, quarterly_bonus],
            ),
        ),
    ]

    # Run strategy comparison with summary output
    print("\n--- STRATEGY COMPARISON (SUMMARY) ---")

    # First, run simulations for each strategy
    strategy_results = []
    for strategy_name, strategy_config in strategies:
        simulator = PropertyPortfolioSimulator(investment, strategy_config)
        snapshots = simulator.simulate()
        strategy_results.append((strategy_name, snapshots))

    # Now compare the results
    simulation_results = compare_strategies(strategy_results)

    print("\n" + "=" * 80)
    print("DETAILED SIMULATION EXAMPLE")
    print("=" * 80)

    # Show detailed simulation with capital injections
    detailed_capital_injections = [
        AdditionalCapitalInjection(
            amount=100_000,
            frequency=AdditionalCapitalFrequency.QUARTERLY,
            start_period=1,
            end_period=20,
        ),
        AdditionalCapitalInjection(
            amount=300_000,
            frequency=AdditionalCapitalFrequency.ONE_TIME,
            specific_periods=[2, 4],  # Year 2 and 4
        ),
    ]

    detailed_strategy = create_mixed_strategy(
        leveraged_property_ratio=0.6,  # 60% leveraged
        cash_property_ratio=0.4,  # 40% cash
        leverage_ratio=0.7,  # 70% LTV when leveraged
        first_property_type=FirstPropertyType.CASH,  # Start with cash
        refinancing=True,
        refinance_years=2.0,
        reinvestment=True,
        tracking=TrackingFrequency.YEARLY,
        years=5,
        additional_capital_injections=detailed_capital_injections,
    )

    from .strategies import (
        PropertyPortfolioSimulator,
        print_detailed_simulation_results,
    )

    detailed_simulator = PropertyPortfolioSimulator(investment, detailed_strategy)
    detailed_snapshots = detailed_simulator.simulate()
    print_detailed_simulation_results(
        detailed_snapshots, "Mixed 60/40 + Capital Injections - DETAILED"
    )

    print("\n" + "=" * 80)
    print("SIMULATION COMPLETE - Detailed data available for charting")
    print(
        "Access snapshots data: simulation_results['strategy_name'][period].property_purchases"
    )
    print(
        "Access refinancing events: simulation_results['strategy_name'][period].refinancing_events"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()
