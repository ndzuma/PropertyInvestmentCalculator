"""
Example of how to access detailed simulation data for charting and analysis
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
    PropertyPortfolioSimulator,
    TrackingFrequency,
    create_cash_strategy,
    create_leveraged_strategy,
)


def example_detailed_data_access():
    """Example of how to access detailed simulation data for charting"""

    # Create base property (same as main.py)
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

    base_property = PropertyInvestment(acquisition, financing, operating, strategy)

    # Example 1: Detailed monthly tracking for charts
    print("EXAMPLE 1: Monthly Tracking Data for Charts")
    print("=" * 60)

    monthly_strategy = create_leveraged_strategy(
        leverage_ratio=0.5,
        refinancing=True,
        refinance_years=1.0,
        reinvestment=True,
        tracking=TrackingFrequency.MONTHLY,
        years=3,  # 3 years for example
    )

    simulator = PropertyPortfolioSimulator(base_property, monthly_strategy)
    snapshots = simulator.simulate()

    # Extract data arrays for charting
    periods = [snap.period for snap in snapshots]
    property_counts = [snap.num_properties for snap in snapshots]
    total_values = [snap.total_property_value for snap in snapshots]
    equity_values = [snap.total_equity for snap in snapshots]
    debt_values = [snap.total_debt for snap in snapshots]
    cash_available = [snap.cash_available for snap in snapshots]
    monthly_cashflows = [snap.monthly_net_cashflow for snap in snapshots]
    total_invested = [snap.total_cash_invested for snap in snapshots]

    print(f"Total data points: {len(snapshots)}")
    print(f"Periods: {periods[:6]}... (first 6 months)")
    print(f"Property counts: {property_counts[:6]}...")
    print(f"Total values: {[f'R{v:,.0f}' for v in total_values[:6]]}...")
    print(f"Monthly cashflows: {[f'R{cf:,.0f}' for cf in monthly_cashflows[:6]]}...")

    # Example 2: Accessing refinancing events in detail
    print("\n\nEXAMPLE 2: Refinancing Events Tracking")
    print("=" * 60)

    refinancing_events_by_period = {}
    for i, snapshot in enumerate(snapshots):
        if snapshot.refinancing_events:
            refinancing_events_by_period[snapshot.period] = snapshot.refinancing_events

    print("Refinancing events found:")
    for period, events in refinancing_events_by_period.items():
        print(f"Period {period}:")
        for event in events:
            print(f"  Property {event.property_id}:")
            print(f"    Property Value: R{event.property_value_at_refi:,.0f}")
            print(f"    Old Loan: R{event.old_loan_amount:,.0f}")
            print(f"    New Loan: R{event.new_loan_amount:,.0f}")
            print(f"    Cash Extracted: R{event.cash_extracted:,.0f}")
            print(f"    New LTV: {event.new_ltv:.1%}")

    # Example 3: Property purchases tracking
    print("\n\nEXAMPLE 3: Property Purchases Tracking")
    print("=" * 60)

    property_purchases_by_period = {}
    for snapshot in snapshots:
        if snapshot.property_purchases:
            property_purchases_by_period[snapshot.period] = snapshot.property_purchases

    print("Property purchases found:")
    for period, purchases in property_purchases_by_period.items():
        print(f"Period {period}:")
        for purchase in purchases:
            print(f"  Property {purchase.property_id}:")
            print(f"    Purchase Price: R{purchase.purchase_price:,.0f}")
            print(f"    Cash Required: R{purchase.cash_required:,.0f}")
            print(f"    Loan Amount: R{purchase.loan_amount:,.0f}")
            print(f"    Financing Type: {purchase.financing_type}")

    # Example 4: Individual property tracking over time
    print("\n\nEXAMPLE 4: Individual Property Value Tracking")
    print("=" * 60)

    # Track individual properties over time
    property_tracking = {}
    for snapshot in snapshots:
        for prop in snapshot.properties:
            if prop.property_id not in property_tracking:
                property_tracking[prop.property_id] = {
                    "periods": [],
                    "values": [],
                    "loan_amounts": [],
                    "cashflows": [],
                    "purchase_period": prop.purchase_period,
                }

            property_tracking[prop.property_id]["periods"].append(snapshot.period)
            property_tracking[prop.property_id]["values"].append(prop.current_value)
            property_tracking[prop.property_id]["loan_amounts"].append(prop.loan_amount)
            property_tracking[prop.property_id]["cashflows"].append(
                prop.monthly_cashflow
            )

    print("Individual property tracking data:")
    for prop_id, data in property_tracking.items():
        print(f"Property {prop_id} (purchased in period {data['purchase_period']}):")
        print(f"  Periods tracked: {len(data['periods'])}")
        print(
            f"  Value progression: R{data['values'][0]:,.0f} -> R{data['values'][-1]:,.0f}"
        )
        print(
            f"  Loan progression: R{data['loan_amounts'][0]:,.0f} -> R{data['loan_amounts'][-1]:,.0f}"
        )

    # Example 5: Cash flow analysis
    print("\n\nEXAMPLE 5: Detailed Cash Flow Analysis")
    print("=" * 60)

    cash_flow_analysis = []
    for snapshot in snapshots:
        analysis = {
            "period": snapshot.period,
            "rental_income": snapshot.monthly_rental_income,
            "operating_expenses": snapshot.monthly_operating_expenses,
            "debt_service": snapshot.monthly_debt_service,
            "net_cashflow": snapshot.monthly_net_cashflow,
            "cash_available": snapshot.cash_available,
            "properties": snapshot.num_properties,
        }
        cash_flow_analysis.append(analysis)

    # Show sample cash flow data
    print("Sample cash flow progression (first 12 months):")
    for i in range(min(12, len(cash_flow_analysis))):
        data = cash_flow_analysis[i]
        print(
            f"Month {data['period']:2d}: "
            f"{data['properties']} props, "
            f"Income: R{data['rental_income']:5,.0f}, "
            f"Expenses: R{data['operating_expenses']:5,.0f}, "
            f"Debt: R{data['debt_service']:5,.0f}, "
            f"Net: R{data['net_cashflow']:5,.0f}, "
            f"Cash: R{data['cash_available']:6,.0f}"
        )

    # Example 6: ROI calculation over time
    print("\n\nEXAMPLE 6: ROI Progression Over Time")
    print("=" * 60)

    roi_progression = []
    initial_investment = snapshots[0].total_cash_invested

    for snapshot in snapshots:
        net_worth = snapshot.total_equity + snapshot.cash_available
        roi = (
            ((net_worth - initial_investment) / initial_investment) * 100
            if initial_investment > 0
            else 0
        )

        roi_data = {
            "period": snapshot.period,
            "total_invested": snapshot.total_cash_invested,
            "equity": snapshot.total_equity,
            "cash": snapshot.cash_available,
            "net_worth": net_worth,
            "roi_percent": roi,
        }
        roi_progression.append(roi_data)

    print("ROI progression (yearly snapshots):")
    yearly_snapshots = [
        roi for roi in roi_progression if roi["period"] % 12 == 0 or roi["period"] == 0
    ]
    for roi_data in yearly_snapshots[:6]:  # First 6 years
        year = roi_data["period"] // 12 if roi_data["period"] > 0 else 0
        print(
            f"Year {year}: "
            f"Invested: R{roi_data['total_invested']:,.0f}, "
            f"Net Worth: R{roi_data['net_worth']:,.0f}, "
            f"ROI: {roi_data['roi_percent']:5.1f}%"
        )

    # Example 7: Simulation termination tracking
    print("\n\nEXAMPLE 7: Simulation Status Tracking")
    print("=" * 60)

    final_snapshot = snapshots[-1]
    if final_snapshot.simulation_ended:
        print(f"Simulation ended early at period {final_snapshot.period}")
        print(f"Reason: {final_snapshot.end_reason}")
    else:
        print(f"Simulation completed successfully for {final_snapshot.period} periods")

    print(f"Final portfolio: {final_snapshot.num_properties} properties")
    print(
        f"Final net worth: R{final_snapshot.total_equity + final_snapshot.cash_available:,.0f}"
    )

    return snapshots, cash_flow_analysis, roi_progression


def compare_multiple_strategies_data():
    """Example of comparing multiple strategies and accessing their data"""

    print("\n" + "=" * 80)
    print("STRATEGY COMPARISON DATA ACCESS")
    print("=" * 80)

    # Create base property
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

    base_property = PropertyInvestment(acquisition, financing, operating, strategy)

    # Define strategies to compare
    strategies = {
        "Cash Only": create_cash_strategy(reinvestment=True, years=5),
        "30% Leverage": create_leveraged_strategy(
            leverage_ratio=0.3, refinancing=True, years=5
        ),
        "50% Leverage": create_leveraged_strategy(
            leverage_ratio=0.5, refinancing=True, years=5
        ),
        "70% Leverage": create_leveraged_strategy(
            leverage_ratio=0.7, refinancing=True, years=5
        ),
    }

    # Run all simulations
    comparison_results = {}
    for name, strat in strategies.items():
        simulator = PropertyPortfolioSimulator(base_property, strat)
        snapshots = simulator.simulate()
        comparison_results[name] = snapshots

    # Extract comparison data for charting
    comparison_data = {}
    for strategy_name, snapshots in comparison_results.items():
        comparison_data[strategy_name] = {
            "periods": [s.period for s in snapshots],
            "property_counts": [s.num_properties for s in snapshots],
            "equity_values": [s.total_equity for s in snapshots],
            "net_worth": [s.total_equity + s.cash_available for s in snapshots],
            "monthly_cashflows": [s.monthly_net_cashflow for s in snapshots],
            "total_property_values": [s.total_property_value for s in snapshots],
            "debt_levels": [s.total_debt for s in snapshots],
        }

    # Show final comparison
    print("Final results comparison:")
    print(
        f"{'Strategy':<15} {'Properties':<10} {'Equity':<12} {'Net Worth':<12} {'Monthly CF':<10}"
    )
    print("-" * 65)

    for strategy_name, data in comparison_data.items():
        final_properties = data["property_counts"][-1]
        final_equity = data["equity_values"][-1]
        final_net_worth = data["net_worth"][-1]
        final_cashflow = data["monthly_cashflows"][-1]

        print(
            f"{strategy_name:<15} {final_properties:<10} R{final_equity / 1000000:<9.1f}M R{final_net_worth / 1000000:<9.1f}M R{final_cashflow:<8,.0f}"
        )

    return comparison_results, comparison_data


if __name__ == "__main__":
    # Run detailed data access example
    snapshots, cashflow_data, roi_data = example_detailed_data_access()

    # Run strategy comparison
    comparison_results, comparison_chart_data = compare_multiple_strategies_data()

    print("\n" + "=" * 80)
    print("DATA ACCESS COMPLETE")
    print("All data structures are now available for creating charts:")
    print("- snapshots: Complete period-by-period data")
    print("- cashflow_data: Detailed cash flow analysis")
    print("- roi_data: ROI progression over time")
    print("- comparison_chart_data: Multi-strategy comparison data")
    print("=" * 80)
