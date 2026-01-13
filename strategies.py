from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from main import FinancingType, PropertyInvestment, RefineFrequency


class StrategyType(Enum):
    CASH_ONLY = "cash_only"
    LEVERAGED = "leveraged"
    MIXED = "mixed"


class FirstPropertyType(Enum):
    CASH = "cash"
    LEVERAGED = "leveraged"


class TrackingFrequency(Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


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
    tracking_frequency: TrackingFrequency = TrackingFrequency.YEARLY
    simulation_years: int = 10

    # Additional capital injection parameters
    additional_capital_injections: List[AdditionalCapitalInjection] = field(
        default_factory=list
    )


@dataclass
class PropertyData:
    """Detailed data for a single property"""

    property_id: int
    purchase_price: float
    current_value: float
    loan_amount: float
    original_loan_amount: float
    monthly_payment: float
    monthly_cashflow: float
    purchase_period: int
    last_refinance_period: Optional[int] = None
    total_principal_paid: float = 0.0


@dataclass
class PropertyYields:
    """Annual yield calculations for a property"""

    property_id: int
    period: int
    rental_yield: float  # Annual rental income / current property value
    net_rental_yield: float  # (Annual rental - expenses) / current property value
    cash_on_cash_return: float  # Annual cashflow / cash invested
    total_return_yield: float  # Net rental yield + capital appreciation
    annual_rental_income: float
    annual_expenses: float
    annual_cashflow: float
    cash_invested: float  # Initial cash + any additional cash from refinancing
    capital_appreciation_rate: float  # Annual appreciation for this period


@dataclass
class RefinancingEvent:
    """Details of a refinancing event"""

    period: int
    property_id: int
    old_loan_amount: float
    new_loan_amount: float
    cash_extracted: float
    new_ltv: float
    property_value_at_refi: float


@dataclass
class PropertyPurchase:
    """Details of a property purchase"""

    period: int
    property_id: int
    purchase_price: float
    cash_required: float
    loan_amount: float
    financing_type: str


@dataclass
class CapitalInjectionEvent:
    """Details of a capital injection event"""

    period: int
    amount: float
    source: str  # "monthly", "quarterly", "yearly", "one_time", etc.
    total_additional_capital_to_date: float


@dataclass
class SimulationSnapshot:
    """Snapshot of portfolio state at a specific period"""

    period: int
    cash_available: float
    total_cash_invested: float
    num_properties: int
    total_property_value: float
    total_debt: float
    total_equity: float
    monthly_rental_income: float
    monthly_operating_expenses: float
    monthly_debt_service: float
    monthly_net_cashflow: float
    annual_cashflow: float
    properties: List[PropertyData]
    refinancing_events: List[RefinancingEvent]
    property_purchases: List[PropertyPurchase]
    capital_injections: List[CapitalInjectionEvent]
    total_additional_capital_injected: float = 0.0
    property_yields: List[PropertyYields] = field(
        default_factory=list
    )  # Annual yields by property
    simulation_ended: bool = False
    end_reason: Optional[str] = None


class PropertyPortfolioSimulator:
    """Simulates property investment strategies over time with detailed tracking"""

    def __init__(self, base_property: PropertyInvestment, strategy: StrategyConfig):
        self.base_property = base_property
        self.strategy = strategy
        self.snapshots: List[SimulationSnapshot] = []
        self.property_counter = 0
        self.simulation_ended = False
        self.end_reason = None
        self.total_additional_capital = 0.0

    def simulate(self) -> List[SimulationSnapshot]:
        """Run the complete simulation and return detailed snapshots"""

        # Initialize portfolio
        portfolio = self._initialize_portfolio()

        # Determine simulation periods
        if self.strategy.tracking_frequency == TrackingFrequency.MONTHLY:
            total_periods = self.strategy.simulation_years * 12
            periods_per_year = 12
        else:
            total_periods = self.strategy.simulation_years
            periods_per_year = 1

        # Create initial snapshot (period 0)
        snapshot = self._create_detailed_snapshot(portfolio, 0, [], [], [])
        self.snapshots.append(snapshot)

        # Run simulation
        for period in range(1, total_periods + 1):
            if self.simulation_ended:
                break

            period_refinancing_events = []
            period_purchases = []
            period_capital_injections = []

            # Apply property appreciation
            self._apply_appreciation(portfolio, periods_per_year)

            # Apply principal payments and collect rent
            self._apply_principal_payments_and_rent(portfolio, periods_per_year)

            # Apply additional capital injections
            capital_injections = self._apply_additional_capital_injections(
                portfolio, period, periods_per_year
            )
            period_capital_injections.extend(capital_injections)

            # Check if we run out of cash for operating expenses
            if not self._check_cash_sufficiency(portfolio):
                self.simulation_ended = True
                self.end_reason = (
                    f"Insufficient cash to cover operating expenses at period {period}"
                )
                break

            # Apply refinancing if enabled and time
            if self.strategy.enable_refinancing:
                refinancing_events = self._apply_refinancing(
                    portfolio, period, periods_per_year
                )
                period_refinancing_events.extend(refinancing_events)

            # Try to buy new properties with available cash
            if self.strategy.enable_reinvestment:
                purchases = self._try_buy_new_properties(portfolio, period)
                period_purchases.extend(purchases)

            # Calculate annual yields if this is an annual period
            property_yields = self._calculate_annual_yields(
                portfolio, period, periods_per_year
            )

            # Create detailed snapshot
            snapshot = self._create_detailed_snapshot(
                portfolio,
                period,
                period_refinancing_events,
                period_purchases,
                period_capital_injections,
                property_yields,
            )

            if self.simulation_ended:
                snapshot.simulation_ended = True
                snapshot.end_reason = self.end_reason

            self.snapshots.append(snapshot)

        return self.snapshots

    def _initialize_portfolio(self) -> Dict[str, Any]:
        """Initialize the portfolio with first property"""

        # Create the first property
        initial_property = deepcopy(self.base_property)

        # Determine financing type for first property
        if self.strategy.strategy_type == StrategyType.CASH_ONLY:
            use_leverage = False
        elif self.strategy.strategy_type == StrategyType.LEVERAGED:
            use_leverage = True
        else:  # MIXED strategy
            use_leverage = (
                self.strategy.first_property_type == FirstPropertyType.LEVERAGED
            )

        if use_leverage:
            initial_property.financing.financing_type = FinancingType.LEVERAGED
            initial_property.financing.ltv_ratio = self.strategy.leverage_ratio
            loan_amount = (
                initial_property.acquisition_costs.purchase_price
                * self.strategy.leverage_ratio
            )
            monthly_payment = initial_property.monthly_bond_payment or 0
        else:
            initial_property.financing.financing_type = FinancingType.CASH
            initial_property.financing.ltv_ratio = 0.0
            initial_property.acquisition_costs.bond_registration = 0
            loan_amount = 0
            monthly_payment = 0

        cash_needed = initial_property.initial_cash_required

        if cash_needed > self.base_property.strategy.available_investment_amount:
            self.simulation_ended = True
            self.end_reason = "Insufficient initial capital for first property"
            return {}

        # Create property data
        property_data = PropertyData(
            property_id=self.property_counter,
            purchase_price=initial_property.acquisition_costs.purchase_price,
            current_value=initial_property.acquisition_costs.purchase_price,
            loan_amount=loan_amount,
            original_loan_amount=loan_amount,
            monthly_payment=monthly_payment,
            monthly_cashflow=initial_property.monthly_cashflow,
            purchase_period=0,
            last_refinance_period=None,
        )

        self.property_counter += 1

        portfolio = {
            "properties": [property_data],
            "cash_available": self.base_property.strategy.available_investment_amount
            - cash_needed,
            "total_cash_invested": cash_needed,
            "total_additional_capital": 0.0,
            "base_property_template": initial_property,
            "leveraged_properties": 1 if use_leverage else 0,
            "cash_properties": 0 if use_leverage else 1,
        }

        return portfolio

    def _apply_appreciation(self, portfolio: Dict[str, Any], periods_per_year: int):
        """Apply property appreciation"""
        appreciation_rate_per_period = (
            self.base_property.financing.appreciation_rate / periods_per_year
        )

        for prop in portfolio["properties"]:
            prop.current_value *= 1 + appreciation_rate_per_period

    def _apply_principal_payments_and_rent(
        self, portfolio: Dict[str, Any], periods_per_year: int
    ):
        """Apply principal payments, collect rent, and pay operating expenses"""

        # Calculate period multiplier
        if periods_per_year == 12:  # Monthly
            period_multiplier = 1
        else:  # Yearly
            period_multiplier = 12

        total_cashflow = 0

        for prop in portfolio["properties"]:
            # Calculate net cashflow for this period
            period_cashflow = prop.monthly_cashflow * period_multiplier
            total_cashflow += period_cashflow

            # Apply principal payment (simplified - assume 1% of payment goes to principal)
            if prop.loan_amount > 0 and prop.monthly_payment > 0:
                monthly_principal = (
                    prop.monthly_payment * 0.01
                )  # Simplified principal calculation
                principal_payment = monthly_principal * period_multiplier
                prop.loan_amount = max(0, prop.loan_amount - principal_payment)
                prop.total_principal_paid += principal_payment

        # Add total cashflow to available cash
        portfolio["cash_available"] += total_cashflow

    def _check_cash_sufficiency(self, portfolio: Dict[str, Any]) -> bool:
        """Check if there's sufficient cash to continue operations"""
        return portfolio["cash_available"] >= 0

    def _apply_refinancing(
        self, portfolio: Dict[str, Any], current_period: int, periods_per_year: int
    ) -> List[RefinancingEvent]:
        """Apply refinancing if conditions are met"""
        refinancing_events = []
        refinance_period_interval = (
            self.strategy.refinance_frequency_years * periods_per_year
        )

        for prop in portfolio["properties"]:
            if prop.loan_amount == 0:  # Can't refinance cash properties with no debt
                continue

            last_refinance = prop.last_refinance_period or prop.purchase_period

            if current_period - last_refinance >= refinance_period_interval:
                # Refinance the property
                old_loan_amount = prop.loan_amount
                new_loan_amount = prop.current_value * self.strategy.leverage_ratio
                cash_extracted = new_loan_amount - old_loan_amount

                if cash_extracted > 0:  # Only refinance if we can extract cash
                    # Update property loan amount
                    prop.loan_amount = new_loan_amount
                    prop.last_refinance_period = current_period

                    # Recalculate monthly payment based on new loan amount
                    if new_loan_amount > 0:
                        # Handle None values for interest rate and loan term
                        if (
                            self.base_property.financing.interest_rate is None
                            or self.base_property.financing.loan_term_years is None
                        ):
                            raise ValueError(
                                "Interest rate and loan term must be provided for leveraged financing"
                            )

                        # Simplified payment calculation based on original interest rate
                        monthly_rate = self.base_property.financing.interest_rate / 12
                        num_payments = self.base_property.financing.loan_term_years * 12

                        if monthly_rate == 0:
                            prop.monthly_payment = new_loan_amount / num_payments
                        else:
                            prop.monthly_payment = (
                                new_loan_amount
                                * (monthly_rate * (1 + monthly_rate) ** num_payments)
                                / ((1 + monthly_rate) ** num_payments - 1)
                            )

                    # Recalculate monthly cashflow
                    base_cashflow = self._calculate_base_monthly_cashflow()
                    prop.monthly_cashflow = base_cashflow - prop.monthly_payment

                    # Add extracted cash to portfolio
                    portfolio["cash_available"] += cash_extracted

                    # Record refinancing event
                    refinancing_event = RefinancingEvent(
                        period=current_period,
                        property_id=prop.property_id,
                        old_loan_amount=old_loan_amount,
                        new_loan_amount=new_loan_amount,
                        cash_extracted=cash_extracted,
                        new_ltv=self.strategy.leverage_ratio,
                        property_value_at_refi=prop.current_value,
                    )
                    refinancing_events.append(refinancing_event)

        return refinancing_events

    def _calculate_base_monthly_cashflow(self) -> float:
        """Calculate base monthly cashflow before debt service"""
        return (
            self.base_property.operating.effective_monthly_rental
            - self.base_property.operating.total_monthly_expenses
        )

    def _try_buy_new_properties(
        self, portfolio: Dict[str, Any], period: int
    ) -> List[PropertyPurchase]:
        """Try to buy new properties with available cash"""
        purchases = []

        while True:
            # Use current market value (average of existing properties)
            if portfolio["properties"]:
                current_market_price = sum(
                    prop.current_value for prop in portfolio["properties"]
                ) / len(portfolio["properties"])
            else:
                current_market_price = (
                    self.base_property.acquisition_costs.purchase_price
                )

            # Calculate proportional costs based on price appreciation
            price_ratio = (
                current_market_price
                / self.base_property.acquisition_costs.purchase_price
            )

            # Calculate all acquisition costs
            transfer_duty = (
                self.base_property.acquisition_costs.transfer_duty * price_ratio
            )
            conveyancing_fees = (
                self.base_property.acquisition_costs.conveyancing_fees * price_ratio
            )
            furnishing_cost = (
                (self.base_property.acquisition_costs.furnishing_cost or 0.0) * price_ratio
            )

            # Determine financing type for this property
            use_leverage = self._should_use_leverage_for_next_property(portfolio)

            if use_leverage:
                bond_registration = (
                    self.base_property.acquisition_costs.bond_registration * price_ratio
                )
                loan_amount = current_market_price * self.strategy.leverage_ratio
                down_payment = current_market_price - loan_amount
                financing_type = f"{self.strategy.leverage_ratio:.0%}_leverage"
            else:
                bond_registration = 0
                loan_amount = 0
                down_payment = current_market_price
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
                        if (
                            self.base_property.financing.interest_rate is None
                            or self.base_property.financing.loan_term_years is None
                        ):
                            raise ValueError(
                                "Interest rate and loan term must be provided for leveraged financing"
                            )

                        monthly_payment = (
                            loan_amount
                            * (monthly_rate * (1 + monthly_rate) ** num_payments)
                            / ((1 + monthly_rate) ** num_payments - 1)
                        )
                else:
                    monthly_payment = 0

                # Calculate monthly cashflow for new property
                base_cashflow = self._calculate_base_monthly_cashflow()
                monthly_cashflow = base_cashflow - monthly_payment

                # Create new property data
                new_property = PropertyData(
                    property_id=self.property_counter,
                    purchase_price=current_market_price,
                    current_value=current_market_price,
                    loan_amount=loan_amount,
                    original_loan_amount=loan_amount,
                    monthly_payment=monthly_payment,
                    monthly_cashflow=monthly_cashflow,
                    purchase_period=period,
                    last_refinance_period=None,
                )

                # Add property to portfolio
                portfolio["properties"].append(new_property)
                portfolio["cash_available"] -= cash_required
                portfolio["total_cash_invested"] += cash_required

                # Update property counters for mixed strategy
                if use_leverage:
                    portfolio["leveraged_properties"] = (
                        portfolio.get("leveraged_properties", 0) + 1
                    )
                else:
                    portfolio["cash_properties"] = (
                        portfolio.get("cash_properties", 0) + 1
                    )

                # Record purchase
                purchase = PropertyPurchase(
                    period=period,
                    property_id=self.property_counter,
                    purchase_price=current_market_price,
                    cash_required=cash_required,
                    loan_amount=loan_amount,
                    financing_type=financing_type,
                )
                purchases.append(purchase)

                self.property_counter += 1

                # Check if remaining cash can still cover negative cashflow
                total_monthly_cashflow = sum(
                    prop.monthly_cashflow for prop in portfolio["properties"]
                )
                if total_monthly_cashflow < 0:
                    months_of_coverage = portfolio["cash_available"] / abs(
                        total_monthly_cashflow
                    )
                    if months_of_coverage < 6:  # Less than 6 months coverage
                        break  # Stop buying to preserve cash
            else:
                break

        return purchases

    def _should_use_leverage_for_next_property(self, portfolio: Dict[str, Any]) -> bool:
        """Determine if the next property should use leverage based on strategy ratios"""

        if self.strategy.strategy_type == StrategyType.CASH_ONLY:
            return False
        elif self.strategy.strategy_type == StrategyType.LEVERAGED:
            return True
        else:  # MIXED strategy
            total_properties = len(portfolio["properties"])
            leveraged_properties = portfolio.get("leveraged_properties", 0)
            cash_properties = portfolio.get("cash_properties", 0)

            if total_properties == 0:
                # This should not happen as we're buying additional properties
                return self.strategy.first_property_type == FirstPropertyType.LEVERAGED

            # Calculate current ratios
            current_leverage_ratio = leveraged_properties / total_properties
            current_cash_ratio = cash_properties / total_properties

            # Determine what type to buy next based on target ratios
            target_leverage_ratio = self.strategy.leveraged_property_ratio
            target_cash_ratio = self.strategy.cash_property_ratio

            # If we're below the target leverage ratio, buy leveraged
            if current_leverage_ratio < target_leverage_ratio:
                return True
            # If we're below the target cash ratio, buy cash
            elif current_cash_ratio < target_cash_ratio:
                return False
            else:
                # If both ratios are met, default to the strategy's preference
                # Use the ratio that has more "room" to grow
                leverage_room = target_leverage_ratio - current_leverage_ratio
                cash_room = target_cash_ratio - current_cash_ratio
                return leverage_room >= cash_room

    def _apply_additional_capital_injections(
        self, portfolio: Dict[str, Any], current_period: int, periods_per_year: int
    ) -> List[CapitalInjectionEvent]:
        """Apply additional capital injections based on strategy configuration"""

        capital_injections = []

        if not self.strategy.additional_capital_injections:
            return capital_injections

        for injection_config in self.strategy.additional_capital_injections:
            should_inject = self._should_inject_capital(
                injection_config, current_period, periods_per_year
            )

            if should_inject:
                # Add capital to portfolio
                portfolio["cash_available"] += injection_config.amount
                portfolio["total_additional_capital"] += injection_config.amount
                self.total_additional_capital += injection_config.amount

                # Create injection event
                injection_event = CapitalInjectionEvent(
                    period=current_period,
                    amount=injection_config.amount,
                    source=injection_config.frequency.value,
                    total_additional_capital_to_date=self.total_additional_capital,
                )
                capital_injections.append(injection_event)

        return capital_injections

    def _should_inject_capital(
        self,
        injection_config: AdditionalCapitalInjection,
        current_period: int,
        periods_per_year: int,
    ) -> bool:
        """Determine if capital should be injected this period"""

        # Check if we're in the injection period range
        if current_period < injection_config.start_period:
            return False

        if injection_config.end_period and current_period > injection_config.end_period:
            return False

        # Handle one-time injections in specific periods
        if injection_config.frequency == AdditionalCapitalFrequency.ONE_TIME:
            if injection_config.specific_periods:
                return current_period in injection_config.specific_periods
            else:
                # One-time injection at start_period
                return current_period == injection_config.start_period

        # Handle recurring injections
        periods_since_start = current_period - injection_config.start_period

        if injection_config.frequency == AdditionalCapitalFrequency.MONTHLY:
            # Every period for monthly tracking, every 12 periods for yearly tracking
            if periods_per_year == 12:  # Monthly tracking
                return True
            else:  # Yearly tracking - inject every period (which represents a year)
                return True

        elif injection_config.frequency == AdditionalCapitalFrequency.QUARTERLY:
            if periods_per_year == 12:  # Monthly tracking
                return periods_since_start % 3 == 0
            else:  # Yearly tracking - inject every period (treating as quarterly within the year)
                return True

        elif injection_config.frequency == AdditionalCapitalFrequency.YEARLY:
            if periods_per_year == 12:  # Monthly tracking
                return periods_since_start % 12 == 0
            else:  # Yearly tracking
                return True

        elif injection_config.frequency == AdditionalCapitalFrequency.FIVE_YEARLY:
            if periods_per_year == 12:  # Monthly tracking
                return periods_since_start % (5 * 12) == 0
            else:  # Yearly tracking
                return periods_since_start % 5 == 0

        return False

    def _calculate_annual_yields(
        self, portfolio: Dict[str, Any], current_period: int, periods_per_year: int
    ) -> List[PropertyYields]:
        """Calculate annual yields for all properties"""

        # Only calculate yields on annual boundaries
        if periods_per_year == 12 and current_period % 12 != 0:
            return []
        elif periods_per_year == 1:
            # For yearly tracking, calculate every period
            pass
        else:
            return []

        property_yields = []

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

        # Get property details
        current_value = property_data.current_value
        purchase_price = property_data.purchase_price
        cash_invested = self._calculate_cash_invested(property_data)

        # Calculate annual income and expenses
        annual_rental_income = self.base_property.operating.monthly_rental_income * 12
        effective_annual_rental = annual_rental_income * (
            1 - self.base_property.operating.vacancy_rate
        )

        # Calculate annual expenses
        annual_levies = self.base_property.operating.monthly_levies * 12
        annual_management = (
            effective_annual_rental
            * self.base_property.operating.property_management_fee_rate
        )
        annual_insurance = self.base_property.operating.monthly_insurance * 12
        annual_maintenance = (
            self.base_property.operating.monthly_maintenance_reserve * 12
        )
        annual_furnishing = (
            (self.base_property.operating.monthly_furnishing_repair_costs or 0.0) * 12
        )

        annual_expenses = (
            annual_levies
            + annual_management
            + annual_insurance
            + annual_maintenance
            + annual_furnishing
        )

        # Calculate annual debt service
        annual_debt_service = (
            property_data.monthly_payment * 12
            if property_data.monthly_payment > 0
            else 0
        )

        # Net annual cashflow (after all expenses including debt service)
        annual_cashflow = (
            effective_annual_rental - annual_expenses - annual_debt_service
        )

        # Calculate yields
        rental_yield = (
            effective_annual_rental / current_value if current_value > 0 else 0
        )

        net_rental_yield = (
            (effective_annual_rental - annual_expenses) / current_value
            if current_value > 0
            else 0
        )

        cash_on_cash_return = (
            annual_cashflow / cash_invested if cash_invested > 0 else 0
        )

        # Calculate capital appreciation rate (annualized)
        periods_since_purchase = current_period - property_data.purchase_period
        if periods_since_purchase > 0:
            if periods_per_year == 12:
                years_held = periods_since_purchase / 12
            else:
                years_held = periods_since_purchase

            if years_held > 0:
                capital_appreciation_rate = (
                    (current_value / purchase_price) ** (1 / years_held)
                ) - 1
            else:
                capital_appreciation_rate = 0
        else:
            capital_appreciation_rate = 0

        # Total return yield = net rental yield + capital appreciation
        total_return_yield = net_rental_yield + capital_appreciation_rate

        return PropertyYields(
            property_id=property_data.property_id,
            period=current_period,
            rental_yield=rental_yield,
            net_rental_yield=net_rental_yield,
            cash_on_cash_return=cash_on_cash_return,
            total_return_yield=total_return_yield,
            annual_rental_income=effective_annual_rental,
            annual_expenses=annual_expenses,
            annual_cashflow=annual_cashflow,
            cash_invested=cash_invested,
            capital_appreciation_rate=capital_appreciation_rate,
        )

    def _calculate_cash_invested(self, property_data: PropertyData) -> float:
        """Calculate total cash invested in a property"""

        # Initial cash investment
        acquisition_costs = self.base_property.acquisition_costs
        total_acquisition_cost = (
            acquisition_costs.purchase_price
            + acquisition_costs.transfer_duty
            + acquisition_costs.conveyancing_fees
            + acquisition_costs.bond_registration
            + (acquisition_costs.furnishing_cost or 0.0)
        )

        # Initial cash required
        if self.base_property.financing.financing_type == FinancingType.CASH:
            initial_cash = total_acquisition_cost
        else:
            # Leveraged purchase
            ltv = self.base_property.financing.ltv_ratio
            loan_amount = acquisition_costs.purchase_price * ltv
            initial_cash = total_acquisition_cost - loan_amount

        # Add any additional cash from refinancing (extracted cash reduces invested amount)
        # This is simplified - in reality we'd track refinancing cash flows per property

        return initial_cash

    def _create_detailed_snapshot(
        self,
        portfolio: Dict[str, Any],
        period: int,
        refinancing_events: List[RefinancingEvent],
        purchases: List[PropertyPurchase],
        capital_injections: List[CapitalInjectionEvent],
        property_yields: Optional[List[PropertyYields]] = None,
    ) -> SimulationSnapshot:
        """Create a detailed snapshot of the current portfolio state"""

        if not portfolio or self.simulation_ended and not portfolio:
            return SimulationSnapshot(
                period=period,
                cash_available=self.base_property.strategy.available_investment_amount,
                total_cash_invested=0,
                total_additional_capital_injected=0,
                num_properties=0,
                total_property_value=0,
                total_debt=0,
                total_equity=0,
                monthly_rental_income=0,
                monthly_operating_expenses=0,
                monthly_debt_service=0,
                monthly_net_cashflow=0,
                annual_cashflow=0,
                properties=[],
                refinancing_events=refinancing_events,
                property_purchases=purchases,
                capital_injections=capital_injections,
                property_yields=property_yields if property_yields is not None else [],
                simulation_ended=self.simulation_ended,
                end_reason=self.end_reason,
            )

        num_properties = len(portfolio["properties"])
        total_property_value = sum(
            prop.current_value for prop in portfolio["properties"]
        )
        total_debt = sum(prop.loan_amount for prop in portfolio["properties"])
        total_equity = total_property_value - total_debt

        # Calculate income and expenses
        monthly_rental_income = (
            num_properties * self.base_property.operating.monthly_rental_income
        )
        monthly_operating_expenses = (
            num_properties * self.base_property.operating.total_monthly_expenses
        )
        monthly_debt_service = sum(
            prop.monthly_payment for prop in portfolio["properties"]
        )
        monthly_net_cashflow = sum(
            prop.monthly_cashflow for prop in portfolio["properties"]
        )
        annual_cashflow = monthly_net_cashflow * 12

        return SimulationSnapshot(
            period=period,
            cash_available=portfolio["cash_available"],
            total_cash_invested=portfolio["total_cash_invested"],
            total_additional_capital_injected=portfolio.get(
                "total_additional_capital", 0.0
            ),
            num_properties=num_properties,
            total_property_value=total_property_value,
            total_debt=total_debt,
            total_equity=total_equity,
            monthly_rental_income=monthly_rental_income,
            monthly_operating_expenses=monthly_operating_expenses,
            monthly_debt_service=monthly_debt_service,
            monthly_net_cashflow=monthly_net_cashflow,
            annual_cashflow=annual_cashflow,
            properties=deepcopy(portfolio["properties"]),
            refinancing_events=refinancing_events,
            property_purchases=purchases,
            capital_injections=capital_injections,
            property_yields=property_yields if property_yields is not None else [],
            simulation_ended=self.simulation_ended,
            end_reason=self.end_reason,
        )


def create_cash_strategy(
    reinvestment: bool = True,
    tracking: TrackingFrequency = TrackingFrequency.YEARLY,
    years: int = 10,
    additional_capital_injections: Optional[List[AdditionalCapitalInjection]] = None,
) -> StrategyConfig:
    """Create a cash-only strategy"""
    return StrategyConfig(
        strategy_type=StrategyType.CASH_ONLY,
        leverage_ratio=0.0,
        cash_ratio=1.0,
        leveraged_property_ratio=0.0,
        cash_property_ratio=1.0,
        first_property_type=FirstPropertyType.CASH,
        enable_refinancing=False,
        enable_reinvestment=reinvestment,
        tracking_frequency=tracking,
        simulation_years=years,
        additional_capital_injections=additional_capital_injections if additional_capital_injections is not None else [],
        if additional_capital_injections is not None
        else [],
    )


def create_leveraged_strategy(
    leverage_ratio: float = 0.7,
    refinancing: bool = True,
    refinance_years: float = 1.0,
    reinvestment: bool = True,
    tracking: TrackingFrequency = TrackingFrequency.YEARLY,
    years: int = 10,
    additional_capital_injections: Optional[List[AdditionalCapitalInjection]] = None,
) -> StrategyConfig:
    """Create a leveraged strategy"""
    return StrategyConfig(
        strategy_type=StrategyType.LEVERAGED,
        leverage_ratio=leverage_ratio,
        cash_ratio=1.0 - leverage_ratio,
        leveraged_property_ratio=1.0,
        cash_property_ratio=0.0,
        first_property_type=FirstPropertyType.LEVERAGED,
        enable_refinancing=refinancing,
        refinance_frequency_years=refinance_years,
        enable_reinvestment=reinvestment,
        tracking_frequency=tracking,
        simulation_years=years,
        additional_capital_injections=additional_capital_injections if additional_capital_injections is not None else [],
        if additional_capital_injections is not None
        else [],
    )


def create_mixed_strategy(
    leveraged_property_ratio: float = 0.7,  # 70% of properties leveraged
    cash_property_ratio: float = 0.3,  # 30% of properties cash
    leverage_ratio: float = 0.5,  # 50% LTV when leveraged
    first_property_type: FirstPropertyType = FirstPropertyType.LEVERAGED,
    refinancing: bool = True,
    refinance_years: float = 1.0,
    reinvestment: bool = True,
    tracking: TrackingFrequency = TrackingFrequency.YEARLY,
    years: int = 10,
    additional_capital_injections: Optional[List[AdditionalCapitalInjection]] = None,
) -> StrategyConfig:
    """Create a mixed strategy with both leveraged and cash properties"""

    # Validate ratios sum to 1.0
    if abs(leveraged_property_ratio + cash_property_ratio - 1.0) > 0.001:
        raise ValueError("Leveraged and cash property ratios must sum to 1.0")

    return StrategyConfig(
        strategy_type=StrategyType.MIXED,
        leverage_ratio=leverage_ratio,
        cash_ratio=1.0 - leverage_ratio,  # For individual leveraged properties
        (leveraged_property_ratio or 0.0) + (cash_property_ratio or 0.0)
        cash_property_ratio=cash_property_ratio,
        first_property_type=first_property_type,
        enable_refinancing=refinancing,
        refinance_frequency_years=refinance_years,
        enable_reinvestment=reinvestment,
        tracking_frequency=tracking,
        simulation_years=years,
        additional_capital_injections=additional_capital_injections if additional_capital_injections is not None else [],
        if additional_capital_injections is not None
        else [],
    )


def print_detailed_simulation_results(
    snapshots: List[SimulationSnapshot], strategy_name: str
):
    """Print detailed simulation results with all events"""
    if not snapshots:
        return

    print(f"\n{'=' * 80}")
    print(f"DETAILED SIMULATION: {strategy_name.upper()}")
    print(f"{'=' * 80}")

    for i, snapshot in enumerate(snapshots):
        period_type = (
            "Month" if len(snapshots) > 15 else "Year"
        )  # Assume monthly if > 15 periods

        print(f"\n{period_type} {snapshot.period}:")
        print(
            f"  Portfolio: {snapshot.num_properties} properties, R{snapshot.total_property_value:,.0f} total value"
        )
        print(
            f"  Equity: R{snapshot.total_equity:,.0f}, Debt: R{snapshot.total_debt:,.0f}"
        )
        print(f"  Cash Available: R{snapshot.cash_available:,.0f}")
        print(f"  Monthly Cashflow: R{snapshot.monthly_net_cashflow:,.0f}")

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

        # Show property yields if available
        if snapshot.property_yields:
            print(f"  PROPERTY YIELDS:")
            for yields in snapshot.property_yields:
                print(f"    Property {yields.property_id}:")
                print(f"      Rental Yield: {yields.rental_yield:.2%}")
                print(f"      Net Rental Yield: {yields.net_rental_yield:.2%}")
                print(f"      Cash-on-Cash Return: {yields.cash_on_cash_return:.2%}")
                print(f"      Total Return Yield: {yields.total_return_yield:.2%}")
                print(
                    f"      Capital Appreciation: {yields.capital_appreciation_rate:.2%}"
                )
                print(f"      Annual Cashflow: R{yields.annual_cashflow:,.0f}")

        # Show refinancing events
        if snapshot.refinancing_events:
            print(f"  REFINANCING EVENTS:")
            for refi in snapshot.refinancing_events:
                print(
                    f"    Property {refi.property_id}: Refinanced to {refi.new_ltv:.0%} LTV"
                )
                print(f"      Property Value: R{refi.property_value_at_refi:,.0f}")
                print(
                    f"      Old Loan: R{refi.old_loan_amount:,.0f} -> New Loan: R{refi.new_loan_amount:,.0f}"
                )
                print(f"      Cash Extracted: R{refi.cash_extracted:,.0f}")

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

        if snapshot.simulation_ended:
            print(f"  SIMULATION ENDED: {snapshot.end_reason}")
            break


def print_simulation_summary(snapshots: List[SimulationSnapshot], strategy_name: str):
    """Print a summary of simulation results"""
    if not snapshots:
        return

    initial = snapshots[0]
    final = snapshots[-1]

    print(f"\n{'=' * 50}")
    print(f"{strategy_name.upper()} STRATEGY SUMMARY")
    print(f"{'=' * 50}")

    print(f"Simulation Period: {len(snapshots) - 1} periods")
    print(
        f"Properties: {initial.num_properties} -> {final.num_properties} (+{final.num_properties - initial.num_properties})"
    )

    print(f"\nFINAL PORTFOLIO:")
    print(f"Total Value: R{final.total_property_value:,.0f}")
    print(f"Total Debt: R{final.total_debt:,.0f}")
    print(f"Total Equity: R{final.total_equity:,.0f}")
    print(f"Cash Available: R{final.cash_available:,.0f}")

    print(f"\nCASH FLOW:")
    print(f"Monthly: R{final.monthly_net_cashflow:,.0f}")
    print(f"Annual: R{final.annual_cashflow:,.0f}")

    print(f"\nINVESTMENT:")
    print(f"Initial Investment: R{final.total_cash_invested:,.0f}")
    print(f"Additional Capital: R{final.total_additional_capital_injected:,.0f}")
    print(
        f"Total Invested: R{final.total_cash_invested + final.total_additional_capital_injected:,.0f}"
    )

    total_invested = final.total_cash_invested + final.total_additional_capital_injected
    net_worth = final.total_equity + final.cash_available
    roi = (
        ((net_worth - total_invested) / total_invested) * 100
        if total_invested > 0
        else 0
    )
    print(f"Net Worth: R{net_worth:,.0f}")
    print(f"ROI: {roi:.2f}%")

    if final.simulation_ended:
        print(f"\nSIMULATION ENDED: {final.end_reason}")


def compare_strategies(
    base_property: PropertyInvestment, strategies: List[tuple], detailed: bool = False
):
    """Compare multiple strategies with optional detailed output"""
    results = {}

    for strategy_name, strategy_config in strategies:
        simulator = PropertyPortfolioSimulator(base_property, strategy_config)
        snapshots = simulator.simulate()
        results[strategy_name] = snapshots

        if detailed:
            print_detailed_simulation_results(snapshots, strategy_name)
        else:
            print_simulation_summary(snapshots, strategy_name)

    return results
