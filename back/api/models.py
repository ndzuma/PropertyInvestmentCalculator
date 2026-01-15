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
    simulation_months: int = 120  # Default 10 years = 120 months
    reinvest_cashflow: bool = True

    # Leveraged strategy parameters
    ltv_ratio: Optional[float] = None
    interest_rate: Optional[float] = None
    loan_term_years: Optional[int] = 20
    appreciation_rate: Optional[float] = 0.06

    # Refinancing parameters
    enable_refinancing: bool = False
    refinance_frequency: RefineFrequencyEnum = RefineFrequencyEnum.NEVER
    target_refinance_ltv: Optional[float] = None

    # Mixed strategy parameters
    leveraged_property_ratio: Optional[float] = None
    cash_property_ratio: Optional[float] = None
    first_property_type: Optional[str] = "cash"


class SimulationRequest(BaseModel):
    property: PropertyRequest
    operating: OperatingRequest
    available_capital: float
    capital_injections: List[CapitalInjectionRequest] = []
    strategies: List[StrategyRequest]


class StrategySummary(BaseModel):
    final_property_count: int
    final_portfolio_value: float
    final_equity: float
    monthly_cashflow: float
    total_cash_invested: float
    simulation_ended: bool = False
    end_reason: Optional[str] = None


class StrategyResult(BaseModel):
    strategy_name: str
    summary: StrategySummary
    snapshots: List[Dict[str, Any]]
    events: Dict[str, List[Dict[str, Any]]]


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
