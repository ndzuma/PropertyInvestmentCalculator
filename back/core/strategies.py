from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .main import FinancingType, PropertyInvestment, RefineFrequency


class StrategyType(Enum):
    CASH_ONLY = "cash_only"
    LEVERAGED = "leveraged"
    MIXED = "mixed"


class TrackingFrequency(Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


class FirstPropertyType(Enum):
    CASH = "cash"
    LEVERAGED = "leveraged"


class AdditionalCapitalFrequency(Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    FIVE_YEARLY = "five_yearly"
    ONE_TIME = "one_time"


@dataclass
class AdditionalCapitalInjection:
    """Configuration for additional capital injections"""

    amount: float
    frequency: AdditionalCapitalFrequency
    start_period: int = 1  # When to start injections (period number)
    end_period: Optional[int] = (
        None  # When to stop (None = continue until simulation ends)
    )
    specific_periods: Optional[List[int]] = (
        None  # For one-time injections in specific periods
    )


@dataclass
class StrategyConfig:
    """Configuration for investment strategy"""

    strategy_type: StrategyType
    simulation_months: int
    leverage_ratio: float = 0.0  # 0.7 for 70% leverage (when leveraged)
    cash_ratio: float = 1.0  # 0.3 for 30% cash (deprecated for mixed strategies)

    # New mixed strategy parameters
    leveraged_property_ratio: float = 0.0  # 0.7 = 70% of properties will be leveraged
    cash_property_ratio: float = 1.0  # 0.3 = 30% of properties will be cash
    first_property_type: FirstPropertyType = FirstPropertyType.CASH

    enable_refinancing: bool = False
    refinance_frequency_years: float = (
        1.0  # 1.0 = yearly, 0.5 = 6 months, 3.0 = 3 years
    )
    enable_reinvestment: bool = True
    tracking_frequency: TrackingFrequency = TrackingFrequency.MONTHLY

    # Additional capital injection parameters
    additional_capital_injections: Optional[List[AdditionalCapitalInjection]] = None


@dataclass
class PropertyData:
    """Detailed data for a single property"""

    property_id: int
    purchase_price: float
    current_value: float
    loan_amount: float
    monthly_payment: float
    financing_type: str  # "cash" or "leveraged" or "60%_leverage" etc.
    months_owned: int
    annual_rental_income: float
    annual_expenses: float
    monthly_cashflow: float
    cost_basis: float  # Total cash invested: purchase_price + all acquisition costs


@dataclass
class PropertyYields:
    """Annual yield calculations for a property"""

    property_id: int
    rental_yield: float  # Annual rental income / property value
    net_rental_yield: float  # (Annual rental income - expenses) / property value
    cash_on_cash_return: float  # Annual cash flow / cash invested
    total_return_yield: float  # Rental yield + capital growth yield
    capital_growth_yield: float  # Property appreciation rate


@dataclass
class PortfolioYields:
    """Annual yield calculations for the entire portfolio"""

    period: int
    portfolio_rental_yield: float  # Total annual rental income / total portfolio value
    portfolio_net_rental_yield: float  # (Total annual rental income - total operating expenses) / total portfolio value
    portfolio_cash_on_cash_return: float  # Total annual cashflow / total cash invested
    portfolio_capital_growth_yield: float  # Annualized portfolio appreciation
    portfolio_total_return_yield: (
        float  # Portfolio net rental yield + portfolio capital growth yield
    )
    total_annual_rental_income: float
    total_annual_operating_expenses: float
    total_annual_cashflow: float
    total_portfolio_value: float
    total_cash_invested: float


@dataclass
class RefinancingEvent:
    """Details of a refinancing event"""

    property_id: int
    property_value: float
    old_loan_amount: float
    new_loan_amount: float
    cash_extracted: float
    new_ltv: float


@dataclass
class PropertyPurchase:
    """Details of a property purchase"""

    property_id: int
    purchase_price: float
    cash_required: float
    financing_type: str
    loan_amount: float


@dataclass
class CapitalInjectionEvent:
    """Details of a capital injection"""

    amount: float
    source: str  # "monthly", "quarterly", "yearly", "one_time"
    total_additional_capital_to_date: float


@dataclass
class SimulationSnapshot:
    """Complete snapshot of portfolio state at a point in time"""

    period: int
    properties: List[PropertyData]
    total_property_value: float
    total_debt: float
    total_equity: float
    cash_available: float
    monthly_cashflow: float
    annual_cashflow: float
    total_cash_invested: float
    total_additional_capital_injected: float
    refinancing_events: List[RefinancingEvent]
    property_purchases: List[PropertyPurchase]
    capital_injections: List[CapitalInjectionEvent]
    property_yields: Optional[List[PropertyYields]] = None
    portfolio_yields: Optional[PortfolioYields] = None
    simulation_ended: bool = False
    end_reason: Optional[str] = None


class PropertyPortfolioSimulator:
    """Simulates property portfolio growth and management over time"""

    def __init__(self, base_property: PropertyInvestment, strategy: StrategyConfig):
        self.base_property = base_property
        self.strategy = strategy
        self.snapshots: List[SimulationSnapshot] = []

        # Track simulation state
        self.simulation_ended = False
        self.end_reason = None

        # Track additional capital injections
        self.total_additional_capital = 0.0

    def simulate(self) -> List[SimulationSnapshot]:
        """Run the complete simulation and return detailed snapshots"""

        # ALWAYS run monthly for accuracy, filter results by tracking frequency
        total_monthly_periods = self.strategy.simulation_months

        # Run monthly simulation
        all_monthly_snapshots = self._run_monthly_simulation(total_monthly_periods)

        # Filter snapshots based on tracking frequency
        filtered_snapshots = self._filter_snapshots_by_frequency(all_monthly_snapshots)

        # Store filtered snapshots for compatibility with existing code
        self.snapshots = filtered_snapshots

        return filtered_snapshots

    def _run_monthly_simulation(
        self, total_monthly_periods: int
    ) -> List[SimulationSnapshot]:
        """Run the complete monthly simulation and return all monthly snapshots"""

        # Initialize portfolio
        portfolio = self._initialize_portfolio()

        # Create initial property purchase event for the first property
        initial_purchase_events = []
        if len(portfolio["properties"]) > 0:
            first_property = portfolio["properties"][0]
            initial_purchase = PropertyPurchase(
                property_id=first_property.property_id,
                purchase_price=first_property.purchase_price,
                cash_required=portfolio["initial_cash_required"],
                financing_type=first_property.financing_type,
                loan_amount=first_property.loan_amount,
            )
            initial_purchase_events.append(initial_purchase)

        # Create initial snapshot (period 0)
        snapshot = self._create_detailed_snapshot(
            portfolio, 0, [], initial_purchase_events, []
        )
        all_snapshots = [snapshot]

        # Run simulation monthly
        for month in range(1, total_monthly_periods + 1):
            if self.simulation_ended:
                break

            period_refinancing_events = []
            period_purchases = []
            period_capital_injections = []

            # Apply monthly property appreciation
            self._apply_appreciation(portfolio)

            # Apply monthly principal payments and collect rent
            self._apply_monthly_operations(portfolio)

            # Apply additional capital injections
            capital_injections = self._apply_additional_capital_injections(
                portfolio, month
            )
            period_capital_injections.extend(capital_injections)

            # Check if we run out of cash for operating expenses
            monthly_operating_deficit = self._calculate_monthly_operating_deficit(
                portfolio
            )
            if (
                monthly_operating_deficit > 0
                and portfolio["cash_available"] < monthly_operating_deficit
            ):
                self.simulation_ended = True
                self.end_reason = (
                    f"Insufficient cash to cover R{monthly_operating_deficit:.0f} "
                    f"monthly operating deficit with only R{portfolio['cash_available']:.0f} available"
                )

            # Apply refinancing if enabled
            if (
                self.strategy.enable_refinancing
                and not self.simulation_ended
                and self._should_refinance(month)
            ):
                refinancing_events = self._apply_refinancing(portfolio)
                period_refinancing_events.extend(refinancing_events)

            # Apply reinvestment if enabled
            if self.strategy.enable_reinvestment and not self.simulation_ended:
                purchases = self._apply_reinvestment(portfolio)
                period_purchases.extend(purchases)

            # Create snapshot for this month
            snapshot = self._create_detailed_snapshot(
                portfolio,
                month,
                period_refinancing_events,
                period_purchases,
                period_capital_injections,
            )
            all_snapshots.append(snapshot)

        return all_snapshots

    def _filter_snapshots_by_frequency(
        self, monthly_snapshots: List[SimulationSnapshot]
    ) -> List[SimulationSnapshot]:
        """Return monthly snapshots since we're now tracking monthly"""
        return monthly_snapshots

    def _initialize_portfolio(self) -> Dict[str, Any]:
        """Initialize the portfolio with the first property"""

        # Determine financing type for first property based on strategy
        if self.strategy.strategy_type == StrategyType.CASH_ONLY:
            financing_type = "cash"
            loan_amount = 0.0
            monthly_payment = 0.0
        elif self.strategy.strategy_type == StrategyType.LEVERAGED:
            financing_type = f"{int(self.strategy.leverage_ratio * 100)}%_leverage"
            loan_amount = (
                self.base_property.acquisition_costs.purchase_price
                * self.strategy.leverage_ratio
            )
            monthly_payment = self._calculate_monthly_payment(loan_amount)
        else:  # MIXED strategy
            if self.strategy.first_property_type == FirstPropertyType.CASH:
                financing_type = "cash"
                loan_amount = 0.0
                monthly_payment = 0.0
            else:
                financing_type = f"{int(self.strategy.leverage_ratio * 100)}%_leverage"
                loan_amount = (
                    self.base_property.acquisition_costs.purchase_price
                    * self.strategy.leverage_ratio
                )
                monthly_payment = self._calculate_monthly_payment(loan_amount)

        # Calculate cash required for first property
        if financing_type == "cash":
            cash_required = (
                self.base_property.acquisition_costs.total_unfurnished_cost
                + (self.base_property.acquisition_costs.furnishing_cost or 0.0)
            )
        else:
            down_payment = self.base_property.acquisition_costs.purchase_price * (
                1 - self.strategy.leverage_ratio
            )
            cash_required = (
                down_payment
                + self.base_property.acquisition_costs.transfer_duty
                + self.base_property.acquisition_costs.conveyancing_fees
                + self.base_property.acquisition_costs.bond_registration
                + (self.base_property.acquisition_costs.furnishing_cost or 0.0)
            )

        # Check if we can afford the first property
        available_cash = self.base_property.strategy.available_investment_amount
        if available_cash < cash_required:
            # Start with no properties if we can't afford the first one
            portfolio = {
                "properties": [],
                "cash_available": available_cash,
                "property_counter": 0,
                "total_additional_capital_injected": 0.0,
            }
            self.simulation_ended = True
            self.end_reason = f"Insufficient cash to buy first property. Need R{cash_required:,.0f}, have R{available_cash:,.0f}"
            return portfolio

        # Calculate cost basis (actual cash invested in property, not total acquisition cost)
        cost_basis = cash_required

        # Create first property
        property_data = PropertyData(
            property_id=0,
            purchase_price=self.base_property.acquisition_costs.purchase_price,
            current_value=self.base_property.acquisition_costs.purchase_price,
            loan_amount=loan_amount,
            monthly_payment=monthly_payment,
            financing_type=financing_type,
            months_owned=0,
            annual_rental_income=self.base_property.operating.annual_rental_income,
            annual_expenses=self._calculate_annual_expenses(),
            monthly_cashflow=self._calculate_monthly_cashflow(),
            cost_basis=cost_basis,
        )

        portfolio = {
            "properties": [property_data],
            "cash_available": available_cash - cash_required,
            "property_counter": 1,
            "total_additional_capital_injected": 0.0,
            "initial_cash_required": cash_required,  # Store for initial purchase event
        }

        return portfolio

    def _calculate_initial_cash_required(self) -> float:
        """Calculate cash required for the initial property purchase"""
        # This will be stored in portfolio during initialization
        # and retrieved when creating the initial purchase event
        return 0.0  # Placeholder, actual value comes from portfolio

    def _calculate_monthly_payment(self, loan_amount: float) -> float:
        """Calculate monthly payment for a given loan amount"""
        if loan_amount <= 0:
            return 0.0

        interest_rate = self.base_property.financing.interest_rate or 0.105
        loan_term_years = self.base_property.financing.loan_term_years or 20
        monthly_rate = interest_rate / 12
        num_payments = loan_term_years * 12

        if monthly_rate == 0:
            return loan_amount / num_payments
        else:
            return (
                loan_amount
                * (monthly_rate * (1 + monthly_rate) ** num_payments)
                / ((1 + monthly_rate) ** num_payments - 1)
            )

    def _apply_appreciation(self, portfolio: Dict[str, Any]):
        """Apply monthly property appreciation to all properties"""
        appreciation_rate = self.base_property.financing.appreciation_rate
        monthly_appreciation_rate = appreciation_rate / 12

        for prop in portfolio["properties"]:
            prop.current_value *= 1 + monthly_appreciation_rate
            prop.months_owned += 1

    def _apply_monthly_operations(self, portfolio: Dict[str, Any]):
        """Apply monthly operations: principal payments and rent collection"""

        monthly_cashflow = 0.0

        for prop in portfolio["properties"]:
            # Apply principal payment (accurate amortization)
            if prop.loan_amount > 0 and prop.monthly_payment > 0:
                # Calculate actual principal payment based on current loan balance
                interest_rate = self.base_property.financing.interest_rate or 0.105
                monthly_rate = interest_rate / 12
                monthly_interest = prop.loan_amount * monthly_rate
                principal_payment = prop.monthly_payment - monthly_interest
                # Ensure principal payment doesn't exceed loan balance
                principal_payment = min(principal_payment, prop.loan_amount)
                prop.loan_amount = max(0, prop.loan_amount - principal_payment)

            # Calculate monthly cash flow from this property (with vacancy adjustment)
            monthly_gross_rent = prop.annual_rental_income / 12
            vacancy_rate = self.base_property.operating.vacancy_rate
            monthly_effective_rent = monthly_gross_rent * (1 - vacancy_rate)
            monthly_expenses = prop.annual_expenses / 12
            property_monthly_cashflow = (
                monthly_effective_rent - monthly_expenses - prop.monthly_payment
            )

            monthly_cashflow += property_monthly_cashflow
            prop.monthly_cashflow = property_monthly_cashflow

        # Apply monthly cash flow to available cash
        portfolio["cash_available"] += monthly_cashflow

    def _calculate_monthly_operating_deficit(self, portfolio: Dict[str, Any]) -> float:
        """Calculate the monthly operating deficit if any"""
        total_monthly_expenses = 0.0

        for prop in portfolio["properties"]:
            monthly_rent = prop.annual_rental_income / 12
            monthly_expenses = prop.annual_expenses / 12
            monthly_deficit = monthly_expenses + prop.monthly_payment - monthly_rent
            if monthly_deficit > 0:
                total_monthly_expenses += monthly_deficit

        return total_monthly_expenses

    def _should_refinance(self, current_month: int) -> bool:
        """Check if properties should be refinanced this month"""
        refinance_frequency_months = int(self.strategy.refinance_frequency_years * 12)
        return current_month % refinance_frequency_months == 0

    def _apply_refinancing(self, portfolio: Dict[str, Any]) -> List[RefinancingEvent]:
        """Apply refinancing to eligible properties"""
        refinancing_events = []

        target_ltv = self.base_property.strategy.target_refinance_ltv or 0.6

        for prop in portfolio["properties"]:
            if prop.financing_type != "cash" and prop.current_value > 0:
                # Calculate new loan amount based on current value
                max_new_loan = prop.current_value * target_ltv
                cash_extracted = max(0, max_new_loan - prop.loan_amount)

                if cash_extracted > 10000:  # Minimum extraction threshold
                    # Create refinancing event
                    event = RefinancingEvent(
                        property_id=prop.property_id,
                        property_value=prop.current_value,
                        old_loan_amount=prop.loan_amount,
                        new_loan_amount=max_new_loan,
                        cash_extracted=cash_extracted,
                        new_ltv=target_ltv,
                    )

                    # Update property
                    prop.loan_amount = max_new_loan

                    # Recalculate monthly payment based on new loan amount
                    if max_new_loan > 0:
                        # Handle None values for interest rate and loan term
                        interest_rate = (
                            self.base_property.financing.interest_rate or 0.105
                        )
                        loan_term_years = (
                            self.base_property.financing.loan_term_years or 20
                        )
                        monthly_rate = interest_rate / 12
                        num_payments = loan_term_years * 12

                        if monthly_rate == 0:
                            prop.monthly_payment = max_new_loan / num_payments
                        else:
                            prop.monthly_payment = (
                                max_new_loan
                                * (monthly_rate * (1 + monthly_rate) ** num_payments)
                                / ((1 + monthly_rate) ** num_payments - 1)
                            )
                    else:
                        prop.monthly_payment = 0

                    # Add cash to portfolio
                    portfolio["cash_available"] += cash_extracted
                    refinancing_events.append(event)

        return refinancing_events

    def _apply_reinvestment(self, portfolio: Dict[str, Any]) -> List[PropertyPurchase]:
        """Apply reinvestment to buy new properties"""
        purchases = []

        while True:
            # Calculate cash required for new property
            price_ratio = 1.0  # Base property price for now

            # Scale costs with price ratio
            purchase_price = (
                self.base_property.acquisition_costs.purchase_price * price_ratio
            )
            transfer_duty = (
                self.base_property.acquisition_costs.transfer_duty * price_ratio
            )
            conveyancing_fees = (
                self.base_property.acquisition_costs.conveyancing_fees * price_ratio
            )
            furnishing_cost = (
                self.base_property.acquisition_costs.furnishing_cost or 0.0
            ) * price_ratio

            # Determine financing type for this property
            use_leverage = self._should_use_leverage_for_next_property(portfolio)

            if use_leverage:
                bond_registration = (
                    self.base_property.acquisition_costs.bond_registration * price_ratio
                )
                down_payment = purchase_price * (1 - self.strategy.leverage_ratio)
                loan_amount = purchase_price * self.strategy.leverage_ratio
                financing_type = f"{int(self.strategy.leverage_ratio * 100)}%_leverage"
            else:
                bond_registration = 0.0
                down_payment = purchase_price
                loan_amount = 0.0
                financing_type = "cash"

            # Total cash required
            cash_required = (
                down_payment
                + transfer_duty
                + conveyancing_fees
                + bond_registration
                + furnishing_cost
            )

            if portfolio["cash_available"] >= cash_required:
                # Calculate monthly payment for new property
                if loan_amount > 0:
                    interest_rate = self.base_property.financing.interest_rate or 0.105
                    loan_term_years = self.base_property.financing.loan_term_years or 20
                    monthly_rate = interest_rate / 12
                    num_payments = loan_term_years * 12

                    if monthly_rate == 0:
                        monthly_payment = loan_amount / num_payments
                    else:
                        monthly_payment = (
                            loan_amount
                            * (monthly_rate * (1 + monthly_rate) ** num_payments)
                            / ((1 + monthly_rate) ** num_payments - 1)
                        )
                else:
                    monthly_payment = 0

                # Calculate cost basis (actual cash invested in property)
                cost_basis = cash_required

                # Create new property
                new_property = PropertyData(
                    property_id=portfolio["property_counter"],
                    purchase_price=purchase_price,
                    current_value=purchase_price,
                    loan_amount=loan_amount,
                    monthly_payment=monthly_payment,
                    financing_type=financing_type,
                    months_owned=0,
                    annual_rental_income=self.base_property.operating.annual_rental_income,
                    annual_expenses=self._calculate_annual_expenses(),
                    monthly_cashflow=self._calculate_monthly_cashflow(),
                    cost_basis=cost_basis,
                )

                # Create purchase event
                purchase = PropertyPurchase(
                    property_id=new_property.property_id,
                    purchase_price=purchase_price,
                    cash_required=cash_required,
                    financing_type=financing_type,
                    loan_amount=loan_amount,
                )

                # Update portfolio
                portfolio["properties"].append(new_property)
                portfolio["cash_available"] -= cash_required
                portfolio["property_counter"] += 1
                purchases.append(purchase)
            else:
                # Can't afford another property
                break

        return purchases

    def _should_use_leverage_for_next_property(self, portfolio: Dict[str, Any]) -> bool:
        """Determine if the next property should use leverage based on strategy"""

        if self.strategy.strategy_type == StrategyType.CASH_ONLY:
            return False
        elif self.strategy.strategy_type == StrategyType.LEVERAGED:
            return True
        else:  # MIXED strategy
            current_properties = len(portfolio["properties"])
            if current_properties == 0:
                return self.strategy.first_property_type == FirstPropertyType.LEVERAGED

            # Calculate current ratios
            leveraged_count = sum(
                1 for prop in portfolio["properties"] if prop.financing_type != "cash"
            )
            cash_count = current_properties - leveraged_count

            current_leverage_ratio = leveraged_count / current_properties
            current_cash_ratio = cash_count / current_properties

            target_leverage_ratio = self.strategy.leveraged_property_ratio
            target_cash_ratio = self.strategy.cash_property_ratio

            # Decide based on which ratio is furthest from target
            leverage_deficit = target_leverage_ratio - current_leverage_ratio
            cash_deficit = target_cash_ratio - current_cash_ratio

            if leverage_deficit > cash_deficit:
                return True
            else:
                return False

    def _calculate_annual_expenses(self) -> float:
        """Calculate annual operating expenses for a property"""
        operating = self.base_property.operating

        annual_levies = operating.monthly_levies * 12
        annual_management = (
            operating.annual_rental_income * operating.property_management_fee_rate
        )
        annual_insurance = operating.monthly_insurance * 12
        annual_maintenance = operating.monthly_maintenance_reserve * 12
        annual_furnishing = (operating.monthly_furnishing_repair_costs or 0.0) * 12

        annual_expenses = (
            annual_levies
            + annual_management
            + annual_insurance
            + annual_maintenance
            + annual_furnishing
        )

        return annual_expenses

    def _calculate_monthly_cashflow(self) -> float:
        """Calculate monthly cash flow for base property"""
        operating = self.base_property.operating

        effective_monthly_rent = operating.monthly_rental_income * (
            1 - operating.vacancy_rate
        )

        monthly_expenses = (
            operating.monthly_levies
            + (operating.monthly_rental_income * operating.property_management_fee_rate)
            + operating.monthly_insurance
            + operating.monthly_maintenance_reserve
            + (operating.monthly_furnishing_repair_costs or 0.0)
        )

        bond_payment = self.base_property.monthly_bond_payment or 0.0

        return effective_monthly_rent - monthly_expenses - bond_payment

    def _calculate_total_cash_invested(self, portfolio: Dict[str, Any]) -> float:
        """Calculate total cash invested across all properties"""
        # Sum the actual cost_basis of all properties
        total_cash_invested = 0.0
        for property_data in portfolio["properties"]:
            total_cash_invested += property_data.cost_basis

        return total_cash_invested

    def _create_detailed_snapshot(
        self,
        portfolio: Dict[str, Any],
        period: int,
        refinancing_events: List[RefinancingEvent],
        purchases: List[PropertyPurchase],
        capital_injections: List[CapitalInjectionEvent],
    ) -> SimulationSnapshot:
        """Create a detailed snapshot of the current portfolio state"""

        # Calculate annual yields if appropriate
        property_yields = self._calculate_annual_yields(
            portfolio,
            period,
            1 if self.strategy.tracking_frequency == TrackingFrequency.YEARLY else 12,
        )

        # Calculate portfolio yields
        portfolio_yields = self._calculate_portfolio_yields(
            portfolio,
            period,
            1 if self.strategy.tracking_frequency == TrackingFrequency.YEARLY else 12,
        )

        # Calculate totals
        total_property_value = sum(
            prop.current_value for prop in portfolio["properties"]
        )
        total_debt = sum(prop.loan_amount for prop in portfolio["properties"])
        total_equity = total_property_value - total_debt

        monthly_cashflow = sum(
            prop.monthly_cashflow for prop in portfolio["properties"]
        )
        annual_cashflow = monthly_cashflow * 12

        # Calculate total cash invested (simplified)
        total_cash_invested = self._calculate_total_cash_invested(portfolio)

        # Create snapshot for yearly tracking
        if self.strategy.tracking_frequency == TrackingFrequency.YEARLY:
            return SimulationSnapshot(
                period=period,
                properties=deepcopy(portfolio["properties"]),
                total_property_value=total_property_value,
                total_debt=total_debt,
                total_equity=total_equity,
                cash_available=portfolio["cash_available"],
                monthly_cashflow=monthly_cashflow,
                annual_cashflow=annual_cashflow,
                total_cash_invested=total_cash_invested,
                total_additional_capital_injected=portfolio[
                    "total_additional_capital_injected"
                ],
                refinancing_events=refinancing_events,
                property_purchases=purchases,
                capital_injections=capital_injections,
                property_yields=property_yields,
                portfolio_yields=portfolio_yields,
                simulation_ended=self.simulation_ended,
                end_reason=self.end_reason,
            )
        else:
            # Monthly tracking snapshot
            return SimulationSnapshot(
                period=period,
                properties=deepcopy(portfolio["properties"]),
                total_property_value=total_property_value,
                total_debt=total_debt,
                total_equity=total_equity,
                cash_available=portfolio["cash_available"],
                monthly_cashflow=monthly_cashflow,
                annual_cashflow=annual_cashflow,
                total_cash_invested=total_cash_invested,
                total_additional_capital_injected=portfolio[
                    "total_additional_capital_injected"
                ],
                refinancing_events=refinancing_events,
                property_purchases=purchases,
                capital_injections=capital_injections,
                property_yields=property_yields,
                simulation_ended=self.simulation_ended,
                end_reason=self.end_reason,
            )

    def _apply_additional_capital_injections(
        self, portfolio: Dict[str, Any], current_month: int
    ) -> List[CapitalInjectionEvent]:
        """Apply additional capital injections based on strategy configuration"""

        capital_injections = []

        if not self.strategy.additional_capital_injections:
            return capital_injections

        for injection_config in self.strategy.additional_capital_injections:
            should_inject = self._should_inject_capital(injection_config, current_month)

            if should_inject:
                portfolio["cash_available"] += injection_config.amount
                self.total_additional_capital += injection_config.amount
                portfolio["total_additional_capital_injected"] = (
                    self.total_additional_capital
                )

                injection_event = CapitalInjectionEvent(
                    amount=injection_config.amount,
                    source=injection_config.frequency.value,
                    total_additional_capital_to_date=self.total_additional_capital,
                )
                capital_injections.append(injection_event)

        return capital_injections

    def _should_inject_capital(
        self,
        injection_config: AdditionalCapitalInjection,
        current_month: int,
    ) -> bool:
        """Determine if capital should be injected this month"""

        # Check if we're in the injection month range
        # Convert period-based config to month-based
        start_month = injection_config.start_period
        end_month = injection_config.end_period

        if current_month < start_month:
            return False

        if end_month and current_month > end_month:
            return False

        # Handle one-time injections in specific months
        if injection_config.frequency == AdditionalCapitalFrequency.ONE_TIME:
            if injection_config.specific_periods:
                return current_month in injection_config.specific_periods
            else:
                # One-time injection at start_month
                return current_month == start_month

        # Handle recurring injections - always work in monthly terms
        months_since_start = current_month - start_month

        if injection_config.frequency == AdditionalCapitalFrequency.MONTHLY:
            return True  # Every month

        elif injection_config.frequency == AdditionalCapitalFrequency.QUARTERLY:
            return months_since_start % 3 == 0  # Every 3 months

        elif injection_config.frequency == AdditionalCapitalFrequency.YEARLY:
            return months_since_start % 12 == 0  # Every 12 months

        elif injection_config.frequency == AdditionalCapitalFrequency.FIVE_YEARLY:
            return months_since_start % (5 * 12) == 0  # Every 60 months

        return False

    def _calculate_annual_yields(
        self, portfolio: Dict[str, Any], current_period: int, periods_per_year: int
    ) -> List[PropertyYields]:
        """Calculate annual yields for all properties"""
        property_yields = []

        # Only calculate yields on annual boundaries or for yearly tracking
        if periods_per_year == 12 and current_period % 12 != 0:
            return property_yields
        elif periods_per_year == 1:
            # For yearly tracking, calculate every period
            pass
        else:
            return property_yields

        for prop in portfolio["properties"]:
            yields = self._calculate_property_yields(
                prop, current_period, periods_per_year
            )
            if yields:
                property_yields.append(yields)

        return property_yields

    def _calculate_property_yields(
        self, property_data: PropertyData, current_period: int, periods_per_year: int
    ) -> PropertyYields:
        """Calculate yields for a single property"""

        current_value = property_data.current_value
        purchase_price = property_data.purchase_price

        # Calculate cash invested (simplified for now)
        if property_data.financing_type == "cash":
            cash_invested = purchase_price
        else:
            # For leveraged properties, estimate initial cash required
            ltv = float(property_data.financing_type.replace("%_leverage", "")) / 100
            down_payment = purchase_price * (1 - ltv)
            # Add estimated transaction costs (simplified)
            transaction_costs = purchase_price * 0.08  # Rough estimate
            cash_invested = down_payment + transaction_costs

        # Use property's stored values
        annual_rental_income = property_data.annual_rental_income
        annual_expenses = property_data.annual_expenses
        annual_debt_service = property_data.monthly_payment * 12
        annual_cashflow = annual_rental_income - annual_expenses - annual_debt_service

        # Calculate rental yield
        rental_yield = (
            annual_rental_income / current_value if current_value > 0 else 0.0
        )

        # Calculate net rental yield (after expenses, before debt service)
        net_annual_income = annual_rental_income - annual_expenses
        net_rental_yield = (
            net_annual_income / current_value if current_value > 0 else 0.0
        )

        # Calculate cash-on-cash return (annual cashflow / cash invested)
        cash_on_cash_return = (
            annual_cashflow / cash_invested if cash_invested > 0 else 0.0
        )

        # Calculate capital growth yield (annualized appreciation)
        years_held = (
            property_data.months_owned / 12 if property_data.months_owned > 0 else 1
        )
        if years_held > 0 and purchase_price > 0:
            capital_growth_yield = (
                (current_value / purchase_price) ** (1 / years_held)
            ) - 1
        else:
            capital_growth_yield = 0.0

        # Calculate total return yield
        total_return_yield = net_rental_yield + capital_growth_yield

        return PropertyYields(
            property_id=property_data.property_id,
            rental_yield=rental_yield,
            net_rental_yield=net_rental_yield,
            cash_on_cash_return=cash_on_cash_return,
            total_return_yield=total_return_yield,
            capital_growth_yield=capital_growth_yield,
        )

    def _calculate_portfolio_yields(
        self, portfolio: Dict[str, Any], current_period: int, periods_per_year: int
    ) -> PortfolioYields:
        """Calculate yields for the entire portfolio"""

        properties = portfolio.get("properties", [])

        if not properties:
            return PortfolioYields(
                period=current_period,
                portfolio_rental_yield=0.0,
                portfolio_net_rental_yield=0.0,
                portfolio_cash_on_cash_return=0.0,
                portfolio_capital_growth_yield=0.0,
                portfolio_total_return_yield=0.0,
                total_annual_rental_income=0.0,
                total_annual_operating_expenses=0.0,
                total_annual_cashflow=0.0,
                total_portfolio_value=0.0,
                total_cash_invested=0.0,
            )

        # Calculate portfolio totals
        total_portfolio_value = sum(prop.current_value for prop in properties)
        total_annual_rental_income = (
            len(properties) * self.base_property.operating.annual_rental_income
        )
        total_annual_operating_expenses = (
            len(properties) * self._calculate_annual_expenses()
        )

        # Calculate total annual cashflow
        total_annual_cashflow = portfolio.get("cash_flow_12_months", 0.0)
        if total_annual_cashflow == 0.0:
            # Fallback calculation if not tracked
            monthly_cashflow = self._calculate_monthly_cashflow()
            total_annual_cashflow = monthly_cashflow * 12 * len(properties)

        # Calculate total cash invested
        total_cash_invested = self._calculate_total_cash_invested(portfolio)

        # Calculate portfolio yields
        portfolio_rental_yield = 0.0
        portfolio_net_rental_yield = 0.0
        portfolio_cash_on_cash_return = 0.0
        portfolio_capital_growth_yield = 0.0

        if total_portfolio_value > 0:
            portfolio_rental_yield = total_annual_rental_income / total_portfolio_value
            portfolio_net_rental_yield = (
                total_annual_rental_income - total_annual_operating_expenses
            ) / total_portfolio_value

        if total_cash_invested > 0:
            portfolio_cash_on_cash_return = total_annual_cashflow / total_cash_invested

        # Calculate portfolio capital growth yield (weighted average)
        total_weighted_growth = 0.0
        total_weight = 0.0

        for prop in properties:
            if prop.months_owned > 0 and prop.purchase_price > 0:
                years_held = prop.months_owned / 12
                if years_held > 0:
                    property_growth = (
                        (prop.current_value / prop.purchase_price) ** (1 / years_held)
                    ) - 1
                    weight = prop.current_value
                    total_weighted_growth += property_growth * weight
                    total_weight += weight

        if total_weight > 0:
            portfolio_capital_growth_yield = total_weighted_growth / total_weight

        # Calculate total return yield
        portfolio_total_return_yield = (
            portfolio_net_rental_yield + portfolio_capital_growth_yield
        )

        return PortfolioYields(
            period=current_period,
            portfolio_rental_yield=portfolio_rental_yield,
            portfolio_net_rental_yield=portfolio_net_rental_yield,
            portfolio_cash_on_cash_return=portfolio_cash_on_cash_return,
            portfolio_capital_growth_yield=portfolio_capital_growth_yield,
            portfolio_total_return_yield=portfolio_total_return_yield,
            total_annual_rental_income=total_annual_rental_income,
            total_annual_operating_expenses=total_annual_operating_expenses,
            total_annual_cashflow=total_annual_cashflow,
            total_portfolio_value=total_portfolio_value,
            total_cash_invested=total_cash_invested,
        )


def create_cash_strategy(
    months: int,
    reinvestment: bool = True,
    tracking: TrackingFrequency = TrackingFrequency.MONTHLY,
    additional_capital_injections: Optional[List[AdditionalCapitalInjection]] = None,
) -> StrategyConfig:
    """Create a cash-only strategy"""
    return StrategyConfig(
        strategy_type=StrategyType.CASH_ONLY,
        simulation_months=months,
        leverage_ratio=0.0,
        cash_ratio=1.0,
        leveraged_property_ratio=0.0,
        cash_property_ratio=1.0,
        first_property_type=FirstPropertyType.CASH,
        enable_refinancing=False,
        enable_reinvestment=reinvestment,
        tracking_frequency=tracking,
        additional_capital_injections=additional_capital_injections or [],
    )


def create_leveraged_strategy(
    months: int,
    leverage_ratio: float = 0.7,
    refinancing: bool = True,
    refinance_years: float = 1.0,
    reinvestment: bool = True,
    tracking: TrackingFrequency = TrackingFrequency.MONTHLY,
    additional_capital_injections: Optional[List[AdditionalCapitalInjection]] = None,
) -> StrategyConfig:
    """Create a leveraged strategy"""
    return StrategyConfig(
        strategy_type=StrategyType.LEVERAGED,
        simulation_months=months,
        leverage_ratio=leverage_ratio,
        cash_ratio=1.0 - leverage_ratio,
        leveraged_property_ratio=1.0,
        cash_property_ratio=0.0,
        first_property_type=FirstPropertyType.LEVERAGED,
        enable_refinancing=refinancing,
        refinance_frequency_years=refinance_years,
        enable_reinvestment=reinvestment,
        tracking_frequency=tracking,
        additional_capital_injections=additional_capital_injections or [],
    )


def create_mixed_strategy(
    months: int,
    leveraged_property_ratio: float = 0.7,  # 70% of properties leveraged
    cash_property_ratio: float = 0.3,  # 30% of properties cash
    leverage_ratio: float = 0.5,  # 50% LTV when leveraged
    first_property_type: FirstPropertyType = FirstPropertyType.LEVERAGED,
    refinancing: bool = True,
    refinance_years: float = 1.0,
    reinvestment: bool = True,
    tracking: TrackingFrequency = TrackingFrequency.MONTHLY,
    additional_capital_injections: Optional[List[AdditionalCapitalInjection]] = None,
) -> StrategyConfig:
    """Create a mixed strategy with both leveraged and cash properties"""

    if leveraged_property_ratio + cash_property_ratio != 1.0:
        raise ValueError(
            f"Property ratios must sum to 1.0, got: {leveraged_property_ratio + cash_property_ratio}"
        )

    return StrategyConfig(
        strategy_type=StrategyType.MIXED,
        simulation_months=months,
        leverage_ratio=leverage_ratio,
        cash_ratio=1.0 - leverage_ratio,
        leveraged_property_ratio=leveraged_property_ratio,
        cash_property_ratio=cash_property_ratio,
        first_property_type=first_property_type,
        enable_refinancing=refinancing,
        refinance_frequency_years=refinance_years,
        enable_reinvestment=reinvestment,
        tracking_frequency=tracking,
        additional_capital_injections=additional_capital_injections or [],
    )


def print_detailed_simulation_results(snapshots: List[SimulationSnapshot], title: str):
    """Print detailed simulation results with all events"""

    print("=" * 80)
    print(f"DETAILED SIMULATION: {title.upper()}")
    print("=" * 80)

    for snapshot in snapshots:
        period_type = "Month" if len(snapshots) > 15 else "Year"
        print(f"\n{period_type} {snapshot.period}:")
        print(
            f"  Portfolio: {len(snapshot.properties)} properties, "
            f"R{snapshot.total_property_value:,.0f} total value"
        )
        print(
            f"  Equity: R{snapshot.total_equity:,.0f}, "
            f"Debt: R{snapshot.total_debt:,.0f}"
        )
        print(f"  Cash Available: R{snapshot.cash_available:,.0f}")
        print(f"  Monthly Cashflow: R{snapshot.monthly_cashflow:,.0f}")

        # Show refinancing events
        if snapshot.refinancing_events:
            print(f"  REFINANCING EVENTS:")
            for event in snapshot.refinancing_events:
                print(
                    f"    Property {event.property_id}: Refinanced to {event.new_ltv:.0%} LTV"
                )
                print(f"      Property Value: R{event.property_value:,.0f}")
                print(
                    f"      Old Loan: R{event.old_loan_amount:,.0f} -> New Loan: R{event.new_loan_amount:,.0f}"
                )
                print(f"      Cash Extracted: R{event.cash_extracted:,.0f}")

        # Show property yields if available
        if snapshot.property_yields:
            print(f"  PROPERTY YIELDS:")
            for yields in snapshot.property_yields:
                print(f"    Property {yields.property_id}:")
                print(f"      Rental Yield: {yields.rental_yield:.2%}")
                print(f"      Net Rental Yield: {yields.net_rental_yield:.2%}")
                print(f"      Cash-on-Cash Return: {yields.cash_on_cash_return:.2%}")
                print(f"      Capital Growth Yield: {yields.capital_growth_yield:.2%}")
                print(f"      Total Return Yield: {yields.total_return_yield:.2%}")

        # Show portfolio yields if available
        if snapshot.portfolio_yields:
            print(f"  PORTFOLIO YIELDS:")
            print(
                f"    Portfolio Rental Yield: {snapshot.portfolio_yields.portfolio_rental_yield:.2%}"
            )
            print(
                f"    Portfolio Net Rental Yield: {snapshot.portfolio_yields.portfolio_net_rental_yield:.2%}"
            )
            print(
                f"    Portfolio Cash-on-Cash Return: {snapshot.portfolio_yields.portfolio_cash_on_cash_return:.2%}"
            )
            print(
                f"    Portfolio Capital Growth Yield: {snapshot.portfolio_yields.portfolio_capital_growth_yield:.2%}"
            )
            print(
                f"    Portfolio Total Return Yield: {snapshot.portfolio_yields.portfolio_total_return_yield:.2%}"
            )
            print(
                f"    Total Portfolio Value: R{snapshot.portfolio_yields.total_portfolio_value:,.0f}"
            )
            print(
                f"    Total Cash Invested: R{snapshot.portfolio_yields.total_cash_invested:,.0f}"
            )

        # Show capital injection events
        if snapshot.capital_injections:
            print(f"  CAPITAL INJECTIONS:")
            for injection in snapshot.capital_injections:
                print(
                    f"    {injection.source.replace('_', ' ').title()}: R{injection.amount:,.0f}"
                )
                print(
                    f"      Total Additional Capital: R{injection.total_additional_capital_to_date:,.0f}"
                )

        # Show property purchases
        if snapshot.property_purchases:
            print(f"  PROPERTY PURCHASES:")
            for purchase in snapshot.property_purchases:
                print(
                    f"    Property {purchase.property_id}: R{purchase.purchase_price:,.0f} ({purchase.financing_type})"
                )
                print(
                    f"      Cash Required: R{purchase.cash_required:,.0f}, Loan: R{purchase.loan_amount:,.0f}"
                )

    # Final summary
    final_snapshot = snapshots[-1]
    print(f"\n" + "=" * 80)
    print(f"FINAL RESULTS")
    print("=" * 80)
    print(f"Properties: {len(final_snapshot.properties)}")
    print(f"Portfolio Value: R{final_snapshot.total_property_value:,.0f}")
    print(f"Total Debt: R{final_snapshot.total_debt:,.0f}")
    print(f"Total Equity: R{final_snapshot.total_equity:,.0f}")
    print(f"Cash Available: R{final_snapshot.cash_available:,.0f}")
    print(
        f"Net Worth: R{final_snapshot.total_equity + final_snapshot.cash_available:,.0f}"
    )

    if final_snapshot.simulation_ended:
        print(f"Simulation ended: {final_snapshot.end_reason}")


def compare_strategies(
    strategy_results: List[tuple[str, List[SimulationSnapshot]]],
    title: str = "STRATEGY COMPARISON",
):
    """Compare multiple strategy results"""

    print("=" * 80)
    print(title)
    print("=" * 80)

    # Header
    print(
        f"{'Strategy':<20} | {'Properties':>10} | {'Portfolio Value':>15} | {'Net Worth':>12} | {'Cash Flow':>10}"
    )
    print("-" * 80)

    # Results for each strategy
    for strategy_name, snapshots in strategy_results:
        final = snapshots[-1]
        net_worth = final.total_equity + final.cash_available

        print(
            f"{strategy_name:<20} | {len(final.properties):>10} | "
            f"R{final.total_property_value:>13,.0f} | R{net_worth:>10,.0f} | R{final.monthly_cashflow:>8,.0f}"
        )

    print("=" * 80)
