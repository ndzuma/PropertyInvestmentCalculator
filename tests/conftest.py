"""
Pytest Configuration and Shared Fixtures

This file contains pytest configuration and shared fixtures that are automatically
available to all test modules. Fixtures defined here can be used by any test
without explicit import.

Fixtures include:
- Common test data objects
- Database/state setup and teardown
- Performance measurement utilities
- Mock objects for external dependencies

Usage:
    def test_something(default_investment, sample_strategy):
        # Fixtures are automatically injected as parameters
        result = some_function(default_investment, sample_strategy)
        assert result.is_valid
"""

import os
import sys
import time
from typing import Dict, List

import pytest

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import PropertyInvestment
from strategies import PropertyPortfolioSimulator, StrategyConfig
from tests.test_fixtures import (
    CapitalInjectionBuilder,
    InvestmentBuilder,
    StrategyConfigBuilder,
    cash_investment,
    cash_strategy,
    default_investment,
    leveraged_investment,
    leveraged_strategy,
    mixed_strategy,
    monthly_injection,
    quarterly_injection,
)

# ============================================================================
# BASIC TEST DATA FIXTURES
# ============================================================================


@pytest.fixture
def default_investment_fixture():
    """Provides a default PropertyInvestment for testing"""
    return default_investment()


@pytest.fixture
def cash_investment_fixture():
    """Provides a cash-only PropertyInvestment for testing"""
    return cash_investment()


@pytest.fixture
def leveraged_investment_fixture():
    """Provides a leveraged PropertyInvestment for testing"""
    return leveraged_investment()


@pytest.fixture
def high_yield_investment_fixture():
    """Provides a high-yield PropertyInvestment for testing"""
    return (
        InvestmentBuilder()
        .with_rental_income(25_000)
        .with_purchase_price(2_000_000)
        .build()
    )


@pytest.fixture
def low_yield_investment_fixture():
    """Provides a low-yield PropertyInvestment for testing"""
    return (
        InvestmentBuilder()
        .with_rental_income(8_000)
        .with_purchase_price(1_500_000)
        .build()
    )


# ============================================================================
# STRATEGY FIXTURES
# ============================================================================


@pytest.fixture
def cash_strategy_fixture():
    """Provides a cash-only strategy configuration"""
    return cash_strategy()


@pytest.fixture
def leveraged_strategy_fixture():
    """Provides a leveraged strategy configuration"""
    return leveraged_strategy()


@pytest.fixture
def mixed_strategy_fixture():
    """Provides a mixed strategy configuration"""
    return mixed_strategy()


@pytest.fixture
def short_simulation_strategy():
    """Provides a strategy for quick testing (2 years)"""
    return cash_strategy(years=2)


@pytest.fixture
def long_simulation_strategy():
    """Provides a strategy for comprehensive testing (10 years)"""
    return leveraged_strategy(years=10)


# ============================================================================
# CAPITAL INJECTION FIXTURES
# ============================================================================


@pytest.fixture
def monthly_injection_fixture():
    """Provides a monthly capital injection"""
    return monthly_injection()


@pytest.fixture
def quarterly_injection_fixture():
    """Provides a quarterly capital injection"""
    return quarterly_injection()


@pytest.fixture
def multiple_injections_fixture():
    """Provides multiple capital injections for testing"""
    return [
        monthly_injection(30_000),
        quarterly_injection(150_000),
        (CapitalInjectionBuilder().one_time(500_000, period=3).build()),
    ]


# ============================================================================
# SIMULATION FIXTURES
# ============================================================================


@pytest.fixture
def basic_simulator(default_investment_fixture, cash_strategy_fixture):
    """Provides a basic portfolio simulator for testing"""
    return PropertyPortfolioSimulator(default_investment_fixture, cash_strategy_fixture)


@pytest.fixture
def leveraged_simulator(leveraged_investment_fixture, leveraged_strategy_fixture):
    """Provides a leveraged portfolio simulator for testing"""
    return PropertyPortfolioSimulator(
        leveraged_investment_fixture, leveraged_strategy_fixture
    )


# ============================================================================
# COMPARISON TEST FIXTURES
# ============================================================================


@pytest.fixture
def strategy_comparison_set():
    """Provides a set of strategies for comparison testing"""
    return {
        "Conservative Cash": cash_strategy(years=5),
        "Moderate Leverage": leveraged_strategy(leverage=0.5, years=5),
        "Aggressive Leverage": leveraged_strategy(leverage=0.7, years=5),
        "Mixed Portfolio": mixed_strategy(leveraged_ratio=0.6, years=5),
    }


@pytest.fixture
def investment_comparison_set():
    """Provides a set of investments for comparison testing"""
    return {
        "Standard Property": default_investment(),
        "High Yield Property": (InvestmentBuilder().with_rental_income(25_000).build()),
        "Low Maintenance Property": (
            InvestmentBuilder()
            .operating_builder.as_low_maintenance()
            .acquisition_builder.parent.build()
        ),
        "Cash Purchase": cash_investment(),
        "High Leverage": leveraged_investment(ltv=0.8),
    }


# ============================================================================
# PERFORMANCE TESTING FIXTURES
# ============================================================================


@pytest.fixture
def performance_timer():
    """Provides a performance timer context manager"""

    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.elapsed = None

        def __enter__(self):
            self.start_time = time.perf_counter()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.end_time = time.perf_counter()
            self.elapsed = self.end_time - self.start_time

    return Timer


@pytest.fixture
def large_portfolio_investment():
    """Provides an investment configuration for large portfolio testing"""
    return (
        InvestmentBuilder()
        .with_investment_amount(50_000_000)  # Large investment amount
        .with_purchase_price(1_000_000)  # Lower price per property
        .build()
    )


# ============================================================================
# MOCK AND STUB FIXTURES
# ============================================================================


@pytest.fixture
def mock_appreciation_rates():
    """Provides mock appreciation rates for testing"""
    return {
        "conservative": 0.03,  # 3% annual appreciation
        "moderate": 0.06,  # 6% annual appreciation
        "aggressive": 0.10,  # 10% annual appreciation
        "volatile": [0.15, -0.05, 0.08, 0.12, -0.02],  # Variable rates
    }


@pytest.fixture
def mock_interest_rates():
    """Provides mock interest rates for testing"""
    return {
        "low": 0.07,  # 7% interest
        "medium": 0.105,  # 10.5% interest
        "high": 0.14,  # 14% interest
    }


# ============================================================================
# ERROR CONDITION FIXTURES
# ============================================================================


@pytest.fixture
def invalid_investment_data():
    """Provides invalid investment data for error testing"""
    return {
        "negative_price": {"purchase_price": -1_000_000},
        "zero_rental": {"monthly_rental_income": 0},
        "invalid_ltv": {"ltv_ratio": 1.5},  # > 100%
        "negative_rate": {"interest_rate": -0.05},
        "zero_investment": {"available_investment_amount": 0},
    }


@pytest.fixture
def edge_case_scenarios():
    """Provides edge case scenarios for robust testing"""
    return {
        "minimal_investment": (
            InvestmentBuilder()
            .with_purchase_price(100_000)
            .with_rental_income(500)
            .with_investment_amount(150_000)
            .build()
        ),
        "maximum_leverage": (
            InvestmentBuilder()
            .as_leveraged_purchase(0.95)  # 95% LTV
            .build()
        ),
        "zero_appreciation": (
            InvestmentBuilder()
            .financing_builder.with_appreciation_rate(0.0)
            .acquisition_builder.parent.build()
        ),
    }


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================


def pytest_configure(config):
    """Pytest configuration hook"""
    # Add custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (may take several seconds to run)"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line(
        "markers", "performance: marks tests as performance/benchmark tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location"""
    for item in items:
        # Mark integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Mark performance tests
        if "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)


# ============================================================================
# UTILITY FIXTURES
# ============================================================================


@pytest.fixture
def assert_approximately():
    """Provides a utility for approximate float assertions"""

    def _assert_approximately(actual, expected, tolerance=0.01):
        """Assert that actual is within tolerance of expected"""
        if expected == 0:
            assert abs(actual) < tolerance, f"Expected ~{expected}, got {actual}"
        else:
            relative_error = abs((actual - expected) / expected)
            assert relative_error < tolerance, (
                f"Expected ~{expected}, got {actual} (relative error: {relative_error:.4f})"
            )

    return _assert_approximately


@pytest.fixture
def snapshot_validator():
    """Provides utilities for validating simulation snapshots"""

    class SnapshotValidator:
        @staticmethod
        def validate_snapshot_consistency(snapshot):
            """Validate that a snapshot has consistent data"""
            # Total value should equal sum of individual property values
            calculated_total = sum(prop.current_value for prop in snapshot.properties)
            assert abs(calculated_total - snapshot.total_property_value) < 0.01

            # Equity should equal total value minus total debt
            calculated_equity = snapshot.total_property_value - snapshot.total_debt
            assert abs(calculated_equity - snapshot.total_equity) < 0.01

            # Portfolio yields should exist if property yields exist
            if snapshot.property_yields:
                assert snapshot.portfolio_yields is not None

        @staticmethod
        def validate_yield_ranges(yields):
            """Validate that yields are within reasonable ranges"""
            if yields.rental_yield is not None:
                assert 0 <= yields.rental_yield <= 1.0  # 0-100%
            if yields.net_rental_yield is not None:
                assert -0.5 <= yields.net_rental_yield <= 0.5  # -50% to +50%

    return SnapshotValidator()
