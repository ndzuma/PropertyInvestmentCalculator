# Property Investment Calculator - Backend API

This is the backend service for the Property Investment Calculator, providing a FastAPI-based REST API for property investment simulations and strategy comparisons.

## Quick Start

### 1. Start the API Server
```bash
cd back
python run_api.py
```

The API will be available at:
- **API Server**: http://localhost:8001
- **Interactive Docs**: http://localhost:8001/docs  
- **API Documentation**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/health

### 2. Test the API

**Option 1: Using the interactive docs**
- Go to http://localhost:8001/docs
- Try the POST /simulate endpoint with the test JSON files

**Option 2: Using curl**
```bash
# Quick test
curl -X POST "http://localhost:8001/simulate" \
  -H "Content-Type: application/json" \
  -d @api/simple_test.json

# Comprehensive test
curl -X POST "http://localhost:8001/simulate" \
  -H "Content-Type: application/json" \
  -d @api/test_request.json
```

## API Endpoints

### Core Endpoints

- **POST /simulate** - Run property investment simulations
- **GET /strategy-presets** - Get predefined strategy configurations
- **POST /validate** - Validate parameters without running simulation
- **GET /health** - Health check

### Test Files

- `api/simple_test.json` - Basic 2-strategy comparison
- `api/test_request.json` - Comprehensive 5-strategy test with capital injections

## Project Structure

```
back/
├── api/                    # FastAPI service layer
│   ├── server.py          # Main FastAPI app
│   ├── models.py          # Pydantic request/response models  
│   ├── endpoints.py       # API endpoint handlers
│   ├── presets.py         # Pre-configured strategies
│   ├── test_api.py        # API integration tests
│   ├── simple_test.json   # Basic test request
│   └── test_request.json  # Comprehensive test request
├── core/                  # Business logic engine
│   ├── main.py           # Property investment classes
│   ├── strategies.py     # Simulation engine
│   └── reports.py        # Reporting functionality
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── conftest.py       # Test configuration
├── examples/             # Usage examples
└── run_api.py           # API server launcher
```

## API Usage

### Simulation Request Format

```json
{
  "property": {
    "purchase_price": 1000000,
    "transfer_duty": 10000,
    "conveyancing_fees": 15000,
    "bond_registration": 0,
    "furnishing_cost": 50000
  },
  "operating": {
    "monthly_rental_income": 12000,
    "vacancy_rate": 0.05,
    "monthly_levies": 1500,
    "property_management_fee_rate": 0.08,
    "monthly_insurance": 600,
    "monthly_maintenance_reserve": 800
  },
  "available_capital": 400000,
  "capital_injections": [
    {
      "amount": 5000,
      "frequency": "monthly",
      "start_period": 1,
      "end_period": 36
    }
  ],
  "strategies": [
    {
      "name": "Cash Strategy",
      "strategy_type": "cash_only",
      "simulation_years": 5,
      "reinvest_cashflow": true
    },
    {
      "name": "Leverage Strategy", 
      "strategy_type": "leveraged",
      "ltv_ratio": 0.7,
      "interest_rate": 0.10,
      "simulation_years": 5,
      "enable_refinancing": true
    }
  ]
}
```

### Response Format

```json
{
  "success": true,
  "results": [
    {
      "strategy_name": "Cash Strategy",
      "summary": {
        "final_property_count": 2,
        "final_portfolio_value": 3200000,
        "final_equity": 3200000,
        "monthly_cashflow": 1800
      },
      "snapshots": [...],
      "events": {
        "property_purchases": [...],
        "refinancing_events": [...],
        "capital_injections": [...]
      }
    }
  ]
}
```

## Strategy Types

### 1. Cash Only
```json
{
  "name": "Conservative Cash",
  "strategy_type": "cash_only",
  "simulation_years": 10,
  "reinvest_cashflow": true
}
```

### 2. Leveraged
```json
{
  "name": "Moderate Leverage",
  "strategy_type": "leveraged", 
  "ltv_ratio": 0.6,
  "interest_rate": 0.10,
  "loan_term_years": 20,
  "enable_refinancing": true,
  "refinance_frequency": "annually",
  "target_refinance_ltv": 0.5
}
```

### 3. Mixed Portfolio
```json
{
  "name": "Balanced Mixed",
  "strategy_type": "mixed",
  "leveraged_property_ratio": 0.6,
  "cash_property_ratio": 0.4,
  "ltv_ratio": 0.7,
  "interest_rate": 0.10,
  "first_property_type": "cash"
}
```

## Capital Injections

Support for multiple capital injection types:

```json
"capital_injections": [
  {
    "amount": 5000,
    "frequency": "monthly",
    "start_period": 1,
    "end_period": 60
  },
  {
    "amount": 50000,
    "frequency": "yearly", 
    "start_period": 12
  },
  {
    "amount": 100000,
    "frequency": "one_time",
    "specific_periods": [24, 48]
  }
]
```

## Testing

### Run API Tests
```bash
cd back
python api/test_api.py
```

### Run Unit Tests
```bash
cd back
python run_unit_tests.py

# Or with pytest
pytest tests/
```

## Dependencies

The API requires:
- FastAPI
- Pydantic 
- Uvicorn

All dependencies should already be available in your environment.

## Development

### Adding New Strategy Presets
Edit `api/presets.py` to add new predefined strategies.

### Extending API Models
Modify `api/models.py` to add new request/response fields.

### Adding New Endpoints
1. Add route to `api/server.py`
2. Add handler to `api/endpoints.py` 
3. Add models to `api/models.py` if needed

### Error Handling
The API includes comprehensive error handling and validation. Check the logs for debugging information.

## Production Notes

- Configure CORS settings in `api/server.py` for production
- Update host/port settings in `run_api.py`
- Consider using environment variables for configuration
- Add proper logging configuration
- Set up proper database if persistent storage is needed

This backend API provides a complete property investment simulation service that can power interactive web frontends, mobile apps, or other client applications.