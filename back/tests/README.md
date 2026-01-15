# Property Investment Calculator Test Suite

This test suite provides comprehensive testing for the Property Investment Calculator application using pytest. The tests are organized for easy maintenance, extension, and execution.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest fixtures and configuration
├── test_fixtures.py            # Test data builders and utilities
├── unit/                       # Unit tests (single component)
│   ├── __init__.py
│   ├── test_dataclasses.py   # PropertyInvestment, costs, parameters
│   ├── test_calculations.py   # Financial calculations (PMT, yields, etc.)
│   ├── test_strategies.py     # Strategy creation and logic
│   ├── test_simulation.py     # Portfolio simulator core
│   └── test_yields.py         # Property and portfolio yields
├── integration/                # Integration tests (multiple components)
│   ├── __init__.py
│   ├── test_full_simulation.py # End-to-end simulation tests
│   ├── test_strategy_comparison.py # Strategy comparison tests
│   └── test_capital_injection.py # Capital injection scenarios
└── performance/                # Performance and stress tests
    ├── __init__.py
    └── test_simulation_speed.py # Performance benchmarks
```

## Running Tests

### Install Dependencies
```bash
pip install pytest pytest-mock pytest-benchmark
```

### Run All Tests
```bash
# From the PropertyInvestmentCalculator directory
pytest tests/

# With verbose output
pytest tests/ -v

# With coverage report
pytest tests/ --cov=. --cov-report=html
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Performance tests only
pytest tests/performance/

# Specific test file
pytest tests/unit/test_calculations.py

# Specific test function
pytest tests/unit/test_calculations.py::test_monthly_payment_calculation
```

### Run Tests by Markers
```bash
# Run only fast tests (exclude slow ones)
pytest tests/ -m "not slow"

# Run only integration tests
pytest tests/ -m integration

# Run only performance tests
pytest tests/ -m performance
```

## Writing Tests

### Using Test Fixtures

The test suite provides powerful fixtures and builders to make test creation easy:

```python
# tests/unit/test_example.py
import pytest
from tests.test_fixtures import InvestmentBuilder, StrategyConfigBuilder

def test_cash_investment_calculation():
    # Simple usage with defaults
    investment = InvestmentBuilder().as_cash_purchase().build()
    
    assert investment.financing.financing_type == FinancingType.CASH
    assert investment.initial_cash_required > 0

def test_leveraged_investment_with_custom_values():
    # Customized investment
    investment = (InvestmentBuilder()
                  .with_purchase_price(2_000_000)
                  .with_leverage(0.8)
                  .with_rental_income(20_000)
                  .build())
    
    assert investment.acquisition_costs.purchase_price == 2_000_000
    assert investment.financing.ltv_ratio == 0.8
    assert investment.operating.monthly_rental_income == 20_000

def test_with_fixtures(default_investment_fixture, cash_strategy_fixture):
    # Using pytest fixtures (automatically injected)
    simulator = PropertyPortfolioSimulator(default_investment_fixture, cash_strategy_fixture)
    snapshots = simulator.simulate()
    
    assert len(snapshots) > 0
```

### Builder Pattern Examples

#### Investment Builder
```python
from tests.test_fixtures import InvestmentBuilder

# Basic scenarios
cash_investment = InvestmentBuilder().as_cash_purchase().build()
leveraged_investment = InvestmentBuilder().as_leveraged_purchase(0.7).build()

# Custom configurations
high_yield = (InvestmentBuilder()
              .with_purchase_price(1_500_000)
              .with_rental_income(18_000)
              .with_leverage(0.6)
              .build())

# Strategy variations
conservative = InvestmentBuilder().as_conservative_strategy().build()
aggressive = InvestmentBuilder().as_aggressive_strategy().build()
```

#### Strategy Builder
```python
from tests.test_fixtures import StrategyConfigBuilder

# Basic strategies
cash_strategy = StrategyConfigBuilder().as_cash_only().build()
leveraged_strategy = StrategyConfigBuilder().as_leveraged_only(0.8).build()
mixed_strategy = StrategyConfigBuilder().as_mixed_strategy(0.6).build()

# With capital injections
strategy_with_injections = (StrategyConfigBuilder()
                           .as_mixed_strategy()
                           .with_capital_injections([monthly_injection(50_000)])
                           .with_simulation_years(10)
                           .build())
```

#### Capital Injection Builder
```python
from tests.test_fixtures import CapitalInjectionBuilder

# Different injection types
monthly = CapitalInjectionBuilder().monthly(50_000).build()
quarterly = CapitalInjectionBuilder().quarterly(200_000).build()
one_time = CapitalInjectionBuilder().one_time(500_000, period=3).build()

# Time-limited injections
limited = (CapitalInjectionBuilder()
           .quarterly(100_000)
           .for_periods(start=1, end=24)
           .build())
```

### Test Categories and Best Practices

#### Unit Tests (`tests/unit/`)
- Test individual components in isolation
- Use mocks for dependencies
- Fast execution (< 1 second per test)
- Focus on edge cases and error conditions

```python
def test_monthly_payment_calculation():
    """Test PMT formula calculation"""
    investment = (InvestmentBuilder()
                  .with_purchase_price(1_000_000)
                  .with_leverage(0.5)
                  .with_interest_rate(0.10)
                  .build())
    
    payment = investment.monthly_bond_payment
    assert payment is not None
    assert 4000 < payment < 5000  # Reasonable range check
```

#### Integration Tests (`tests/integration/`)
- Test component interactions
- Use real implementations
- Test realistic workflows
- Verify end-to-end scenarios

```python
def test_full_simulation_with_refinancing():
    """Test complete simulation with refinancing events"""
    investment = InvestmentBuilder().as_aggressive_strategy().build()
    strategy = StrategyConfigBuilder().as_leveraged_only().build()
    
    simulator = PropertyPortfolioSimulator(investment, strategy)
    snapshots = simulator.simulate()
    
    # Verify refinancing occurred
    refinancing_events = [s for s in snapshots if s.refinancing_events]
    assert len(refinancing_events) > 0
```

#### Performance Tests (`tests/performance/`)
- Measure execution time
- Test with large datasets
- Memory usage validation
- Regression detection

```python
@pytest.mark.performance
def test_large_portfolio_simulation_speed(performance_timer):
    """Test simulation performance with large portfolio"""
    investment = InvestmentBuilder().with_investment_amount(100_000_000).build()
    strategy = StrategyConfigBuilder().with_simulation_years(20).build()
    
    with performance_timer() as timer:
        simulator = PropertyPortfolioSimulator(investment, strategy)
        snapshots = simulator.simulate()
    
    assert timer.elapsed < 10.0  # Should complete within 10 seconds
    assert len(snapshots) > 0
```

## Adding New Tests

### 1. Choose the Right Category
- **Unit tests**: Testing individual functions/classes
- **Integration tests**: Testing component interactions
- **Performance tests**: Testing speed/memory usage

### 2. Use Existing Patterns
```python
# Follow this naming convention
def test_[component]_[specific_behavior]():
    # Arrange
    investment = InvestmentBuilder().with_custom_config().build()
    
    # Act
    result = investment.some_calculation()
    
    # Assert
    assert result.is_valid()
    assert result.value > expected_minimum
```

### 3. Leverage Test Fixtures
```python
# Use builders for complex objects
def test_complex_scenario():
    investment = (InvestmentBuilder()
                  .with_purchase_price(2_000_000)
                  .as_leveraged_purchase(0.8)
                  .build())
    
    # Use fixtures for common scenarios
    def test_with_common_data(default_investment_fixture):
        # Test logic here
        pass
```

### 4. Add Appropriate Markers
```python
@pytest.mark.slow
def test_time_consuming_operation():
    # Long-running test
    pass

@pytest.mark.performance
def test_performance_benchmark():
    # Performance test
    pass
```

## Test Utilities

### Assertion Helpers
```python
def test_with_approximate_assertions(assert_approximately):
    result = calculate_yield(investment)
    assert_approximately(result, 0.0875, tolerance=0.001)  # 8.75% ± 0.1%
```

### Snapshot Validation
```python
def test_snapshot_consistency(snapshot_validator):
    snapshots = simulator.simulate()
    
    for snapshot in snapshots:
        snapshot_validator.validate_snapshot_consistency(snapshot)
        
        if snapshot.property_yields:
            for yields in snapshot.property_yields:
                snapshot_validator.validate_yield_ranges(yields)
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v3
```

## Tips for Effective Testing

1. **Start with happy path tests**, then add edge cases
2. **Use descriptive test names** that explain the scenario
3. **Keep tests independent** - each test should be able to run alone
4. **Use builders** instead of creating objects manually
5. **Test behavior, not implementation** - focus on outputs, not internal logic
6. **Add performance tests** for complex calculations
7. **Use fixtures** to avoid code duplication
8. **Run tests frequently** during development

## Debugging Failed Tests

### Verbose Output
```bash
pytest tests/unit/test_calculations.py::test_failing_case -v -s
```

### Debug with PDB
```python
def test_debug_example():
    investment = InvestmentBuilder().build()
    import pdb; pdb.set_trace()  # Debugger will start here
    result = investment.some_calculation()
    assert result.is_valid()
```

### Capture Output
```bash
pytest tests/ --capture=no  # Show print statements
```

This test structure provides a solid foundation for maintaining and expanding test coverage as the Property Investment Calculator grows in complexity.