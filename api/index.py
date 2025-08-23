"""
Vercel serverless function entry point for GrowCalculator.
This file handles all HTTP requests and serves the FastAPI application.
"""
import os
import sys
from pathlib import Path

# Add the parent directory to Python path to import our modules
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="GrowCalculator",
    description="A modern plant value calculator for Roblox Grow a Garden",
    version="1.0.0"
)

# Add CORS middleware for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Test route to verify the app works
@app.get("/")
async def root():
    """Test root endpoint."""
    return {"message": "GrowCalculator API is working!"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "GrowCalculator"}

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
