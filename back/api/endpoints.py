from typing import List

from core.main import (
    FinancingParameters,
    FinancingType,
    InvestmentStrategy,
    OperatingParameters,
    PropertyAcquisitionCosts,
    PropertyInvestment,
    RefineFrequency,
)
from core.strategies import (
    AdditionalCapitalFrequency,
    AdditionalCapitalInjection,
    FirstPropertyType,
    PropertyPortfolioSimulator,
    StrategyConfig,
    StrategyType,
    TrackingFrequency,
    create_cash_strategy,
    create_leveraged_strategy,
    create_mixed_strategy,
)

from .models import (
    SimulationRequest,
    SimulationResponse,
    StrategyResult,
    StrategySummary,
    ValidationResponse,
)
from .presets import get_strategy_presets


def validate_parameters(request: SimulationRequest) -> ValidationResponse:
    """Validate simulation parameters without running simulation"""
    errors = []

    # Basic validation
    if request.available_capital <= 0:
        errors.append("Available capital must be greater than 0")

    if request.property.purchase_price <= 0:
        errors.append("Purchase price must be greater than 0")

    if request.operating.monthly_rental_income <= 0:
        errors.append("Monthly rental income must be greater than 0")

    # Strategy-specific validation
    for strategy in request.strategies:
        if strategy.strategy_type == "leveraged" or strategy.strategy_type == "mixed":
            if (
                not strategy.ltv_ratio
                or strategy.ltv_ratio <= 0
                or strategy.ltv_ratio >= 1
            ):
                errors.append(
                    f"Strategy '{strategy.name}': LTV ratio must be between 0 and 1"
                )

            if not strategy.interest_rate or strategy.interest_rate <= 0:
                errors.append(
                    f"Strategy '{strategy.name}': Interest rate must be greater than 0"
                )

        if strategy.strategy_type == "mixed":
            if (
                strategy.leveraged_property_ratio is None
                or strategy.cash_property_ratio is None
            ):
                errors.append(
                    f"Strategy '{strategy.name}': Mixed strategy requires property ratios"
                )
            elif (
                strategy.leveraged_property_ratio + strategy.cash_property_ratio
            ) != 1.0:
                errors.append(
                    f"Strategy '{strategy.name}': Property ratios must sum to 1.0"
                )

    return ValidationResponse(valid=len(errors) == 0, errors=errors)


def convert_capital_injections(injections: List) -> List[AdditionalCapitalInjection]:
    """Convert API capital injections to core objects"""
    result = []
    for injection in injections:
        # Map API enum to core enum
        frequency_mapping = {
            "monthly": AdditionalCapitalFrequency.MONTHLY,
            "quarterly": AdditionalCapitalFrequency.QUARTERLY,
            "yearly": AdditionalCapitalFrequency.YEARLY,
            "five_yearly": AdditionalCapitalFrequency.FIVE_YEARLY,
            "one_time": AdditionalCapitalFrequency.ONE_TIME,
        }

        core_injection = AdditionalCapitalInjection(
            amount=injection.amount,
            frequency=frequency_mapping[injection.frequency],
            start_period=injection.start_period,
            end_period=injection.end_period,
            specific_periods=injection.specific_periods,
        )
        result.append(core_injection)

    return result


def create_property_investment(
    request: SimulationRequest, strategy_config: StrategyConfig
) -> PropertyInvestment:
    """Create PropertyInvestment object from API request"""

    # Create acquisition costs
    acquisition = PropertyAcquisitionCosts(
        purchase_price=request.property.purchase_price,
        transfer_duty=request.property.transfer_duty,
        conveyancing_fees=request.property.conveyancing_fees,
        bond_registration=request.property.bond_registration,
        furnishing_cost=request.property.furnishing_cost or 0.0,
    )

    # Create operating parameters
    operating = OperatingParameters(
        monthly_rental_income=request.operating.monthly_rental_income,
        vacancy_rate=request.operating.vacancy_rate,
        monthly_levies=request.operating.monthly_levies,
        property_management_fee_rate=request.operating.property_management_fee_rate,
        monthly_insurance=request.operating.monthly_insurance,
        monthly_maintenance_reserve=request.operating.monthly_maintenance_reserve,
        monthly_furnishing_repair_costs=request.operating.monthly_furnishing_repair_costs
        or 0.0,
    )

    # Create financing parameters based on strategy type
    if strategy_config.strategy_type == StrategyType.CASH_ONLY:
        financing = FinancingParameters(
            ltv_ratio=0.0,
            financing_type=FinancingType.CASH,
            appreciation_rate=request.appreciation_rate,  # Use global appreciation rate
        )
    else:
        financing = FinancingParameters(
            ltv_ratio=strategy_config.leverage_ratio,
            financing_type=FinancingType.LEVERAGED,
            appreciation_rate=request.appreciation_rate,  # Use global appreciation rate
            interest_rate=0.10,  # Will be overridden by strategy
            loan_term_years=20,  # Will be overridden by strategy
        )

    # Create investment strategy
    investment_strategy = InvestmentStrategy(
        available_investment_amount=request.available_capital,
        reinvest_cashflow=strategy_config.enable_reinvestment,
        enable_refinancing=strategy_config.enable_refinancing,
        refinance_frequency=RefineFrequency.ANNUALLY
        if strategy_config.enable_refinancing
        else RefineFrequency.NEVER,
        target_refinance_ltv=0.6,  # Default
    )

    return PropertyInvestment(acquisition, financing, operating, investment_strategy)


def convert_refinance_frequency_to_years(strategy_request) -> float:
    """Convert refinance frequency enum to years as float"""
    if not strategy_request.enable_refinancing:
        return 1.0  # Default, but refinancing is disabled anyway

    if strategy_request.refinance_frequency == "annually":
        return 1.0
    elif strategy_request.refinance_frequency == "bi_annually":
        return 0.5
    elif strategy_request.refinance_frequency == "quarterly":
        return 0.25
    elif strategy_request.refinance_frequency == "other":
        if strategy_request.custom_refinance_months:
            return strategy_request.custom_refinance_months / 12.0
        else:
            return 1.0  # Default to annually if no custom period specified
    else:  # "never" or unknown
        return 1.0


def create_strategy_config(
    strategy_request, capital_injections: List[AdditionalCapitalInjection]
) -> StrategyConfig:
    """Create StrategyConfig from API strategy request"""

    if strategy_request.strategy_type == "cash_only":
        return create_cash_strategy(
            reinvestment=strategy_request.reinvest_cashflow,
            tracking=TrackingFrequency.MONTHLY,
            months=strategy_request.simulation_months,
            additional_capital_injections=capital_injections,
        )

    elif strategy_request.strategy_type == "leveraged":
        refinance_years = convert_refinance_frequency_to_years(strategy_request)
        return create_leveraged_strategy(
            leverage_ratio=strategy_request.ltv_ratio,
            refinancing=strategy_request.enable_refinancing,
            refinance_years=refinance_years,
            reinvestment=strategy_request.reinvest_cashflow,
            tracking=TrackingFrequency.MONTHLY,
            months=strategy_request.simulation_months,
            additional_capital_injections=capital_injections,
        )

    elif strategy_request.strategy_type == "mixed":
        first_property_type = (
            FirstPropertyType.CASH
            if strategy_request.first_property_type == "cash"
            else FirstPropertyType.LEVERAGED
        )

        refinance_years = convert_refinance_frequency_to_years(strategy_request)
        return create_mixed_strategy(
            leveraged_property_ratio=strategy_request.leveraged_property_ratio,
            cash_property_ratio=strategy_request.cash_property_ratio,
            leverage_ratio=strategy_request.ltv_ratio,
            first_property_type=first_property_type,
            refinancing=strategy_request.enable_refinancing,
            refinance_years=refinance_years,
            reinvestment=strategy_request.reinvest_cashflow,
            tracking=TrackingFrequency.MONTHLY,
            months=strategy_request.simulation_months,
            additional_capital_injections=capital_injections,
        )

    else:
        raise ValueError(f"Unknown strategy type: {strategy_request.strategy_type}")


def simulate_strategies(request: SimulationRequest) -> SimulationResponse:
    """Run simulations for all strategies in the request"""
    try:
        # Validate parameters first
        validation = validate_parameters(request)
        if not validation.valid:
            return SimulationResponse(
                success=False,
                results=[],
                error=f"Validation failed: {', '.join(validation.errors)}",
            )

        # Convert capital injections once
        capital_injections = convert_capital_injections(request.capital_injections)

        # Run simulation for each strategy
        results = []
        for strategy_request in request.strategies:
            # Create strategy config
            strategy_config = create_strategy_config(
                strategy_request, capital_injections
            )

            # Create property investment with strategy-specific parameters
            property_investment = create_property_investment(request, strategy_config)

            # Override financing parameters with global and strategy-specific values
            # Use global appreciation rate for all properties
            property_investment.financing.appreciation_rate = request.appreciation_rate
            if strategy_request.interest_rate:
                property_investment.financing.interest_rate = (
                    strategy_request.interest_rate
                )
            if strategy_request.loan_term_years:
                property_investment.financing.loan_term_years = (
                    strategy_request.loan_term_years
                )
            if strategy_request.target_refinance_ltv:
                property_investment.strategy.target_refinance_ltv = (
                    strategy_request.target_refinance_ltv
                )

            # Run simulation
            simulator = PropertyPortfolioSimulator(property_investment, strategy_config)
            snapshots = simulator.simulate()

            # Convert results to API format with enhanced metrics
            final_snapshot = snapshots[-1]

            # Calculate final metrics
            final_monthly_expenses = 0
            final_annual_rental_income = 0
            final_annual_expenses = 0
            final_total_cost_basis = 0

            for prop in final_snapshot.properties:
                final_annual_rental_income += prop.annual_rental_income
                final_annual_expenses += prop.annual_expenses
                final_monthly_expenses += prop.annual_expenses / 12
                final_total_cost_basis += prop.cost_basis

            # Calculate final yield metrics
            final_rental_yield = (
                final_annual_rental_income / final_snapshot.total_property_value
                if final_snapshot.total_property_value > 0
                else 0
            )
            final_net_rental_yield = (
                (final_annual_rental_income - final_annual_expenses)
                / final_snapshot.total_property_value
                if final_snapshot.total_property_value > 0
                else 0
            )
            final_cash_on_cash_return = (
                final_snapshot.annual_cashflow / final_snapshot.total_cash_invested
                if final_snapshot.total_cash_invested > 0
                else 0
            )
            final_debt_to_equity_ratio = (
                final_snapshot.total_debt / final_snapshot.total_equity
                if final_snapshot.total_equity > 0
                else 0
            )
            final_loan_to_value_ratio = (
                final_snapshot.total_debt / final_snapshot.total_property_value
                if final_snapshot.total_property_value > 0
                else 0
            )

            # Improved ROI calculation using cost basis
            # ROI = (Current Equity - Total Cost Basis) / Total Cost Basis
            # This gives a cleaner view of return on actual cash invested in properties
            final_return_on_investment = (
                (final_snapshot.total_equity - final_total_cost_basis)
                / final_total_cost_basis
                if final_total_cost_basis > 0
                else 0
            )

            summary = StrategySummary(
                final_property_count=len(final_snapshot.properties),
                final_portfolio_value=final_snapshot.total_property_value,
                final_equity=final_snapshot.total_equity,
                monthly_cashflow=final_snapshot.monthly_cashflow,
                total_cash_invested=final_snapshot.total_cash_invested,
                initial_available_capital=request.available_capital,
                simulation_ended=final_snapshot.simulation_ended,
                end_reason=final_snapshot.end_reason,
                # Enhanced financial metrics
                total_debt=final_snapshot.total_debt,
                monthly_expenses=final_monthly_expenses,
                annual_cashflow=final_snapshot.annual_cashflow,
                rental_yield=final_rental_yield,
                net_rental_yield=final_net_rental_yield,
                cash_on_cash_return=final_cash_on_cash_return,
                return_on_investment=final_return_on_investment,
                total_cost_basis=final_total_cost_basis,
                debt_to_equity_ratio=final_debt_to_equity_ratio,
                loan_to_value_ratio=final_loan_to_value_ratio,
                total_annual_rental_income=final_annual_rental_income,
                total_annual_expenses=final_annual_expenses,
            )

            # Convert snapshots to dictionaries with comprehensive data
            snapshot_dicts = []
            for snapshot in snapshots:
                # Calculate additional metrics
                monthly_expenses = 0
                total_annual_rental_income = 0
                total_annual_expenses = 0
                total_cost_basis = 0

                for prop in snapshot.properties:
                    total_annual_rental_income += prop.annual_rental_income
                    total_annual_expenses += prop.annual_expenses
                    monthly_expenses += prop.annual_expenses / 12
                    total_cost_basis += prop.cost_basis

                # Calculate yield metrics
                rental_yield = (
                    total_annual_rental_income / snapshot.total_property_value
                    if snapshot.total_property_value > 0
                    else 0
                )
                net_rental_yield = (
                    (total_annual_rental_income - total_annual_expenses)
                    / snapshot.total_property_value
                    if snapshot.total_property_value > 0
                    else 0
                )
                cash_on_cash_return = (
                    snapshot.annual_cashflow / snapshot.total_cash_invested
                    if snapshot.total_cash_invested > 0
                    else 0
                )
                debt_to_equity_ratio = (
                    snapshot.total_debt / snapshot.total_equity
                    if snapshot.total_equity > 0
                    else 0
                )
                loan_to_value_ratio = (
                    snapshot.total_debt / snapshot.total_property_value
                    if snapshot.total_property_value > 0
                    else 0
                )

                # Improved ROI calculation using cost basis
                return_on_investment = (
                    (snapshot.total_equity - total_cost_basis) / total_cost_basis
                    if total_cost_basis > 0
                    else 0
                )

                snapshot_dict = {
                    "period": snapshot.period,
                    "total_property_value": snapshot.total_property_value,
                    "total_debt": snapshot.total_debt,
                    "total_equity": snapshot.total_equity,
                    "monthly_cashflow": snapshot.monthly_cashflow,
                    "annual_cashflow": snapshot.annual_cashflow,
                    "cash_available": snapshot.cash_available,
                    "property_count": len(snapshot.properties),
                    "total_cash_invested": snapshot.total_cash_invested,
                    "monthly_expenses": monthly_expenses,
                    "total_annual_rental_income": total_annual_rental_income,
                    "total_annual_expenses": total_annual_expenses,
                    "rental_yield": rental_yield,
                    "net_rental_yield": net_rental_yield,
                    "cash_on_cash_return": cash_on_cash_return,
                    "return_on_investment": return_on_investment,
                    "total_cost_basis": total_cost_basis,
                    "debt_to_equity_ratio": debt_to_equity_ratio,
                    "loan_to_value_ratio": loan_to_value_ratio,
                    # Portfolio yields if available
                    "portfolio_yields": {
                        "portfolio_rental_yield": snapshot.portfolio_yields.portfolio_rental_yield
                        if snapshot.portfolio_yields
                        else 0,
                        "portfolio_net_rental_yield": snapshot.portfolio_yields.portfolio_net_rental_yield
                        if snapshot.portfolio_yields
                        else 0,
                        "portfolio_cash_on_cash_return": snapshot.portfolio_yields.portfolio_cash_on_cash_return
                        if snapshot.portfolio_yields
                        else 0,
                        "portfolio_capital_growth_yield": snapshot.portfolio_yields.portfolio_capital_growth_yield
                        if snapshot.portfolio_yields
                        else 0,
                        "portfolio_total_return_yield": snapshot.portfolio_yields.portfolio_total_return_yield
                        if snapshot.portfolio_yields
                        else 0,
                    }
                    if snapshot.portfolio_yields
                    else None,
                    # Individual property data
                    "properties": [
                        {
                            "property_id": prop.property_id,
                            "purchase_price": prop.purchase_price,
                            "current_value": prop.current_value,
                            "loan_amount": prop.loan_amount,
                            "monthly_payment": prop.monthly_payment,
                            "financing_type": prop.financing_type,
                            "months_owned": prop.months_owned,
                            "annual_rental_income": prop.annual_rental_income,
                            "annual_expenses": prop.annual_expenses,
                            "monthly_cashflow": prop.monthly_cashflow,
                            "cost_basis": prop.cost_basis,
                        }
                        for prop in snapshot.properties
                    ],
                    # Property yields if available
                    "property_yields": [
                        {
                            "property_id": yield_data.property_id,
                            "rental_yield": yield_data.rental_yield,
                            "net_rental_yield": yield_data.net_rental_yield,
                            "cash_on_cash_return": yield_data.cash_on_cash_return,
                            "total_return_yield": yield_data.total_return_yield,
                            "capital_growth_yield": yield_data.capital_growth_yield,
                        }
                        for yield_data in snapshot.property_yields
                    ]
                    if snapshot.property_yields
                    else [],
                }
                snapshot_dicts.append(snapshot_dict)

            # Collect all events across all snapshots with period information
            all_events_with_periods = []

            for snapshot in snapshots:
                # Add property purchases with period
                for event in snapshot.property_purchases:
                    all_events_with_periods.append(
                        {
                            "type": "purchase",
                            "period": snapshot.period,
                            "property_id": event.property_id,
                            "purchase_price": event.purchase_price,
                            "financing_type": event.financing_type,
                            "cash_required": event.cash_required,
                            "loan_amount": event.loan_amount,
                        }
                    )

                # Add refinancing events with period
                for event in snapshot.refinancing_events:
                    all_events_with_periods.append(
                        {
                            "type": "refinance",
                            "period": snapshot.period,
                            "property_id": event.property_id,
                            "cash_extracted": event.cash_extracted,
                            "new_loan_amount": event.new_loan_amount,
                            "old_loan_amount": event.old_loan_amount,
                            "new_ltv": event.new_ltv,
                        }
                    )

                # Add capital injections with period
                for event in snapshot.capital_injections:
                    all_events_with_periods.append(
                        {
                            "type": "capital_injection",
                            "period": snapshot.period,
                            "amount": event.amount,
                            "source": event.source,
                            "total_additional_capital_to_date": event.total_additional_capital_to_date,
                        }
                    )

            # Sort events chronologically by period
            all_events_with_periods.sort(key=lambda x: x["period"])

            # Separate events by type for backwards compatibility
            property_purchases = [
                e for e in all_events_with_periods if e["type"] == "purchase"
            ]
            refinancing_events = [
                e for e in all_events_with_periods if e["type"] == "refinance"
            ]
            capital_injections = [
                e for e in all_events_with_periods if e["type"] == "capital_injection"
            ]

            # Convert events to dictionaries
            events = {
                "property_purchases": [
                    {
                        "property_id": event["property_id"],
                        "purchase_price": event["purchase_price"],
                        "financing_type": event["financing_type"],
                        "cash_required": event["cash_required"],
                        "loan_amount": event["loan_amount"],
                        "period": event["period"],
                    }
                    for event in property_purchases
                ],
                "refinancing_events": [
                    {
                        "property_id": event["property_id"],
                        "cash_extracted": event["cash_extracted"],
                        "new_loan_amount": event["new_loan_amount"],
                        "old_loan_amount": event["old_loan_amount"],
                        "new_ltv": event["new_ltv"],
                        "period": event["period"],
                    }
                    for event in refinancing_events
                ],
                "capital_injections": [
                    {
                        "amount": event["amount"],
                        "source": event["source"],
                        "total_additional_capital_to_date": event[
                            "total_additional_capital_to_date"
                        ],
                        "period": event["period"],
                    }
                    for event in capital_injections
                ],
                "chronological_events": all_events_with_periods,
            }

            strategy_result = StrategyResult(
                strategy_name=strategy_request.name,
                summary=summary,
                snapshots=snapshot_dicts,
                events=events,
            )
            results.append(strategy_result)

        return SimulationResponse(success=True, results=results)

    except Exception as e:
        return SimulationResponse(
            success=False, results=[], error=f"Simulation error: {str(e)}"
        )


def get_presets() -> List:
    """Get all available strategy presets"""
    return get_strategy_presets()
