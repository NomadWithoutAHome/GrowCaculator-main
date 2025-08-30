"""
Main calculator routes for rendering HTML pages.
"""
import logging
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

from services.calculator_service import calculator_service
from services.vercel_shared_results_service import vercel_shared_results_service
from services.discord_webhook_service import discord_webhook_service
from services.traits_service import traits_service
from models.calculator import SharedResult, SharedResultResponse
from fastapi import HTTPException
from datetime import datetime, timedelta

router = APIRouter()

# Get the correct templates directory path for Vercel
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main calculator page."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "plants": calculator_service.get_plants(),
            "variants": calculator_service.get_variants(),
            "mutations": calculator_service.get_mutations(),
        }
    )


@router.get("/mutation-calculator", response_class=HTMLResponse)
async def mutation_calculator(request: Request):
    """Dedicated mutation calculator page."""
    return templates.TemplateResponse(
        "mutation_calculator.html",
        {
            "request": request,
            "mutations": calculator_service.get_mutations(),
        }
    )


@router.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """About page."""
    return templates.TemplateResponse(
        "about.html",
        {"request": request}
    )


@router.get("/share/{share_id}", response_class=HTMLResponse)
async def share_result(request: Request, share_id: str):
    """Share results page."""
    return templates.TemplateResponse(
        "share.html",
        {"request": request, "share_id": share_id}
    )


@router.get("/traits", response_class=HTMLResponse)
async def traits_explorer(request: Request):
    """Plant traits explorer page."""
    return templates.TemplateResponse(
        "traits.html",
        {"request": request}
    )


@router.post("/api/share", response_model=SharedResultResponse)
async def create_shared_result(share_data: dict):
    """Create a new shared result."""
    try:
        # Generate share ID if not provided
        if 'share_id' not in share_data:
            share_data['share_id'] = f"share_{int(datetime.utcnow().timestamp())}_{hash(str(share_data)) % 10000}"
        
        # Set expiration to 24 hours from now
        share_data['expires_at'] = (datetime.utcnow() + timedelta(hours=24)).isoformat()
        
        # Create the shared result
        success = vercel_shared_results_service.create_shared_result(share_data)
        
        if success:
            # Send Discord webhook notification (non-blocking)
            try:
                await discord_webhook_service.send_calculation_result(share_data)
            except Exception as e:
                logger.error(f"Failed to send Discord webhook: {e}")
                # Don't fail the share creation if webhook fails
            
            return SharedResultResponse(
                success=True,
                data=SharedResult(**share_data)
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to create shared result")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/share/{share_id}", response_model=SharedResultResponse)
async def get_shared_result(share_id: str):
    """Retrieve a shared result by ID."""
    try:
        result = vercel_shared_results_service.get_shared_result(share_id)
        
        if result:
            return SharedResultResponse(
                success=True,
                data=SharedResult(**result)
            )
        else:
            return SharedResultResponse(
                success=False,
                error="Shared result not found or has expired"
            )
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/api/share/{share_id}")
async def delete_shared_result(share_id: str):
    """Delete a shared result by ID."""
    try:
        success = vercel_shared_results_service.delete_shared_result(share_id)
        
        if success:
            return {"success": True, "message": "Shared result deleted"}
        else:
            raise HTTPException(status_code=404, detail="Shared result not found")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/share/cleanup")
async def cleanup_expired_results():
    """Clean up expired shared results."""
    try:
        deleted_count = vercel_shared_results_service.cleanup_expired_results()
        return {
            "success": True,
            "deleted_count": deleted_count,
            "message": f"Cleaned up {deleted_count} expired results"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/share/stats")
async def get_share_stats():
    """Get database statistics for shared results."""
    try:
        stats = vercel_shared_results_service.get_database_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Traits API endpoints
@router.get("/api/traits/plant/{plant_name}")
async def get_plant_traits(plant_name: str):
    """Get traits for a specific plant."""
    try:
        # Get traits and the actual plant name (handles case-insensitive matching)
        traits = traits_service.get_plant_traits(plant_name)
        
        # Find the actual plant name in the data (case-insensitive)
        actual_plant_name = None
        decoded_search_name = traits_service._decode_plant_name(plant_name)
        
        for stored_name in traits_service.traits_data.keys():
            if stored_name.lower() == decoded_search_name.lower():
                actual_plant_name = stored_name
                break
        
        if not actual_plant_name:
            actual_plant_name = decoded_search_name
        
        return {
            "success": True,
            "plant": actual_plant_name,
            "traits": traits
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/traits/search/{trait}")
async def search_traits(trait: str):
    """Get plants that have a specific trait."""
    try:
        plants = traits_service.get_plants_by_trait(trait)
        return {
            "success": True,
            "trait": trait,
            "plants": plants  # These are already decoded by the service
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/traits/statistics")
async def get_trait_statistics():
    """Get comprehensive trait statistics."""
    try:
        stats = traits_service.get_trait_statistics()
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/traits/all")
async def get_all_plants_traits():
    """Get all plants with their traits."""
    try:
        all_traits = traits_service.get_all_plants_traits()
        return {
            "success": True,
            "plants": all_traits
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
