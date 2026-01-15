#!/usr/bin/env python3
"""
Test script to verify API imports and basic functionality
"""

import os
import sys

# Add parent directory to Python path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)


def test_core_imports():
    """Test that core module imports work"""
    try:
        print("Testing core imports...")

        from core.main import (
            FinancingParameters,
            InvestmentStrategy,
            OperatingParameters,
            PropertyAcquisitionCosts,
            PropertyInvestment,
        )

        print("✓ Core main imports work")

        from core.strategies import (
            PropertyPortfolioSimulator,
            create_cash_strategy,
            create_leveraged_strategy,
            create_mixed_strategy,
        )

        print("✓ Core strategies imports work")
        return True

    except Exception as e:
        print(f"❌ Core imports failed: {e}")
        return False


def test_api_imports():
    """Test that all API components import correctly"""
    try:
        print("Testing API imports...")

        from api.models import (
            OperatingRequest,
            PropertyRequest,
            SimulationRequest,
            SimulationResponse,
            StrategyRequest,
        )

        print("✓ API models imports work")

        from api.endpoints import get_presets, simulate_strategies, validate_parameters

        print("✓ API endpoints imports work")

        from api.presets import get_strategy_presets

        print("✓ API presets imports work")

        from api.server import app

        print("✓ API server imports work")
        return True

    except Exception as e:
        print(f"❌ API imports failed: {e}")
        return False


def test_presets():
    """Test that presets work correctly"""
    try:
        from api.presets import get_strategy_presets

        presets = get_strategy_presets()
        print(f"\n✓ Found {len(presets)} strategy presets:")
        for preset in presets:
            print(f"  - {preset.name}: {preset.description}")
        return True
    except Exception as e:
        print(f"❌ Presets test failed: {e}")
        return False


def test_basic_simulation():
    """Test a basic simulation to ensure everything works end-to-end"""
    try:
        print("\nTesting basic simulation...")

        from api.endpoints import simulate_strategies
        from api.models import (
            OperatingRequest,
            PropertyRequest,
            SimulationRequest,
            StrategyRequest,
        )

        # Create a simple test request
        request = SimulationRequest(
            property=PropertyRequest(
                purchase_price=1000000,
                transfer_duty=10000,
                conveyancing_fees=15000,
                bond_registration=0,  # Cash purchase
                furnishing_cost=50000,
            ),
            operating=OperatingRequest(
                monthly_rental_income=12000,
                vacancy_rate=0.05,
                monthly_levies=1500,
                property_management_fee_rate=0.08,
                monthly_insurance=600,
                monthly_maintenance_reserve=800,
            ),
            available_capital=500000,
            capital_injections=[],
            strategies=[
                StrategyRequest(
                    name="Test Cash Strategy",
                    strategy_type="cash_only",
                    simulation_years=2,  # Short test
                    reinvest_cashflow=True,
                )
            ],
        )

        # Run simulation
        result = simulate_strategies(request)

        if result.success and len(result.results) == 1:
            strategy_result = result.results[0]
            print(f"✓ Basic simulation successful!")
            print(f"  - Strategy: {strategy_result.strategy_name}")
            print(
                f"  - Final properties: {strategy_result.summary.final_property_count}"
            )
            print(
                f"  - Portfolio value: R{strategy_result.summary.final_portfolio_value:,.0f}"
            )
            print(f"  - Snapshots: {len(strategy_result.snapshots)}")
            return True
        else:
            print(f"❌ Simulation failed: {result.error}")
            return False

    except Exception as e:
        print(f"❌ Basic simulation test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Property Investment Calculator API Test")
    print("=" * 50)

    # Test core imports first
    core_success = test_core_imports()
    if not core_success:
        print("\n❌ Core imports failed - check core module structure")
        sys.exit(1)

    # Test API imports
    api_success = test_api_imports()
    if not api_success:
        print("\n❌ API imports failed - check API module structure")
        sys.exit(1)

    # Test presets
    preset_success = test_presets()

    # Test basic simulation
    sim_success = test_basic_simulation()

    print("\n" + "=" * 50)
    if core_success and api_success and preset_success and sim_success:
        print("🎉 All tests passed! API is fully functional.")
        print("\n🚀 Ready to run API server:")
        print("   uvicorn api.server:app --reload")
        print("\n📖 API docs will be available at:")
        print("   http://localhost:8000/docs")
    else:
        print("❌ Some tests failed. Check errors above.")
        sys.exit(1)
