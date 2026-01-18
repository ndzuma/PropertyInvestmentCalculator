# Property Investment Calculator

A comprehensive property investment simulation tool that helps analyze different investment strategies, compare returns, and optimize portfolio decisions.

## What it does

- **Compare Investment Strategies**: Cash vs leveraged vs mixed approaches
- **Simulate Multiple Scenarios**: Run 5+ year simulations with different parameters
- **Portfolio Growth Analysis**: Track property acquisitions and portfolio value over time
- **Financial Metrics**: ROI, cash flow, equity growth, and more
- **Capital Injection Modeling**: Add regular or one-time capital contributions

## Quick Start

### 1. Start the Backend
```bash
cd back
pip install -r requirements.txt
python run_api.py
```
Backend runs on http://localhost:8000

### 2. Start the Frontend
```bash
cd front
npm install
npm run dev
```
Frontend runs on http://localhost:3000

### 3. Use the Calculator
1. Enter property details (price, costs, rental income)
2. Set operating expenses (levies, insurance, maintenance)
3. Choose your available capital
4. Add investment strategies to compare
5. Run simulation and analyze results

## Project Structure

```
PropertyInvestmentCalculator/
├── back/                   # Python FastAPI backend
│   ├── api/                # REST API endpoints
│   ├── core/               # Investment calculation engine
│   ├── requirements.txt    # Python dependencies
│   └── run_api.py         # Start server
├── front/                  # Next.js frontend
│   ├── app/                # React components
│   ├── lib/                # Utilities
│   ├── package.json        # Node dependencies
│   └── .env.local         # Local config
└── DEPLOYMENT.md          # Railway deployment guide
```

## Features

### Investment Strategies
- **Cash Only**: Purchase properties with available cash, reinvest rental income
- **Leveraged**: Use mortgages to acquire more properties faster
- **Mixed Portfolio**: Combine cash and leveraged properties

### Analysis Tools
- Monthly cash flow projections
- Portfolio growth charts
- Property acquisition timeline
- ROI and yield calculations
- Equity vs debt tracking

### Flexible Inputs
- Property purchase costs (price, transfer duty, fees)
- Rental income and vacancy rates
- Operating expenses (levies, management, maintenance)
- Mortgage terms (LTV, interest rate, term)
- Capital injections (monthly, yearly, one-time)

## Example Use Cases

**First-time Investor**: Compare buying one property cash vs leveraged to see which builds wealth faster

**Portfolio Expansion**: Model adding R5,000/month to see how it accelerates property acquisitions

**Strategy Optimization**: Test different LTV ratios to find the optimal leverage level

**Market Analysis**: Adjust rental yields and property appreciation to model different markets

## Technology Stack

- **Backend**: Python, FastAPI, Uvicorn
- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **Charts**: Recharts
- **Deployment**: Railway (or any cloud platform)

## Development

See individual README files:
- [Backend README](back/README.md) - API documentation and development setup
- [Frontend README](front/README.md) - UI development and component structure

## Deployment

For production deployment to Railway or other platforms, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Environment Setup

### Backend (.env)
```bash
PORT=8000
HOSTURL=0.0.0.0
RELOAD=true
CORS_ORIGINS=*
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development Roadmap

Planned features and improvements, ordered from simplest to most complex:

### 🟢 Simple (Quick Wins)
- [ ] **Dockerization** - Add Dockerfile for easy homelab deployment
- [ ] **HTTP Status Codes** - Improve API status code support for better monitoring
- [ ] **Rate Limiting** - Add API rate limiting to prevent abuse
- [ ] **Load Test Data** - Create comprehensive test datasets

### 🟡 Medium Complexity
- [ ] **Enhanced Error Handling** - Detailed error responses for better monitoring and debugging
- [ ] **Save/Load Simulation Data** - Persist and restore simulation configurations
- [ ] **Backend Testing Suite** - Bulletproof calculation testing and validation
- [ ] **Taxation Support** - Add tax calculations for different scenarios

### 🟠 Complex Features  
- [ ] **User Accounts** - Save simulation history, add notes, user preferences
- [ ] **Country-Specific Settings** - Localized mortgage rates, taxes, and regulations (ZA, UK, etc.)

### 🔴 Advanced (Long-term)
- [ ] **Rental Price Predictor AI** - Machine learning model for rental price predictions
  - [ ] Phase 1: Preset models for common areas
  - [ ] Phase 2: Custom model upload and training
  - [ ] Phase 3: Real-time market data integration

Each feature will be developed with proper testing, documentation, and backwards compatibility.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test both frontend and backend
5. Submit a pull request

## License

Copyright (c) 2025 Ndzuma Malate

This project is licensed for **personal use only**. Commercial use, distribution, or modification for commercial purposes is not permitted without explicit written permission from the author.

For commercial licensing inquiries, please contact Ndzuma Malate.