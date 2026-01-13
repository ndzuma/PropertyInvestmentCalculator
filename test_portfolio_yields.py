#!/usr/bin/env python3
"""
Test script to verify portfolio yields functionality
"""

import sys

sys.path.append(".")

from main import *
from strategies import *


def test_portfolio_yields():
    """Test that portfolio yields are calculated correctly"""
    print("Testing Portfolio Yields Functionality")
    print("=" * 50)

    # Create a simple test investment
    acquisition = PropertyAcquisitionCosts(
        purchase_price=1_000_000,
        transfer_duty=10_000,
        conveyancing_fees=20_000,
        bond_registration=15_000,
        furnishing_cost=50_000,
    )

    financing = FinancingParameters(
        ltv_ratio=0.6,  # 60% LTV
        financing_type=FinancingType.LEVERAGED,
        appreciation_rate=0.05,  # 5% annual appreciation
        interest_rate=0.10,  # 10% interest rate
        loan_term_years=25,
    )

    operating = OperatingParameters(
        monthly_rental_income=8_000,
        vacancy_rate=0.05,  # 5% vacancy
        monthly_levies=1_500,
        property_management_fee_rate=0.08,  # 8%
        monthly_insurance=500,
        monthly_maintenance_reserve=800,
        monthly_furnishing_repair_costs=200,
    )

    strategy_config = InvestmentStrategy(
        available_investment_amount=1_500_000,
        reinvest_cashflow=True,
        enable_refinancing=False,
        refinance_frequency=RefineFrequency.NEVER,
    )

    investment = PropertyInvestment(acquisition, financing, operating, strategy_config)

    # Test with cash strategy (simple case)
    print("\n1. Testing Cash Strategy Portfolio Yields:")
    print("-" * 40)

    cash_strategy = create_cash_strategy(
        reinvestment=True, tracking=TrackingFrequency.YEARLY, years=3
    )

    simulator = PropertyPortfolioSimulator(investment, cash_strategy)
    snapshots = simulator.simulate()

    for snapshot in snapshots:
        if snapshot.portfolio_yields:
            yields = snapshot.portfolio_yields
            print(f"\nYear {snapshot.period}:")
            print(f"  Properties: {len(snapshot.properties)}")
            print(f"  Portfolio Value: R{yields.total_portfolio_value:,.0f}")
            print(f"  Total Cash Invested: R{yields.total_cash_invested:,.0f}")
            print(f"  Portfolio Rental Yield: {yields.portfolio_rental_yield:.2%}")
            print(
                f"  Portfolio Net Rental Yield: {yields.portfolio_net_rental_yield:.2%}"
            )
            print(
                f"  Portfolio Cash-on-Cash Return: {yields.portfolio_cash_on_cash_return:.2%}"
            )
            print(
                f"  Portfolio Capital Growth Yield: {yields.portfolio_capital_growth_yield:.2%}"
            )
            print(
                f"  Portfolio Total Return Yield: {yields.portfolio_total_return_yield:.2%}"
            )

            # Verify calculations
            expected_rental_yield = (
                yields.total_annual_rental_income / yields.total_portfolio_value
            )
            expected_net_rental = (
                yields.total_annual_rental_income
                - yields.total_annual_operating_expenses
            ) / yields.total_portfolio_value
            expected_cash_on_cash = (
                yields.total_annual_cashflow / yields.total_cash_invested
            )

            print(f"\n  Verification:")
            print(
                f"    Rental Yield Expected: {expected_rental_yield:.2%} | Actual: {yields.portfolio_rental_yield:.2%}"
            )
            print(
                f"    Net Rental Expected: {expected_net_rental:.2%} | Actual: {yields.portfolio_net_rental_yield:.2%}"
            )
            print(
                f"    Cash-on-Cash Expected: {expected_cash_on_cash:.2%} | Actual: {yields.portfolio_cash_on_cash_return:.2%}"
            )

    # Test with leveraged strategy (more complex case)
    print("\n\n2. Testing Leveraged Strategy Portfolio Yields:")
    print("-" * 40)

    leveraged_strategy = create_leveraged_strategy(
        leverage_ratio=0.6,
        refinancing=False,
        reinvestment=True,
        tracking=TrackingFrequency.YEARLY,
        years=3,
    )

    simulator = PropertyPortfolioSimulator(investment, leveraged_strategy)
    snapshots = simulator.simulate()

    for snapshot in snapshots:
        if snapshot.portfolio_yields:
            yields = snapshot.portfolio_yields
            print(f"\nYear {snapshot.period}:")
            print(f"  Properties: {len(snapshot.properties)}")
            print(f"  Portfolio Value: R{yields.total_portfolio_value:,.0f}")
            print(f"  Total Debt: R{snapshot.total_debt:,.0f}")
            print(f"  Total Equity: R{snapshot.total_equity:,.0f}")
            print(f"  Portfolio Rental Yield: {yields.portfolio_rental_yield:.2%}")
            print(
                f"  Portfolio Net Rental Yield: {yields.portfolio_net_rental_yield:.2%}"
            )
            print(
                f"  Portfolio Cash-on-Cash Return: {yields.portfolio_cash_on_cash_return:.2%}"
            )
            print(
                f"  Portfolio Capital Growth Yield: {yields.portfolio_capital_growth_yield:.2%}"
            )
            print(
                f"  Portfolio Total Return Yield: {yields.portfolio_total_return_yield:.2%}"
            )

    # Test portfolio yields consistency
    print("\n\n3. Testing Portfolio Yields vs Property Yields Consistency:")
    print("-" * 55)

    final_snapshot = snapshots[-1]
    if final_snapshot.portfolio_yields and final_snapshot.property_yields:
        portfolio_yields = final_snapshot.portfolio_yields
        property_yields = final_snapshot.property_yields

        # Calculate weighted average of property yields
        total_value = sum(prop.current_value for prop in final_snapshot.properties)
        weighted_rental_yield = sum(
            (prop.current_value / total_value) * yields.rental_yield
            for prop, yields in zip(final_snapshot.properties, property_yields)
        )
        weighted_net_rental_yield = sum(
            (prop.current_value / total_value) * yields.net_rental_yield
            for prop, yields in zip(final_snapshot.properties, property_yields)
        )

        print(f"Portfolio Rental Yield: {portfolio_yields.portfolio_rental_yield:.2%}")
        print(f"Weighted Avg Property Rental Yield: {weighted_rental_yield:.2%}")
        print(
            f"Portfolio Net Rental Yield: {portfolio_yields.portfolio_net_rental_yield:.2%}"
        )
        print(
            f"Weighted Avg Property Net Rental Yield: {weighted_net_rental_yield:.2%}"
        )

        # Check if they're reasonably close (within 0.1%)
        rental_diff = abs(
            portfolio_yields.portfolio_rental_yield - weighted_rental_yield
        )
        net_rental_diff = abs(
            portfolio_yields.portfolio_net_rental_yield - weighted_net_rental_yield
        )

        print(f"\nConsistency Check:")
        print(
            f"  Rental Yield Difference: {rental_diff:.4f} ({'PASS' if rental_diff < 0.001 else 'FAIL'})"
        )
        print(
            f"  Net Rental Yield Difference: {net_rental_diff:.4f} ({'PASS' if net_rental_diff < 0.001 else 'FAIL'})"
        )

    print("\n" + "=" * 50)
    print("Portfolio Yields Test Complete!")


if __name__ == "__main__":
    test_portfolio_yields()
