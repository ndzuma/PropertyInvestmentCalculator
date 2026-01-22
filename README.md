# Property Investment Calculator

A comprehensive property investment simulation tool that helps analyze different investment strategies, compare returns, and optimize portfolio decisions.

## Why I Built This

I created this tool to accurately simulate multiple property investing strategies - from different leveraged approaches to fully cash purchases, and everything in between. The real catalyst? My mom wanted to know where to buy an investment property, and I wanted to build her a simple yet sophisticated calculator that could actually answer her questions properly.

As for the tech stack - I just love how straightforward FastAPI is, and I can move incredibly fast with Next.js. Plus, the App Router might be my favorite web feature ever. Python lets me prototype at lightning speed, and well... one thing led to another and here we are with a full-blown investment calculator that spiraled way beyond what mom originally asked for. 🚀

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

### ✅ COMPLETED FEATURES

- [x] **Core Investment Engine** - Property simulation with cash flow calculations
- [x] **Strategy Comparison** - Cash only, leveraged, and mixed portfolio strategies
- [x] **Portfolio Growth Analysis** - Multi-year property acquisition simulations
- [x] **Enhanced Error Handling** - Timeout protection and graceful error responses
- [x] **Rate Limiting** - API protection against abuse (10 simulations/min)
- [x] **Save/Load Simulation Data** - JSON-based simulation presets and user configurations
- [x] **Country-Specific Settings** - Localized settings for South Africa and UK markets
- [x] **Professional UI/UX Redesign** - Sonner toast notifications and improved user experience

### 🚀 UPCOMING FEATURES

Planned improvements, ordered by priority:

#### 🟢 Next Phase (High Priority)
- [ ] **Database Persistence** - PostgreSQL backend for simulation history
- [ ] **User Authentication** - Save personal simulations and preferences
- [ ] **Advanced Reporting** - PDF export and detailed analytics
- [ ] **Mobile Optimization** - Responsive design improvements

#### 🟡 Medium Term
- [ ] **Multi-Currency Support** - USD, EUR, AUD market calculations
- [ ] **Taxation Integration** - Capital gains, rental income tax calculations
- [ ] **Market Data Integration** - Real-time property price feeds
- [ ] **Dockerization** - Container deployment for easy self-hosting

#### 🟠 Advanced Features
- [ ] **Team Collaboration** - Shared simulations and investor groups
- [ ] **API Webhooks** - Integration with external property platforms
- [ ] **Advanced Modeling** - Monte Carlo simulations and risk analysis

#### 🔴 Research & Innovation
- [ ] **AI Market Predictions** - Machine learning property value forecasting
- [ ] **Automated Property Sourcing** - Integration with property listing APIs
- [ ] **Portfolio Optimization** - AI-driven strategy recommendations

Each feature includes comprehensive testing, documentation, and maintains backwards compatibility.

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