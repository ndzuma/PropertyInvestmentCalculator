#!/usr/bin/env python3
"""
Simple script to run the Property Investment Calculator API server
"""

import os

import uvicorn
from api.server import app
from dotenv import load_dotenv

if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    # Get configuration from environment variables
    host = os.getenv("HOSTURL", "0.0.0.0")  # Bind to all interfaces for Railway
    port = int(os.getenv("PORT", "8000"))  # Use port 8000 as requested
    reload = os.getenv("RELOAD", "true").lower() == "true"

    print("🚀 Starting Property Investment Calculator API...")
    print(f"📖 API docs will be available at: http://{host}:{port}/docs")
    print(f"🔧 Interactive API at: http://{host}:{port}/redoc")
    print(f"📡 Health check at: http://{host}:{port}/health")
    print(f"🌐 Server binding to: {host}:{port}")
    print("\nPress CTRL+C to stop the server")
    print("=" * 60)

    try:
        uvicorn.run(
            "api.server:app", host=host, port=port, reload=reload, log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 API server stopped")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
