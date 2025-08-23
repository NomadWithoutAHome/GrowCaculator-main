"""
Main calculator routes for rendering HTML pages.
"""
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path

from services.calculator_service import calculator_service
from services.vercel_shared_results_service import vercel_shared_results_service
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
