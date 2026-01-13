"""
Example showcasing mixed strategy functionality for property investment simulation
"""

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
    TrackingFrequency,
    create_cash_strategy,
    create_leveraged_strategy,
    create_mixed_strategy,
    print_detailed_simulation_results,
)


def create_base_property():
    """Create base property for all examples"""
    acquisition = PropertyAcquisitionCosts(
        purchase_price=1_650_000,
        transfer_duty=13_200,
        conveyancing_fees=32_000,
        bond_registration=22_000,
        furnishing_cost=80_000,
    )

    financing = FinancingParameters(
        ltv_ratio=0.5,
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
        target_refinance_ltv=0.6,
    )

    return PropertyInvestment(acquisition, financing, operating, strategy)


def example_1_mixed_70_30_start_leverage():
    """Example 1: 70% leveraged, 30% cash properties, start with leverage"""

    print("=" * 80)
    print("EXAMPLE 1: Mixed 70/30 Strategy (Start with Leverage)")
    print("70% of properties will be leveraged (50% LTV)")
    print("30% of properties will be cash purchases")
    print("First property: Leveraged")
    print("=" * 80)

    base_property = create_base_property()

    strategy = create_mixed_strategy(
        leveraged_property_ratio=0.7,
        cash_property_ratio=0.3,
        leverage_ratio=0.5,  # 50% LTV when leveraged
        first_property_type=FirstPropertyType.LEVERAGED,
        refinancing=True,
        refinance_years=1.0,
        reinvestment=True,
        tracking=TrackingFrequency.YEARLY,
        years=8,
    )

    simulator = PropertyPortfolioSimulator(base_property, strategy)
    snapshots = simulator.simulate()

    # Show property purchase pattern
    print("\nProperty Purchase Pattern:")
    print("Period | Property ID | Type      | Purchase Price | Financing")
    print("-" * 65)

    for snapshot in snapshots:
        if snapshot.property_purchases:
            for purchase in snapshot.property_purchases:
                financing_type = (
                    "Leveraged" if "leverage" in purchase.financing_type else "Cash"
                )
                print(
                    f"{snapshot.period:6d} | {purchase.property_id:11d} | {financing_type:9s} | R{purchase.purchase_price:11,.0f} | {purchase.financing_type}"
                )

    # Show final portfolio breakdown
    final_snapshot = snapshots[-1]
    leveraged_count = sum(
        1 for prop in final_snapshot.properties if prop.loan_amount > 0
    )
    cash_count = sum(1 for prop in final_snapshot.properties if prop.loan_amount == 0)
    total_count = len(final_snapshot.properties)

    print(f"\nFinal Portfolio Breakdown:")
    print(f"Total Properties: {total_count}")
    print(
        f"Leveraged Properties: {leveraged_count} ({leveraged_count / total_count * 100:.1f}%)"
    )
    print(f"Cash Properties: {cash_count} ({cash_count / total_count * 100:.1f}%)")
    print(f"Total Portfolio Value: R{final_snapshot.total_property_value:,.0f}")
    print(f"Total Debt: R{final_snapshot.total_debt:,.0f}")
    print(f"Total Equity: R{final_snapshot.total_equity:,.0f}")
    print(f"Monthly Net Cash Flow: R{final_snapshot.monthly_net_cashflow:,.0f}")

    return snapshots


def example_2_mixed_50_50_start_cash():
    """Example 2: 50% leveraged, 50% cash properties, start with cash"""

    print("\n" + "=" * 80)
    print("EXAMPLE 2: Mixed 50/50 Strategy (Start with Cash)")
    print("50% of properties will be leveraged (60% LTV)")
    print("50% of properties will be cash purchases")
    print("First property: Cash")
    print("=" * 80)

    base_property = create_base_property()

    strategy = create_mixed_strategy(
        leveraged_property_ratio=0.5,
        cash_property_ratio=0.5,
        leverage_ratio=0.6,  # 60% LTV when leveraged
        first_property_type=FirstPropertyType.CASH,
        refinancing=True,
        refinance_years=2.0,  # Refinance every 2 years
        reinvestment=True,
        tracking=TrackingFrequency.YEARLY,
        years=6,
    )

    simulator = PropertyPortfolioSimulator(base_property, strategy)
    snapshots = simulator.simulate()

    # Show detailed progression
    print("\nDetailed Progression:")
    print(
        "Year | Props | Leveraged | Cash | Portfolio Value | Monthly CF | Cash Available"
    )
    print("-" * 80)

    for snapshot in snapshots:
        leveraged_count = sum(1 for prop in snapshot.properties if prop.loan_amount > 0)
        cash_count = sum(1 for prop in snapshot.properties if prop.loan_amount == 0)

        print(
            f"{snapshot.period:4d} | {len(snapshot.properties):5d} | {leveraged_count:9d} | {cash_count:4d} | "
            f"R{snapshot.total_property_value:12,.0f} | R{snapshot.monthly_net_cashflow:8,.0f} | "
            f"R{snapshot.cash_available:12,.0f}"
        )

    return snapshots


def example_3_compare_start_types():
    """Example 3: Compare starting with leverage vs cash in same mixed strategy"""

    print("\n" + "=" * 80)
    print("EXAMPLE 3: Comparison - Same Strategy, Different Starting Property")
    print("Both strategies: 60% leveraged, 40% cash (50% LTV)")
    print("Strategy A: Start with Leveraged property")
    print("Strategy B: Start with Cash property")
    print("=" * 80)

    base_property = create_base_property()

    # Strategy A: Start with leverage
    strategy_a = create_mixed_strategy(
        leveraged_property_ratio=0.6,
        cash_property_ratio=0.4,
        leverage_ratio=0.5,
        first_property_type=FirstPropertyType.LEVERAGED,
        refinancing=True,
        refinance_years=1.0,
        reinvestment=True,
        tracking=TrackingFrequency.YEARLY,
        years=5,
    )

    # Strategy B: Start with cash
    strategy_b = create_mixed_strategy(
        leveraged_property_ratio=0.6,
        cash_property_ratio=0.4,
        leverage_ratio=0.5,
        first_property_type=FirstPropertyType.CASH,
        refinancing=True,
        refinance_years=1.0,
        reinvestment=True,
        tracking=TrackingFrequency.YEARLY,
        years=5,
    )

    sim_a = PropertyPortfolioSimulator(base_property, strategy_a)
    snapshots_a = sim_a.simulate()

    sim_b = PropertyPortfolioSimulator(base_property, strategy_b)
    snapshots_b = sim_b.simulate()

    print("\nComparison Results:")
    print(
        "Strategy | Properties | Leveraged | Cash | Final Equity | Monthly CF | Net Worth"
    )
    print("-" * 85)

    final_a = snapshots_a[-1]
    leveraged_a = sum(1 for prop in final_a.properties if prop.loan_amount > 0)
    cash_a = sum(1 for prop in final_a.properties if prop.loan_amount == 0)
    net_worth_a = final_a.total_equity + final_a.cash_available

    final_b = snapshots_b[-1]
    leveraged_b = sum(1 for prop in final_b.properties if prop.loan_amount > 0)
    cash_b = sum(1 for prop in final_b.properties if prop.loan_amount == 0)
    net_worth_b = final_b.total_equity + final_b.cash_available

    print(
        f"Start Lev|     {len(final_a.properties):5d} |     {leveraged_a:5d} | {cash_a:4d} | "
        f"R{final_a.total_equity:10,.0f} | R{final_a.monthly_net_cashflow:8,.0f} | R{net_worth_a:9,.0f}"
    )
    print(
        f"Start Cash|    {len(final_b.properties):5d} |     {leveraged_b:5d} | {cash_b:4d} | "
        f"R{final_b.total_equity:10,.0f} | R{final_b.monthly_net_cashflow:8,.0f} | R{net_worth_b:9,.0f}"
    )

    return snapshots_a, snapshots_b


def example_4_extreme_mixed_strategies():
    """Example 4: Test extreme mixed strategies"""

    print("\n" + "=" * 80)
    print("EXAMPLE 4: Extreme Mixed Strategies")
    print("Testing edge cases and extreme ratios")
    print("=" * 80)

    base_property = create_base_property()

    # Strategy 1: 90% leveraged, 10% cash
    strategy_90_10 = create_mixed_strategy(
        leveraged_property_ratio=0.9,
        cash_property_ratio=0.1,
        leverage_ratio=0.7,  # Aggressive 70% LTV
        first_property_type=FirstPropertyType.LEVERAGED,
        refinancing=True,
        refinance_years=1.0,
        reinvestment=True,
        tracking=TrackingFrequency.YEARLY,
        years=5,
    )

    # Strategy 2: 10% leveraged, 90% cash
    strategy_10_90 = create_mixed_strategy(
        leveraged_property_ratio=0.1,
        cash_property_ratio=0.9,
        leverage_ratio=0.3,  # Conservative 30% LTV when leveraged
        first_property_type=FirstPropertyType.CASH,
        refinancing=False,  # No refinancing for conservative strategy
        reinvestment=True,
        tracking=TrackingFrequency.YEARLY,
        years=5,
    )

    print("\nStrategy 1: Aggressive 90% Leveraged")
    sim_aggressive = PropertyPortfolioSimulator(base_property, strategy_90_10)
    snapshots_aggressive = sim_aggressive.simulate()

    print("\nStrategy 2: Conservative 10% Leveraged")
    sim_conservative = PropertyPortfolioSimulator(base_property, strategy_10_90)
    snapshots_conservative = sim_conservative.simulate()

    # Compare results
    print("\nExtreme Strategy Comparison:")
    print("Strategy    | Properties | Portfolio Value | Debt | Equity | Monthly CF")
    print("-" * 75)

    final_agg = snapshots_aggressive[-1]
    final_cons = snapshots_conservative[-1]

    print(
        f"Aggressive  |     {len(final_agg.properties):5d} | R{final_agg.total_property_value:13,.0f} | "
        f"R{final_agg.total_debt:9,.0f} | R{final_agg.total_equity:9,.0f} | R{final_agg.monthly_net_cashflow:8,.0f}"
    )
    print(
        f"Conservative|     {len(final_cons.properties):5d} | R{final_cons.total_property_value:13,.0f} | "
        f"R{final_cons.total_debt:9,.0f} | R{final_cons.total_equity:9,.0f} | R{final_cons.monthly_net_cashflow:8,.0f}"
    )

    return snapshots_aggressive, snapshots_conservative


def example_5_monthly_tracking_mixed():
    """Example 5: Monthly tracking of mixed strategy to show detailed transitions"""

    print("\n" + "=" * 80)
    print("EXAMPLE 5: Monthly Tracking - Mixed Strategy Property Purchases")
    print("Track month-by-month to see exactly when leverage/cash decisions are made")
    print("=" * 80)

    base_property = create_base_property()

    strategy = create_mixed_strategy(
        leveraged_property_ratio=0.67,  # 2/3 leveraged
        cash_property_ratio=0.33,  # 1/3 cash
        leverage_ratio=0.5,
        first_property_type=FirstPropertyType.LEVERAGED,
        refinancing=True,
        refinance_years=1.0,
        reinvestment=True,
        tracking=TrackingFrequency.MONTHLY,
        years=3,  # 3 years for detailed tracking
    )

    simulator = PropertyPortfolioSimulator(base_property, strategy)
    snapshots = simulator.simulate()

    print("\nMonthly Property Purchase Decisions:")
    print("Month | Action | Property ID | Type | Price | Current Ratio (Lev/Cash)")
    print("-" * 70)

    for snapshot in snapshots:
        if snapshot.property_purchases:
            for purchase in snapshot.property_purchases:
                # Calculate current ratios
                leveraged = sum(
                    1 for prop in snapshot.properties if prop.loan_amount > 0
                )
                cash = sum(1 for prop in snapshot.properties if prop.loan_amount == 0)
                total = len(snapshot.properties)

                financing_type = (
                    "Leveraged" if "leverage" in purchase.financing_type else "Cash"
                )
                ratio_text = (
                    f"{leveraged / total:.2f}/{cash / total:.2f}"
                    if total > 0
                    else "0/0"
                )

                print(
                    f"{snapshot.period:5d} | Purchase | {purchase.property_id:11d} | {financing_type:8s} | "
                    f"R{purchase.purchase_price / 1000000:.1f}M | {ratio_text}"
                )

    return snapshots


if __name__ == "__main__":
    print("MIXED STRATEGY EXAMPLES")
    print("=" * 80)
    print("Demonstrating portfolio strategies with mixed financing types")

    # Run all examples
    snapshots_1 = example_1_mixed_70_30_start_leverage()
    snapshots_2 = example_2_mixed_50_50_start_cash()
    snapshots_3a, snapshots_3b = example_3_compare_start_types()
    snapshots_4a, snapshots_4b = example_4_extreme_mixed_strategies()
    snapshots_5 = example_5_monthly_tracking_mixed()

    print("\n" + "=" * 80)
    print("ALL MIXED STRATEGY EXAMPLES COMPLETE")
    print("Data available for further analysis and charting")
    print("=" * 80)
