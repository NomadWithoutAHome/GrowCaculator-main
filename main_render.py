"""
Main FastAPI application entry point for Render deployment.
This replaces the Vercel-specific api/index.py structure.
"""
import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import logging

# Set up logging for production
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="GrowCalculator",
    description="A modern plant value calculator for Roblox Grow a Garden",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (Render handles this differently than Vercel)
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception as e:
    logger.error(f"Could not mount static files: {e}")

# Include your existing routes
from routes import calculator, api
app.include_router(calculator.router)
app.include_router(api.router, prefix="/api")

# Templates
templates = Jinja2Templates(directory="templates")

# Import the shared results service for Render
from services.vercel_shared_results_service import vercel_shared_results_service

# SEO Routes - Serve robots.txt and sitemap.xml
@app.get("/robots.txt")
async def serve_robots():
    """Serve robots.txt file for search engine crawlers."""
    robots_path = Path("robots.txt")
    if robots_path.exists():
        return FileResponse(robots_path, media_type="text/plain")
    return JSONResponse(status_code=404, content={"error": "robots.txt not found"})

@app.get("/sitemap.xml")
async def serve_sitemap():
    """Serve sitemap.xml file for search engine indexing."""
    sitemap_path = Path("sitemap.xml")
    if sitemap_path.exists():
        return FileResponse(sitemap_path, media_type="application/xml")
    return JSONResponse(status_code=404, content={"error": "sitemap.xml not found"})

# Startup logic (moved to avoid deprecation warning)
async def startup_logic():
    """Run startup logic."""
    logger.info("Starting GrowCalculator application on Render...")
    
    # Clean up any expired results on startup
    try:
        deleted_count = vercel_shared_results_service.cleanup_expired_results()
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} expired shared results on startup")
        else:
            logger.info("No expired results found on startup")
    except Exception as e:
        logger.error(f"Error during startup cleanup: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint for Render."""
    return {"status": "healthy", "service": "GrowCalculator"}

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

# --------------------------------------------------------------------
# Discord webhook integration for status embeds
# --------------------------------------------------------------------
import httpx
import datetime

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1412898921717432451/U9PcRTHpwx1WhYk8c3vhsIWnWuFkCwdoZWa04GyFHIiJf0pciOlESHhSqbdEFvfbuBOx"
DISCORD_MESSAGE_ID = "1412900301480005663"

async def update_status_embed(description: str, color: int):
    """Update the pinned Discord embed instead of creating new messages."""
    try:
        now_iso = datetime.datetime.utcnow().isoformat()

        embed = {
            "title": "Hey Listen!",           # Always the same
            "description": description,       # Wakeup or shutdown message
            "color": color,                   # Green or red
            "footer": {"text": "GrowCalculator Render Status"},
            "timestamp": now_iso              # Native Discord timestamp
        }

        data = {"embeds": [embed]}
        webhook_edit_url = f"{DISCORD_WEBHOOK_URL}/messages/{DISCORD_MESSAGE_ID}"

        async with httpx.AsyncClient() as client:
            resp = await client.patch(webhook_edit_url, json=data, timeout=10)
            if resp.is_error:
                logger.error(f"Failed to update Discord status embed: {resp.text}")

    except Exception as e:
        logger.error(f"Error while updating Discord embed: {e}")

# Startup & shutdown events
@app.on_event("startup")
async def notify_wakeup():
    GREEN = 0x57F287  # Discord green
    await startup_logic()
    await update_status_embed("Someone woke up the website!", GREEN)

@app.on_event("shutdown")
async def notify_shutdown():
    RED = 0xED4245  # Discord red
    await update_status_embed("The website went to sleep!", RED)

# --------------------------------------------------------------------
# For local dev / manual run
# --------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main_render:app",
        host="0.0.0.0",
        port=port,
        log_level="warning"
    )
