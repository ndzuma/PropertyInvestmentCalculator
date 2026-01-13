"""
Test Fixtures and Utilities

This module provides reusable test data builders and utilities for creating
test objects across the Property Investment Calculator test suite.

The Builder Pattern is used to make test object creation easy, readable, and flexible.
Each builder provides sensible defaults while allowing easy customization.

Usage Examples:
    # Simple usage with defaults
    investment = InvestmentBuilder().build()

    # Customized investment
    investment = (InvestmentBuilder()
                  .with_purchase_price(2_000_000)
                  .with_leverage(0.8)
                  .with_rental_income(20_000)
                  .build())

    # Multiple variations
    cash_investment = InvestmentBuilder().as_cash_purchase().build()
    leveraged_investment = InvestmentBuilder().as_leveraged_purchase(0.7).build()
"""

import sys
from dataclasses import replace
from typing import List, Optional

# Add parent directory to path for imports
sys.path.append("..")

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
    StrategyConfig,
    StrategyType,
    TrackingFrequency,
)


class PropertyAcquisitionCostsBuilder:
    """Builder for creating PropertyAcquisitionCosts test objects"""

    def __init__(self):
        self.purchase_price = 1_650_000
        self.transfer_duty = 13_200
        self.conveyancing_fees = 32_000
        self.bond_registration = 22_000
        self.furnishing_cost = 80_000

    def with_purchase_price(self, price: float):
        """Set the purchase price"""
        self.purchase_price = price
        return self

    def with_transfer_duty(self, duty: float):
        """Set the transfer duty"""
        self.transfer_duty = duty
        return self

    def with_conveyancing_fees(self, fees: float):
        """Set the conveyancing fees"""
        self.conveyancing_fees = fees
        return self

    def with_bond_registration(self, cost: float):
        """Set the bond registration cost"""
        self.bond_registration = cost
        return self

    def with_furnishing_cost(self, cost: Optional[float]):
        """Set the furnishing cost"""
        self.furnishing_cost = cost
        return self

    def as_cash_purchase(self):
        """Configure for cash purchase (no bond registration)"""
        self.bond_registration = 0
        return self

    def as_unfurnished(self):
        """Configure as unfurnished property"""
        self.furnishing_cost = 0
        return self

    def build(self) -> PropertyAcquisitionCosts:
        """Build the PropertyAcquisitionCosts object"""
        return PropertyAcquisitionCosts(
            purchase_price=self.purchase_price,
            transfer_duty=self.transfer_duty,
            conveyancing_fees=self.conveyancing_fees,
            bond_registration=self.bond_registration,
            furnishing_cost=self.furnishing_cost,
        )


class FinancingParametersBuilder:
    """Builder for creating FinancingParameters test objects"""

    def __init__(self):
        self.ltv_ratio = 0.5
        self.financing_type = FinancingType.LEVERAGED
        self.appreciation_rate = 0.06
        self.interest_rate = 0.105
        self.loan_term_years = 20

    def with_ltv_ratio(self, ratio: float):
        """Set the LTV ratio"""
        self.ltv_ratio = ratio
        return self

    def with_appreciation_rate(self, rate: float):
        """Set the appreciation rate"""
        self.appreciation_rate = rate
        return self

    def with_interest_rate(self, rate: Optional[float]):
        """Set the interest rate"""
        self.interest_rate = rate
        return self

    def with_loan_term_years(self, years: Optional[int]):
        """Set the loan term in years"""
        self.loan_term_years = years
        return self

    def as_cash_financing(self):
        """Configure for cash financing"""
        self.financing_type = FinancingType.CASH
        self.interest_rate = None
        self.loan_term_years = None
        self.ltv_ratio = 0.0
        return self

    def as_leveraged_financing(self, ltv: float = 0.5, rate: float = 0.105):
        """Configure for leveraged financing"""
        self.financing_type = FinancingType.LEVERAGED
        self.ltv_ratio = ltv
        self.interest_rate = rate
        return self

    def build(self) -> FinancingParameters:
        """Build the FinancingParameters object"""
        return FinancingParameters(
            ltv_ratio=self.ltv_ratio,
            financing_type=self.financing_type,
            appreciation_rate=self.appreciation_rate,
            interest_rate=self.interest_rate,
            loan_term_years=self.loan_term_years,
        )


class OperatingParametersBuilder:
    """Builder for creating OperatingParameters test objects"""

    def __init__(self):
        self.monthly_rental_income = 15_000
        self.vacancy_rate = 0.05
        self.monthly_levies = 2_500
        self.property_management_fee_rate = 0.08
        self.monthly_insurance = 800
        self.monthly_maintenance_reserve = 1_000
        self.monthly_furnishing_repair_costs = 500

    def with_monthly_rental_income(self, income: float):
        """Set the monthly rental income"""
        self.monthly_rental_income = income
        return self

    def with_vacancy_rate(self, rate: float):
        """Set the vacancy rate"""
        self.vacancy_rate = rate
        return self

    def with_monthly_levies(self, levies: float):
        """Set the monthly levies"""
        self.monthly_levies = levies
        return self

    def with_management_fee_rate(self, rate: float):
        """Set the property management fee rate"""
        self.property_management_fee_rate = rate
        return self

    def with_monthly_insurance(self, insurance: float):
        """Set the monthly insurance"""
        self.monthly_insurance = insurance
        return self

    def with_maintenance_reserve(self, reserve: float):
        """Set the monthly maintenance reserve"""
        self.monthly_maintenance_reserve = reserve
        return self

    def with_furnishing_repair_costs(self, costs: Optional[float]):
        """Set the monthly furnishing repair costs"""
        self.monthly_furnishing_repair_costs = costs
        return self

    def as_high_yield(self, income: float = 20_000):
        """Configure as high-yield property"""
        self.monthly_rental_income = income
        return self

    def as_low_maintenance(self):
        """Configure as low maintenance property"""
        self.monthly_levies = 1_000
        self.monthly_maintenance_reserve = 500
        self.monthly_furnishing_repair_costs = 200
        return self

    def build(self) -> OperatingParameters:
        """Build the OperatingParameters object"""
        return OperatingParameters(
            monthly_rental_income=self.monthly_rental_income,
            vacancy_rate=self.vacancy_rate,
            monthly_levies=self.monthly_levies,
            property_management_fee_rate=self.property_management_fee_rate,
            monthly_insurance=self.monthly_insurance,
            monthly_maintenance_reserve=self.monthly_maintenance_reserve,
            monthly_furnishing_repair_costs=self.monthly_furnishing_repair_costs,
        )


class InvestmentStrategyBuilder:
    """Builder for creating InvestmentStrategy test objects"""

    def __init__(self):
        self.available_investment_amount = 2_000_000
        self.reinvest_cashflow = True
        self.enable_refinancing = False
        self.refinance_frequency = RefineFrequency.NEVER
        self.target_refinance_ltv = None

    def with_investment_amount(self, amount: float):
        """Set the available investment amount"""
        self.available_investment_amount = amount
        return self

    def with_reinvestment(self, reinvest: bool = True):
        """Set whether to reinvest cashflow"""
        self.reinvest_cashflow = reinvest
        return self

    def with_refinancing(
        self,
        enabled: bool = True,
        frequency: RefineFrequency = RefineFrequency.ANNUALLY,
        target_ltv: float = 0.6,
    ):
        """Configure refinancing settings"""
        self.enable_refinancing = enabled
        self.refinance_frequency = frequency
        self.target_refinance_ltv = target_ltv if enabled else None
        return self

    def as_conservative(self):
        """Configure as conservative strategy"""
        self.reinvest_cashflow = True
        self.enable_refinancing = False
        return self

    def as_aggressive(self):
        """Configure as aggressive strategy"""
        self.reinvest_cashflow = True
        self.enable_refinancing = True
        self.refinance_frequency = RefineFrequency.BI_ANNUALLY
        self.target_refinance_ltv = 0.7
        return self

    def build(self) -> InvestmentStrategy:
        """Build the InvestmentStrategy object"""
        return InvestmentStrategy(
            available_investment_amount=self.available_investment_amount,
            reinvest_cashflow=self.reinvest_cashflow,
            enable_refinancing=self.enable_refinancing,
            refinance_frequency=self.refinance_frequency,
            target_refinance_ltv=self.target_refinance_ltv,
        )


class InvestmentBuilder:
    """Main builder for creating complete PropertyInvestment test objects"""

    def __init__(self):
        self.acquisition_builder = PropertyAcquisitionCostsBuilder()
        self.financing_builder = FinancingParametersBuilder()
        self.operating_builder = OperatingParametersBuilder()
        self.strategy_builder = InvestmentStrategyBuilder()

    def with_purchase_price(self, price: float):
        """Set the purchase price"""
        self.acquisition_builder.with_purchase_price(price)
        return self

    def with_leverage(self, ltv: float):
        """Set the leverage ratio"""
        self.financing_builder.with_ltv_ratio(ltv)
        return self

    def with_interest_rate(self, rate: float):
        """Set the interest rate"""
        self.financing_builder.with_interest_rate(rate)
        return self

    def with_rental_income(self, income: float):
        """Set the monthly rental income"""
        self.operating_builder.with_monthly_rental_income(income)
        return self

    def with_appreciation_rate(self, rate: float):
        """Set the appreciation rate"""
        self.financing_builder.with_appreciation_rate(rate)
        return self

    def with_investment_amount(self, amount: float):
        """Set the available investment amount"""
        self.strategy_builder.with_investment_amount(amount)
        return self

    def as_cash_purchase(self):
        """Configure as cash purchase"""
        self.acquisition_builder.as_cash_purchase()
        self.financing_builder.as_cash_financing()
        return self

    def as_leveraged_purchase(self, ltv: float = 0.5):
        """Configure as leveraged purchase"""
        self.financing_builder.as_leveraged_financing(ltv)
        self.acquisition_builder.bond_registration = 22_000
        return self

    def as_high_yield_property(self):
        """Configure as high-yield property"""
        self.operating_builder.as_high_yield()
        return self

    def as_conservative_strategy(self):
        """Configure as conservative investment strategy"""
        self.strategy_builder.as_conservative()
        return self

    def as_aggressive_strategy(self):
        """Configure as aggressive investment strategy"""
        self.strategy_builder.as_aggressive()
        return self

    def build(self) -> PropertyInvestment:
        """Build the complete PropertyInvestment object"""
        return PropertyInvestment(
            acquisition_costs=self.acquisition_builder.build(),
            financing=self.financing_builder.build(),
            operating=self.operating_builder.build(),
            strategy=self.strategy_builder.build(),
        )


class StrategyConfigBuilder:
    """Builder for creating StrategyConfig test objects"""

    def __init__(self):
        self.strategy_type = StrategyType.MIXED
        self.leverage_ratio = 0.5
        self.cash_ratio = 0.5
        self.leveraged_property_ratio = 0.6
        self.cash_property_ratio = 0.4
        self.first_property_type = FirstPropertyType.CASH
        self.enable_refinancing = True
        self.refinance_frequency_years = 1.0
        self.enable_reinvestment = True
        self.tracking_frequency = TrackingFrequency.YEARLY
        self.simulation_years = 5
        self.additional_capital_injections = []

    def with_strategy_type(self, strategy_type: StrategyType):
        """Set the strategy type"""
        self.strategy_type = strategy_type
        return self

    def with_leverage_ratio(self, ratio: float):
        """Set the leverage ratio"""
        self.leverage_ratio = ratio
        return self

    def with_tracking_frequency(self, frequency: TrackingFrequency):
        """Set the tracking frequency"""
        self.tracking_frequency = frequency
        return self

    def with_simulation_years(self, years: int):
        """Set the simulation years"""
        self.simulation_years = years
        return self

    def with_capital_injections(self, injections: List[AdditionalCapitalInjection]):
        """Set additional capital injections"""
        self.additional_capital_injections = injections
        return self

    def as_cash_only(self):
        """Configure as cash-only strategy"""
        self.strategy_type = StrategyType.CASH_ONLY
        self.leverage_ratio = 0.0
        self.cash_ratio = 1.0
        self.leveraged_property_ratio = 0.0
        self.cash_property_ratio = 1.0
        self.first_property_type = FirstPropertyType.CASH
        self.enable_refinancing = False
        return self

    def as_leveraged_only(self, leverage: float = 0.7):
        """Configure as leveraged-only strategy"""
        self.strategy_type = StrategyType.LEVERAGED
        self.leverage_ratio = leverage
        self.cash_ratio = 1 - leverage
        self.leveraged_property_ratio = 1.0
        self.cash_property_ratio = 0.0
        self.first_property_type = FirstPropertyType.LEVERAGED
        return self

    def as_mixed_strategy(self, leveraged_ratio: float = 0.6):
        """Configure as mixed strategy"""
        self.strategy_type = StrategyType.MIXED
        self.leveraged_property_ratio = leveraged_ratio
        self.cash_property_ratio = 1 - leveraged_ratio
        return self

    def build(self) -> StrategyConfig:
        """Build the StrategyConfig object"""
        return StrategyConfig(
            strategy_type=self.strategy_type,
            leverage_ratio=self.leverage_ratio,
            cash_ratio=self.cash_ratio,
            leveraged_property_ratio=self.leveraged_property_ratio,
            cash_property_ratio=self.cash_property_ratio,
            first_property_type=self.first_property_type,
            enable_refinancing=self.enable_refinancing,
            refinance_frequency_years=self.refinance_frequency_years,
            enable_reinvestment=self.enable_reinvestment,
            tracking_frequency=self.tracking_frequency,
            simulation_years=self.simulation_years,
            additional_capital_injections=self.additional_capital_injections,
        )


class CapitalInjectionBuilder:
    """Builder for creating AdditionalCapitalInjection test objects"""

    def __init__(self):
        self.amount = 100_000
        self.frequency = AdditionalCapitalFrequency.QUARTERLY
        self.start_period = 1
        self.end_period = None
        self.specific_periods = None

    def with_amount(self, amount: float):
        """Set the injection amount"""
        self.amount = amount
        return self

    def monthly(self, amount: float = None):
        """Configure as monthly injection"""
        if amount:
            self.amount = amount
        self.frequency = AdditionalCapitalFrequency.MONTHLY
        return self

    def quarterly(self, amount: float = None):
        """Configure as quarterly injection"""
        if amount:
            self.amount = amount
        self.frequency = AdditionalCapitalFrequency.QUARTERLY
        return self

    def one_time(self, amount: float = None, period: int = 1):
        """Configure as one-time injection"""
        if amount:
            self.amount = amount
        self.frequency = AdditionalCapitalFrequency.ONE_TIME
        self.specific_periods = [period]
        return self

    def for_periods(self, start: int, end: int = None):
        """Set the period range"""
        self.start_period = start
        self.end_period = end
        return self

    def build(self) -> AdditionalCapitalInjection:
        """Build the AdditionalCapitalInjection object"""
        return AdditionalCapitalInjection(
            amount=self.amount,
            frequency=self.frequency,
            start_period=self.start_period,
            end_period=self.end_period,
            specific_periods=self.specific_periods,
        )


# Convenience factory functions for common test scenarios
def default_investment() -> PropertyInvestment:
    """Create a default investment for testing"""
    return InvestmentBuilder().build()


def cash_investment(amount: float = 2_000_000) -> PropertyInvestment:
    """Create a cash-only investment for testing"""
    return InvestmentBuilder().as_cash_purchase().with_investment_amount(amount).build()


def leveraged_investment(
    ltv: float = 0.5, amount: float = 2_000_000
) -> PropertyInvestment:
    """Create a leveraged investment for testing"""
    return (
        InvestmentBuilder()
        .as_leveraged_purchase(ltv)
        .with_investment_amount(amount)
        .build()
    )


def high_yield_investment() -> PropertyInvestment:
    """Create a high-yield investment for testing"""
    return InvestmentBuilder().as_high_yield_property().build()


def conservative_investment() -> PropertyInvestment:
    """Create a conservative investment for testing"""
    return InvestmentBuilder().as_conservative_strategy().build()


def aggressive_investment() -> PropertyInvestment:
    """Create an aggressive investment for testing"""
    return InvestmentBuilder().as_aggressive_strategy().build()


def cash_strategy(years: int = 5) -> StrategyConfig:
    """Create a cash-only strategy for testing"""
    return StrategyConfigBuilder().as_cash_only().with_simulation_years(years).build()


def leveraged_strategy(leverage: float = 0.7, years: int = 5) -> StrategyConfig:
    """Create a leveraged strategy for testing"""
    return (
        StrategyConfigBuilder()
        .as_leveraged_only(leverage)
        .with_simulation_years(years)
        .build()
    )


def mixed_strategy(leveraged_ratio: float = 0.6, years: int = 5) -> StrategyConfig:
    """Create a mixed strategy for testing"""
    return (
        StrategyConfigBuilder()
        .as_mixed_strategy(leveraged_ratio)
        .with_simulation_years(years)
        .build()
    )


def monthly_injection(amount: float = 50_000) -> AdditionalCapitalInjection:
    """Create a monthly capital injection for testing"""
    return CapitalInjectionBuilder().monthly(amount).build()


def quarterly_injection(amount: float = 200_000) -> AdditionalCapitalInjection:
    """Create a quarterly capital injection for testing"""
    return CapitalInjectionBuilder().quarterly(amount).build()


def one_time_injection(
    amount: float = 500_000, period: int = 3
) -> AdditionalCapitalInjection:
    """Create a one-time capital injection for testing"""
    return CapitalInjectionBuilder().one_time(amount, period).build()
