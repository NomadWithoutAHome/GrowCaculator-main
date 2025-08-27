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
from fastapi.responses import FileResponse, JSONResponse
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

# SEO Routes - Serve robots.txt and sitemap.xml at root level
@app.get("/robots.txt")
async def serve_robots():
    """Serve robots.txt file for search engine crawlers."""
    robots_path = parent_dir / "robots.txt"
    if robots_path.exists():
        return FileResponse(robots_path, media_type="text/plain")
    return JSONResponse(status_code=404, content={"error": "robots.txt not found"})

@app.get("/sitemap.xml")
async def serve_sitemap():
    """Serve sitemap.xml file for search engine indexing."""
    sitemap_path = parent_dir / "sitemap.xml"
    if sitemap_path.exists():
        # Simple file serving like the working website - no custom headers
        return FileResponse(sitemap_path, media_type="application/xml")
    return JSONResponse(status_code=404, content={"error": "sitemap.xml not found"})

# Static files handling for Vercel
@app.get("/static/{path:path}")
async def serve_static(path: str):
    """Serve static files from the static directory."""
    static_path = parent_dir / "static" / path
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
