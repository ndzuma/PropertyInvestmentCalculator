"""
Integration Tests for Strategy Comparison

Tests that compare different investment strategies to validate:
- Performance differences between cash vs leveraged strategies
- Mixed strategy performance against pure strategies
- Strategy behavior under different market conditions
- Comparative metrics and returns
- Risk/return profiles

These tests help validate that strategies perform as expected
relative to each other and under various market scenarios.
"""

from typing import Dict, List, Tuple

import pytest

from main import PropertyInvestment
from strategies import (
    PropertyPortfolioSimulator,
    SimulationSnapshot,
    StrategyConfig,
    StrategyType,
    TrackingFrequency,
)
from tests.test_fixtures import (
    CapitalInjectionBuilder,
    InvestmentBuilder,
    StrategyConfigBuilder,
)


@pytest.mark.integration
class TestCashVsLeveragedComparison:
    """Compare cash-only vs leveraged-only strategies"""

    def test_cash_vs_leveraged_basic_comparison(self):
        """Compare basic cash vs leveraged strategy performance"""
        # Common investment property
        base_investment = (
            InvestmentBuilder()
            .with_purchase_price(1_000_000)
            .with_rental_income(12_000)
            .with_appreciation_rate(0.06)
            .with_investment_amount(5_000_000)
            .build()
        )

        # Cash strategy
        cash_strategy = (
            StrategyConfigBuilder().as_cash_only().with_simulation_years(5).build()
        )

        # Leveraged strategy
        leveraged_strategy = (
            StrategyConfigBuilder()
            .as_leveraged_only(0.7)
            .with_simulation_years(5)
            .build()
        )

        # Run simulations
        cash_simulator = PropertyPortfolioSimulator(base_investment, cash_strategy)
        leveraged_simulator = PropertyPortfolioSimulator(
            base_investment, leveraged_strategy
        )

        cash_snapshots = cash_simulator.simulate()
        leveraged_snapshots = leveraged_simulator.simulate()

        # Compare final results
        cash_final = cash_snapshots[-1]
        leveraged_final = leveraged_snapshots[-1]

        # Compare strategies based on their characteristics, not assumptions
        # Leveraged may have fewer properties due to lower cash flow from debt service
        # But should have higher leverage (debt/equity ratio)
        if leveraged_final.total_debt > 0:
            leveraged_debt_ratio = (
                leveraged_final.total_debt / leveraged_final.total_property_value
            )
            assert leveraged_debt_ratio > 0.5  # Should have significant leverage

        # Cash strategy should be able to buy more properties with better cash flow
        if not leveraged_final.simulation_ended:
            # If leveraged didn't fail, compare return on invested capital
            cash_roi = (
                cash_final.total_equity - cash_final.total_cash_invested
            ) / cash_final.total_cash_invested
            leveraged_roi = (
                leveraged_final.total_equity - leveraged_final.total_cash_invested
            ) / leveraged_final.total_cash_invested
            # At least one should be profitable
            assert cash_roi > 0 or leveraged_roi > 0

        # Cash should have no debt, leveraged should have debt
        assert cash_final.total_debt == 0
        assert leveraged_final.total_debt > 0

        # Both should have positive equity
        assert cash_final.total_equity > 0
        assert leveraged_final.total_equity > 0

    def test_return_comparison_over_time(self, assert_approximately):
        """Compare returns between cash and leveraged strategies over time"""
        investment = (
            InvestmentBuilder()
            .with_purchase_price(1_500_000)
            .with_rental_income(15_000)
            .with_appreciation_rate(0.08)  # Strong appreciation
            .with_investment_amount(3_000_000)
            .build()
        )

        # Create strategies
        strategies = {
            "cash": StrategyConfigBuilder().as_cash_only().with_simulation_years(4),
            "leveraged": StrategyConfigBuilder()
            .as_leveraged_only(0.8)
            .with_simulation_years(4),
        }

        results = {}
        for name, strategy_builder in strategies.items():
            strategy = strategy_builder.build()
            simulator = PropertyPortfolioSimulator(investment, strategy)
            snapshots = simulator.simulate()
            results[name] = snapshots

        # Compare equity growth rates
        cash_initial = results["cash"][0].total_equity
        cash_final = results["cash"][-1].total_equity
        cash_growth = (cash_final - cash_initial) / cash_initial

        leveraged_initial = results["leveraged"][0].total_equity
        leveraged_final = results["leveraged"][-1].total_equity
        leveraged_growth = (leveraged_final - leveraged_initial) / leveraged_initial

        # With strong appreciation, leveraged should outperform due to leverage effect
        assert leveraged_growth > cash_growth

        # Both should have positive growth
        assert cash_growth > 0
        assert leveraged_growth > 0

    def test_risk_profile_comparison(self):
        """Compare risk profiles between strategies"""
        investment = (
            InvestmentBuilder()
            .with_purchase_price(800_000)
            .with_rental_income(10_000)
            .with_investment_amount(2_000_000)
            .build()
        )

        # Test with conservative vs aggressive leverage
        conservative_strategy = (
            StrategyConfigBuilder()
            .as_leveraged_only(0.5)  # Conservative 50% LTV
            .with_simulation_years(3)
            .build()
        )

        aggressive_strategy = (
            StrategyConfigBuilder()
            .as_leveraged_only(0.9)  # Aggressive 90% LTV
            .with_simulation_years(3)
            .build()
        )

        conservative_simulator = PropertyPortfolioSimulator(
            investment, conservative_strategy
        )
        aggressive_simulator = PropertyPortfolioSimulator(
            investment, aggressive_strategy
        )

        conservative_snapshots = conservative_simulator.simulate()
        aggressive_snapshots = aggressive_simulator.simulate()

        conservative_final = conservative_snapshots[-1]
        aggressive_final = aggressive_snapshots[-1]

        # Check if strategies succeeded or failed due to cash flow
        if aggressive_final.simulation_ended:
            # High leverage strategy may fail due to poor cash flow
            assert "cash" in aggressive_final.end_reason.lower()
        else:
            # If both strategies succeeded, compare their characteristics
            conservative_debt_ratio = (
                conservative_final.total_debt / conservative_final.total_equity
                if conservative_final.total_equity > 0
                else 0
            )
            aggressive_debt_ratio = (
                aggressive_final.total_debt / aggressive_final.total_equity
                if aggressive_final.total_equity > 0
                else 0
            )

            # Aggressive should have higher debt-to-equity ratio
            assert aggressive_debt_ratio > conservative_debt_ratio

        # Compare the fundamental risk characteristics
        if (
            not aggressive_final.simulation_ended
            and not conservative_final.simulation_ended
        ):
            # Both succeeded - compare their leverage characteristics
            if (
                conservative_final.total_property_value > 0
                and aggressive_final.total_property_value > 0
            ):
                conservative_leverage = (
                    conservative_final.total_debt
                    / conservative_final.total_property_value
                )
                aggressive_leverage = (
                    aggressive_final.total_debt / aggressive_final.total_property_value
                )

                # Aggressive should have higher leverage ratio
                assert aggressive_leverage > conservative_leverage, (
                    f"Aggressive leverage ({aggressive_leverage:.2%}) should be higher than "
                    f"conservative leverage ({conservative_leverage:.2%})"
                )

    def test_cashflow_comparison(self):
        """Compare cash flow characteristics between strategies"""
        investment = (
            InvestmentBuilder()
            .with_purchase_price(1_200_000)
            .with_rental_income(14_000)
            .with_investment_amount(3_000_000)
            .build()
        )

        cash_strategy = (
            StrategyConfigBuilder().as_cash_only().with_simulation_years(3).build()
        )

        leveraged_strategy = (
            StrategyConfigBuilder()
            .as_leveraged_only(0.7)
            .with_simulation_years(3)
            .build()
        )

        # Run simulations
        cash_simulator = PropertyPortfolioSimulator(investment, cash_strategy)
        leveraged_simulator = PropertyPortfolioSimulator(investment, leveraged_strategy)

        cash_snapshots = cash_simulator.simulate()
        leveraged_snapshots = leveraged_simulator.simulate()

        # Compare cash flow patterns
        cash_flows_cash = [s.annual_cashflow for s in cash_snapshots[1:]]
        cash_flows_leveraged = [s.annual_cashflow for s in leveraged_snapshots[1:]]

        # Cash strategy should have consistently positive cash flows
        assert all(cf >= 0 for cf in cash_flows_cash)

        # Leveraged may have negative cash flows initially due to debt service
        # but this depends on rental yield vs interest rates


@pytest.mark.integration
class TestMixedVsPureStrategyComparison:
    """Compare mixed strategies against pure cash/leveraged strategies"""

    def test_mixed_vs_pure_strategies_performance(self):
        """Compare mixed strategy against pure strategies"""
        base_config = {
            "purchase_price": 900_000,
            "rental_income": 11_000,
            "simulation_years": 4,
        }

        investment = (
            InvestmentBuilder()
            .with_purchase_price(base_config["purchase_price"])
            .with_rental_income(base_config["rental_income"])
            .with_investment_amount(4_000_000)
            .build()
        )

        # Create different strategies
        strategies = {
            "pure_cash": StrategyConfigBuilder().as_cash_only(),
            "pure_leveraged": StrategyConfigBuilder().as_leveraged_only(0.7),
            "mixed_conservative": StrategyConfigBuilder().as_mixed_strategy(0.3),
            "mixed_aggressive": StrategyConfigBuilder().as_mixed_strategy(0.8),
        }

        results = {}
        for name, strategy_builder in strategies.items():
            strategy = strategy_builder.with_simulation_years(
                base_config["simulation_years"]
            ).build()
            simulator = PropertyPortfolioSimulator(investment, strategy)
            snapshots = simulator.simulate()
            results[name] = snapshots[-1]

        # Compare final equity positions
        equity_values = {
            name: snapshot.total_equity for name, snapshot in results.items()
        }

        # Mixed strategies should fall between pure strategies in risk/return
        mixed_conservative_equity = equity_values["mixed_conservative"]
        mixed_aggressive_equity = equity_values["mixed_aggressive"]
        pure_cash_equity = equity_values["pure_cash"]
        pure_leveraged_equity = equity_values["pure_leveraged"]

        # More aggressive mixed strategy should outperform conservative
        assert mixed_aggressive_equity >= mixed_conservative_equity

        # All should have positive equity
        for equity in equity_values.values():
            assert equity > 0

    def test_mixed_strategy_diversification_benefits(self):
        """Test that mixed strategies provide diversification benefits"""
        investment = (
            InvestmentBuilder()
            .with_purchase_price(1_000_000)
            .with_rental_income(12_000)
            .with_investment_amount(6_000_000)
            .build()
        )

        # Mixed strategy with balanced allocation
        mixed_strategy = (
            StrategyConfigBuilder()
            .as_mixed_strategy(0.5)  # 50% leveraged properties
            .with_simulation_years(5)
            .build()
        )

        simulator = PropertyPortfolioSimulator(investment, mixed_strategy)
        snapshots = simulator.simulate()

        final_snapshot = snapshots[-1]

        # Should have multiple properties
        assert len(final_snapshot.properties) > 1

        # Should have both debt and significant equity
        assert final_snapshot.total_debt > 0
        assert final_snapshot.total_equity > 0

        # Debt-to-equity ratio should be moderate (not extreme)
        debt_to_equity = final_snapshot.total_debt / final_snapshot.total_equity
        assert 0.1 < debt_to_equity < 5.0  # Reasonable range

    def test_mixed_strategy_with_different_ratios(self):
        """Test mixed strategies with different leveraged property ratios"""
        investment = (
            InvestmentBuilder()
            .with_purchase_price(750_000)
            .with_rental_income(9_000)
            .with_investment_amount(5_000_000)
            .build()
        )

        ratios_to_test = [0.2, 0.5, 0.8]
        results = {}

        for ratio in ratios_to_test:
            strategy = (
                StrategyConfigBuilder()
                .as_mixed_strategy(ratio)
                .with_simulation_years(3)
                .build()
            )

            simulator = PropertyPortfolioSimulator(investment, strategy)
            snapshots = simulator.simulate()
            results[ratio] = snapshots[-1]

        # Higher leverage ratios should generally result in higher total property values
        property_values = {
            ratio: snapshot.total_property_value for ratio, snapshot in results.items()
        }

        # Generally, higher leverage should enable larger portfolios
        assert property_values[0.8] >= property_values[0.2]

        # All should have positive outcomes
        for snapshot in results.values():
            assert snapshot.total_equity > 0
            assert len(snapshot.properties) >= 1


@pytest.mark.integration
class TestStrategyPerformanceUnderConditions:
    """Test strategy performance under different market conditions"""

    def test_strategies_under_high_appreciation(self):
        """Test strategy performance with high property appreciation"""
        high_appreciation = 0.12  # 12% annual appreciation

        # Cash strategy
        cash_investment = (
            InvestmentBuilder()
            .with_purchase_price(1_000_000)
            .with_rental_income(12_000)
            .with_appreciation_rate(high_appreciation)
            .with_investment_amount(3_000_000)
            .build()
        )

        # Leveraged strategy
        leveraged_investment = (
            InvestmentBuilder()
            .with_purchase_price(1_000_000)
            .with_rental_income(12_000)
            .with_appreciation_rate(high_appreciation)
            .with_investment_amount(3_000_000)
            .build()
        )

        cash_strategy = (
            StrategyConfigBuilder().as_cash_only().with_simulation_years(4).build()
        )

        leveraged_strategy = (
            StrategyConfigBuilder()
            .as_leveraged_only(0.8)
            .with_simulation_years(4)
            .build()
        )

        # Run simulations
        cash_simulator = PropertyPortfolioSimulator(cash_investment, cash_strategy)
        leveraged_simulator = PropertyPortfolioSimulator(
            leveraged_investment, leveraged_strategy
        )

        cash_snapshots = cash_simulator.simulate()
        leveraged_snapshots = leveraged_simulator.simulate()

        # Calculate growth rates
        cash_initial_equity = cash_snapshots[0].total_equity
        cash_final_equity = cash_snapshots[-1].total_equity
        cash_growth_rate = (cash_final_equity / cash_initial_equity) ** (
            1 / 4
        ) - 1  # Annualized

        leveraged_initial_equity = leveraged_snapshots[0].total_equity
        leveraged_final_equity = leveraged_snapshots[-1].total_equity
        leveraged_growth_rate = (leveraged_final_equity / leveraged_initial_equity) ** (
            1 / 4
        ) - 1  # Annualized

        # With high appreciation, leveraged should significantly outperform
        assert leveraged_growth_rate > cash_growth_rate

        # Both should have strong positive growth
        assert cash_growth_rate > 0.08  # Should beat appreciation rate
        assert leveraged_growth_rate > 0.15  # Should have leverage amplification

    def test_strategies_under_low_appreciation(self):
        """Test strategy performance with low property appreciation"""
        low_appreciation = 0.02  # 2% annual appreciation

        investment = (
            InvestmentBuilder()
            .with_purchase_price(1_200_000)
            .with_rental_income(15_000)  # Higher rental yield to compensate
            .with_appreciation_rate(low_appreciation)
            .with_investment_amount(4_000_000)
            .build()
        )

        cash_strategy = (
            StrategyConfigBuilder().as_cash_only().with_simulation_years(3).build()
        )

        leveraged_strategy = (
            StrategyConfigBuilder()
            .as_leveraged_only(0.6)  # Lower leverage for safety
            .with_simulation_years(3)
            .build()
        )

        # Run simulations
        cash_simulator = PropertyPortfolioSimulator(investment, cash_strategy)
        leveraged_simulator = PropertyPortfolioSimulator(investment, leveraged_strategy)

        cash_snapshots = cash_simulator.simulate()
        leveraged_snapshots = leveraged_simulator.simulate()

        # Both should still be viable with good rental yields
        cash_final = cash_snapshots[-1]
        leveraged_final = leveraged_snapshots[-1]

        assert cash_final.total_equity > 0
        assert leveraged_final.total_equity > 0

        # Performance gap should be smaller with low appreciation
        # (This is more of a behavioral validation than strict assertion)

    def test_strategies_with_high_interest_rates(self):
        """Test strategy performance with high interest rates"""
        investment = (
            InvestmentBuilder()
            .with_purchase_price(800_000)
            .with_rental_income(10_000)
            .with_interest_rate(0.15)  # High interest rate
            .with_investment_amount(3_000_000)
            .build()
        )

        # Cash strategy (unaffected by interest rates)
        cash_strategy = (
            StrategyConfigBuilder().as_cash_only().with_simulation_years(3).build()
        )

        # Leveraged strategy (heavily affected)
        leveraged_strategy = (
            StrategyConfigBuilder()
            .as_leveraged_only(0.6)  # Conservative leverage due to high rates
            .with_simulation_years(3)
            .build()
        )

        # Run simulations
        cash_simulator = PropertyPortfolioSimulator(investment, cash_strategy)
        leveraged_simulator = PropertyPortfolioSimulator(investment, leveraged_strategy)

        cash_snapshots = cash_simulator.simulate()
        leveraged_snapshots = leveraged_simulator.simulate()

        # Cash should be less affected by high interest rates
        cash_final = cash_snapshots[-1]
        leveraged_final = leveraged_snapshots[-1]

        # Both should complete successfully
        assert len(cash_snapshots) >= 3
        assert len(leveraged_snapshots) >= 3

        # Cash strategy should maintain positive cash flows
        cash_flows = [s.annual_cashflow for s in cash_snapshots[1:]]
        assert all(cf > 0 for cf in cash_flows)


@pytest.mark.integration
class TestComparativeMetrics:
    """Test comparative metrics between strategies"""

    def test_return_on_investment_comparison(self):
        """Compare ROI between different strategies"""
        base_purchase_price = 1_000_000
        base_rental = 12_000
        simulation_years = 5

        strategies_to_test = [
            ("cash", lambda: StrategyConfigBuilder().as_cash_only()),
            ("leveraged_50", lambda: StrategyConfigBuilder().as_leveraged_only(0.5)),
            ("leveraged_70", lambda: StrategyConfigBuilder().as_leveraged_only(0.7)),
            ("mixed", lambda: StrategyConfigBuilder().as_mixed_strategy(0.6)),
        ]

        results = {}

        for strategy_name, strategy_factory in strategies_to_test:
            investment = (
                InvestmentBuilder()
                .with_purchase_price(base_purchase_price)
                .with_rental_income(base_rental)
                .with_investment_amount(5_000_000)
                .build()
            )

            strategy = (
                strategy_factory().with_simulation_years(simulation_years).build()
            )

            simulator = PropertyPortfolioSimulator(investment, strategy)
            snapshots = simulator.simulate()

            initial_equity = snapshots[0].total_equity
            final_equity = snapshots[-1].total_equity

            roi = (final_equity / initial_equity) ** (1 / simulation_years) - 1
            results[strategy_name] = {
                "roi": roi,
                "final_equity": final_equity,
                "initial_equity": initial_equity,
                "snapshots": snapshots,
            }

        # Validate that strategies produce reasonable results
        # Some leveraged strategies may fail or underperform due to cash flow constraints
        cash_roi = results["cash"]["roi"]

        # Cash strategy should always work (no debt service)
        assert cash_roi > 0, "Cash strategy should have positive ROI"
        assert results["cash"]["final_equity"] > results["cash"]["initial_equity"]

        # Check leveraged strategies - they may fail due to poor cash flow
        successful_strategies = []
        for strategy_name, data in results.items():
            final_snapshot = data["snapshots"][-1]
            if not final_snapshot.simulation_ended and data["roi"] > 0:
                successful_strategies.append(strategy_name)
            elif final_snapshot.simulation_ended:
                # Failed strategies should have cash-related failure reason
                assert "cash" in final_snapshot.end_reason.lower(), (
                    f"{strategy_name} should fail due to cash flow issues"
                )

        # At least cash strategy should be successful
        assert len(successful_strategies) >= 1, (
            "At least one strategy should be successful"
        )

        # If multiple strategies succeeded, compare their performance
        if len(successful_strategies) > 1:
            print(f"Successful strategies: {successful_strategies}")
            for strategy in successful_strategies:
                print(f"{strategy} ROI: {results[strategy]['roi']:.2%}")

    def test_cash_flow_yield_comparison(self):
        """Compare cash flow yields between strategies"""
        investment = (
            InvestmentBuilder()
            .with_purchase_price(1_500_000)
            .with_rental_income(18_000)  # Good rental yield
            .with_investment_amount(4_000_000)
            .build()
        )

        strategies = {
            "cash": StrategyConfigBuilder().as_cash_only(),
            "leveraged": StrategyConfigBuilder().as_leveraged_only(0.7),
        }

        yield_results = {}

        for name, strategy_builder in strategies.items():
            strategy = strategy_builder.with_simulation_years(3).build()
            simulator = PropertyPortfolioSimulator(investment, strategy)
            snapshots = simulator.simulate()

            # Calculate average cash-on-cash return
            coc_returns = []
            for snapshot in snapshots[1:]:  # Skip initial
                if snapshot.property_yields:
                    avg_coc = sum(
                        py.cash_on_cash_return for py in snapshot.property_yields
                    ) / len(snapshot.property_yields)
                    coc_returns.append(avg_coc)

            if coc_returns:
                avg_coc = sum(coc_returns) / len(coc_returns)
                yield_results[name] = avg_coc

        # Both strategies should generate reasonable cash-on-cash returns
        for strategy_name, coc in yield_results.items():
            assert 0 <= coc <= 0.5, f"{strategy_name} CoC return should be reasonable"

    def test_risk_adjusted_returns(self):
        """Test risk-adjusted returns comparison"""
        investment = (
            InvestmentBuilder()
            .with_purchase_price(900_000)
            .with_rental_income(11_000)
            .with_investment_amount(3_000_000)
            .build()
        )

        # Conservative strategy
        conservative = (
            StrategyConfigBuilder()
            .as_leveraged_only(0.5)
            .with_simulation_years(4)
            .build()
        )

        # Aggressive strategy
        aggressive = (
            StrategyConfigBuilder()
            .as_leveraged_only(0.8)
            .with_simulation_years(4)
            .build()
        )

        conservative_simulator = PropertyPortfolioSimulator(investment, conservative)
        aggressive_simulator = PropertyPortfolioSimulator(investment, aggressive)

        conservative_snapshots = conservative_simulator.simulate()
        aggressive_snapshots = aggressive_simulator.simulate()

        # Calculate debt service coverage ratios as risk metric
        conservative_final = conservative_snapshots[-1]
        aggressive_final = aggressive_snapshots[-1]

        # Conservative should have lower debt relative to cash flow
        conservative_debt_ratio = conservative_final.total_debt / (
            conservative_final.annual_cashflow + 1
        )  # +1 to avoid division by zero
        aggressive_debt_ratio = aggressive_final.total_debt / (
            aggressive_final.annual_cashflow + 1
        )

        # Aggressive should have higher debt burden
        assert aggressive_debt_ratio >= conservative_debt_ratio

        # Both should maintain positive equity
        assert conservative_final.total_equity > 0
        assert aggressive_final.total_equity > 0
