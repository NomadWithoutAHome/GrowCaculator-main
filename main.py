"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from routes import calculator, api
from services.shared_results_service import shared_results_service
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GrowCalculator",
    description="A modern plant value calculator for Roblox Grow a Garden",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(calculator.router)
app.include_router(api.router, prefix="/api")

# Templates
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Starting GrowCalculator application...")
    
    # Clean up any expired results on startup
    try:
        deleted_count = shared_results_service.cleanup_expired_results()
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} expired shared results on startup")
        else:
            logger.info("No expired results found on startup")
    except Exception as e:
        logger.error(f"Error during startup cleanup: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down GrowCalculator application...")
    
    # Clean up expired results before shutdown
    try:
        deleted_count = shared_results_service.cleanup_expired_results()
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} expired shared results on shutdown")
    except Exception as e:
        logger.error(f"Error during shutdown cleanup: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
