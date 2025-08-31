#!/usr/bin/env python3
"""Run the AI Agent Task Manager application"""
import uvicorn
from src.ui.app import app

if __name__ == "__main__":
    print("🚀 Starting AI Agent Task Manager...")
    print("📍 Open http://localhost:8000 in your browser")
    print("📚 API documentation available at http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )