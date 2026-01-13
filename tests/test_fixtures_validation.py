#!/usr/bin/env python3
"""
Test Fixtures Validation

Quick test to verify that all test fixtures and builders are working correctly.
This file validates that the test infrastructure is properly set up.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_import_fixtures():
    """Test that we can import all fixture modules"""
    try:
        from tests.test_fixtures import (
            CapitalInjectionBuilder,
            InvestmentBuilder,
            StrategyConfigBuilder,
            cash_investment,
            default_investment,
            leveraged_investment,
        )

        print("✅ All fixture imports successful")
        return True
    except ImportError as e:
        print(f"❌ Fixture import failed: {e}")
        return False


def test_investment_builder():
    """Test that InvestmentBuilder creates valid objects"""
    try:
        from main import FinancingType
        from tests.test_fixtures import InvestmentBuilder

        # Test default investment
        investment = InvestmentBuilder().build()
        assert investment.acquisition_costs.purchase_price > 0
        assert investment.operating.monthly_rental_income > 0
        print("✅ Default investment builder works")

        # Test cash purchase
        cash_investment = InvestmentBuilder().as_cash_purchase().build()
        assert cash_investment.financing.financing_type == FinancingType.CASH
        assert cash_investment.acquisition_costs.bond_registration == 0
        print("✅ Cash purchase builder works")

        # Test leveraged purchase
        leveraged_investment = InvestmentBuilder().as_leveraged_purchase(0.7).build()
        assert leveraged_investment.financing.financing_type == FinancingType.LEVERAGED
        assert leveraged_investment.financing.ltv_ratio == 0.7
        print("✅ Leveraged purchase builder works")

        # Test custom values
        custom_investment = (
            InvestmentBuilder()
            .with_purchase_price(2_000_000)
            .with_rental_income(18_000)
            .with_leverage(0.6)
            .build()
        )
        assert custom_investment.acquisition_costs.purchase_price == 2_000_000
        assert custom_investment.operating.monthly_rental_income == 18_000
        assert custom_investment.financing.ltv_ratio == 0.6
        print("✅ Custom investment builder works")

        return True
    except Exception as e:
        print(f"❌ Investment builder test failed: {e}")
        return False


def test_strategy_builder():
    """Test that StrategyConfigBuilder creates valid objects"""
    try:
        from strategies import FirstPropertyType, StrategyType
        from tests.test_fixtures import StrategyConfigBuilder

        # Test cash strategy
        cash_strategy = StrategyConfigBuilder().as_cash_only().build()
        assert cash_strategy.strategy_type == StrategyType.CASH_ONLY
        assert cash_strategy.leverage_ratio == 0.0
        print("✅ Cash strategy builder works")

        # Test leveraged strategy
        leveraged_strategy = StrategyConfigBuilder().as_leveraged_only(0.8).build()
        assert leveraged_strategy.strategy_type == StrategyType.LEVERAGED
        assert leveraged_strategy.leverage_ratio == 0.8
        print("✅ Leveraged strategy builder works")

        # Test mixed strategy
        mixed_strategy = StrategyConfigBuilder().as_mixed_strategy(0.6).build()
        assert mixed_strategy.strategy_type == StrategyType.MIXED
        assert mixed_strategy.leveraged_property_ratio == 0.6
        print("✅ Mixed strategy builder works")

        return True
    except Exception as e:
        print(f"❌ Strategy builder test failed: {e}")
        return False


def test_capital_injection_builder():
    """Test that CapitalInjectionBuilder creates valid objects"""
    try:
        from strategies import AdditionalCapitalFrequency
        from tests.test_fixtures import CapitalInjectionBuilder

        # Test monthly injection
        monthly = CapitalInjectionBuilder().monthly(50_000).build()
        assert monthly.amount == 50_000
        assert monthly.frequency == AdditionalCapitalFrequency.MONTHLY
        print("✅ Monthly injection builder works")

        # Test quarterly injection
        quarterly = CapitalInjectionBuilder().quarterly(200_000).build()
        assert quarterly.amount == 200_000
        assert quarterly.frequency == AdditionalCapitalFrequency.QUARTERLY
        print("✅ Quarterly injection builder works")

        # Test one-time injection
        one_time = CapitalInjectionBuilder().one_time(500_000, period=3).build()
        assert one_time.amount == 500_000
        assert one_time.frequency == AdditionalCapitalFrequency.ONE_TIME
        assert one_time.specific_periods == [3]
        print("✅ One-time injection builder works")

        return True
    except Exception as e:
        print(f"❌ Capital injection builder test failed: {e}")
        return False


def test_convenience_functions():
    """Test that convenience factory functions work"""
    try:
        from tests.test_fixtures import (
            cash_investment,
            cash_strategy,
            default_investment,
            leveraged_investment,
            leveraged_strategy,
            mixed_strategy,
            monthly_injection,
            quarterly_injection,
        )

        # Test investment functions
        inv1 = default_investment()
        inv2 = cash_investment(1_500_000)
        inv3 = leveraged_investment(0.8, 3_000_000)

        assert inv1.strategy.available_investment_amount == 2_000_000  # default
        assert inv2.strategy.available_investment_amount == 1_500_000
        assert inv3.strategy.available_investment_amount == 3_000_000
        assert inv3.financing.ltv_ratio == 0.8
        print("✅ Investment convenience functions work")

        # Test strategy functions
        s1 = cash_strategy(3)
        s2 = leveraged_strategy(0.7, 4)
        s3 = mixed_strategy(0.6, 5)

        assert s1.simulation_years == 3
        assert s2.simulation_years == 4
        assert s2.leverage_ratio == 0.7
        assert s3.simulation_years == 5
        print("✅ Strategy convenience functions work")

        # Test injection functions
        i1 = monthly_injection(30_000)
        i2 = quarterly_injection(150_000)

        assert i1.amount == 30_000
        assert i2.amount == 150_000
        print("✅ Injection convenience functions work")

        return True
    except Exception as e:
        print(f"❌ Convenience functions test failed: {e}")
        return False


def test_simulation_integration():
    """Test that fixtures work with actual simulation"""
    try:
        from strategies import PropertyPortfolioSimulator
        from tests.test_fixtures import InvestmentBuilder, StrategyConfigBuilder

        # Create test objects using builders
        investment = InvestmentBuilder().as_cash_purchase().build()
        strategy = (
            StrategyConfigBuilder().as_cash_only().with_simulation_years(2).build()
        )

        # Test simulation
        simulator = PropertyPortfolioSimulator(investment, strategy)
        snapshots = simulator.simulate()

        assert len(snapshots) > 0
        assert snapshots[0].properties is not None
        assert snapshots[-1].total_property_value > 0
        print("✅ Fixtures work with actual simulation")

        return True
    except Exception as e:
        print(f"❌ Simulation integration test failed: {e}")
        return False


def run_all_tests():
    """Run all validation tests"""
    print("🧪 Testing Property Investment Calculator Test Fixtures")
    print("=" * 60)

    tests = [
        test_import_fixtures,
        test_investment_builder,
        test_strategy_builder,
        test_capital_injection_builder,
        test_convenience_functions,
        test_simulation_integration,
    ]

    results = []
    for test in tests:
        print(f"\nRunning {test.__name__}...")
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ {test.__name__} failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    print("VALIDATION RESULTS:")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("🎉 All fixture validation tests passed!")
        print("The test infrastructure is ready for use.")
    else:
        print("⚠️  Some tests failed. Please fix issues before proceeding.")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
