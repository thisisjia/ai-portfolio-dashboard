#!/usr/bin/env python
"""Main entry point for the backend server."""

import uvicorn
from src.solutions.resume_dashboard.main import app

if __name__ == "__main__":
    uvicorn.run(
        "src.solutions.resume_dashboard.main:app",
        host="0.0.0.0",
        port=9001,
        reload=True,
        log_level="info"
    )