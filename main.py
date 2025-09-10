"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from routes import calculator, api
from services.shared_results_service import shared_results_service
from services.tracking_middleware import TrackingMiddleware
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

# Add tracking middleware
from services.tracking_middleware import TrackingMiddleware
app.add_middleware(TrackingMiddleware)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(calculator.router)
app.include_router(api.router, prefix="/api")

# Templates
templates = Jinja2Templates(directory="templates")


@app.get("/logs")
async def view_logs(request: Request):
    """Display tracking service logs in a web interface."""
    try:
        from services.tracking_service import get_log_entries
        logs = get_log_entries()
        return templates.TemplateResponse("logs.html", {
            "request": request,
            "logs": logs,
            "total_entries": len(logs),
            "max_entries": 100
        })
    except Exception as e:
        logger.error(f"Error displaying logs: {str(e)}")
        return templates.TemplateResponse("logs.html", {
            "request": request,
            "logs": [],
            "total_entries": 0,
            "max_entries": 100
        })


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
