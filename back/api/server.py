from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .endpoints import get_presets, simulate_strategies, validate_parameters
from .models import (
    HealthResponse,
    SimulationRequest,
    SimulationResponse,
    StrategyPreset,
    ValidationResponse,
)

# Create FastAPI app
app = FastAPI(
    title="Property Investment Calculator API",
    description="API for running property investment simulations and strategy comparisons",
    version="1.0.0",
)

# Add CORS middleware for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", summary="API information")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Property Investment Calculator API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", service="property-investment-calculator")


@app.post("/simulate", response_model=SimulationResponse)
def simulate_endpoint(request: SimulationRequest):
    """
    Run property investment simulations for multiple strategies.

    Takes property details, operating parameters, available capital,
    capital injections, and multiple strategies to compare.
    Returns detailed results for each strategy.
    """
    try:
        result = simulate_strategies(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@app.get("/strategy-presets", response_model=List[StrategyPreset])
def strategy_presets_endpoint():
    """Get predefined strategy presets for quick testing"""
    try:
        presets = get_presets()
        return presets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get presets: {str(e)}")


@app.post("/validate", response_model=ValidationResponse)
def validate_endpoint(request: SimulationRequest):
    """Validate simulation parameters without running simulation"""
    try:
        result = validate_parameters(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation failed: {str(e)}")


# Run with: uvicorn api.server:app --reload
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
