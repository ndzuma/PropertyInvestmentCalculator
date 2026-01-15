#!/usr/bin/env python3
"""
Simple script to run the Property Investment Calculator API server
"""

import uvicorn

from api.server import app

if __name__ == "__main__":
    print("🚀 Starting Property Investment Calculator API...")
    print("📖 API docs will be available at: http://localhost:8001/docs")
    print("🔧 Interactive API at: http://localhost:8001/redoc")
    print("📡 Health check at: http://localhost:8001/health")
    print("\nPress CTRL+C to stop the server")
    print("=" * 60)

    try:
        uvicorn.run(
            "api.server:app", host="127.0.0.1", port=8001, reload=True, log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 API server stopped")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
