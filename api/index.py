"""
Vercel serverless function entry point for GrowCalculator.
This file handles all HTTP requests and serves the FastAPI application.
"""
import os
import sys
from pathlib import Path

# Add the parent directory to Python path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from routes import calculator, api
from services.vercel_shared_results_service import vercel_shared_results_service
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

# Include routers
app.include_router(calculator.router)
app.include_router(api.router, prefix="/api")

# Templates
templates = Jinja2Templates(directory="templates")

# Static files handling for Vercel
@app.get("/static/{path:path}")
async def serve_static(path: str):
    """Serve static files from the static directory."""
    from fastapi.responses import JSONResponse
    static_path = Path(__file__).parent.parent / "static" / path
    if static_path.exists():
        return FileResponse(static_path)
    return JSONResponse(status_code=404, content={"error": "File not found"})

@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Starting GrowCalculator application on Vercel...")
    
    # Clean up any expired results on startup
    try:
        deleted_count = vercel_shared_results_service.cleanup_expired_results()
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} expired shared results on startup")
        else:
            logger.info("No expired results found on startup")
    except Exception as e:
        logger.error(f"Error during startup cleanup: {e}")

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
