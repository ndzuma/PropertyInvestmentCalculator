# Frontend - Property Investment Calculator

React/Next.js web interface for the Property Investment Calculator.

## Quick Start

```bash
cd front
npm install
npm run dev
```

App runs on http://localhost:3000

## Configuration

Copy `.env.example` to `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Make sure the backend is running on port 8000.

## Features

### Input Forms
- **Property Details**: Purchase price, transfer costs, furnishing
- **Operating Expenses**: Rental income, levies, maintenance, insurance
- **Capital Injections**: Monthly/yearly additional investments
- **Strategy Builder**: Create multiple investment strategies

### Analysis Tools
- **Portfolio Charts**: Property count and value over time
- **Cash Flow Analysis**: Monthly income vs expenses
- **Strategy Comparison**: Side-by-side results
- **Detailed Breakdowns**: Per-property metrics and costs

### Strategy Types
- **Cash Only**: Buy with available capital, reinvest income
- **Leveraged**: Use mortgages for faster acquisition
- **Mixed**: Combine cash and leveraged properties

## Components

```
app/
├── components/
│   ├── PropertyDetails.tsx       # Property input form
│   ├── OperatingExpenses.tsx     # Operating costs form
│   ├── CapitalInjections.tsx     # Additional capital form
│   ├── StrategyBuilder.tsx       # Strategy creation
│   ├── StrategyList.tsx          # Strategy management
│   ├── SimulationResults.tsx     # Results display
│   └── SimulationResultsCharts.tsx # Charts and graphs
├── types/
│   └── api.ts                    # TypeScript interfaces
└── page.tsx                      # Main calculator page
```

## Building

```bash
# Development
npm run dev

# Production build
npm run build
npm start

# Linting
npm run lint
```

## Key Dependencies

- **Next.js** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **Radix UI** - Component primitives

## Usage Flow

1. Enter property details (price, rental income)
2. Set operating expenses (levies, maintenance)
3. Configure available capital
4. Add capital injections (optional)
5. Create investment strategies
6. Run simulation
7. Analyze results and charts

## API Integration

Frontend connects to backend via `/lib/api-config.ts`:
- Centralized API configuration
- Environment-based URLs
- Error handling
- Type-safe requests

## Development

- Components use TypeScript for type safety
- All API responses are strongly typed
- Environment variables for backend URL
- Responsive design with Tailwind
- Interactive charts with Recharts

## Deployment

Set environment variable for production:
```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

See `DEPLOYMENT.md` for full deployment instructions.