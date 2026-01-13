#!/usr/bin/env python3
"""
Basic test script to verify the property investment calculator functionality
"""

import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import (
    FinancingParameters,
    FinancingType,
    InvestmentStrategy,
    OperatingParameters,
    PropertyAcquisitionCosts,
    PropertyInvestment,
    RefineFrequency,
)
from strategies import (
    FirstPropertyType,
    PropertyPortfolioSimulator,
    StrategyConfig,
    StrategyType,
    TrackingFrequency,
)


def create_simple_property():
    """Create a simple property for testing"""

    acquisition = PropertyAcquisitionCosts(
        purchase_price=1_000_000,
        transfer_duty=10_000,
        conveyancing_fees=15_000,
        bond_registration=15_000,
        furnishing_cost=50_000,
    )

    financing = FinancingParameters(
        ltv_ratio=0.8,  # 80% LTV
        financing_type=FinancingType.LEVERAGED,
        appreciation_rate=0.06,  # 6% annual appreciation
        interest_rate=0.10,  # 10% interest rate
        loan_term_years=20,
    )

    operating = OperatingParameters(
        monthly_rental_income=12_000,
        vacancy_rate=0.05,  # 5% vacancy
        monthly_levies=1_500,
        property_management_fee_rate=0.08,  # 8% of rental income
        monthly_insurance=600,
        monthly_maintenance_reserve=800,
        monthly_furnishing_repair_costs=300,
    )

    strategy = InvestmentStrategy(
        available_investment_amount=500_000,  # R500k available
        reinvest_cashflow=True,
        enable_refinancing=False,
        refinance_frequency=RefineFrequency.NEVER,
        target_refinance_ltv=None,
    )

    return PropertyInvestment(acquisition, financing, operating, strategy)


def test_cash_strategy():
    """Test cash-only strategy"""
    print("Testing Cash-Only Strategy...")

    property_investment = create_simple_property()

    # Override to cash strategy
    property_investment.financing.financing_type = FinancingType.CASH
    property_investment.financing.ltv_ratio = 0.0

    strategy_config = StrategyConfig(
        strategy_type=StrategyType.CASH_ONLY,
        leverage_ratio=0.0,
        cash_ratio=1.0,
        leveraged_property_ratio=0.0,
        cash_property_ratio=1.0,
        first_property_type=FirstPropertyType.CASH,
        enable_refinancing=False,
        refinance_frequency_years=1.0,
        enable_reinvestment=True,
        tracking_frequency=TrackingFrequency.YEARLY,
        simulation_years=3,
        additional_capital_injections=[],
    )

    simulator = PropertyPortfolioSimulator(property_investment, strategy_config)
    snapshots = simulator.simulate()

    print(f"Simulation completed with {len(snapshots)} snapshots")

    if snapshots:
        final_snapshot = snapshots[-1]
        print(f"Final properties: {len(final_snapshot.properties)}")
        print(f"Final portfolio value: R{final_snapshot.total_property_value:,.0f}")
        print(f"Cash available: R{final_snapshot.cash_available:,.0f}")
        print(
            f"Net worth: R{final_snapshot.total_equity + final_snapshot.cash_available:,.0f}"
        )

        if final_snapshot.simulation_ended:
            print(f"Simulation ended: {final_snapshot.end_reason}")

    print("-" * 50)
    return snapshots


def test_leveraged_strategy():
    """Test leveraged strategy"""
    print("Testing Leveraged Strategy...")

    property_investment = create_simple_property()

    strategy_config = StrategyConfig(
        strategy_type=StrategyType.LEVERAGED,
        leverage_ratio=0.8,  # 80% LTV
        cash_ratio=0.2,
        leveraged_property_ratio=1.0,
        cash_property_ratio=0.0,
        first_property_type=FirstPropertyType.LEVERAGED,
        enable_refinancing=False,
        refinance_frequency_years=1.0,
        enable_reinvestment=True,
        tracking_frequency=TrackingFrequency.YEARLY,
        simulation_years=3,
        additional_capital_injections=[],
    )

    simulator = PropertyPortfolioSimulator(property_investment, strategy_config)
    snapshots = simulator.simulate()

    print(f"Simulation completed with {len(snapshots)} snapshots")

    if snapshots:
        final_snapshot = snapshots[-1]
        print(f"Final properties: {len(final_snapshot.properties)}")
        print(f"Final portfolio value: R{final_snapshot.total_property_value:,.0f}")
        print(f"Total debt: R{final_snapshot.total_debt:,.0f}")
        print(f"Total equity: R{final_snapshot.total_equity:,.0f}")
        print(f"Cash available: R{final_snapshot.cash_available:,.0f}")
        print(
            f"Net worth: R{final_snapshot.total_equity + final_snapshot.cash_available:,.0f}"
        )

        if final_snapshot.simulation_ended:
            print(f"Simulation ended: {final_snapshot.end_reason}")

    print("-" * 50)
    return snapshots


def test_property_calculations():
    """Test basic property calculations"""
    print("Testing Property Calculations...")

    property_investment = create_simple_property()

    print(
        f"Purchase price: R{property_investment.acquisition_costs.purchase_price:,.0f}"
    )
    print(
        f"Total furnished cost: R{property_investment.acquisition_costs.total_furnished_cost:,.0f}"
    )
    print(
        f"Monthly rental income: R{property_investment.operating.monthly_rental_income:,.0f}"
    )
    print(
        f"Effective monthly rental: R{property_investment.operating.effective_monthly_rental:,.0f}"
    )
    print(
        f"Total monthly expenses: R{property_investment.operating.total_monthly_expenses:,.0f}"
    )
    print(
        f"Annual rental income: R{property_investment.operating.annual_rental_income:,.0f}"
    )

    if property_investment.monthly_bond_payment:
        print(f"Monthly bond payment: R{property_investment.monthly_bond_payment:,.0f}")
        monthly_cashflow = (
            property_investment.operating.effective_monthly_rental
            - property_investment.operating.total_monthly_expenses
            - property_investment.monthly_bond_payment
        )
        print(f"Monthly cash flow: R{monthly_cashflow:,.0f}")
    else:
        print("No bond payment (cash purchase)")
        monthly_cashflow = (
            property_investment.operating.effective_monthly_rental
            - property_investment.operating.total_monthly_expenses
        )
        print(f"Monthly cash flow: R{monthly_cashflow:,.0f}")

    print("-" * 50)


def test_yield_calculations():
    """Test yield calculations on a completed simulation"""
    print("Testing Yield Calculations...")

    property_investment = create_simple_property()

    strategy_config = StrategyConfig(
        strategy_type=StrategyType.LEVERAGED,
        leverage_ratio=0.8,  # 80% LTV
        cash_ratio=0.2,
        leveraged_property_ratio=1.0,
        cash_property_ratio=0.0,
        first_property_type=FirstPropertyType.LEVERAGED,
        enable_refinancing=False,
        refinance_frequency_years=1.0,
        enable_reinvestment=True,
        tracking_frequency=TrackingFrequency.YEARLY,
        simulation_years=3,
        additional_capital_injections=[],
    )

    simulator = PropertyPortfolioSimulator(property_investment, strategy_config)
    snapshots = simulator.simulate()

    print(f"Simulation completed with {len(snapshots)} snapshots")

    # Check yields for each snapshot
    for i, snapshot in enumerate(snapshots):
        if snapshot.property_yields:
            print(f"\nYear {snapshot.period} Yields:")
            for yields in snapshot.property_yields:
                print(f"  Property {yields.property_id}:")
                print(f"    Rental Yield: {yields.rental_yield:.2%}")
                print(f"    Net Rental Yield: {yields.net_rental_yield:.2%}")
                print(f"    Cash-on-Cash Return: {yields.cash_on_cash_return:.2%}")
                print(f"    Capital Growth Yield: {yields.capital_growth_yield:.2%}")
                print(f"    Total Return Yield: {yields.total_return_yield:.2%}")

    print("-" * 50)
    return snapshots


def main():
    """Run all tests"""
    print("=" * 60)
    print("PROPERTY INVESTMENT CALCULATOR - BASIC TESTS")
    print("=" * 60)

    try:
        # Test basic calculations
        test_property_calculations()

        # Test cash strategy
        cash_snapshots = test_cash_strategy()

        # Test leveraged strategy
        leveraged_snapshots = test_leveraged_strategy()

        # Test yield calculations
        yield_snapshots = test_yield_calculations()

        print("=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)

        # Quick comparison
        if cash_snapshots and leveraged_snapshots:
            print("\nQuick Comparison:")
            cash_final = cash_snapshots[-1]
            leveraged_final = leveraged_snapshots[-1]

            print(
                f"Cash Strategy    - Properties: {len(cash_final.properties)}, Net Worth: R{cash_final.total_equity + cash_final.cash_available:,.0f}"
            )
            print(
                f"Leveraged Strategy - Properties: {len(leveraged_final.properties)}, Net Worth: R{leveraged_final.total_equity + leveraged_final.cash_available:,.0f}"
            )

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
