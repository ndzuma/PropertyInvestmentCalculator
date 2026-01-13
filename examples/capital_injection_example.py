"""
Example showcasing additional capital injection functionality for property investment simulation
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
    AdditionalCapitalFrequency,
    AdditionalCapitalInjection,
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
        available_investment_amount=1_000_000,  # Reduced to show capital injection impact
        reinvest_cashflow=True,
        enable_refinancing=True,
        refinance_frequency=RefineFrequency.ANNUALLY,
        target_refinance_ltv=0.6,
    )

    return PropertyInvestment(acquisition, financing, operating, strategy)


def example_1_monthly_capital_injection():
    """Example 1: Monthly additional capital injection"""

    print("=" * 80)
    print("EXAMPLE 1: Monthly Capital Injection")
    print("Inject R50,000 every month for aggressive portfolio growth")
    print("=" * 80)

    base_property = create_base_property()

    # Define monthly capital injection
    monthly_injection = AdditionalCapitalInjection(
        amount=50_000,
        frequency=AdditionalCapitalFrequency.MONTHLY,
        start_period=1,
        end_period=None,  # Continue until simulation ends
    )

    strategy = create_leveraged_strategy(
        leverage_ratio=0.5,
        refinancing=True,
        refinance_years=1.0,
        reinvestment=True,
        tracking=TrackingFrequency.MONTHLY,
        years=2,  # 24 months
        additional_capital_injections=[monthly_injection],
    )

    simulator = PropertyPortfolioSimulator(base_property, strategy)
    snapshots = simulator.simulate()

    # Show capital injection impact
    print("\nCapital Injection Timeline (First 12 months):")
    print("Month | Properties | Cash Available | Capital Injected | Total Additional")
    print("-" * 75)

    for i, snapshot in enumerate(snapshots[:13]):  # First 13 snapshots (0-12)
        injection_amount = 0
        if snapshot.capital_injections:
            injection_amount = sum(inj.amount for inj in snapshot.capital_injections)

        print(
            f"{snapshot.period:5d} | {len(snapshot.properties):10d} | "
            f"R{snapshot.cash_available:12,.0f} | R{injection_amount:14,.0f} | "
            f"R{snapshot.total_additional_capital_injected:12,.0f}"
        )

    final = snapshots[-1]
    print(f"\nFinal Results (Month {final.period}):")
    print(f"Properties: {len(final.properties)}")
    print(f"Portfolio Value: R{final.total_property_value:,.0f}")
    print(f"Initial Investment: R{final.total_cash_invested:,.0f}")
    print(f"Additional Capital: R{final.total_additional_capital_injected:,.0f}")
    print(
        f"Total Invested: R{final.total_cash_invested + final.total_additional_capital_injected:,.0f}"
    )

    return snapshots


def example_2_quarterly_capital_injection():
    """Example 2: Quarterly capital injection with end period"""

    print("\n" + "=" * 80)
    print("EXAMPLE 2: Quarterly Capital Injection (Limited Period)")
    print("Inject R200,000 every quarter for first 3 years only")
    print("=" * 80)

    base_property = create_base_property()

    # Define quarterly capital injection for 3 years
    quarterly_injection = AdditionalCapitalInjection(
        amount=200_000,
        frequency=AdditionalCapitalFrequency.QUARTERLY,
        start_period=1,
        end_period=36,  # Stop after 3 years (36 months)
    )

    strategy = create_mixed_strategy(
        leveraged_property_ratio=0.7,
        cash_property_ratio=0.3,
        leverage_ratio=0.6,
        first_property_type=FirstPropertyType.LEVERAGED,
        refinancing=True,
        refinance_years=1.0,
        reinvestment=True,
        tracking=TrackingFrequency.MONTHLY,
        years=5,  # 60 months total
        additional_capital_injections=[quarterly_injection],
    )

    simulator = PropertyPortfolioSimulator(base_property, strategy)
    snapshots = simulator.simulate()

    # Show quarterly injection pattern
    print("\nQuarterly Capital Injections:")
    print(
        "Quarter | Month | Amount    | Total Additional | Properties | Portfolio Value"
    )
    print("-" * 80)

    quarter = 0
    for snapshot in snapshots:
        if snapshot.capital_injections:
            quarter += 1
            injection_amount = sum(inj.amount for inj in snapshot.capital_injections)
            print(
                f"{quarter:7d} | {snapshot.period:5d} | R{injection_amount:7,.0f} | "
                f"R{snapshot.total_additional_capital_injected:14,.0f} | {len(snapshot.properties):10d} | "
                f"R{snapshot.total_property_value:13,.0f}"
            )

    return snapshots


def example_3_yearly_capital_injection():
    """Example 3: Annual capital injection with increasing amounts"""

    print("\n" + "=" * 80)
    print("EXAMPLE 3: Annual Capital Injection")
    print("Different amounts each year to simulate salary increases/bonuses")
    print("=" * 80)

    base_property = create_base_property()

    # Define multiple yearly injections with different amounts
    year_2_injection = AdditionalCapitalInjection(
        amount=300_000,
        frequency=AdditionalCapitalFrequency.ONE_TIME,
        specific_periods=[2],
    )

    year_3_injection = AdditionalCapitalInjection(
        amount=400_000,
        frequency=AdditionalCapitalFrequency.ONE_TIME,
        specific_periods=[3],
    )

    year_5_injection = AdditionalCapitalInjection(
        amount=500_000,
        frequency=AdditionalCapitalFrequency.ONE_TIME,
        specific_periods=[5],
    )

    year_7_injection = AdditionalCapitalInjection(
        amount=600_000,
        frequency=AdditionalCapitalFrequency.ONE_TIME,
        specific_periods=[7],
    )

    strategy = create_cash_strategy(
        reinvestment=True,
        tracking=TrackingFrequency.YEARLY,
        years=10,
        additional_capital_injections=[
            year_2_injection,
            year_3_injection,
            year_5_injection,
            year_7_injection,
        ],
    )

    simulator = PropertyPortfolioSimulator(base_property, strategy)
    snapshots = simulator.simulate()

    print("\nAnnual Capital Injection Timeline:")
    print("Year | Capital Injected | Cumulative Additional | Properties | Net Worth")
    print("-" * 70)

    for snapshot in snapshots:
        injection_amount = 0
        if snapshot.capital_injections:
            injection_amount = sum(inj.amount for inj in snapshot.capital_injections)

        net_worth = snapshot.total_equity + snapshot.cash_available

        print(
            f"{snapshot.period:4d} | R{injection_amount:14,.0f} | "
            f"R{snapshot.total_additional_capital_injected:18,.0f} | {len(snapshot.properties):10d} | "
            f"R{net_worth:9,.0f}"
        )

    return snapshots


def example_4_multiple_injection_types():
    """Example 4: Multiple types of capital injections combined"""

    print("\n" + "=" * 80)
    print("EXAMPLE 4: Multiple Capital Injection Types")
    print("Combination of monthly savings + annual bonus + one-time inheritance")
    print("=" * 80)

    base_property = create_base_property()

    # Monthly savings
    monthly_savings = AdditionalCapitalInjection(
        amount=25_000,
        frequency=AdditionalCapitalFrequency.MONTHLY,
        start_period=1,
        end_period=60,  # 5 years
    )

    # Annual bonus
    annual_bonus = AdditionalCapitalInjection(
        amount=150_000,
        frequency=AdditionalCapitalFrequency.YEARLY,
        start_period=1,
        end_period=None,
    )

    # One-time inheritance in year 4
    inheritance = AdditionalCapitalInjection(
        amount=800_000,
        frequency=AdditionalCapitalFrequency.ONE_TIME,
        specific_periods=[4],
    )

    strategy = create_mixed_strategy(
        leveraged_property_ratio=0.6,
        cash_property_ratio=0.4,
        leverage_ratio=0.5,
        first_property_type=FirstPropertyType.CASH,
        refinancing=True,
        refinance_years=2.0,
        reinvestment=True,
        tracking=TrackingFrequency.YEARLY,
        years=8,
        additional_capital_injections=[monthly_savings, annual_bonus, inheritance],
    )

    simulator = PropertyPortfolioSimulator(base_property, strategy)
    snapshots = simulator.simulate()

    print("\nCombined Capital Injection Results:")
    print("Year | Monthly | Annual | One-time | Total Year | Cumulative | Properties")
    print("-" * 75)

    for snapshot in snapshots:
        monthly_amount = 0
        annual_amount = 0
        onetime_amount = 0

        for injection in snapshot.capital_injections:
            if injection.source == "monthly":
                monthly_amount += injection.amount
            elif injection.source == "yearly":
                annual_amount += injection.amount
            elif injection.source == "one_time":
                onetime_amount += injection.amount

        total_year = monthly_amount + annual_amount + onetime_amount

        print(
            f"{snapshot.period:4d} | R{monthly_amount:5,.0f}K | R{annual_amount:4,.0f}K | "
            f"R{onetime_amount:6,.0f}K | R{total_year:7,.0f}K | R{snapshot.total_additional_capital_injected:8,.0f}K | "
            f"{len(snapshot.properties):10d}"
        )

    return snapshots


def example_5_detailed_monthly_tracking():
    """Example 5: Detailed monthly tracking showing injection impacts"""

    print("\n" + "=" * 80)
    print("EXAMPLE 5: Detailed Monthly Tracking with Capital Injections")
    print("Shows exactly when capital arrives and how it affects property purchases")
    print("=" * 80)

    base_property = create_base_property()

    # Quarterly capital injection
    quarterly_injection = AdditionalCapitalInjection(
        amount=300_000,
        frequency=AdditionalCapitalFrequency.QUARTERLY,
        start_period=3,  # Start in month 3
        end_period=24,  # End after 2 years
    )

    strategy = create_leveraged_strategy(
        leverage_ratio=0.6,
        refinancing=True,
        refinance_years=1.0,
        reinvestment=True,
        tracking=TrackingFrequency.MONTHLY,
        years=3,
        additional_capital_injections=[quarterly_injection],
    )

    simulator = PropertyPortfolioSimulator(base_property, strategy)
    snapshots = simulator.simulate()

    # Use detailed simulation output
    print_detailed_simulation_results(snapshots, "Capital Injection Impact")

    return snapshots


def example_6_no_injection_comparison():
    """Example 6: Compare same strategy with and without capital injections"""

    print("\n" + "=" * 80)
    print("EXAMPLE 6: Comparison - With vs Without Capital Injections")
    print("Same strategy, different capital injection scenarios")
    print("=" * 80)

    base_property = create_base_property()

    # Strategy without capital injection
    strategy_no_injection = create_leveraged_strategy(
        leverage_ratio=0.5,
        refinancing=True,
        reinvestment=True,
        tracking=TrackingFrequency.YEARLY,
        years=5,
        additional_capital_injections=[],
    )

    # Strategy with quarterly injections
    quarterly_injection = AdditionalCapitalInjection(
        amount=150_000,
        frequency=AdditionalCapitalFrequency.QUARTERLY,
        start_period=1,
    )

    strategy_with_injection = create_leveraged_strategy(
        leverage_ratio=0.5,
        refinancing=True,
        reinvestment=True,
        tracking=TrackingFrequency.YEARLY,
        years=5,
        additional_capital_injections=[quarterly_injection],
    )

    # Run both simulations
    sim_no_injection = PropertyPortfolioSimulator(base_property, strategy_no_injection)
    snapshots_no = sim_no_injection.simulate()

    sim_with_injection = PropertyPortfolioSimulator(
        base_property, strategy_with_injection
    )
    snapshots_with = sim_with_injection.simulate()

    # Compare results
    print("\nComparison Results:")
    print(
        "Scenario        | Properties | Portfolio Value | Additional Capital | Net Worth"
    )
    print("-" * 80)

    final_no = snapshots_no[-1]
    final_with = snapshots_with[-1]

    net_worth_no = final_no.total_equity + final_no.cash_available
    net_worth_with = final_with.total_equity + final_with.cash_available

    print(
        f"No Injection    | {len(final_no.properties):10d} | R{final_no.total_property_value:13,.0f} | "
        f"R{final_no.total_additional_capital_injected:14,.0f} | R{net_worth_no:9,.0f}"
    )
    print(
        f"With Injection  | {len(final_with.properties):10d} | R{final_with.total_property_value:13,.0f} | "
        f"R{final_with.total_additional_capital_injected:14,.0f} | R{net_worth_with:9,.0f}"
    )

    # Calculate the impact
    additional_properties = len(final_with.properties) - len(final_no.properties)
    additional_value = final_with.total_property_value - final_no.total_property_value
    net_worth_difference = net_worth_with - net_worth_no

    print(f"\nImpact of Capital Injections:")
    print(f"Additional Properties: {additional_properties}")
    print(f"Additional Portfolio Value: R{additional_value:,.0f}")
    print(f"Net Worth Increase: R{net_worth_difference:,.0f}")
    print(
        f"Total Additional Capital Injected: R{final_with.total_additional_capital_injected:,.0f}"
    )

    if final_with.total_additional_capital_injected > 0:
        capital_efficiency = (
            net_worth_difference / final_with.total_additional_capital_injected
        )
        print(
            f"Capital Efficiency: R{capital_efficiency:.2f} net worth per R1 injected"
        )

    return snapshots_no, snapshots_with


if __name__ == "__main__":
    print("ADDITIONAL CAPITAL INJECTION EXAMPLES")
    print("=" * 80)
    print("Demonstrating various capital injection strategies")

    # Run all examples
    print("\nRunning all capital injection examples...")

    snapshots_1 = example_1_monthly_capital_injection()
    snapshots_2 = example_2_quarterly_capital_injection()
    snapshots_3 = example_3_yearly_capital_injection()
    snapshots_4 = example_4_multiple_injection_types()
    snapshots_5 = example_5_detailed_monthly_tracking()
    snapshots_6a, snapshots_6b = example_6_no_injection_comparison()

    print("\n" + "=" * 80)
    print("ALL CAPITAL INJECTION EXAMPLES COMPLETE")
    print("Data available for advanced portfolio growth analysis")
    print("=" * 80)
