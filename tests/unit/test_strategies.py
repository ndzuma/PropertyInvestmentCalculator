"""
Unit Tests for Strategy Creation and Configuration

Tests for strategy creation functions and strategy configuration logic:
- Strategy factory functions (create_cash_strategy, create_leveraged_strategy, etc.)
- StrategyConfig validation and defaults
- Capital injection configuration
- Strategy type and parameter validation
- Edge cases and error conditions

These tests focus on:
- Correct strategy configuration
- Parameter validation
- Default value handling
- Strategy type consistency
- Capital injection setup
"""

import os
import sys

import pytest

# Add parent directories to path for imports
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from strategies import (
    AdditionalCapitalFrequency,
    AdditionalCapitalInjection,
    FirstPropertyType,
    StrategyConfig,
    StrategyType,
    TrackingFrequency,
    create_cash_strategy,
    create_leveraged_strategy,
    create_mixed_strategy,
)
from tests.test_fixtures import (
    CapitalInjectionBuilder,
    StrategyConfigBuilder,
    monthly_injection,
    quarterly_injection,
)


class TestStrategyFactoryFunctions:
    """Test strategy factory functions"""

    def test_create_cash_strategy_defaults(self):
        """Test create_cash_strategy with default parameters"""
        strategy = create_cash_strategy()

        assert strategy.strategy_type == StrategyType.CASH_ONLY
        assert strategy.leverage_ratio == 0.0
        assert strategy.cash_ratio == 1.0
        assert strategy.leveraged_property_ratio == 0.0
        assert strategy.cash_property_ratio == 1.0
        assert strategy.first_property_type == FirstPropertyType.CASH
        assert strategy.enable_refinancing is False
        assert strategy.enable_reinvestment is True
        assert strategy.tracking_frequency == TrackingFrequency.YEARLY
        assert strategy.simulation_years == 10

    def test_create_cash_strategy_custom_parameters(self):
        """Test create_cash_strategy with custom parameters"""
        strategy = create_cash_strategy(
            reinvestment=False,
            tracking=TrackingFrequency.MONTHLY,
            years=5,
        )

        assert strategy.strategy_type == StrategyType.CASH_ONLY
        assert strategy.enable_reinvestment is False
        assert strategy.tracking_frequency == TrackingFrequency.MONTHLY
        assert strategy.simulation_years == 5

    def test_create_cash_strategy_with_capital_injections(self):
        """Test create_cash_strategy with capital injections"""
        injections = [monthly_injection(25_000), quarterly_injection(100_000)]

        strategy = create_cash_strategy(
            reinvestment=True,
            years=3,
            additional_capital_injections=injections,
        )

        assert strategy.strategy_type == StrategyType.CASH_ONLY
        assert len(strategy.additional_capital_injections) == 2
        assert strategy.additional_capital_injections[0].amount == 25_000
        assert strategy.additional_capital_injections[1].amount == 100_000

    def test_create_leveraged_strategy_defaults(self):
        """Test create_leveraged_strategy with default parameters"""
        strategy = create_leveraged_strategy()

        assert strategy.strategy_type == StrategyType.LEVERAGED
        assert strategy.leverage_ratio == 0.7  # Default leverage
        assert abs(strategy.cash_ratio - 0.3) < 0.001  # Handle floating point precision
        assert strategy.leveraged_property_ratio == 1.0
        assert strategy.cash_property_ratio == 0.0
        assert strategy.first_property_type == FirstPropertyType.LEVERAGED
        assert strategy.enable_refinancing is True
        assert strategy.refinance_frequency_years == 1.0  # Default refinance frequency

    def test_create_leveraged_strategy_custom_leverage(self):
        """Test create_leveraged_strategy with custom leverage ratio"""
        strategy = create_leveraged_strategy(
            leverage_ratio=0.8,
            refinancing=False,
            refinance_years=1.0,
        )

        assert strategy.leverage_ratio == 0.8
        assert strategy.cash_ratio == 0.2
        assert strategy.enable_refinancing is False
        assert strategy.refinance_frequency_years == 1.0

    def test_create_leveraged_strategy_with_reinvestment(self):
        """Test create_leveraged_strategy reinvestment settings"""
        strategy = create_leveraged_strategy(
            leverage_ratio=0.6,
            refinancing=True,
            reinvestment=False,
        )

        assert strategy.leverage_ratio == 0.6
        assert strategy.enable_refinancing is True
        assert strategy.enable_reinvestment is False

    def test_create_mixed_strategy_defaults(self):
        """Test create_mixed_strategy with default parameters"""
        strategy = create_mixed_strategy()

        assert strategy.strategy_type == StrategyType.MIXED
        assert (
            strategy.leverage_ratio == 0.5
        )  # Default leverage for leveraged properties
        assert strategy.leveraged_property_ratio == 0.7  # Default 70% leveraged
        assert strategy.cash_property_ratio == 0.3  # Default 30% cash
        assert (
            strategy.first_property_type == FirstPropertyType.LEVERAGED
        )  # Default first property

    def test_create_mixed_strategy_custom_ratios(self):
        """Test create_mixed_strategy with custom property ratios"""
        strategy = create_mixed_strategy(
            leveraged_property_ratio=0.8,
            cash_property_ratio=0.2,
            leverage_ratio=0.75,
        )

        assert strategy.leveraged_property_ratio == 0.8
        assert strategy.cash_property_ratio == 0.2
        assert strategy.leverage_ratio == 0.75

    def test_create_mixed_strategy_first_property_type(self):
        """Test create_mixed_strategy with different first property types"""
        # Test leveraged first
        leveraged_first = create_mixed_strategy(
            first_property_type=FirstPropertyType.LEVERAGED
        )
        assert leveraged_first.first_property_type == FirstPropertyType.LEVERAGED

        # Test cash first
        cash_first = create_mixed_strategy(first_property_type=FirstPropertyType.CASH)
        assert cash_first.first_property_type == FirstPropertyType.CASH

    def test_create_mixed_strategy_with_refinancing(self):
        """Test create_mixed_strategy refinancing configuration"""
        strategy = create_mixed_strategy(
            refinancing=True,
            refinance_years=0.5,  # Every 6 months
        )

        assert strategy.enable_refinancing is True
        assert strategy.refinance_frequency_years == 0.5


class TestStrategyConfigBuilder:
    """Test StrategyConfigBuilder functionality"""

    def test_builder_default_values(self):
        """Test builder creates strategy with sensible defaults"""
        strategy = StrategyConfigBuilder().build()

        assert strategy.strategy_type == StrategyType.MIXED
        assert strategy.leverage_ratio == 0.5
        assert strategy.cash_ratio == 0.5
        assert strategy.enable_reinvestment is True
        assert strategy.simulation_years == 5
        assert len(strategy.additional_capital_injections) == 0

    def test_builder_cash_only_configuration(self):
        """Test builder cash-only configuration"""
        strategy = StrategyConfigBuilder().as_cash_only().build()

        assert strategy.strategy_type == StrategyType.CASH_ONLY
        assert strategy.leverage_ratio == 0.0
        assert strategy.cash_ratio == 1.0
        assert strategy.leveraged_property_ratio == 0.0
        assert strategy.cash_property_ratio == 1.0
        assert strategy.first_property_type == FirstPropertyType.CASH
        assert strategy.enable_refinancing is False

    def test_builder_leveraged_only_configuration(self):
        """Test builder leveraged-only configuration"""
        strategy = StrategyConfigBuilder().as_leveraged_only(0.8).build()

        assert strategy.strategy_type == StrategyType.LEVERAGED
        assert strategy.leverage_ratio == 0.8
        assert abs(strategy.cash_ratio - 0.2) < 0.001  # Handle floating point precision
        assert strategy.leveraged_property_ratio == 1.0
        assert strategy.cash_property_ratio == 0.0
        assert strategy.first_property_type == FirstPropertyType.LEVERAGED

    def test_builder_mixed_strategy_configuration(self):
        """Test builder mixed strategy configuration"""
        strategy = StrategyConfigBuilder().as_mixed_strategy(0.7).build()

        assert strategy.strategy_type == StrategyType.MIXED
        assert strategy.leveraged_property_ratio == 0.7
        assert strategy.cash_property_ratio == 0.3

    def test_builder_custom_parameters(self):
        """Test builder with custom parameters"""
        strategy = (
            StrategyConfigBuilder()
            .with_strategy_type(StrategyType.CASH_ONLY)
            .with_leverage_ratio(0.0)
            .with_tracking_frequency(TrackingFrequency.MONTHLY)
            .with_simulation_years(8)
            .build()
        )

        assert strategy.strategy_type == StrategyType.CASH_ONLY
        assert strategy.leverage_ratio == 0.0
        assert strategy.tracking_frequency == TrackingFrequency.MONTHLY
        assert strategy.simulation_years == 8

    def test_builder_with_capital_injections(self):
        """Test builder with capital injections"""
        injections = [
            monthly_injection(30_000),
            quarterly_injection(120_000),
        ]

        strategy = (
            StrategyConfigBuilder()
            .as_cash_only()
            .with_capital_injections(injections)
            .build()
        )

        assert len(strategy.additional_capital_injections) == 2
        assert strategy.additional_capital_injections[0].amount == 30_000
        assert strategy.additional_capital_injections[1].amount == 120_000

    def test_builder_method_chaining(self):
        """Test builder method chaining works correctly"""
        strategy = (
            StrategyConfigBuilder()
            .as_mixed_strategy(0.75)
            .with_leverage_ratio(0.85)
            .with_simulation_years(7)
            .with_tracking_frequency(TrackingFrequency.MONTHLY)
            .build()
        )

        assert strategy.strategy_type == StrategyType.MIXED
        assert strategy.leveraged_property_ratio == 0.75
        assert strategy.leverage_ratio == 0.85
        assert strategy.simulation_years == 7
        assert strategy.tracking_frequency == TrackingFrequency.MONTHLY


class TestCapitalInjectionConfiguration:
    """Test capital injection configuration and validation"""

    def test_monthly_injection_creation(self):
        """Test monthly capital injection creation"""
        injection = CapitalInjectionBuilder().monthly(40_000).build()

        assert injection.amount == 40_000
        assert injection.frequency == AdditionalCapitalFrequency.MONTHLY
        assert injection.start_period == 1
        assert injection.end_period is None
        assert injection.specific_periods is None

    def test_quarterly_injection_creation(self):
        """Test quarterly capital injection creation"""
        injection = CapitalInjectionBuilder().quarterly(150_000).build()

        assert injection.amount == 150_000
        assert injection.frequency == AdditionalCapitalFrequency.QUARTERLY
        assert injection.start_period == 1
        assert injection.end_period is None

    def test_one_time_injection_creation(self):
        """Test one-time capital injection creation"""
        injection = CapitalInjectionBuilder().one_time(500_000, period=3).build()

        assert injection.amount == 500_000
        assert injection.frequency == AdditionalCapitalFrequency.ONE_TIME
        assert injection.specific_periods == [3]

    def test_injection_with_period_range(self):
        """Test capital injection with period range"""
        injection = (
            CapitalInjectionBuilder()
            .quarterly(100_000)
            .for_periods(start=2, end=12)
            .build()
        )

        assert injection.start_period == 2
        assert injection.end_period == 12
        assert injection.frequency == AdditionalCapitalFrequency.QUARTERLY

    def test_injection_builder_customization(self):
        """Test capital injection builder customization"""
        injection = (
            CapitalInjectionBuilder()
            .with_amount(75_000)
            .monthly()
            .for_periods(start=3, end=24)
            .build()
        )

        assert injection.amount == 75_000
        assert injection.frequency == AdditionalCapitalFrequency.MONTHLY
        assert injection.start_period == 3
        assert injection.end_period == 24

    def test_multiple_injections_in_strategy(self):
        """Test strategy with multiple capital injections"""
        injections = [
            CapitalInjectionBuilder().monthly(20_000).build(),
            CapitalInjectionBuilder().quarterly(80_000).build(),
            CapitalInjectionBuilder().one_time(300_000, period=4).build(),
        ]

        strategy = (
            StrategyConfigBuilder()
            .as_mixed_strategy()
            .with_capital_injections(injections)
            .build()
        )

        assert len(strategy.additional_capital_injections) == 3

        # Verify each injection type
        monthly = strategy.additional_capital_injections[0]
        quarterly = strategy.additional_capital_injections[1]
        one_time = strategy.additional_capital_injections[2]

        assert monthly.frequency == AdditionalCapitalFrequency.MONTHLY
        assert quarterly.frequency == AdditionalCapitalFrequency.QUARTERLY
        assert one_time.frequency == AdditionalCapitalFrequency.ONE_TIME


class TestStrategyValidationAndEdgeCases:
    """Test strategy validation and edge cases"""

    def test_strategy_type_enum_validation(self):
        """Test strategy type enum values are valid"""
        # Test all strategy types are accessible
        assert StrategyType.CASH_ONLY
        assert StrategyType.LEVERAGED
        assert StrategyType.MIXED

        # Test strategy creation with each type
        cash_strategy = StrategyConfigBuilder().as_cash_only().build()
        leveraged_strategy = StrategyConfigBuilder().as_leveraged_only().build()
        mixed_strategy = StrategyConfigBuilder().as_mixed_strategy().build()

        assert cash_strategy.strategy_type == StrategyType.CASH_ONLY
        assert leveraged_strategy.strategy_type == StrategyType.LEVERAGED
        assert mixed_strategy.strategy_type == StrategyType.MIXED

    def test_first_property_type_validation(self):
        """Test first property type enum validation"""
        # Test both property types
        assert FirstPropertyType.CASH
        assert FirstPropertyType.LEVERAGED

        # Test in strategy configuration
        cash_first = create_mixed_strategy(first_property_type=FirstPropertyType.CASH)
        leveraged_first = create_mixed_strategy(
            first_property_type=FirstPropertyType.LEVERAGED
        )

        assert cash_first.first_property_type == FirstPropertyType.CASH
        assert leveraged_first.first_property_type == FirstPropertyType.LEVERAGED

    def test_tracking_frequency_validation(self):
        """Test tracking frequency enum validation"""
        # Test all tracking frequencies
        assert TrackingFrequency.MONTHLY
        assert TrackingFrequency.YEARLY

        monthly_strategy = create_cash_strategy(tracking=TrackingFrequency.MONTHLY)
        yearly_strategy = create_cash_strategy(tracking=TrackingFrequency.YEARLY)

        assert monthly_strategy.tracking_frequency == TrackingFrequency.MONTHLY
        assert yearly_strategy.tracking_frequency == TrackingFrequency.YEARLY

    def test_capital_injection_frequency_validation(self):
        """Test capital injection frequency enum validation"""
        # Test all injection frequencies
        assert AdditionalCapitalFrequency.MONTHLY
        assert AdditionalCapitalFrequency.QUARTERLY
        assert AdditionalCapitalFrequency.ONE_TIME

        monthly = CapitalInjectionBuilder().monthly().build()
        quarterly = CapitalInjectionBuilder().quarterly().build()
        one_time = CapitalInjectionBuilder().one_time(100_000, 1).build()

        assert monthly.frequency == AdditionalCapitalFrequency.MONTHLY
        assert quarterly.frequency == AdditionalCapitalFrequency.QUARTERLY
        assert one_time.frequency == AdditionalCapitalFrequency.ONE_TIME

    def test_extreme_leverage_ratios(self):
        """Test strategies with extreme leverage ratios"""
        # Very low leverage
        low_leverage = create_leveraged_strategy(leverage_ratio=0.1)
        assert low_leverage.leverage_ratio == 0.1
        assert low_leverage.cash_ratio == 0.9

        # Very high leverage
        high_leverage = create_leveraged_strategy(leverage_ratio=0.95)
        assert high_leverage.leverage_ratio == 0.95
        assert high_leverage.cash_ratio == 0.05

    def test_extreme_property_ratios(self):
        """Test mixed strategies with extreme property ratios"""
        # Almost all leveraged
        mostly_leveraged = create_mixed_strategy(
            leveraged_property_ratio=0.95, cash_property_ratio=0.05
        )
        assert mostly_leveraged.leveraged_property_ratio == 0.95
        assert mostly_leveraged.cash_property_ratio == 0.05

        # Almost all cash
        mostly_cash = create_mixed_strategy(
            leveraged_property_ratio=0.1, cash_property_ratio=0.9
        )
        assert mostly_cash.leveraged_property_ratio == 0.1
        assert mostly_cash.cash_property_ratio == 0.9

    def test_very_short_simulation_period(self):
        """Test strategy with very short simulation period"""
        strategy = create_cash_strategy(years=1)
        assert strategy.simulation_years == 1

    def test_very_long_simulation_period(self):
        """Test strategy with very long simulation period"""
        strategy = create_leveraged_strategy(years=50)
        assert strategy.simulation_years == 50

    def test_zero_leverage_ratio(self):
        """Test strategy with zero leverage ratio"""
        # Should behave like cash-only
        zero_leverage = create_leveraged_strategy(leverage_ratio=0.0)
        assert zero_leverage.leverage_ratio == 0.0
        assert zero_leverage.cash_ratio == 1.0

    def test_strategy_consistency_cash_only(self):
        """Test cash-only strategy internal consistency"""
        strategy = create_cash_strategy()

        # Cash strategy should have no leveraged properties
        assert strategy.leveraged_property_ratio == 0.0
        assert strategy.cash_property_ratio == 1.0
        assert strategy.leverage_ratio == 0.0
        assert strategy.cash_ratio == 1.0
        assert strategy.first_property_type == FirstPropertyType.CASH
        assert strategy.enable_refinancing is False

    def test_strategy_consistency_leveraged_only(self):
        """Test leveraged-only strategy internal consistency"""
        strategy = create_leveraged_strategy(leverage_ratio=0.7)

        # Leveraged strategy should have no cash properties
        assert strategy.leveraged_property_ratio == 1.0
        assert strategy.cash_property_ratio == 0.0
        assert strategy.leverage_ratio == 0.7
        assert strategy.cash_ratio == 0.3
        assert strategy.first_property_type == FirstPropertyType.LEVERAGED

    def test_strategy_consistency_mixed(self):
        """Test mixed strategy internal consistency"""
        strategy = create_mixed_strategy(
            leveraged_property_ratio=0.6, cash_property_ratio=0.4, leverage_ratio=0.8
        )

        # Mixed strategy should have both property types
        assert strategy.leveraged_property_ratio == 0.6
        assert strategy.cash_property_ratio == 0.4
        assert strategy.leverage_ratio == 0.8
        assert strategy.cash_ratio == 0.2  # 1 - leverage_ratio

    def test_empty_capital_injections_list(self):
        """Test strategy with empty capital injections list"""
        strategy = (
            StrategyConfigBuilder().as_cash_only().with_capital_injections([]).build()
        )

        assert len(strategy.additional_capital_injections) == 0

    def test_large_capital_injection_amounts(self):
        """Test strategy with very large capital injection amounts"""
        large_injection = CapitalInjectionBuilder().one_time(100_000_000, 1).build()

        strategy = (
            StrategyConfigBuilder()
            .as_leveraged_only()
            .with_capital_injections([large_injection])
            .build()
        )

        assert strategy.additional_capital_injections[0].amount == 100_000_000

    def test_very_frequent_refinancing(self):
        """Test strategy with very frequent refinancing"""
        strategy = create_leveraged_strategy(
            refinancing=True,
            refinance_years=0.25,  # Every 3 months
        )

        assert strategy.enable_refinancing is True
        assert strategy.refinance_frequency_years == 0.25

    def test_no_refinancing_leveraged_strategy(self):
        """Test leveraged strategy with refinancing disabled"""
        strategy = create_leveraged_strategy(refinancing=False)

        assert strategy.enable_refinancing is False
        # Refinance frequency should still be set for potential future use
        assert strategy.refinance_frequency_years is not None
