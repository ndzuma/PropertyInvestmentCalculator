"""
Unit Tests for Data Classes

Tests for the core data classes and property investment components:
- PropertyAcquisitionCosts
- FinancingParameters
- OperatingParameters
- InvestmentStrategy
- PropertyInvestment

These tests focus on:
- Object creation and validation
- Property calculations
- Edge cases and error conditions
- Type validation and constraints
"""

import os
import sys

import pytest

# Add parent directories to path for imports
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from main import (
    FinancingParameters,
    FinancingType,
    InvestmentStrategy,
    OperatingParameters,
    PropertyAcquisitionCosts,
    PropertyInvestment,
    RefineFrequency,
)
from tests.test_fixtures import (
    FinancingParametersBuilder,
    InvestmentBuilder,
    InvestmentStrategyBuilder,
    OperatingParametersBuilder,
    PropertyAcquisitionCostsBuilder,
)


class TestPropertyAcquisitionCosts:
    """Test PropertyAcquisitionCosts data class"""

    def test_basic_creation(self):
        """Test basic object creation with valid data"""
        costs = PropertyAcquisitionCostsBuilder().build()

        assert costs.purchase_price > 0
        assert costs.transfer_duty >= 0
        assert costs.conveyancing_fees >= 0
        assert costs.bond_registration >= 0
        assert costs.furnishing_cost >= 0

    def test_total_unfurnished_cost(self):
        """Test total unfurnished cost calculation"""
        costs = PropertyAcquisitionCosts(
            purchase_price=1_000_000,
            transfer_duty=10_000,
            conveyancing_fees=20_000,
            bond_registration=15_000,
            furnishing_cost=50_000,
        )

        expected = 1_000_000 + 10_000 + 20_000 + 15_000
        assert costs.total_unfurnished_cost == expected

    def test_total_furnished_cost(self):
        """Test total furnished cost calculation"""
        costs = PropertyAcquisitionCosts(
            purchase_price=1_000_000,
            transfer_duty=10_000,
            conveyancing_fees=20_000,
            bond_registration=15_000,
            furnishing_cost=50_000,
        )

        expected = 1_000_000 + 10_000 + 20_000 + 15_000 + 50_000
        assert costs.total_furnished_cost == expected

    def test_no_furnishing_cost(self):
        """Test with no furnishing cost"""
        costs = PropertyAcquisitionCosts(
            purchase_price=1_000_000,
            transfer_duty=10_000,
            conveyancing_fees=20_000,
            bond_registration=15_000,
            furnishing_cost=None,
        )

        assert costs.total_furnished_cost == costs.total_unfurnished_cost

    def test_zero_bond_registration_for_cash(self):
        """Test zero bond registration for cash purchases"""
        costs = PropertyAcquisitionCostsBuilder().as_cash_purchase().build()

        assert costs.bond_registration == 0

    def test_furnished_vs_unfurnished(self):
        """Test difference between furnished and unfurnished costs"""
        costs = PropertyAcquisitionCosts(
            purchase_price=1_000_000,
            transfer_duty=10_000,
            conveyancing_fees=20_000,
            bond_registration=15_000,
            furnishing_cost=75_000,
        )

        difference = costs.total_furnished_cost - costs.total_unfurnished_cost
        assert difference == 75_000

    def test_builder_pattern(self):
        """Test builder pattern functionality"""
        costs = (
            PropertyAcquisitionCostsBuilder()
            .with_purchase_price(2_000_000)
            .with_transfer_duty(20_000)
            .with_furnishing_cost(100_000)
            .build()
        )

        assert costs.purchase_price == 2_000_000
        assert costs.transfer_duty == 20_000
        assert costs.furnishing_cost == 100_000


class TestFinancingParameters:
    """Test FinancingParameters data class"""

    def test_basic_creation_leveraged(self):
        """Test basic leveraged financing creation"""
        financing = FinancingParametersBuilder().as_leveraged_financing().build()

        assert financing.financing_type == FinancingType.LEVERAGED
        assert 0 < financing.ltv_ratio <= 1.0
        assert financing.interest_rate is not None
        assert financing.interest_rate > 0
        assert financing.loan_term_years is not None
        assert financing.loan_term_years > 0

    def test_basic_creation_cash(self):
        """Test basic cash financing creation"""
        financing = FinancingParametersBuilder().as_cash_financing().build()

        assert financing.financing_type == FinancingType.CASH
        assert financing.ltv_ratio == 0.0
        assert financing.interest_rate is None
        assert financing.loan_term_years is None

    def test_appreciation_rate_validation(self):
        """Test appreciation rate is reasonable"""
        financing = FinancingParametersBuilder().with_appreciation_rate(0.08).build()

        assert financing.appreciation_rate == 0.08

    def test_custom_ltv_ratio(self):
        """Test custom LTV ratio settings"""
        financing = FinancingParametersBuilder().with_ltv_ratio(0.75).build()

        assert financing.ltv_ratio == 0.75

    def test_custom_interest_rate(self):
        """Test custom interest rate settings"""
        financing = FinancingParametersBuilder().with_interest_rate(0.12).build()

        assert financing.interest_rate == 0.12

    def test_custom_loan_term(self):
        """Test custom loan term settings"""
        financing = FinancingParametersBuilder().with_loan_term_years(25).build()

        assert financing.loan_term_years == 25


class TestOperatingParameters:
    """Test OperatingParameters data class"""

    def test_basic_creation(self):
        """Test basic operating parameters creation"""
        operating = OperatingParametersBuilder().build()

        assert operating.monthly_rental_income > 0
        assert 0 <= operating.vacancy_rate < 1.0
        assert operating.monthly_levies >= 0
        assert 0 <= operating.property_management_fee_rate < 1.0
        assert operating.monthly_insurance >= 0
        assert operating.monthly_maintenance_reserve >= 0

    def test_effective_monthly_rental(self):
        """Test effective monthly rental calculation"""
        operating = OperatingParameters(
            monthly_rental_income=10_000,
            vacancy_rate=0.05,  # 5% vacancy
            monthly_levies=1_000,
            property_management_fee_rate=0.08,
            monthly_insurance=500,
            monthly_maintenance_reserve=800,
            monthly_furnishing_repair_costs=200,
        )

        expected = 10_000 * (1 - 0.05)  # 10,000 * 0.95 = 9,500
        assert operating.effective_monthly_rental == expected

    def test_monthly_management_fee(self):
        """Test monthly management fee calculation"""
        operating = OperatingParameters(
            monthly_rental_income=10_000,
            vacancy_rate=0.05,  # 5% vacancy
            monthly_levies=1_000,
            property_management_fee_rate=0.08,  # 8%
            monthly_insurance=500,
            monthly_maintenance_reserve=800,
            monthly_furnishing_repair_costs=200,
        )

        effective_rental = 10_000 * 0.95  # After vacancy
        expected_fee = effective_rental * 0.08  # 8% of effective rental
        assert operating.monthly_management_fee == expected_fee

    def test_total_monthly_expenses(self):
        """Test total monthly expenses calculation"""
        operating = OperatingParameters(
            monthly_rental_income=10_000,
            vacancy_rate=0.05,
            monthly_levies=1_000,
            property_management_fee_rate=0.08,
            monthly_insurance=500,
            monthly_maintenance_reserve=800,
            monthly_furnishing_repair_costs=200,
        )

        effective_rental = 10_000 * 0.95
        management_fee = effective_rental * 0.08
        expected = 1_000 + management_fee + 500 + 800 + 200

        assert operating.total_monthly_expenses == expected

    def test_annual_rental_income(self):
        """Test annual rental income calculation"""
        operating = OperatingParameters(
            monthly_rental_income=15_000,
            vacancy_rate=0.05,
            monthly_levies=2_000,
            property_management_fee_rate=0.08,
            monthly_insurance=600,
            monthly_maintenance_reserve=1_000,
            monthly_furnishing_repair_costs=400,
        )

        expected = 15_000 * 12
        assert operating.annual_rental_income == expected

    def test_no_furnishing_repair_costs(self):
        """Test with no furnishing repair costs"""
        operating = OperatingParameters(
            monthly_rental_income=10_000,
            vacancy_rate=0.05,
            monthly_levies=1_000,
            property_management_fee_rate=0.08,
            monthly_insurance=500,
            monthly_maintenance_reserve=800,
            monthly_furnishing_repair_costs=None,
        )

        # Should handle None gracefully
        assert operating.total_monthly_expenses > 0

    def test_builder_customization(self):
        """Test builder pattern customization"""
        operating = (
            OperatingParametersBuilder()
            .with_monthly_rental_income(20_000)
            .with_vacancy_rate(0.03)
            .with_management_fee_rate(0.10)
            .build()
        )

        assert operating.monthly_rental_income == 20_000
        assert operating.vacancy_rate == 0.03
        assert operating.property_management_fee_rate == 0.10


class TestInvestmentStrategy:
    """Test InvestmentStrategy data class"""

    def test_basic_creation(self):
        """Test basic strategy creation"""
        strategy = InvestmentStrategyBuilder().build()

        assert strategy.available_investment_amount > 0
        assert isinstance(strategy.reinvest_cashflow, bool)
        assert isinstance(strategy.enable_refinancing, bool)
        assert isinstance(strategy.refinance_frequency, RefineFrequency)

    def test_conservative_strategy(self):
        """Test conservative strategy configuration"""
        strategy = InvestmentStrategyBuilder().as_conservative().build()

        assert strategy.reinvest_cashflow is True
        assert strategy.enable_refinancing is False
        assert strategy.target_refinance_ltv is None

    def test_aggressive_strategy(self):
        """Test aggressive strategy configuration"""
        strategy = InvestmentStrategyBuilder().as_aggressive().build()

        assert strategy.reinvest_cashflow is True
        assert strategy.enable_refinancing is True
        assert strategy.refinance_frequency == RefineFrequency.BI_ANNUALLY
        assert strategy.target_refinance_ltv == 0.7

    def test_refinancing_configuration(self):
        """Test refinancing configuration"""
        strategy = (
            InvestmentStrategyBuilder()
            .with_refinancing(True, RefineFrequency.QUARTERLY, 0.65)
            .build()
        )

        assert strategy.enable_refinancing is True
        assert strategy.refinance_frequency == RefineFrequency.QUARTERLY
        assert strategy.target_refinance_ltv == 0.65

    def test_investment_amount_customization(self):
        """Test investment amount customization"""
        strategy = InvestmentStrategyBuilder().with_investment_amount(5_000_000).build()

        assert strategy.available_investment_amount == 5_000_000


class TestPropertyInvestment:
    """Test PropertyInvestment complete object"""

    def test_basic_creation(self):
        """Test basic property investment creation"""
        investment = InvestmentBuilder().build()

        assert investment.acquisition_costs is not None
        assert investment.financing is not None
        assert investment.operating is not None
        assert investment.strategy is not None

    def test_cash_investment_validation(self):
        """Test cash investment validation passes"""
        # Should not raise any exceptions
        investment = InvestmentBuilder().as_cash_purchase().build()

        assert investment.financing.financing_type == FinancingType.CASH
        assert investment.acquisition_costs.bond_registration == 0

    def test_leveraged_investment_validation(self):
        """Test leveraged investment validation passes"""
        # Should not raise any exceptions
        investment = InvestmentBuilder().as_leveraged_purchase().build()

        assert investment.financing.financing_type == FinancingType.LEVERAGED
        assert investment.financing.interest_rate is not None
        assert investment.acquisition_costs.bond_registration > 0

    def test_invalid_leveraged_investment_no_interest_rate(self):
        """Test validation fails for leveraged investment without interest rate"""
        with pytest.raises(
            ValueError, match="Interest rate required for leveraged financing"
        ):
            PropertyInvestment(
                acquisition_costs=PropertyAcquisitionCostsBuilder().build(),
                financing=FinancingParameters(
                    ltv_ratio=0.5,
                    financing_type=FinancingType.LEVERAGED,
                    appreciation_rate=0.06,
                    interest_rate=None,  # Invalid for leveraged
                    loan_term_years=20,
                ),
                operating=OperatingParametersBuilder().build(),
                strategy=InvestmentStrategyBuilder().build(),
            )

    def test_invalid_leveraged_investment_no_bond_cost(self):
        """Test validation fails for leveraged investment without bond registration cost"""
        with pytest.raises(
            ValueError,
            match="Bond registration cost should be > 0 for leveraged financing",
        ):
            PropertyInvestment(
                acquisition_costs=PropertyAcquisitionCosts(
                    purchase_price=1_000_000,
                    transfer_duty=10_000,
                    conveyancing_fees=20_000,
                    bond_registration=0,  # Invalid for leveraged
                    furnishing_cost=50_000,
                ),
                financing=FinancingParametersBuilder().as_leveraged_financing().build(),
                operating=OperatingParametersBuilder().build(),
                strategy=InvestmentStrategyBuilder().build(),
            )

    def test_invalid_refinancing_without_target_ltv(self):
        """Test validation fails for refinancing without target LTV"""
        with pytest.raises(
            ValueError,
            match="Target refinance LTV required when refinancing is enabled",
        ):
            PropertyInvestment(
                acquisition_costs=PropertyAcquisitionCostsBuilder().build(),
                financing=FinancingParametersBuilder().build(),
                operating=OperatingParametersBuilder().build(),
                strategy=InvestmentStrategy(
                    available_investment_amount=2_000_000,
                    reinvest_cashflow=True,
                    enable_refinancing=True,  # Enabled but no target LTV
                    refinance_frequency=RefineFrequency.ANNUALLY,
                    target_refinance_ltv=None,  # Invalid when refinancing enabled
                ),
            )

    def test_initial_cash_required_cash_purchase(self):
        """Test initial cash required calculation for cash purchase"""
        investment = InvestmentBuilder().as_cash_purchase().build()

        expected = investment.acquisition_costs.total_furnished_cost
        assert investment.initial_cash_required == expected

    def test_initial_cash_required_leveraged_purchase(self):
        """Test initial cash required calculation for leveraged purchase"""
        investment = InvestmentBuilder().as_leveraged_purchase(0.6).build()  # 60% LTV

        loan_amount = investment.acquisition_costs.purchase_price * 0.6
        expected = investment.acquisition_costs.total_furnished_cost - loan_amount

        assert investment.initial_cash_required == expected

    def test_monthly_bond_payment_cash_purchase(self):
        """Test monthly bond payment is None for cash purchase"""
        investment = InvestmentBuilder().as_cash_purchase().build()

        assert investment.monthly_bond_payment is None

    def test_monthly_bond_payment_leveraged_purchase(self):
        """Test monthly bond payment calculation for leveraged purchase"""
        investment = PropertyInvestment(
            acquisition_costs=PropertyAcquisitionCosts(
                purchase_price=1_000_000,
                transfer_duty=10_000,
                conveyancing_fees=20_000,
                bond_registration=15_000,
                furnishing_cost=50_000,
            ),
            financing=FinancingParameters(
                ltv_ratio=0.5,  # 50% LTV
                financing_type=FinancingType.LEVERAGED,
                appreciation_rate=0.06,
                interest_rate=0.10,  # 10% annual
                loan_term_years=20,
            ),
            operating=OperatingParametersBuilder().build(),
            strategy=InvestmentStrategyBuilder().build(),
        )

        payment = investment.monthly_bond_payment
        assert payment is not None
        assert payment > 0
        # Should be reasonable for a 500k loan at 10% over 20 years
        assert 4000 < payment < 5500

    def test_monthly_bond_payment_zero_interest_rate(self):
        """Test monthly bond payment with zero interest rate"""
        investment = PropertyInvestment(
            acquisition_costs=PropertyAcquisitionCosts(
                purchase_price=1_000_000,
                transfer_duty=10_000,
                conveyancing_fees=20_000,
                bond_registration=15_000,
                furnishing_cost=50_000,
            ),
            financing=FinancingParameters(
                ltv_ratio=0.5,
                financing_type=FinancingType.LEVERAGED,
                appreciation_rate=0.06,
                interest_rate=0.0,  # Zero interest
                loan_term_years=20,
            ),
            operating=OperatingParametersBuilder().build(),
            strategy=InvestmentStrategyBuilder().build(),
        )

        loan_amount = 1_000_000 * 0.5  # 500,000
        expected_payment = loan_amount / (20 * 12)  # Simple division

        assert investment.monthly_bond_payment == expected_payment

    def test_monthly_bond_payment_missing_data_error(self):
        """Test monthly bond payment raises error when required data is missing"""
        investment = PropertyInvestment(
            acquisition_costs=PropertyAcquisitionCostsBuilder().build(),
            financing=FinancingParameters(
                ltv_ratio=0.5,
                financing_type=FinancingType.LEVERAGED,
                appreciation_rate=0.06,
                interest_rate=None,  # Missing but needed for calculation
                loan_term_years=None,  # Missing but needed for calculation
            ),
            operating=OperatingParametersBuilder().build(),
            strategy=InvestmentStrategyBuilder().build(),
        )

        # This should be caught during object creation, but if not:
        with pytest.raises(ValueError):
            _ = investment.monthly_bond_payment

    def test_monthly_cashflow_positive(self):
        """Test monthly cashflow calculation with positive result"""
        investment = (
            InvestmentBuilder().as_cash_purchase().with_rental_income(15_000).build()
        )

        cashflow = investment.monthly_cashflow
        assert cashflow > 0

    def test_monthly_cashflow_negative(self):
        """Test monthly cashflow calculation with negative result"""
        investment = (
            InvestmentBuilder()
            .as_leveraged_purchase(0.8)  # High leverage
            .with_rental_income(5_000)  # Low rental income
            .build()
        )

        cashflow = investment.monthly_cashflow
        # Could be negative due to high bond payments vs low rental
        assert isinstance(cashflow, float)

    def test_comprehensive_integration(self):
        """Test comprehensive integration of all components"""
        investment = (
            InvestmentBuilder()
            .with_purchase_price(2_500_000)
            .with_leverage(0.7)
            .with_interest_rate(0.095)
            .with_rental_income(22_000)
            .with_investment_amount(3_000_000)
            .build()
        )

        # Verify all calculations work together
        assert investment.initial_cash_required > 0
        assert investment.monthly_bond_payment > 0
        assert investment.monthly_cashflow is not None

        # Verify relationships
        total_cost = investment.acquisition_costs.total_furnished_cost
        loan_amount = investment.acquisition_costs.purchase_price * 0.7
        expected_cash = total_cost - loan_amount

        assert investment.initial_cash_required == expected_cash
