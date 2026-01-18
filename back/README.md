# Backend API - Property Investment Calculator

FastAPI backend service for property investment simulations and strategy comparisons.

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

- `POST /simulate` - Run property investment simulations
- `GET /strategy-presets` - Get predefined strategies
- `POST /validate` - Validate parameters
- `GET /health` - Health check

## Example Request

```json
{
  "property": {
    "purchase_price": 1000000,
    "transfer_duty": 10000,
    "conveyancing_fees": 15000
  },
  "operating": {
    "monthly_rental_income": 12000,
    "vacancy_rate": 0.05,
    "monthly_levies": 1500
  },
  "available_capital": 400000,
  "strategies": [
    {
      "name": "Cash Only",
      "strategy_type": "cash_only",
      "simulation_years": 5
    }
  ]
}
```

## Testing

```bash
# Run all tests
python run_unit_tests.py

# Test API directly
python api/test_api.py

# Use test files
curl -X POST "http://localhost:8000/simulate" \
  -H "Content-Type: application/json" \
  -d @api/test_request.json
```

## Structure

```
back/
├── api/           # FastAPI routes and models
├── core/          # Investment calculation engine  
├── tests/         # Test suite
└── examples/      # Usage examples
```

## Development

- Modify `core/strategies.py` for simulation logic
- Add routes in `api/server.py`
- Update models in `api/models.py`
- Add presets in `api/presets.py`

## Dependencies

Main packages:
- FastAPI - Web framework
- Pydantic - Data validation
- Uvicorn - ASGI server
- python-dotenv - Environment variables

All dependencies in `requirements.txt`.