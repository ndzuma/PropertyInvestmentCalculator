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
            appreciation_rate=0.06,  # Default
        )
    else:
        financing = FinancingParameters(
            ltv_ratio=strategy_config.leverage_ratio,
            financing_type=FinancingType.LEVERAGED,
            appreciation_rate=0.06,  # Will be overridden by strategy
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
        return create_leveraged_strategy(
            leverage_ratio=strategy_request.ltv_ratio,
            refinancing=strategy_request.enable_refinancing,
            refinance_years=1.0,  # Default to yearly
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

        return create_mixed_strategy(
            leveraged_property_ratio=strategy_request.leveraged_property_ratio,
            cash_property_ratio=strategy_request.cash_property_ratio,
            leverage_ratio=strategy_request.ltv_ratio,
            first_property_type=first_property_type,
            refinancing=strategy_request.enable_refinancing,
            refinance_years=1.0,  # Default to yearly
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

            # Override financing parameters with strategy-specific values
            if strategy_request.appreciation_rate:
                property_investment.financing.appreciation_rate = (
                    strategy_request.appreciation_rate
                )
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

            # Convert results to API format
            final_snapshot = snapshots[-1]
            summary = StrategySummary(
                final_property_count=len(final_snapshot.properties),
                final_portfolio_value=final_snapshot.total_property_value,
                final_equity=final_snapshot.total_equity,
                monthly_cashflow=final_snapshot.monthly_cashflow,
                total_cash_invested=final_snapshot.total_cash_invested,
                simulation_ended=final_snapshot.simulation_ended,
                end_reason=final_snapshot.end_reason,
            )

            # Convert snapshots to dictionaries
            snapshot_dicts = []
            for snapshot in snapshots:
                snapshot_dict = {
                    "period": snapshot.period,
                    "total_property_value": snapshot.total_property_value,
                    "total_equity": snapshot.total_equity,
                    "monthly_cashflow": snapshot.monthly_cashflow,
                    "cash_available": snapshot.cash_available,
                    "property_count": len(snapshot.properties),
                }
                snapshot_dicts.append(snapshot_dict)

            # Convert events to dictionaries
            events = {
                "property_purchases": [
                    {
                        "property_id": event.property_id,
                        "purchase_price": event.purchase_price,
                        "financing_type": event.financing_type,
                        "cash_required": event.cash_required,
                        "loan_amount": event.loan_amount,
                    }
                    for event in final_snapshot.property_purchases
                ],
                "refinancing_events": [
                    {
                        "property_id": event.property_id,
                        "cash_extracted": event.cash_extracted,
                        "new_loan_amount": event.new_loan_amount,
                        "old_loan_amount": event.old_loan_amount,
                        "new_ltv": event.new_ltv,
                    }
                    for event in final_snapshot.refinancing_events
                ],
                "capital_injections": [
                    {
                        "amount": event.amount,
                        "source": event.source,
                        "total_additional_capital_to_date": event.total_additional_capital_to_date,
                    }
                    for event in final_snapshot.capital_injections
                ],
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
