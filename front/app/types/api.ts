export interface PropertyRequest {
  purchase_price: number;
  transfer_duty: number;
  conveyancing_fees: number;
  bond_registration: number;
  furnishing_cost?: number;
}

export interface OperatingRequest {
  monthly_rental_income: number;
  vacancy_rate: number;
  monthly_levies: number;
  property_management_fee_rate: number;
  monthly_insurance: number;
  monthly_maintenance_reserve: number;
  monthly_furnishing_repair_costs?: number;
}

export type CapitalInjectionFrequency =
  | "monthly"
  | "quarterly"
  | "yearly"
  | "five_yearly"
  | "one_time";

export interface CapitalInjectionRequest {
  amount?: number;
  frequency: CapitalInjectionFrequency;
  start_period: number;
  end_period?: number;
  specific_periods?: number[];
}

export type StrategyType = "cash_only" | "leveraged" | "mixed";
export type RefineFrequency =
  | "never"
  | "annually"
  | "bi_annually"
  | "quarterly"
  | "other";

export interface StrategyRequest {
  name: string;
  strategy_type: StrategyType;
  simulation_months: number;
  reinvest_cashflow: boolean;

  // Leveraged strategy parameters
  ltv_ratio?: number;
  interest_rate?: number;
  loan_term_years?: number;
  appreciation_rate?: number;

  // Refinancing parameters
  enable_refinancing: boolean;
  refinance_frequency: RefineFrequency;
  custom_refinance_months?: number;
  target_refinance_ltv?: number;

  // Mixed strategy parameters
  leveraged_property_ratio?: number;
  cash_property_ratio?: number;
  first_property_type?: "cash" | "leveraged";
}

export interface SimulationRequest {
  property: PropertyRequest;
  operating: OperatingRequest;
  available_capital: number;
  capital_injections: CapitalInjectionRequest[];
  strategies: StrategyRequest[];
}

export interface StrategySummary {
  final_property_count: number;
  final_portfolio_value: number;
  final_equity: number;
  monthly_cashflow: number;
  total_cash_invested: number;
  simulation_ended: boolean;
  end_reason?: string;

  // Enhanced financial metrics
  total_debt: number;
  monthly_expenses: number;
  annual_cashflow: number;
  rental_yield: number;
  net_rental_yield: number;
  cash_on_cash_return: number;
  return_on_investment: number;
  total_cost_basis: number;
  debt_to_equity_ratio: number;
  loan_to_value_ratio: number;
  total_annual_rental_income: number;
  total_annual_expenses: number;
}

export interface PropertyData {
  property_id: number;
  purchase_price: number;
  current_value: number;
  loan_amount: number;
  monthly_payment: number;
  financing_type: string;
  months_owned: number;
  annual_rental_income: number;
  annual_expenses: number;
  monthly_cashflow: number;
  cost_basis: number;
}

export interface PropertyYields {
  property_id: number;
  rental_yield: number;
  net_rental_yield: number;
  cash_on_cash_return: number;
  total_return_yield: number;
  capital_growth_yield: number;
}

export interface PortfolioYields {
  portfolio_rental_yield: number;
  portfolio_net_rental_yield: number;
  portfolio_cash_on_cash_return: number;
  portfolio_capital_growth_yield: number;
  portfolio_total_return_yield: number;
}

export interface StrategyResult {
  strategy_name: string;
  summary: StrategySummary;
  snapshots: Array<{
    period: number;
    total_property_value: number;
    total_debt: number;
    total_equity: number;
    monthly_cashflow: number;
    annual_cashflow: number;
    cash_available: number;
    property_count: number;
    total_cash_invested: number;
    monthly_expenses: number;
    total_annual_rental_income: number;
    total_annual_expenses: number;
    rental_yield: number;
    net_rental_yield: number;
    cash_on_cash_return: number;
    return_on_investment: number;
    total_cost_basis: number;
    debt_to_equity_ratio: number;
    loan_to_value_ratio: number;
    portfolio_yields?: PortfolioYields;
    properties: PropertyData[];
    property_yields: PropertyYields[];
  }>;
  events: {
    property_purchases: Array<{
      property_id: number;
      purchase_price: number;
      financing_type: string;
      cash_required: number;
      loan_amount: number;
    }>;
    refinancing_events: Array<{
      property_id: number;
      cash_extracted: number;
      new_loan_amount: number;
      old_loan_amount: number;
      new_ltv: number;
    }>;
    capital_injections: Array<{
      amount: number;
      source: string;
      total_additional_capital_to_date: number;
    }>;
  };
}

export interface SimulationResponse {
  success: boolean;
  results: StrategyResult[];
  error?: string;
}

export interface StrategyPreset {
  name: string;
  description: string;
  strategy_type: StrategyType;
  config: Partial<StrategyRequest>;
}

export interface ValidationResponse {
  valid: boolean;
  errors: string[];
}
