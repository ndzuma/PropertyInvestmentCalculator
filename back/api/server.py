import os
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Load environment variables from .env file
load_dotenv()

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)

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

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS origins from environment variable
cors_origins = os.getenv("CORS_ORIGINS", "*")
if cors_origins == "*":
    allowed_origins = ["*"]
else:
    allowed_origins = [origin.strip() for origin in cors_origins.split(",")]

# Add CORS middleware for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
@limiter.limit("10/minute")
def simulate_endpoint(request: Request, simulation_request: SimulationRequest):
    """
    Run property investment simulations for multiple strategies.

    Takes property details, operating parameters, available capital,
    capital injections, and multiple strategies to compare.
    Returns detailed results for each strategy.

    Rate limited to 10 requests per minute per IP address.
    """
    try:
        result = simulate_strategies(simulation_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@app.get("/strategy-presets", response_model=List[StrategyPreset])
@limiter.limit("100/minute")
def strategy_presets_endpoint(request: Request):
    """Get predefined strategy presets for quick testing"""
    try:
        presets = get_presets()
        return presets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get presets: {str(e)}")


@app.post("/validate", response_model=ValidationResponse)
@limiter.limit("100/minute")
def validate_endpoint(request: Request, validation_request: SimulationRequest):
    """Validate simulation parameters without running simulation"""
    try:
        result = validate_parameters(validation_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation failed: {str(e)}")


# Run with: uvicorn api.server:app --reload
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
