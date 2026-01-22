# Frontend - Property Investment Calculator

Modern React/Next.js web interface with professional UI/UX design, featuring intelligent country-specific settings, toast notifications, and seamless simulation management.

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

### 🎨 Modern UI/UX Design
- **Professional Toast Notifications**: Elegant Sonner-powered feedback system
- **Responsive Design**: Optimized for desktop and mobile experiences
- **shadcn/ui Components**: Consistent, accessible design system
- **Real-time Validation**: Immediate feedback on user inputs

### 🌍 Intelligent Location Settings
- **Country Selector**: Smart cascading location picker (Country → Region → City → Area)
- **Localized Markets**: Pre-configured settings for South Africa and UK
- **Investor Type Awareness**: Different rules for local vs international investors
- **Auto-population**: Intelligent form filling based on location selection

### 📁 Simulation Management
- **Save/Load Presets**: JSON-based simulation configurations
- **Professional Downloads**: Export complete simulation setups
- **Preset Library**: Pre-built scenarios for quick testing
- **Validation Feedback**: Clear error handling with helpful guidance

### 📊 Advanced Analysis Tools
- **Interactive Charts**: Portfolio growth and cash flow visualization with Recharts
- **Strategy Comparison**: Side-by-side performance analysis
- **Detailed Metrics**: ROI, yield, equity growth, and cash-on-cash returns
- **Property-level Breakdown**: Individual property performance tracking

### 🏠 Investment Strategy Types
- **Cash Only**: Conservative approach with available capital reinvestment
- **Leveraged**: Mortgage-backed acceleration with LTV management
- **Mixed Portfolio**: Sophisticated blend of cash and leveraged properties
- **Custom Refinancing**: Flexible refinancing schedules and targets

### 💡 User Experience Enhancements
- **Smart Validation**: Real-time LTV warnings for international investors
- **Progress Feedback**: Loading states and operation confirmations
- **Error Recovery**: Graceful handling of network issues and timeouts
- **Contextual Help**: Descriptive tooltips and guidance throughout

## Components Architecture

### 🏗️ Core Components
```
app/
├── components/
│   ├── PropertyDetails.tsx          # Property input form with validation
│   ├── OperatingExpenses.tsx        # Operating costs with market defaults
│   ├── CapitalInjections.tsx        # Flexible capital injection modeling
│   ├── StrategyBuilder.tsx          # Advanced strategy creation with validation
│   ├── StrategyList.tsx             # Strategy management and overview
│   ├── CountrySelector.tsx          # Intelligent location-based settings ✨
│   ├── SimulationButtons.tsx        # Load/save simulation management ✨
│   ├── LoadSimulationDialog.tsx     # Preset and file loading interface ✨
│   ├── DownloadSimulationDialog.tsx # Professional export functionality ✨
│   ├── SimulationResults.tsx        # Comprehensive results display
│   └── SimulationResultsCharts.tsx  # Interactive data visualizations
├── types/
│   └── api.ts                       # Complete TypeScript interface definitions
├── lib/
│   └── api-config.ts                # Centralized API client configuration
├── layout.tsx                       # App layout with Sonner toast provider ✨
└── page.tsx                         # Main orchestrating component
```

### 🎯 UI Component System
- **shadcn/ui Foundation**: Button, Input, Dialog, Select, and more
- **Custom Composites**: InputGroup components for enhanced UX
- **Toast Notifications**: Sonner integration for professional feedback
- **Responsive Layout**: Tailwind CSS grid and flexbox systems

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

### 🚀 Core Framework
- **Next.js 16** - Modern React framework with App Router
- **TypeScript** - Full type safety and development experience
- **React 18** - Latest React with concurrent features

### 🎨 UI & Styling
- **Tailwind CSS** - Utility-first styling framework
- **shadcn/ui** - High-quality component library built on Radix UI
- **Radix UI** - Accessible, unstyled component primitives
- **Lucide React** - Beautiful, customizable icons

### 📊 Data & Visualization
- **Recharts** - Powerful, responsive charts built on D3
- **Sonner** - Elegant toast notification system ✨

### 🔧 Development Tools
- **ESLint** - Code linting and quality enforcement
- **Prettier** - Consistent code formatting
- **PostCSS** - CSS processing and optimization

## Enhanced Usage Flow

### 🎯 Professional Workflow
1. **Location Intelligence** 🌍
   - Select country and drill down to specific areas
   - Auto-apply market-specific settings (rates, fees, regulations)
   - Choose investor type (local/international) for appropriate rules

2. **Smart Configuration** ⚙️
   - Enter property details with intelligent validation
   - Configure operating expenses with market defaults
   - Set available capital and optional injection schedules
   - Load existing presets or start fresh

3. **Advanced Strategy Building** 📈
   - Create multiple strategies with real-time validation
   - Get instant LTV warnings for international investors
   - Configure complex refinancing schedules
   - Mix cash and leveraged approaches

4. **Seamless Simulation** 🚀
   - Run comprehensive multi-year projections
   - Get professional feedback via toast notifications
   - Handle errors gracefully with retry guidance
   - View progress and completion status

5. **Rich Analysis** 📊
   - Explore interactive charts and detailed metrics
   - Compare strategies side-by-side
   - Drill down to property-level performance
   - Export results and save configurations

### 💾 Data Management
- **Save Configurations**: Export complete simulation setups as JSON
- **Load Presets**: Quick-start with predefined scenarios
- **File Validation**: Robust error handling for uploaded configurations
- **Success Feedback**: Clear confirmation of all operations

## API Integration & Error Handling

### 🔌 Robust Backend Communication
Frontend connects to backend via `/lib/api-config.ts`:
- **Centralized Configuration**: Single source for API settings
- **Environment Flexibility**: Development and production URL management
- **Comprehensive Error Handling**: Network timeouts, rate limiting, validation errors
- **Type-safe Requests**: Full TypeScript integration with backend models

### 🛡️ Production-Ready Error Management
- **Rate Limit Handling**: User-friendly feedback for API limits (10 sims/min)
- **Timeout Protection**: Graceful handling of long-running simulations
- **Network Resilience**: Clear messaging for connection issues
- **Validation Feedback**: Detailed error descriptions for invalid inputs

### 📊 Real-time Feedback System
- **Success Notifications**: Confirmation for all successful operations
- **Warning Alerts**: Proactive guidance for potential issues
- **Error Recovery**: Clear instructions for resolving problems
- **Progress Indicators**: Loading states throughout the application

## Development Experience

### 🛠️ Developer Tools & Standards
- **Full TypeScript**: Complete type safety across components and API layer
- **Strongly Typed APIs**: Backend integration with comprehensive interface definitions
- **Component Architecture**: Modular, reusable component design patterns
- **State Management**: React hooks with intelligent state organization

### 🎨 Design System Integration
- **shadcn/ui Standards**: Consistent component usage and customization
- **Tailwind Conventions**: Utility-first responsive design patterns
- **Accessibility Focus**: ARIA compliance and keyboard navigation support
- **Mobile-First Approach**: Progressive enhancement for larger screens

### 🚀 Performance Optimizations
- **Next.js App Router**: Modern routing with layout optimization
- **Component Lazy Loading**: Efficient bundle splitting and loading
- **Chart Performance**: Optimized Recharts rendering for large datasets
- **Memory Management**: Efficient state cleanup and garbage collection

### 🔧 Development Workflow
```bash
# Install dependencies
npm install

# Development with hot reload
npm run dev

# Type checking
npm run type-check

# Production build
npm run build

# Code quality
npm run lint
npm run format
```

## Production Deployment

### 🌐 Environment Configuration
Set production environment variables:
```bash
# Required: Backend API endpoint
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app

# Optional: Analytics and monitoring
NEXT_PUBLIC_ANALYTICS_ID=your-analytics-id
```

### 🚀 Build Optimization
```bash
# Production build with optimizations
npm run build

# Static export (if needed)
npm run export

# Start production server
npm start
```

### 📊 Performance Monitoring
- **Next.js Analytics**: Built-in performance monitoring
- **Bundle Analysis**: Optimize load times and bundle size
- **Core Web Vitals**: Track user experience metrics
- **Error Tracking**: Production error monitoring and alerting

### 🔒 Security Considerations
- **Environment Variables**: Secure API configuration management
- **Input Validation**: Client-side validation with backend verification
- **Rate Limiting**: Coordinated with backend API protection
- **Content Security**: CSP headers and secure deployment practices

See `../DEPLOYMENT.md` for comprehensive deployment instructions and platform-specific guides.