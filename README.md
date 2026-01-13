# Property Investment Calculator

A comprehensive Python-based property investment simulator that models acquisition costs, financing options, operating expenses, cash flow, reinvestment strategies, refinancing, and capital injections over time.

## Features

### Core Functionality
- **Property Acquisition Modeling**: Purchase price, transfer duties, conveyancing fees, bond registration, furnishing costs
- **Flexible Financing**: Cash purchases, leveraged purchases with configurable LTV ratios
- **Operating Expenses**: Rental income, vacancy rates, levies, management fees, insurance, maintenance
- **Cash Flow Analysis**: Monthly and annual cash flow calculations with detailed breakdowns
- **Portfolio Growth**: Automatic reinvestment and property acquisition based on available cash

### Advanced Features
- **Refinancing Simulation**: Periodic refinancing with cash extraction based on property appreciation
- **Capital Injections**: Monthly, quarterly, yearly, or one-time additional capital contributions
- **Mixed Strategies**: Combine cash and leveraged properties in configurable ratios
- **Yield Calculations**: Rental yield, net rental yield, cash-on-cash return, total return yield
- **Detailed Tracking**: Property-level data, refinancing events, purchase history, capital injection tracking

### Simulation Options
- **Strategy Types**: Cash-only, leveraged-only, or mixed portfolios
- **Tracking Frequency**: Monthly or yearly snapshots
- **Time Horizons**: Configurable simulation periods (1-50+ years)
- **Scenario Comparison**: Compare multiple strategies side-by-side

## Quick Start

### Basic Example

```python
from main import (
    PropertyAcquisitionCosts, FinancingParameters, OperatingParameters,
    InvestmentStrategy, PropertyInvestment, FinancingType, RefineFrequency
)
from strategies import PropertyPortfolioSimulator, create_leveraged_strategy

# Define property costs
acquisition = PropertyAcquisitionCosts(
    purchase_price=1_000_000,
    transfer_duty=10_000,
    conveyancing_fees=15_000,
    bond_registration=15_000,
    furnishing_cost=50_000,
)

# Define financing
financing = FinancingParameters(
    ltv_ratio=0.8,  # 80% loan-to-value
    financing_type=FinancingType.LEVERAGED,
    appreciation_rate=0.06,  # 6% annual appreciation
    interest_rate=0.10,  # 10% interest rate
    loan_term_years=20,
)

# Define operating parameters
operating = OperatingParameters(
    monthly_rental_income=12_000,
    vacancy_rate=0.05,  # 5% vacancy
    monthly_levies=1_500,
    property_management_fee_rate=0.08,  # 8% of rental income
    monthly_insurance=600,
    monthly_maintenance_reserve=800,
    monthly_furnishing_repair_costs=300,
)

# Define investment strategy
strategy = InvestmentStrategy(
    available_investment_amount=500_000,
    reinvest_cashflow=True,
    enable_refinancing=True,
    refinance_frequency=RefineFrequency.ANNUALLY,
    target_refinance_ltv=0.6,  # Refinance to 60% LTV
)

# Create property investment
property_investment = PropertyInvestment(acquisition, financing, operating, strategy)

# Create and run simulation
strategy_config = create_leveraged_strategy(
    leverage_ratio=0.8,
    refinancing=True,
    refinance_years=1.0,
    reinvestment=True,
    years=10
)

simulator = PropertyPortfolioSimulator(property_investment, strategy_config)
snapshots = simulator.simulate()

# Analyze results
final_snapshot = snapshots[-1]
print(f"Final properties: {len(final_snapshot.properties)}")
print(f"Portfolio value: R{final_snapshot.total_property_value:,.0f}")
print(f"Total equity: R{final_snapshot.total_equity:,.0f}")
print(f"Monthly cash flow: R{final_snapshot.monthly_cashflow:,.0f}")
```

## Simulation Behavior

The simulator runs with monthly internal calculations for accurate handling of:
- Monthly/quarterly injections and their timing
- Loan amortization and monthly bond payments  
- Cash flow deficits and early termination
- Refinancing checks (which rely on monthly accruals)

For yearly tracking frequency, the simulator samples snapshots annually while maintaining monthly precision internally.

## Yield Calculations

The simulator automatically calculates four key yield metrics annually:

### 1. Rental Yield
```
Rental Yield = Annual Rental Income / Current Property Value
```
Shows the gross return from rental income relative to property value.

### 2. Net Rental Yield  
```
Net Rental Yield = (Annual Rental Income - Operating Expenses) / Current Property Value
```
Shows the net return after operating expenses but before debt service.

### 3. Cash-on-Cash Return
```
Cash-on-Cash Return = Annual Net Cash Flow / Cash Invested
```
Shows the actual cash return on the money you invested (including debt service).

### 4. Total Return Yield
```
Total Return Yield = Net Rental Yield + Capital Growth Yield
```
Combines rental returns with capital appreciation for total investment performance.

## Capital Injections

Add additional capital throughout the simulation:

```python
from strategies import AdditionalCapitalInjection, AdditionalCapitalFrequency

# Monthly savings
monthly_injection = AdditionalCapitalInjection(
    amount=25_000,
    frequency=AdditionalCapitalFrequency.MONTHLY,
    start_period=1,
    end_period=60,  # 5 years
)

# Annual bonus
annual_bonus = AdditionalCapitalInjection(
    amount=150_000,
    frequency=AdditionalCapitalFrequency.YEARLY,
    start_period=1,
)

# One-time inheritance
inheritance = AdditionalCapitalInjection(
    amount=500_000,
    frequency=AdditionalCapitalFrequency.ONE_TIME,
    specific_periods=[3],  # Year 3
)

strategy_config = create_leveraged_strategy(
    additional_capital_injections=[monthly_injection, annual_bonus, inheritance]
)
```

## Mixed Strategies

Combine cash and leveraged properties in your portfolio:

```python
from strategies import create_mixed_strategy, FirstPropertyType

strategy_config = create_mixed_strategy(
    leveraged_property_ratio=0.7,  # 70% of properties leveraged
    cash_property_ratio=0.3,       # 30% cash purchases
    leverage_ratio=0.6,             # 60% LTV when leveraged
    first_property_type=FirstPropertyType.LEVERAGED,
    refinancing=True,
    reinvestment=True,
    years=10
)
```

## Data Access and Analysis

The simulator provides detailed data for analysis and charting:

```python
# Extract data from snapshots
periods = [snap.period for snap in snapshots]
property_counts = [len(snap.properties) for snap in snapshots]
portfolio_values = [snap.total_property_value for snap in snapshots]
equity_values = [snap.total_equity for snap in snapshots]
cash_flows = [snap.monthly_cashflow for snap in snapshots]

# Access individual property data
for snapshot in snapshots:
    for prop in snapshot.properties:
        print(f"Property {prop.property_id}: Value R{prop.current_value:,.0f}, "
              f"Loan R{prop.loan_amount:,.0f}, Type: {prop.financing_type}")

# Access refinancing events
for snapshot in snapshots:
    for event in snapshot.refinancing_events:
        print(f"Property {event.property_id} refinanced: "
              f"Extracted R{event.cash_extracted:,.0f}")

# Access yield data
for snapshot in snapshots:
    if snapshot.property_yields:
        for yields in snapshot.property_yields:
            print(f"Property {yields.property_id} yields:")
            print(f"  Rental Yield: {yields.rental_yield:.2%}")
            print(f"  Net Rental Yield: {yields.net_rental_yield:.2%}")
            print(f"  Cash-on-Cash: {yields.cash_on_cash_return:.2%}")
            print(f"  Total Return: {yields.total_return_yield:.2%}")
```

## File Structure

```
PropertyInvestmentCalculator/
├── main.py                         # Core data classes and property definitions
├── strategies.py                   # Simulation engine and strategy configurations
├── reports.py                     # Reporting and output formatting
├── test_basic.py                  # Basic functionality tests
├── test_portfolio_yields.py       # Portfolio yield calculation tests
├── run_unit_tests.py              # Test runner script
├── tests/                         # Comprehensive test suite
│   ├── unit/                      # Unit tests for individual components
│   ├── integration/               # Integration tests for full workflows
│   ├── conftest.py               # Test configuration and fixtures
│   └── README.md                 # Testing documentation
├── examples/                      # Example scripts and use cases
│   ├── example_data_access.py    # Data extraction examples
│   ├── capital_injection_example.py # Capital injection scenarios
│   ├── mixed_strategy_example.py # Mixed financing strategies
│   └── yield_example.py          # Yield calculation examples
└── README.md                     # This file
```

## Core Classes

### PropertyAcquisitionCosts
- `purchase_price`: Property purchase price
- `transfer_duty`: Transfer duty fees
- `conveyancing_fees`: Legal fees
- `bond_registration`: Bond registration costs
- `furnishing_cost`: Optional furnishing costs

### FinancingParameters
- `ltv_ratio`: Loan-to-value ratio (0.0 to 1.0)
- `financing_type`: CASH or LEVERAGED
- `appreciation_rate`: Annual property appreciation rate
- `interest_rate`: Bond interest rate (for leveraged purchases)
- `loan_term_years`: Loan term in years

### OperatingParameters
- `monthly_rental_income`: Gross monthly rental income
- `vacancy_rate`: Vacancy rate as percentage
- `monthly_levies`: Monthly levy payments
- `property_management_fee_rate`: Management fee as percentage of rental income
- `monthly_insurance`: Monthly insurance costs
- `monthly_maintenance_reserve`: Monthly maintenance reserve
- `monthly_furnishing_repair_costs`: Monthly furnishing/repair costs

### InvestmentStrategy
- `available_investment_amount`: Initial investment capital
- `reinvest_cashflow`: Whether to reinvest positive cash flow
- `enable_refinancing`: Whether to enable periodic refinancing
- `refinance_frequency`: How often to refinance
- `target_refinance_ltv`: LTV ratio to refinance to

## Strategy Types

### Cash-Only Strategy
```python
strategy = create_cash_strategy(
    reinvestment=True,
    tracking=TrackingFrequency.YEARLY,
    years=10
)
```

### Leveraged Strategy  
```python
strategy = create_leveraged_strategy(
    leverage_ratio=0.8,     # 80% LTV
    refinancing=True,
    refinance_years=2.0,    # Refinance every 2 years
    reinvestment=True,
    years=10
)
```

### Mixed Strategy
```python
strategy = create_mixed_strategy(
    leveraged_property_ratio=0.6,  # 60% leveraged properties
    cash_property_ratio=0.4,       # 40% cash properties  
    leverage_ratio=0.7,             # 70% LTV when leveraged
    first_property_type=FirstPropertyType.CASH,
    refinancing=True,
    years=10
)
```

## Example Outputs

### Basic Simulation Results
```
Final properties: 3
Portfolio value: R5,432,100
Total equity: R3,124,500
Monthly cash flow: R2,150
Net worth: R3,245,600
```

### Yield Analysis (Annual)
```
Property 0 yields:
  Rental Yield: 12.50%
  Net Rental Yield: 8.75%
  Cash-on-Cash: 4.20%
  Total Return: 14.75%

Property 1 yields:
  Rental Yield: 11.80%
  Net Rental Yield: 8.25%
  Cash-on-Cash: 3.85%
  Total Return: 14.25%
```

### Capital Injection Impact
```
Year 0: R0 injected, 1 property, R1,200,000 portfolio
Year 1: R100,000 injected, 2 properties, R2,650,000 portfolio  
Year 2: R100,000 injected, 3 properties, R4,250,000 portfolio
Year 3: R500,000 injected, 5 properties, R7,100,000 portfolio
```

## Installation and Setup

1. Clone or download the repository
2. Ensure Python 3.7+ is installed
3. Install dependencies: `pip install -r requirements.txt`
4. Run examples: `python examples/example_data_access.py`

## Testing

Run the basic test suite:
```bash
# Basic tests
python test_basic.py

# Portfolio yield tests  
python test_portfolio_yields.py

# All unit tests
python run_unit_tests.py

# Full test suite (requires pytest)
pytest tests/
```

This will test:
- Property calculation methods
- Cash and leveraged strategies
- Yield calculations
- Simulation functionality
- Integration scenarios

### Test Structure
- **Unit tests**: Test individual components and functions
- **Integration tests**: Test complete simulation workflows
- Tests include scenarios for cash deficits, early termination, and edge cases
- All tests run with monthly internal precision for accuracy

## Contributing

The codebase is modular and extensible. Key areas for enhancement:

1. **Tax Modeling**: Add tax calculations for rental income and capital gains
2. **Advanced Amortization**: Replace simplified principal payments with full amortization schedules
3. **Transaction Costs**: Add variable transfer duty based on price bands
4. **Risk Modeling**: Add vacancy impact and market volatility
5. **Visualization**: Add charting capabilities for results analysis
6. **Configuration Files**: Support YAML/JSON configuration instead of code-based setup

## License

This project is provided as-is for educational and analytical purposes.