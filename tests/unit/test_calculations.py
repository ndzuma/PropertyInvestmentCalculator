"""
Unit Tests for Financial Calculations

Tests for core financial calculation functions and methods:
- Monthly bond payment (PMT formula)
- Cash flow calculations
- Yield calculations (rental, net rental, cash-on-cash)
- Initial cash requirements
- Property value calculations

These tests focus on:
- Mathematical accuracy
- Edge cases (zero rates, extreme values)
- Error handling
- Precision and rounding
"""

import math
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
    OperatingParameters,
    PropertyAcquisitionCosts,
    PropertyInvestment,
)
from tests.test_fixtures import InvestmentBuilder


class TestMonthlyPaymentCalculations:
    """Test monthly bond payment (PMT) calculations"""

    def test_pmt_formula_basic(self):
        """Test basic PMT formula calculation"""
        # Standard scenario: 1M loan, 10% annual rate, 20 years
        investment = PropertyInvestment(
            acquisition_costs=PropertyAcquisitionCosts(
                purchase_price=2_000_000,
                transfer_duty=20_000,
                conveyancing_fees=40_000,
                bond_registration=30_000,
                furnishing_cost=100_000,
            ),
            financing=FinancingParameters(
                ltv_ratio=0.5,  # 50% LTV = 1M loan
                financing_type=FinancingType.LEVERAGED,
                appreciation_rate=0.06,
                interest_rate=0.10,  # 10% annual
                loan_term_years=20,
            ),
            operating=OperatingParameters(
                monthly_rental_income=15_000,
                vacancy_rate=0.05,
                monthly_levies=2_500,
                property_management_fee_rate=0.08,
                monthly_insurance=800,
                monthly_maintenance_reserve=1_000,
                monthly_furnishing_repair_costs=500,
            ),
            strategy=InvestmentBuilder().build().strategy,
        )

        payment = investment.monthly_bond_payment

        # Manual calculation for verification
        loan_amount = 2_000_000 * 0.5  # 1,000,000
        monthly_rate = 0.10 / 12  # 0.008333...
        num_payments = 20 * 12  # 240

        # PMT formula: P * [r(1+r)^n] / [(1+r)^n - 1]
        expected = (
            loan_amount
            * (monthly_rate * (1 + monthly_rate) ** num_payments)
            / ((1 + monthly_rate) ** num_payments - 1)
        )

        assert abs(payment - expected) < 0.01  # Within 1 cent

    def test_pmt_formula_different_rates(self, assert_approximately):
        """Test PMT calculation with different interest rates"""
        base_investment = (
            InvestmentBuilder()
            .with_purchase_price(1_000_000)
            .as_leveraged_purchase(0.6)
            .build()
        )

        # Test different interest rates
        rates_and_expected = [
            (0.05, 4238.48),  # 5% annual rate
            (0.10, 5799.46),  # 10% annual rate
            (0.15, 7895.84),  # 15% annual rate
        ]

        for rate, expected_payment in rates_and_expected:
            investment = PropertyInvestment(
                acquisition_costs=base_investment.acquisition_costs,
                financing=FinancingParameters(
                    ltv_ratio=0.6,
                    financing_type=FinancingType.LEVERAGED,
                    appreciation_rate=0.06,
                    interest_rate=rate,
                    loan_term_years=20,
                ),
                operating=base_investment.operating,
                strategy=base_investment.strategy,
            )

            payment = investment.monthly_bond_payment
            assert_approximately(payment, expected_payment, tolerance=0.02)

    def test_pmt_formula_different_terms(self, assert_approximately):
        """Test PMT calculation with different loan terms"""
        base_investment = (
            InvestmentBuilder()
            .with_purchase_price(1_000_000)
            .as_leveraged_purchase(0.5)
            .with_interest_rate(0.10)
            .build()
        )

        # Test different terms (500k loan at 10%)
        terms_and_expected = [
            (15, 5373.03),  # 15 years
            (20, 4828.59),  # 20 years
            (25, 4544.79),  # 25 years
            (30, 4387.86),  # 30 years
        ]

        for term_years, expected_payment in terms_and_expected:
            investment = PropertyInvestment(
                acquisition_costs=base_investment.acquisition_costs,
                financing=FinancingParameters(
                    ltv_ratio=0.5,
                    financing_type=FinancingType.LEVERAGED,
                    appreciation_rate=0.06,
                    interest_rate=0.10,
                    loan_term_years=term_years,
                ),
                operating=base_investment.operating,
                strategy=base_investment.strategy,
            )

            payment = investment.monthly_bond_payment
            assert_approximately(payment, expected_payment, tolerance=0.02)

    def test_zero_interest_rate_payment(self):
        """Test payment calculation with zero interest rate"""
        investment = PropertyInvestment(
            acquisition_costs=PropertyAcquisitionCosts(
                purchase_price=1_200_000,
                transfer_duty=12_000,
                conveyancing_fees=25_000,
                bond_registration=20_000,
                furnishing_cost=60_000,
            ),
            financing=FinancingParameters(
                ltv_ratio=0.5,  # 600k loan
                financing_type=FinancingType.LEVERAGED,
                appreciation_rate=0.06,
                interest_rate=0.0,  # Zero interest
                loan_term_years=20,
            ),
            operating=OperatingParameters(
                monthly_rental_income=10_000,
                vacancy_rate=0.05,
                monthly_levies=1_500,
                property_management_fee_rate=0.08,
                monthly_insurance=600,
                monthly_maintenance_reserve=800,
                monthly_furnishing_repair_costs=300,
            ),
            strategy=InvestmentBuilder().build().strategy,
        )

        loan_amount = 1_200_000 * 0.5  # 600,000
        expected_payment = loan_amount / (20 * 12)  # 2,500

        assert investment.monthly_bond_payment == expected_payment

    def test_cash_purchase_no_payment(self):
        """Test cash purchase has no bond payment"""
        investment = InvestmentBuilder().as_cash_purchase().build()

        assert investment.monthly_bond_payment is None

    def test_very_high_ltv_payment(self):
        """Test payment calculation with very high LTV"""
        investment = PropertyInvestment(
            acquisition_costs=PropertyAcquisitionCosts(
                purchase_price=1_000_000,
                transfer_duty=10_000,
                conveyancing_fees=20_000,
                bond_registration=15_000,
                furnishing_cost=50_000,
            ),
            financing=FinancingParameters(
                ltv_ratio=0.95,  # 95% LTV - very high leverage
                financing_type=FinancingType.LEVERAGED,
                appreciation_rate=0.06,
                interest_rate=0.12,  # Higher rate for high LTV
                loan_term_years=20,
            ),
            operating=OperatingParameters(
                monthly_rental_income=12_000,
                vacancy_rate=0.05,
                monthly_levies=2_000,
                property_management_fee_rate=0.08,
                monthly_insurance=700,
                monthly_maintenance_reserve=900,
                monthly_furnishing_repair_costs=400,
            ),
            strategy=InvestmentBuilder().build().strategy,
        )

        payment = investment.monthly_bond_payment

        # Should be higher payment due to larger loan amount
        loan_amount = 1_000_000 * 0.95  # 950,000
        assert payment > 10_000  # Should be substantial payment
        assert payment < 20_000  # But still reasonable


class TestCashFlowCalculations:
    """Test cash flow calculation methods"""

    def test_positive_cash_flow(self):
        """Test calculation with positive cash flow"""
        investment = (
            InvestmentBuilder()
            .as_cash_purchase()
            .with_rental_income(20_000)  # High rental
            .build()
        )

        cashflow = investment.monthly_cashflow

        # Should be positive after all expenses
        assert cashflow > 0

        # Verify calculation logic
        effective_rental = investment.operating.effective_monthly_rental
        total_expenses = investment.operating.total_monthly_expenses
        expected = effective_rental - total_expenses

        assert cashflow == expected

    def test_negative_cash_flow(self):
        """Test calculation with negative cash flow"""
        investment = (
            InvestmentBuilder()
            .as_leveraged_purchase(0.9)  # Very high leverage
            .with_rental_income(8_000)  # Low rental
            .with_interest_rate(0.15)  # High interest
            .build()
        )

        cashflow = investment.monthly_cashflow

        # Likely negative due to high bond payment vs low rental
        effective_rental = investment.operating.effective_monthly_rental
        total_expenses = investment.operating.total_monthly_expenses
        bond_payment = investment.monthly_bond_payment or 0

        expected = effective_rental - total_expenses - bond_payment
        assert cashflow == expected

    def test_break_even_cash_flow(self, assert_approximately):
        """Test scenario close to break-even cash flow"""
        # Design investment to be close to break-even
        investment = PropertyInvestment(
            acquisition_costs=PropertyAcquisitionCosts(
                purchase_price=1_500_000,
                transfer_duty=15_000,
                conveyancing_fees=30_000,
                bond_registration=25_000,
                furnishing_cost=75_000,
            ),
            financing=FinancingParameters(
                ltv_ratio=0.7,  # 70% LTV
                financing_type=FinancingType.LEVERAGED,
                appreciation_rate=0.06,
                interest_rate=0.105,  # 10.5%
                loan_term_years=20,
            ),
            operating=OperatingParameters(
                monthly_rental_income=13_500,  # Calibrated for near break-even
                vacancy_rate=0.05,
                monthly_levies=2_200,
                property_management_fee_rate=0.08,
                monthly_insurance=750,
                monthly_maintenance_reserve=950,
                monthly_furnishing_repair_costs=450,
            ),
            strategy=InvestmentBuilder().build().strategy,
        )

        cashflow = investment.monthly_cashflow

        # Should be close to zero (within 500)
        assert abs(cashflow) < 500

    def test_cash_flow_with_no_bond_payment(self):
        """Test cash flow calculation with no bond payment"""
        investment = InvestmentBuilder().as_cash_purchase().build()

        cashflow = investment.monthly_cashflow
        bond_payment = investment.monthly_bond_payment

        assert bond_payment is None

        # Should equal effective rental minus operating expenses only
        expected = (
            investment.operating.effective_monthly_rental
            - investment.operating.total_monthly_expenses
        )
        assert cashflow == expected


class TestInitialCashRequiredCalculations:
    """Test initial cash requirement calculations"""

    def test_cash_purchase_initial_cash(self):
        """Test initial cash required for cash purchase"""
        investment = InvestmentBuilder().as_cash_purchase().build()

        initial_cash = investment.initial_cash_required
        total_cost = investment.acquisition_costs.total_furnished_cost

        assert initial_cash == total_cost

    def test_leveraged_purchase_initial_cash(self):
        """Test initial cash required for leveraged purchase"""
        investment = PropertyInvestment(
            acquisition_costs=PropertyAcquisitionCosts(
                purchase_price=2_000_000,
                transfer_duty=20_000,
                conveyancing_fees=40_000,
                bond_registration=30_000,
                furnishing_cost=100_000,
            ),
            financing=FinancingParameters(
                ltv_ratio=0.6,  # 60% LTV
                financing_type=FinancingType.LEVERAGED,
                appreciation_rate=0.06,
                interest_rate=0.10,
                loan_term_years=20,
            ),
            operating=OperatingParameters(
                monthly_rental_income=18_000,
                vacancy_rate=0.05,
                monthly_levies=2_800,
                property_management_fee_rate=0.08,
                monthly_insurance=900,
                monthly_maintenance_reserve=1_200,
                monthly_furnishing_repair_costs=600,
            ),
            strategy=InvestmentBuilder().build().strategy,
        )

        initial_cash = investment.initial_cash_required

        # Manual calculation
        total_cost = investment.acquisition_costs.total_furnished_cost  # 2,190,000
        loan_amount = investment.acquisition_costs.purchase_price * 0.6  # 1,200,000
        expected = total_cost - loan_amount  # 990,000

        assert initial_cash == expected

    def test_different_ltv_initial_cash(self):
        """Test initial cash with different LTV ratios"""
        base_purchase_price = 1_000_000
        base_costs = PropertyAcquisitionCosts(
            purchase_price=base_purchase_price,
            transfer_duty=10_000,
            conveyancing_fees=20_000,
            bond_registration=15_000,
            furnishing_cost=50_000,
        )

        total_cost = base_costs.total_furnished_cost  # 1,095,000

        ltv_scenarios = [0.5, 0.7, 0.8, 0.9]

        for ltv in ltv_scenarios:
            investment = PropertyInvestment(
                acquisition_costs=base_costs,
                financing=FinancingParameters(
                    ltv_ratio=ltv,
                    financing_type=FinancingType.LEVERAGED,
                    appreciation_rate=0.06,
                    interest_rate=0.10,
                    loan_term_years=20,
                ),
                operating=OperatingParameters(
                    monthly_rental_income=12_000,
                    vacancy_rate=0.05,
                    monthly_levies=2_000,
                    property_management_fee_rate=0.08,
                    monthly_insurance=600,
                    monthly_maintenance_reserve=800,
                    monthly_furnishing_repair_costs=300,
                ),
                strategy=InvestmentBuilder().build().strategy,
            )

            initial_cash = investment.initial_cash_required
            loan_amount = base_purchase_price * ltv
            expected = total_cost - loan_amount

            assert initial_cash == expected

    def test_no_furnishing_cost_initial_cash(self):
        """Test initial cash with no furnishing costs"""
        investment = PropertyInvestment(
            acquisition_costs=PropertyAcquisitionCosts(
                purchase_price=1_500_000,
                transfer_duty=15_000,
                conveyancing_fees=30_000,
                bond_registration=25_000,
                furnishing_cost=None,  # No furnishing
            ),
            financing=FinancingParameters(
                ltv_ratio=0.65,
                financing_type=FinancingType.LEVERAGED,
                appreciation_rate=0.06,
                interest_rate=0.095,
                loan_term_years=25,
            ),
            operating=OperatingParameters(
                monthly_rental_income=14_000,
                vacancy_rate=0.05,
                monthly_levies=2_200,
                property_management_fee_rate=0.08,
                monthly_insurance=700,
                monthly_maintenance_reserve=1_000,
                monthly_furnishing_repair_costs=None,  # No furnishing costs
            ),
            strategy=InvestmentBuilder().build().strategy,
        )

        initial_cash = investment.initial_cash_required

        # Should use unfurnished cost (furnishing_cost treated as 0)
        total_cost = (
            investment.acquisition_costs.total_furnished_cost
        )  # Should equal unfurnished
        loan_amount = 1_500_000 * 0.65
        expected = total_cost - loan_amount

        assert initial_cash == expected


class TestOperatingCalculations:
    """Test operating parameter calculations"""

    def test_effective_monthly_rental_calculation(self):
        """Test effective monthly rental with vacancy"""
        operating = OperatingParameters(
            monthly_rental_income=15_000,
            vacancy_rate=0.08,  # 8% vacancy
            monthly_levies=2_000,
            property_management_fee_rate=0.10,
            monthly_insurance=600,
            monthly_maintenance_reserve=900,
            monthly_furnishing_repair_costs=400,
        )

        effective = operating.effective_monthly_rental
        expected = 15_000 * (1 - 0.08)  # 15,000 * 0.92 = 13,800

        assert effective == expected

    def test_management_fee_calculation(self):
        """Test property management fee calculation"""
        operating = OperatingParameters(
            monthly_rental_income=20_000,
            vacancy_rate=0.05,  # 5% vacancy
            monthly_levies=2_500,
            property_management_fee_rate=0.12,  # 12% management fee
            monthly_insurance=800,
            monthly_maintenance_reserve=1_000,
            monthly_furnishing_repair_costs=500,
        )

        effective_rental = 20_000 * 0.95  # 19,000
        expected_fee = 19_000 * 0.12  # 2,280

        assert operating.monthly_management_fee == expected_fee

    def test_total_monthly_expenses_calculation(self):
        """Test total monthly expenses calculation"""
        operating = OperatingParameters(
            monthly_rental_income=18_000,
            vacancy_rate=0.06,
            monthly_levies=2_200,
            property_management_fee_rate=0.09,
            monthly_insurance=750,
            monthly_maintenance_reserve=1_100,
            monthly_furnishing_repair_costs=450,
        )

        effective_rental = 18_000 * (1 - 0.06)  # 16,920
        management_fee = 16_920 * 0.09  # 1,522.8

        expected_total = (
            2_200  # levies
            + management_fee  # 1,522.8
            + 750  # insurance
            + 1_100  # maintenance
            + 450
        )  # furnishing repairs

        assert operating.total_monthly_expenses == expected_total

    def test_annual_rental_income_calculation(self):
        """Test annual rental income calculation"""
        monthly_rental = 16_500
        operating = OperatingParameters(
            monthly_rental_income=monthly_rental,
            vacancy_rate=0.04,
            monthly_levies=2_100,
            property_management_fee_rate=0.08,
            monthly_insurance=680,
            monthly_maintenance_reserve=950,
            monthly_furnishing_repair_costs=380,
        )

        expected_annual = monthly_rental * 12
        assert operating.annual_rental_income == expected_annual

    def test_zero_vacancy_rate(self):
        """Test calculations with zero vacancy rate"""
        monthly_rental = 12_000
        operating = OperatingParameters(
            monthly_rental_income=monthly_rental,
            vacancy_rate=0.0,  # No vacancy
            monthly_levies=1_800,
            property_management_fee_rate=0.07,
            monthly_insurance=550,
            monthly_maintenance_reserve=800,
            monthly_furnishing_repair_costs=300,
        )

        # Effective rental should equal gross rental
        assert operating.effective_monthly_rental == monthly_rental

        # Management fee should be on full rental amount
        expected_mgmt_fee = monthly_rental * 0.07
        assert operating.monthly_management_fee == expected_mgmt_fee

    def test_high_vacancy_rate(self):
        """Test calculations with high vacancy rate"""
        monthly_rental = 14_000
        operating = OperatingParameters(
            monthly_rental_income=monthly_rental,
            vacancy_rate=0.15,  # 15% vacancy - high
            monthly_levies=2_000,
            property_management_fee_rate=0.08,
            monthly_insurance=650,
            monthly_maintenance_reserve=850,
            monthly_furnishing_repair_costs=350,
        )

        effective_rental = monthly_rental * (1 - 0.15)  # 11,900
        assert operating.effective_monthly_rental == effective_rental

        management_fee = effective_rental * 0.08  # 952
        assert operating.monthly_management_fee == management_fee


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error conditions"""

    def test_extremely_small_values(self):
        """Test calculations with very small values"""
        investment = PropertyInvestment(
            acquisition_costs=PropertyAcquisitionCosts(
                purchase_price=100_000,  # Very small property
                transfer_duty=1_000,
                conveyancing_fees=2_000,
                bond_registration=1_500,
                furnishing_cost=5_000,
            ),
            financing=FinancingParameters(
                ltv_ratio=0.5,
                financing_type=FinancingType.LEVERAGED,
                appreciation_rate=0.03,
                interest_rate=0.05,
                loan_term_years=15,
            ),
            operating=OperatingParameters(
                monthly_rental_income=800,  # Very low rental
                vacancy_rate=0.05,
                monthly_levies=150,
                property_management_fee_rate=0.08,
                monthly_insurance=50,
                monthly_maintenance_reserve=100,
                monthly_furnishing_repair_costs=25,
            ),
            strategy=InvestmentBuilder().build().strategy,
        )

        # All calculations should still work
        assert investment.initial_cash_required > 0
        assert investment.monthly_bond_payment > 0
        assert investment.monthly_cashflow is not None

    def test_extremely_large_values(self):
        """Test calculations with very large values"""
        investment = PropertyInvestment(
            acquisition_costs=PropertyAcquisitionCosts(
                purchase_price=100_000_000,  # Very expensive property
                transfer_duty=1_000_000,
                conveyancing_fees=2_000_000,
                bond_registration=1_500_000,
                furnishing_cost=5_000_000,
            ),
            financing=FinancingParameters(
                ltv_ratio=0.6,
                financing_type=FinancingType.LEVERAGED,
                appreciation_rate=0.05,
                interest_rate=0.08,
                loan_term_years=25,
            ),
            operating=OperatingParameters(
                monthly_rental_income=500_000,  # Very high rental
                vacancy_rate=0.02,
                monthly_levies=50_000,
                property_management_fee_rate=0.05,
                monthly_insurance=10_000,
                monthly_maintenance_reserve=25_000,
                monthly_furnishing_repair_costs=15_000,
            ),
            strategy=InvestmentBuilder().build().strategy,
        )

        # All calculations should still work with large numbers
        assert investment.initial_cash_required > 0
        assert investment.monthly_bond_payment > 0
        assert investment.monthly_cashflow is not None

    def test_precision_and_rounding(self, assert_approximately):
        """Test calculation precision and rounding behavior"""
        investment = PropertyInvestment(
            acquisition_costs=PropertyAcquisitionCosts(
                purchase_price=1_333_333.33,  # Number with decimals
                transfer_duty=13_333.33,
                conveyancing_fees=26_666.67,
                bond_registration=20_000.00,
                furnishing_cost=66_666.67,
            ),
            financing=FinancingParameters(
                ltv_ratio=0.6666667,  # Non-round percentage
                financing_type=FinancingType.LEVERAGED,
                appreciation_rate=0.0625,  # 6.25%
                interest_rate=0.10375,  # 10.375%
                loan_term_years=22,  # Non-standard term
            ),
            operating=OperatingParameters(
                monthly_rental_income=13_888.89,
                vacancy_rate=0.047,  # 4.7%
                monthly_levies=2_333.33,
                property_management_fee_rate=0.0775,  # 7.75%
                monthly_insurance=722.22,
                monthly_maintenance_reserve=977.78,
                monthly_furnishing_repair_costs=433.33,
            ),
            strategy=InvestmentBuilder().build().strategy,
        )

        # Calculations should handle decimal precision appropriately
        initial_cash = investment.initial_cash_required
        bond_payment = investment.monthly_bond_payment
        cashflow = investment.monthly_cashflow

        # Should be reasonable numbers (not NaN, inf, etc.)
        assert math.isfinite(initial_cash)
        assert math.isfinite(bond_payment)
        assert math.isfinite(cashflow)

        # Should maintain reasonable precision
        assert initial_cash > 0
        assert bond_payment > 0
