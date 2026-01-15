"""
Example showcasing yield calculation functionality for property investment simulation
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    PropertyPortfolioSimulator,
    TrackingFrequency,
    create_cash_strategy,
    create_leveraged_strategy,
    create_mixed_strategy,
    print_detailed_simulation_results,
)


def create_base_property():
    """Create base property for yield examples"""
    acquisition = PropertyAcquisitionCosts(
        purchase_price=1_650_000,
        transfer_duty=13_200,
        conveyancing_fees=32_000,
        bond_registration=22_000,
        furnishing_cost=80_000,
    )

    financing = FinancingParameters(
        ltv_ratio=0.7,
        financing_type=FinancingType.LEVERAGED,
        appreciation_rate=0.06,
        interest_rate=0.105,
        loan_term_years=20,
    )

    operating = OperatingParameters(
        monthly_rental_income=15_000,
        vacancy_rate=0.05,
        monthly_levies=2_500,
        property_management_fee_rate=0.08,
        monthly_insurance=800,
        monthly_maintenance_reserve=1_000,
        monthly_furnishing_repair_costs=500,
    )

    strategy = InvestmentStrategy(
        available_investment_amount=2_000_000,
        reinvest_cashflow=True,
        enable_refinancing=True,
        refinance_frequency=RefineFrequency.ANNUALLY,
        target_refinance_ltv=0.7,
    )

    return PropertyInvestment(acquisition, financing, operating, strategy)


def example_1_leveraged_yields():
    """Example 1: Yields for leveraged property investment"""

    print("=" * 80)
    print("EXAMPLE 1: Leveraged Property Yields")
    print("Track yields over 5 years with 70% LTV")
    print("=" * 80)

    base_property = create_base_property()

    strategy = create_leveraged_strategy(
        leverage_ratio=0.7,
        refinancing=True,
        refinance_years=1.0,
        reinvestment=True,
        tracking=TrackingFrequency.YEARLY,
        years=5,
    )

    simulator = PropertyPortfolioSimulator(base_property, strategy)
    snapshots = simulator.simulate()

    print("\nAnnual Yield Summary:")
    print("Year | Properties | Rental Yield | Net Rental | Cash-on-Cash | Total Return")
    print("-" * 80)

    for snapshot in snapshots[1:]:  # Skip period 0
        if snapshot.property_yields:
            # Calculate portfolio averages weighted by property value
            total_value = sum(prop.current_value for prop in snapshot.properties)

            avg_rental_yield = 0
            avg_net_rental_yield = 0
            avg_coc_return = 0
            avg_total_return = 0

            for yields in snapshot.property_yields:
                # Find property value for weighting
                prop_value = next(
                    prop.current_value
                    for prop in snapshot.properties
                    if prop.property_id == yields.property_id
                )
                weight = prop_value / total_value if total_value > 0 else 0

                avg_rental_yield += yields.rental_yield * weight
                avg_net_rental_yield += yields.net_rental_yield * weight
                avg_coc_return += yields.cash_on_cash_return * weight
                avg_total_return += yields.total_return_yield * weight

            print(
                f"{snapshot.period:4d} | {len(snapshot.properties):10d} | "
                f"{avg_rental_yield:10.2%} | {avg_net_rental_yield:9.2%} | "
                f"{avg_coc_return:11.2%} | {avg_total_return:10.2%}"
            )

    # Show detailed yield breakdown for final year
    final_snapshot = snapshots[-1]
    if final_snapshot.property_yields:
        print(f"\nDetailed Yield Breakdown - Year {final_snapshot.period}:")
        print(
            "Property | Purchase Price | Current Value | Rental | Net Rental | CoC | Total Return"
        )
        print("-" * 90)

        for yields in final_snapshot.property_yields:
            prop = next(
                p
                for p in final_snapshot.properties
                if p.property_id == yields.property_id
            )
            print(
                f"   {yields.property_id:5d} | R{prop.purchase_price:12,.0f} | R{prop.current_value:11,.0f} | "
                f"{yields.rental_yield:5.2%} | {yields.net_rental_yield:9.2%} | "
                f"{yields.cash_on_cash_return:4.1%} | {yields.total_return_yield:10.2%}"
            )

    return snapshots


def example_2_cash_vs_leveraged_yields():
    """Example 2: Compare yields between cash and leveraged strategies"""

    print("\n" + "=" * 80)
    print("EXAMPLE 2: Cash vs Leveraged Yield Comparison")
    print("Same property, different financing strategies")
    print("=" * 80)

    base_property = create_base_property()

    # Cash strategy
    cash_strategy = create_cash_strategy(
        reinvestment=True,
        tracking=TrackingFrequency.YEARLY,
        years=5,
    )

    # Leveraged strategy
    leveraged_strategy = create_leveraged_strategy(
        leverage_ratio=0.7,
        refinancing=True,
        refinance_years=1.0,
        reinvestment=True,
        tracking=TrackingFrequency.YEARLY,
        years=5,
    )

    # Run both simulations
    cash_simulator = PropertyPortfolioSimulator(base_property, cash_strategy)
    cash_snapshots = cash_simulator.simulate()

    leveraged_simulator = PropertyPortfolioSimulator(base_property, leveraged_strategy)
    leveraged_snapshots = leveraged_simulator.simulate()

    print("\nYield Comparison by Year:")
    print(
        "Strategy  | Year | Properties | Rental Yield | Net Rental | Cash-on-Cash | Total Return"
    )
    print("-" * 85)

    # Print cash results
    for snapshot in cash_snapshots[1:]:
        if snapshot.property_yields:
            yields = snapshot.property_yields[0]  # First property for comparison
            print(
                f"Cash      | {snapshot.period:4d} | {len(snapshot.properties):10d} | "
                f"{yields.rental_yield:10.2%} | {yields.net_rental_yield:9.2%} | "
                f"{yields.cash_on_cash_return:11.2%} | {yields.total_return_yield:10.2%}"
            )

    print("-" * 85)

    # Print leveraged results
    for snapshot in leveraged_snapshots[1:]:
        if snapshot.property_yields:
            yields = snapshot.property_yields[0]  # First property for comparison
            print(
                f"Leveraged | {snapshot.period:4d} | {len(snapshot.properties):10d} | "
                f"{yields.rental_yield:10.2%} | {yields.net_rental_yield:9.2%} | "
                f"{yields.cash_on_cash_return:11.2%} | {yields.total_return_yield:10.2%}"
            )

    return cash_snapshots, leveraged_snapshots


def example_3_monthly_yield_tracking():
    """Example 3: Monthly yield tracking with detailed breakdown"""

    print("\n" + "=" * 80)
    print("EXAMPLE 3: Monthly Yield Tracking")
    print("Detailed month-by-month yield analysis")
    print("=" * 80)

    base_property = create_base_property()

    strategy = create_leveraged_strategy(
        leverage_ratio=0.6,
        refinancing=True,
        refinance_years=1.0,
        reinvestment=True,
        tracking=TrackingFrequency.MONTHLY,
        years=2,  # 24 months
    )

    simulator = PropertyPortfolioSimulator(base_property, strategy)
    snapshots = simulator.simulate()

    # Use detailed output to show monthly progression
    print_detailed_simulation_results(snapshots, "Monthly Yield Tracking")

    return snapshots


def example_4_portfolio_yield_analysis():
    """Example 4: Multi-property portfolio yield analysis"""

    print("\n" + "=" * 80)
    print("EXAMPLE 4: Portfolio Yield Analysis")
    print("Multiple properties with different acquisition timings")
    print("=" * 80)

    base_property = create_base_property()

    strategy = create_leveraged_strategy(
        leverage_ratio=0.5,
        refinancing=True,
        refinance_years=2.0,
        reinvestment=True,
        tracking=TrackingFrequency.YEARLY,
        years=8,
    )

    simulator = PropertyPortfolioSimulator(base_property, strategy)
    snapshots = simulator.simulate()

    print("\nPortfolio Yield Evolution:")
    print(
        "Year | Props | Total Value | Avg Rental | Avg Net | Avg CoC | Portfolio Return"
    )
    print("-" * 85)

    for snapshot in snapshots[1:]:
        if snapshot.property_yields and len(snapshot.property_yields) > 0:
            # Calculate portfolio-weighted averages
            total_value = sum(prop.current_value for prop in snapshot.properties)
            total_cashflow = sum(
                yields.annual_cashflow for yields in snapshot.property_yields
            )
            total_cash_invested = sum(
                yields.cash_invested for yields in snapshot.property_yields
            )

            # Weighted averages
            avg_rental = sum(
                yields.rental_yield
                * (
                    next(
                        prop.current_value
                        for prop in snapshot.properties
                        if prop.property_id == yields.property_id
                    )
                    / total_value
                )
                for yields in snapshot.property_yields
            )

            avg_net_rental = sum(
                yields.net_rental_yield
                * (
                    next(
                        prop.current_value
                        for prop in snapshot.properties
                        if prop.property_id == yields.property_id
                    )
                    / total_value
                )
                for yields in snapshot.property_yields
            )

            # Portfolio-level cash-on-cash
            portfolio_coc = (
                total_cashflow / total_cash_invested if total_cash_invested > 0 else 0
            )

            # Portfolio return (weighted total return)
            portfolio_return = sum(
                yields.total_return_yield
                * (
                    next(
                        prop.current_value
                        for prop in snapshot.properties
                        if prop.property_id == yields.property_id
                    )
                    / total_value
                )
                for yields in snapshot.property_yields
            )

            print(
                f"{snapshot.period:4d} | {len(snapshot.properties):5d} | R{total_value:9,.0f}K | "
                f"{avg_rental:8.2%} | {avg_net_rental:6.2%} | {portfolio_coc:6.2%} | {portfolio_return:13.2%}"
            )

    # Show individual property performance in final year
    final_snapshot = snapshots[-1]
    if final_snapshot.property_yields:
        print(f"\nIndividual Property Performance - Year {final_snapshot.period}:")
        print(
            "ID | Age | Purchase Price | Current Value | Cashflow | Rental | CoC | Total Return"
        )
        print("-" * 90)

        for yields in final_snapshot.property_yields:
            prop = next(
                p
                for p in final_snapshot.properties
                if p.property_id == yields.property_id
            )
            property_age = final_snapshot.period - prop.purchase_period

            print(
                f"{yields.property_id:2d} | {property_age:3d} | R{prop.purchase_price:12,.0f} | "
                f"R{prop.current_value:11,.0f} | R{yields.annual_cashflow:7,.0f} | "
                f"{yields.rental_yield:5.2%} | {yields.cash_on_cash_return:4.1%} | {yields.total_return_yield:10.2%}"
            )

    return snapshots


def example_5_yield_sensitivity_analysis():
    """Example 5: Yield sensitivity to different leverage ratios"""

    print("\n" + "=" * 80)
    print("EXAMPLE 5: Leverage Impact on Yields")
    print("Compare yields across different LTV ratios")
    print("=" * 80)

    base_property = create_base_property()

    leverage_ratios = [0.3, 0.5, 0.7, 0.8]
    results = {}

    for ltv in leverage_ratios:
        # Update the financing parameters
        base_property.financing.ltv_ratio = ltv

        strategy = create_leveraged_strategy(
            leverage_ratio=ltv,
            refinancing=False,  # No refinancing for cleaner comparison
            reinvestment=False,  # Single property for comparison
            tracking=TrackingFrequency.YEARLY,
            years=5,
        )

        simulator = PropertyPortfolioSimulator(base_property, strategy)
        snapshots = simulator.simulate()
        results[ltv] = snapshots

    print("\nLeverage Impact on 5-Year Average Yields:")
    print(
        "LTV   | Rental Yield | Net Rental | Cash-on-Cash | Total Return | Cash Invested"
    )
    print("-" * 80)

    for ltv, snapshots in results.items():
        # Calculate 5-year averages
        valid_yields = []
        total_cash_invested = 0

        for snapshot in snapshots[1:]:  # Skip year 0
            if snapshot.property_yields:
                valid_yields.extend(snapshot.property_yields)
                if not total_cash_invested and snapshot.property_yields:
                    total_cash_invested = snapshot.property_yields[0].cash_invested

        if valid_yields:
            avg_rental = sum(y.rental_yield for y in valid_yields) / len(valid_yields)
            avg_net_rental = sum(y.net_rental_yield for y in valid_yields) / len(
                valid_yields
            )
            avg_coc = sum(y.cash_on_cash_return for y in valid_yields) / len(
                valid_yields
            )
            avg_total_return = sum(y.total_return_yield for y in valid_yields) / len(
                valid_yields
            )

            print(
                f"{ltv:.1%} | {avg_rental:10.2%} | {avg_net_rental:9.2%} | "
                f"{avg_coc:11.2%} | {avg_total_return:10.2%} | R{total_cash_invested:11,.0f}"
            )

    return results


if __name__ == "__main__":
    print("PROPERTY INVESTMENT YIELD ANALYSIS")
    print("=" * 80)
    print("Comprehensive yield calculations across different strategies")

    # Run all examples
    print("\nRunning yield analysis examples...")

    snapshots_1 = example_1_leveraged_yields()
    cash_snapshots, leveraged_snapshots = example_2_cash_vs_leveraged_yields()
    snapshots_3 = example_3_monthly_yield_tracking()
    snapshots_4 = example_4_portfolio_yield_analysis()
    results_5 = example_5_yield_sensitivity_analysis()

    print("\n" + "=" * 80)
    print("ALL YIELD ANALYSIS EXAMPLES COMPLETE")
    print("=" * 80)
    print("\nKey Insights:")
    print("- Leveraging increases cash-on-cash returns but adds risk")
    print("- Portfolio yields evolve as properties age and new ones are added")
    print("- Higher LTV ratios amplify both returns and risks")
    print("- Yield tracking enables data-driven investment decisions")
