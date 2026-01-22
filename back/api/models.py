from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class FinancingTypeEnum(str, Enum):
    CASH = "cash"
    LEVERAGED = "leveraged"


class StrategyTypeEnum(str, Enum):
    CASH_ONLY = "cash_only"
    LEVERAGED = "leveraged"
    MIXED = "mixed"


class RefineFrequencyEnum(str, Enum):
    NEVER = "never"
    ANNUALLY = "annually"
    BI_ANNUALLY = "bi_annually"
    QUARTERLY = "quarterly"
    OTHER = "other"


class CapitalInjectionFrequencyEnum(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    FIVE_YEARLY = "five_yearly"
    ONE_TIME = "one_time"


class PropertyRequest(BaseModel):
    purchase_price: float
    transfer_duty: float
    conveyancing_fees: float
    bond_registration: float
    furnishing_cost: Optional[float] = 0.0


class OperatingRequest(BaseModel):
    monthly_rental_income: float
    vacancy_rate: float
    monthly_levies: float
    property_management_fee_rate: float
    monthly_insurance: float
    monthly_maintenance_reserve: float
    monthly_furnishing_repair_costs: Optional[float] = 0.0


class CapitalInjectionRequest(BaseModel):
    amount: float
    frequency: CapitalInjectionFrequencyEnum
    start_period: int = 1
    end_period: Optional[int] = None
    specific_periods: Optional[List[int]] = None


class StrategyRequest(BaseModel):
    name: str
    strategy_type: StrategyTypeEnum
    simulation_months: int
    reinvest_cashflow: bool = True

    # Leveraged strategy parameters
    ltv_ratio: Optional[float] = None
    interest_rate: Optional[float] = None
    loan_term_years: Optional[int] = 20

    # Refinancing parameters
    enable_refinancing: bool = False
    refinance_frequency: RefineFrequencyEnum = RefineFrequencyEnum.NEVER
    custom_refinance_months: Optional[int] = None
    target_refinance_ltv: Optional[float] = None

    # Mixed strategy parameters
    leveraged_property_ratio: Optional[float] = None
    cash_property_ratio: Optional[float] = None
    cash_percentage: Optional[float] = None
    first_property_type: Optional[str] = "cash"


class SimulationRequest(BaseModel):
    property: PropertyRequest
    operating: OperatingRequest
    available_capital: float
    capital_injections: List[CapitalInjectionRequest] = []
    strategies: List[StrategyRequest]
    appreciation_rate: float = 0.06


class PropertyExpenses(BaseModel):
    mortgage_payment: float
    property_taxes: float = 0.0  # Not currently calculated
    insurance: float
    maintenance: float
    management_fees: float
    levies: float
    furnishing_repair_costs: float = 0.0
    total: float


class PropertyCostBasis(BaseModel):
    down_payment: float
    transfer_duty: float
    conveyancing_fees: float
    bond_registration: float
    furnishing_costs: float
    total: float


class PropertyDetail(BaseModel):
    # Basic Property Info
    property_id: int
    purchase_price: float
    current_value: float
    purchase_date: Optional[str] = None  # or month index
    months_owned: int

    # Financing Details
    loan_amount: float
    down_payment: float
    interest_rate: float
    loan_term_months: int
    financing_type: str

    # Mortgage Details
    monthly_mortgage_payment: float
    monthly_principal: float
    monthly_interest: float
    remaining_loan_balance: float
    months_remaining: int
    ltv_ratio: float  # current LTV

    # Income & Expenses Breakdown
    monthly_rental_income: float
    annual_rental_income: float
    monthly_expenses: PropertyExpenses
    annual_expenses: float

    # Cash Flow & Performance
    monthly_cashflow: float
    annual_cashflow: float
    cash_on_cash_return: float
    cap_rate: float

    # Investment Tracking
    cost_basis: PropertyCostBasis
    total_cash_invested: float
    current_equity: float
    equity_growth: float

    # Yield Calculations
    gross_rental_yield: float
    net_rental_yield: float

    # Appreciation Tracking
    appreciation_amount: float
    appreciation_percentage: float

    # Performance Metrics
    roi_percentage: float
    total_return: float


class StrategySummary(BaseModel):
    final_property_count: int
    final_portfolio_value: float
    final_equity: float
    monthly_cashflow: float
    total_cash_invested: float
    initial_available_capital: float
    simulation_ended: bool = False
    end_reason: Optional[str] = None

    # Enhanced financial metrics
    total_debt: float
    monthly_expenses: float  # Now includes mortgage payments
    annual_cashflow: float
    rental_yield: float
    net_rental_yield: float
    cash_on_cash_return: float
    return_on_investment: float
    total_cost_basis: float
    debt_to_equity_ratio: float
    loan_to_value_ratio: float
    total_annual_rental_income: float
    total_annual_expenses: float

    # Comprehensive property details
    properties: List[PropertyDetail] = []


class StrategyResult(BaseModel):
    strategy_name: str
    summary: StrategySummary
    snapshots: List[Dict[str, Any]]
    events: Dict[str, List[Dict[str, Any]]]
    properties: List[PropertyDetail] = []


class SimulationResponse(BaseModel):
    success: bool
    results: List[StrategyResult]
    error: Optional[str] = None


class StrategyPreset(BaseModel):
    name: str
    description: str
    strategy_type: StrategyTypeEnum
    config: Dict[str, Any]


class ValidationResponse(BaseModel):
    valid: bool
    errors: List[str] = []


class HealthResponse(BaseModel):
    status: str
    service: str
