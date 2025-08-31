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

# Import the recipe service
from services.recipe_service import recipe_service

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


@router.get("/traits")
async def traits_page(request: Request):
    """Render the traits page."""
    return templates.TemplateResponse("traits.html", {"request": request})


@router.get("/recipes")
async def recipes_page(request: Request):
    """Render the recipes page."""
    return templates.TemplateResponse("recipes.html", {"request": request})


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


# Recipe API endpoints
@router.get("/api/recipes/all")
async def get_all_recipes():
    """Get all available recipes."""
    try:
        recipes = recipe_service.get_all_recipes()
        return {
            "success": True,
            "recipes": recipes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/recipes/all-with-stats")
async def get_all_recipes_with_stats():
    """Get all available recipes with combination statistics."""
    try:
        recipes = recipe_service.get_all_recipes_with_stats()
        return {
            "success": True,
            "recipes": recipes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/recipes/{recipe_name}")
async def get_recipe(recipe_name: str):
    """Get a specific recipe by name."""
    try:
        recipe = recipe_service.get_recipe(recipe_name)
        if recipe:
            return {
                "success": True,
                "recipe": recipe
            }
        else:
            raise HTTPException(status_code=404, detail=f"Recipe '{recipe_name}' not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))





@router.get("/api/recipes/categories")
async def get_recipe_categories():
    """Get all ingredient categories and their available items."""
    try:
        logger.info("get_recipe_categories called")
        categories = recipe_service.get_recipe_categories()
        logger.info(f"get_recipe_categories success: {len(categories)} categories")
        
        # Add debug info to the response
        return {
            "success": True,
            "categories": categories,
            "debug_info": {
                "total_categories": len(categories),
                "category_names": list(categories.keys()),
                "sample_category": list(categories.items())[0] if categories else None
            }
        }
    except Exception as e:
        logger.error(f"get_recipe_categories error: {e}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Return the actual error details in the response instead of raising HTTPException
        return {
            "success": False,
            "error": str(e),
            "error_type": str(type(e).__name__),
            "traceback": traceback.format_exc(),
            "categories": {}
        }


@router.get("/api/recipes/difficulty/{difficulty}")
async def get_recipes_by_difficulty(difficulty: str):
    """Get recipes filtered by difficulty (Easy, Medium, Hard)."""
    try:
        if difficulty not in ["Easy", "Medium", "Hard"]:
            raise HTTPException(status_code=400, detail="Difficulty must be Easy, Medium, or Hard")
        
        recipes = recipe_service.get_recipes_by_difficulty(difficulty)
        return {
            "success": True,
            "difficulty": difficulty,
            "recipes": recipes
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/recipes/search/{query}")
async def search_recipes(query: str):
    """Search recipes by name or description."""
    try:
        results = recipe_service.search_recipes(query)
        return {
            "success": True,
            "query": query,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/recipes/mechanics")
async def get_cooking_mechanics():
    """Get information about how cooking works in the game."""
    try:
        mechanics = recipe_service.get_cooking_mechanics()
        return {
            "success": True,
            "mechanics": mechanics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/recipes/share")
async def share_recipe(recipe_data: dict):
    """Share a recipe with a unique link."""
    try:
        # Generate unique share ID
        import time
        import random
        share_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Add share_id to recipe data for Discord webhook
        recipe_data['share_id'] = share_id
        recipe_data['result_type'] = 'recipe'
        
        # Store the shared recipe
        shared_result = shared_results_service.create_shared_result(
            share_id=share_id,
            result_type="recipe",
            data=recipe_data
        )
        
        # Send Discord webhook notification
        await discord_webhook_service.send_calculation_result(recipe_data)
        
        return {
            "success": True,
            "share_id": share_id,
            "share_url": f"https://www.fruitcalculator.dohmboy64.com/share/recipe_{share_id}"
        }
    except Exception as e:
        logger.error(f"Error sharing recipe: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/share/recipe_{share_id}")
async def get_shared_recipe(share_id: str):
    """Get a shared recipe by share ID."""
    try:
        shared_result = shared_results_service.get_shared_result(share_id)
        if not shared_result:
            raise HTTPException(status_code=404, detail="Shared recipe not found")
        
        return templates.TemplateResponse("share_recipe.html", {
            "request": {},
            "recipe_data": shared_result["data"],
            "share_id": share_id,
            "created_at": shared_result["created_at"]
        })
    except Exception as e:
        logger.error(f"Error getting shared recipe: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/recipes/shop-seeds")
async def get_shop_seeds():
    """Get list of shop seeds (basic seeds available in the shop)."""
    try:
        shop_seeds = recipe_service.get_shop_seeds()
        return {
            "success": True,
            "shop_seeds": shop_seeds
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/recipes/generate/{recipe_name}")
async def generate_random_recipe(recipe_name: str, shop_seeds_only: bool = False):
    """Generate a random recipe with random ingredient combinations."""
    try:
        random_recipe = recipe_service.generate_random_recipe(recipe_name, shop_seeds_only)
        return {
            "success": True,
            "recipe": random_recipe
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
