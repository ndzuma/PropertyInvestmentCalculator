# Backend API - Property Investment Calculator

FastAPI backend service for property investment simulations and strategy comparisons with production-ready safety features.

## Quick Start

```bash
cd back
pip install -r requirements.txt
python run_api.py
```

API available at:
- **Server**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

## Configuration

Copy `.env.example` to `.env` and adjust settings:

```bash
PORT=8000
HOSTURL=127.0.0.1  # Use 0.0.0.0 for deployment
RELOAD=true
CORS_ORIGINS=*
```

## API Endpoints

- `POST /simulate` - Run property investment simulations (rate limited: 10/min)
- `GET /strategy-presets` - Get predefined strategies (100/min)
- `POST /validate` - Validate simulation parameters (100/min)
- `GET /health` - Health check endpoint

## Safety Features

### 🛡️ Production Protections
- **Timeout Protection**: 5-second timeout per strategy simulation
- **Rate Limiting**: 10 simulations/minute, 100 other requests/minute
- **Validation**: Comprehensive input validation with detailed error messages
- **Error Handling**: Graceful failures with meaningful HTTP status codes

### 🌍 Country-Specific Support
- **Localized Settings**: South Africa and UK market configurations
- **Investment Rules**: LTV restrictions for international investors
- **Currency Support**: ZAR and GBP with appropriate rate structures

## Example Request

```json
{
  "property": {
    "purchase_price": 1000000,
    "transfer_duty": 50000,
    "conveyancing_fees": 25000,
    "bond_registration": 12000,
    "furnishing_cost": 80000
  },
  "operating": {
    "monthly_rental_income": 12000,
    "vacancy_rate": 0.08,
    "monthly_levies": 1500,
    "property_management_fee_rate": 0.08,
    "monthly_insurance": 800,
    "monthly_maintenance_reserve": 1000
  },
  "available_capital": 500000,
  "capital_injections": [
    {
      "amount": 50000,
      "frequency": "yearly",
      "start_period": 12,
      "end_period": 60
    }
  ],
  "strategies": [
    {
      "name": "Conservative Cash",
      "strategy_type": "cash_only",
      "simulation_months": 120,
      "reinvest_cashflow": true
    },
    {
      "name": "Leveraged 70%",
      "strategy_type": "leveraged",
      "simulation_months": 120,
      "reinvest_cashflow": true,
      "ltv_ratio": 0.7,
      "interest_rate": 0.115,
      "enable_refinancing": false
    }
  ],
  "appreciation_rate": 0.06
}
```

## Error Responses

The API returns detailed error responses for validation failures:

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "strategies", 0, "ltv_ratio"],
      "msg": "LTV ratio must be between 0.01 and 0.99"
    }
  ]
}
```

Rate limiting returns HTTP 429:
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds."
}
```

## Testing

```bash
# Run all tests
python run_unit_tests.py

# Test basic functionality
python test_basic.py

# Test portfolio yields
python test_portfolio_yields.py

# Test API directly with curl
curl -X POST "http://localhost:8000/simulate" \
  -H "Content-Type: application/json" \
  -d '{"property":{"purchase_price":1000000},"operating":{"monthly_rental_income":10000},"available_capital":300000,"strategies":[{"name":"Test","strategy_type":"cash_only","simulation_months":12,"reinvest_cashflow":true}]}'

# Test rate limiting
for i in {1..12}; do curl -X POST http://localhost:8000/simulate; done
```

## Structure

```
back/
├── api/
│   ├── endpoints.py     # API routes with rate limiting
│   ├── models.py        # Pydantic data models
│   └── presets.py       # Strategy presets
├── core/
│   ├── main.py          # Core investment types
│   ├── strategies.py    # Strategy simulation engine
│   └── reports.py       # Results formatting
├── tests/               # Comprehensive test suite
├── examples/            # Usage examples
└── run_api.py          # Application entry point
```

## Development

- **Simulation Logic**: Modify `core/strategies.py` for investment calculations
- **API Routes**: Add endpoints in `api/endpoints.py`
- **Data Models**: Update Pydantic models in `api/models.py`
- **Strategy Presets**: Add predefined strategies in `api/presets.py`
- **Rate Limiting**: Adjust limits in `api/endpoints.py` (currently 10/min simulations)
- **Validation**: Enhance parameter validation in `api/endpoints.py`

### Performance Considerations
- Each simulation has a 5-second timeout to prevent hanging
- Rate limiting prevents API abuse while allowing legitimate usage
- Memory-efficient calculation engine for long-term simulations
- Graceful error handling maintains API stability

## Dependencies

Main packages:
- **FastAPI** - Modern web framework with automatic API docs
- **Pydantic** - Data validation and settings management
- **Uvicorn** - High-performance ASGI server
- **SlowAPI** - Rate limiting middleware for FastAPI
- **python-dotenv** - Environment configuration management

Development packages:
- **pytest** - Testing framework
- **requests** - HTTP client for testing

All dependencies managed in `requirements.txt`.

## Production Deployment

Environment variables for production:
```bash
PORT=8000
HOSTURL=0.0.0.0
RELOAD=false
CORS_ORIGINS=https://yourdomain.com
```

The API includes comprehensive logging and monitoring endpoints suitable for production deployment on Railway, AWS, or other cloud platforms.