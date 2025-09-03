"""
Main FastAPI application entry point for Render deployment.
This replaces the Vercel-specific api/index.py structure.
"""
import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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

# For Render deployment

# --- Discord webhook on startup ---
import httpx
import datetime

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1412898921717432451/U9PcRTHpwx1WhYk8c3vhsIWnWuFkCwdoZWa04GyFHIiJf0pciOlESHhSqbdEFvfbuBOx"

async def send_wakeup_webhook():
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    embed = {
        "title": "Hey Listen!",
        "description": "<@1033059396676227193> Someone woke up the website!",
        "color": 5763719,
        "fields": [
            {"name": "Time", "value": now}
        ],
        "footer": {"text": "GrowCalculator Render Status"}
    }
    data = {"content": "<@1033059396676227193>", "embeds": [embed]}
    async with httpx.AsyncClient() as client:
        await client.post(DISCORD_WEBHOOK_URL, json=data)

@app.on_event("startup")
async def notify_wakeup():
    await send_wakeup_webhook()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main_render:app",
        host="0.0.0.0", 
        port=port,
        log_level="warning"
    )
