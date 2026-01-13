#!/usr/bin/env python3
"""
Simple Unit Test Runner

Runs unit tests to verify they work correctly without requiring pytest installation.
This script imports and runs key unit test functions to validate the test suite.
"""

import os
import sys
import traceback

# Add current directory to path
sys.path.append(".")


def run_test_function(test_func, test_name):
    """Run a single test function and return success status"""
    try:
        test_func()
        print(f"✅ {test_name}")
        return True
    except Exception as e:
        print(f"❌ {test_name} - {str(e)}")
        print(f"   {traceback.format_exc().split('Traceback')[-1].strip()}")
        return False


def run_dataclass_tests():
    """Run dataclass unit tests"""
    print("\n📦 Testing DataClass Unit Tests...")

    try:
        from tests.unit.test_dataclasses import (
            TestFinancingParameters,
            TestInvestmentStrategy,
            TestOperatingParameters,
            TestPropertyAcquisitionCosts,
            TestPropertyInvestment,
        )

        results = []

        # Test PropertyAcquisitionCosts
        test_class = TestPropertyAcquisitionCosts()
        results.append(
            run_test_function(
                test_class.test_basic_creation,
                "PropertyAcquisitionCosts.basic_creation",
            )
        )
        results.append(
            run_test_function(
                test_class.test_total_unfurnished_cost,
                "PropertyAcquisitionCosts.total_unfurnished_cost",
            )
        )
        results.append(
            run_test_function(
                test_class.test_total_furnished_cost,
                "PropertyAcquisitionCosts.total_furnished_cost",
            )
        )

        # Test FinancingParameters
        test_class = TestFinancingParameters()
        results.append(
            run_test_function(
                test_class.test_basic_creation_leveraged,
                "FinancingParameters.basic_creation_leveraged",
            )
        )
        results.append(
            run_test_function(
                test_class.test_basic_creation_cash,
                "FinancingParameters.basic_creation_cash",
            )
        )

        # Test OperatingParameters
        test_class = TestOperatingParameters()
        results.append(
            run_test_function(
                test_class.test_basic_creation, "OperatingParameters.basic_creation"
            )
        )
        results.append(
            run_test_function(
                test_class.test_effective_monthly_rental,
                "OperatingParameters.effective_monthly_rental",
            )
        )

        # Test InvestmentStrategy
        test_class = TestInvestmentStrategy()
        results.append(
            run_test_function(
                test_class.test_basic_creation, "InvestmentStrategy.basic_creation"
            )
        )

        # Test PropertyInvestment
        test_class = TestPropertyInvestment()
        results.append(
            run_test_function(
                test_class.test_basic_creation, "PropertyInvestment.basic_creation"
            )
        )
        results.append(
            run_test_function(
                test_class.test_cash_investment_validation,
                "PropertyInvestment.cash_investment_validation",
            )
        )
        results.append(
            run_test_function(
                test_class.test_leveraged_investment_validation,
                "PropertyInvestment.leveraged_investment_validation",
            )
        )

        return results

    except Exception as e:
        print(f"❌ Failed to import dataclass tests: {e}")
        return [False]


def run_calculation_tests():
    """Run calculation unit tests"""
    print("\n🧮 Testing Calculation Unit Tests...")

    try:
        from tests.unit.test_calculations import (
            TestCashFlowCalculations,
            TestInitialCashRequiredCalculations,
            TestMonthlyPaymentCalculations,
        )

        # Create assert_approximately function for tests that need it
        def assert_approximately(actual, expected, tolerance=0.01):
            if expected == 0:
                assert abs(actual) < tolerance
            else:
                relative_error = abs((actual - expected) / expected)
                assert relative_error < tolerance

        results = []

        # Test Monthly Payment Calculations
        test_class = TestMonthlyPaymentCalculations()
        results.append(
            run_test_function(
                test_class.test_cash_purchase_no_payment,
                "MonthlyPayment.cash_purchase_no_payment",
            )
        )
        results.append(
            run_test_function(
                test_class.test_zero_interest_rate_payment,
                "MonthlyPayment.zero_interest_rate_payment",
            )
        )

        # Test Cash Flow Calculations
        test_class = TestCashFlowCalculations()
        results.append(
            run_test_function(
                test_class.test_positive_cash_flow, "CashFlow.positive_cash_flow"
            )
        )
        results.append(
            run_test_function(
                test_class.test_cash_flow_with_no_bond_payment,
                "CashFlow.no_bond_payment",
            )
        )

        # Test Initial Cash Required
        test_class = TestInitialCashRequiredCalculations()
        results.append(
            run_test_function(
                test_class.test_cash_purchase_initial_cash, "InitialCash.cash_purchase"
            )
        )
        results.append(
            run_test_function(
                test_class.test_leveraged_purchase_initial_cash,
                "InitialCash.leveraged_purchase",
            )
        )

        return results

    except Exception as e:
        print(f"❌ Failed to import calculation tests: {e}")
        return [False]


def run_strategy_tests():
    """Run strategy unit tests"""
    print("\n🎯 Testing Strategy Unit Tests...")

    try:
        from tests.unit.test_strategies import (
            TestCapitalInjectionConfiguration,
            TestStrategyConfigBuilder,
            TestStrategyFactoryFunctions,
        )

        results = []

        # Test Strategy Factory Functions
        test_class = TestStrategyFactoryFunctions()
        results.append(
            run_test_function(
                test_class.test_create_cash_strategy_defaults,
                "StrategyFactory.cash_strategy_defaults",
            )
        )
        results.append(
            run_test_function(
                test_class.test_create_leveraged_strategy_defaults,
                "StrategyFactory.leveraged_strategy_defaults",
            )
        )
        results.append(
            run_test_function(
                test_class.test_create_mixed_strategy_defaults,
                "StrategyFactory.mixed_strategy_defaults",
            )
        )

        # Test Strategy Builder
        test_class = TestStrategyConfigBuilder()
        results.append(
            run_test_function(
                test_class.test_builder_default_values, "StrategyBuilder.default_values"
            )
        )
        results.append(
            run_test_function(
                test_class.test_builder_cash_only_configuration,
                "StrategyBuilder.cash_only_config",
            )
        )
        results.append(
            run_test_function(
                test_class.test_builder_leveraged_only_configuration,
                "StrategyBuilder.leveraged_only_config",
            )
        )

        # Test Capital Injection
        test_class = TestCapitalInjectionConfiguration()
        results.append(
            run_test_function(
                test_class.test_monthly_injection_creation,
                "CapitalInjection.monthly_creation",
            )
        )
        results.append(
            run_test_function(
                test_class.test_quarterly_injection_creation,
                "CapitalInjection.quarterly_creation",
            )
        )
        results.append(
            run_test_function(
                test_class.test_one_time_injection_creation,
                "CapitalInjection.one_time_creation",
            )
        )

        return results

    except Exception as e:
        print(f"❌ Failed to import strategy tests: {e}")
        return [False]


def run_yield_tests():
    """Run yield calculation unit tests"""
    print("\n📊 Testing Yield Unit Tests...")

    try:
        from tests.unit.test_yields import (
            TestPortfolioYieldCalculations,
            TestPropertyYieldCalculations,
        )

        # Create assert_approximately function
        def assert_approximately(actual, expected, tolerance=0.01):
            if expected == 0:
                assert abs(actual) < tolerance
            else:
                relative_error = abs((actual - expected) / expected)
                assert relative_error < tolerance

        results = []

        # Test Property Yield Calculations
        test_class = TestPropertyYieldCalculations()
        results.append(
            run_test_function(
                test_class.test_rental_yield_calculation,
                "PropertyYields.rental_yield_calculation",
            )
        )
        results.append(
            run_test_function(
                test_class.test_cash_on_cash_return_calculation,
                "PropertyYields.cash_on_cash_return",
            )
        )
        results.append(
            run_test_function(
                test_class.test_total_return_yield_calculation,
                "PropertyYields.total_return_yield",
            )
        )
        results.append(
            run_test_function(
                test_class.test_zero_appreciation_capital_growth,
                "PropertyYields.zero_appreciation",
            )
        )

        # Test Portfolio Yield Calculations
        test_class = TestPortfolioYieldCalculations()
        results.append(
            run_test_function(
                test_class.test_single_property_portfolio_yields,
                "PortfolioYields.single_property",
            )
        )
        results.append(
            run_test_function(
                test_class.test_portfolio_total_return_calculation,
                "PortfolioYields.total_return",
            )
        )

        return results

    except Exception as e:
        print(f"❌ Failed to import yield tests: {e}")
        return [False]


def main():
    """Main test runner function"""
    print("🧪 Property Investment Calculator Unit Test Runner")
    print("=" * 60)

    all_results = []

    # Run all test categories
    all_results.extend(run_dataclass_tests())
    all_results.extend(run_calculation_tests())
    all_results.extend(run_strategy_tests())
    all_results.extend(run_yield_tests())

    # Summary
    passed = sum(all_results)
    total = len(all_results)

    print("\n" + "=" * 60)
    print("UNIT TEST RESULTS:")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed / total) * 100:.1f}%")

    if passed == total:
        print("🎉 All unit tests passed!")
        print("The unit test suite is working correctly.")
    else:
        print("⚠️  Some unit tests failed. Check the output above for details.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
