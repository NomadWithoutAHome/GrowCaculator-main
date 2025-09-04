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
from models.calculator import SharedResult, SharedResultResponse, BatchSharedResult, BatchSharedResultResponse
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


@router.post("/api/share-batch")
async def create_batch_shared_result(batch_data: dict):
    """Create a new batch shared result."""
    try:
        # Generate batch share ID
        share_id = f"batch_{int(datetime.utcnow().timestamp())}_{hash(str(batch_data)) % 10000}"

        # Prepare batch data for storage
        batch_share_data = {
            'share_id': share_id,
            'type': 'batch',
            'plants': batch_data.get('plants', []),
            'total_value': 0,  # Will be calculated
            'total_plants': 0,  # Will be calculated
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }

        # Calculate totals from plants
        total_value = 0
        total_plants = 0

        for plant in batch_data.get('plants', []):
            # Calculate value for this plant
            try:
                # Import calculator service to calculate plant values
                from services.calculator_service import calculator_service

                # Get plant data
                plant_data = calculator_service.get_plant_data(plant['plant'])
                if plant_data:
                    # Simple calculation (you might want to use the full calculation logic)
                    base_value = plant_data.base_price

                    # Get variant multiplier
                    variants = calculator_service.get_variants()
                    variant_multiplier = 1
                    for variant in variants:
                        if variant.name == plant['variant']:
                            variant_multiplier = variant.multiplier
                            break

                    mutation_multiplier = calculator_service.calculate_mutation_multiplier(plant.get('mutations', []))

                    # Calculate weight scaling (simplified)
                    weight_ratio = min(2.0, max(0.5, plant['weight'] / plant_data.base_weight))

                    plant_value = base_value * variant_multiplier * mutation_multiplier * weight_ratio
                    total_value += plant_value * plant.get('quantity', 1)
                    total_plants += plant.get('quantity', 1)

                    # Add calculated values to plant data
                    plant['result'] = plant_value
                    plant['total'] = plant_value * plant.get('quantity', 1)

            except Exception as e:
                logger.error(f"Error calculating value for plant {plant['plant']}: {e}")
                # Use fallback values
                fallback_value = 100  # Default fallback
                total_value += fallback_value * plant.get('quantity', 1)
                total_plants += plant.get('quantity', 1)
                plant['result'] = fallback_value
                plant['total'] = fallback_value * plant.get('quantity', 1)

        # Update totals
        batch_share_data['total_value'] = total_value
        batch_share_data['total_plants'] = total_plants

        # Use the local shared_results_service for batch data
        from services.shared_results_service import shared_results_service
        success = shared_results_service.create_shared_result(batch_share_data)

        if success:
            # Send Discord webhook notification (non-blocking)
            try:
                batch_data['share_id'] = share_id
                batch_data['result_type'] = 'batch'
                await discord_webhook_service.send_calculation_result(batch_data)
            except Exception as e:
                logger.error(f"Failed to send Discord webhook: {e}")
                # Don't fail the share creation if webhook fails

            return {
                "success": True,
                "share_id": share_id,
                "share_url": f"/share/{share_id}"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create batch shared result")

    except Exception as e:
        logger.error(f"Error creating batch shared result: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/share/{share_id}")
async def get_shared_result(share_id: str):
    """Retrieve a shared result by ID."""
    try:
        # Check if this is a batch share ID
        if share_id.startswith('batch_'):
            # For batch results, use the local shared_results_service
            from services.shared_results_service import shared_results_service
            result = shared_results_service.get_shared_result(share_id)
        else:
            # For regular shares, use the vercel service
            result = vercel_shared_results_service.get_shared_result(share_id)

        if result:
            return {
                "success": True,
                "data": result
            }
        else:
            return {
                "success": False,
                "error": "Shared result not found or has expired"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


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
        shared_result = vercel_shared_results_service.create_shared_result({
            'share_id': share_id,
            'result_type': 'recipe',
            **recipe_data
        })
        
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
        shared_result = vercel_shared_results_service.get_shared_result(share_id)
        if not shared_result:
            raise HTTPException(status_code=404, detail="Shared recipe not found")
        
        # Parse created_at if it's a string
        created_at = shared_result.get('created_at', datetime.utcnow().isoformat())
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except:
                created_at = datetime.utcnow()
        
        return templates.TemplateResponse("share_recipe.html", {
            "request": {},  # Empty dict is sufficient for this template
            "recipe_data": shared_result,  # Pass the shared_result directly
            "share_id": share_id,
            "created_at": created_at
        })
    except Exception as e:
        logger.error(f"Error getting shared recipe: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/share/{share_id}", response_class=HTMLResponse)
async def share_result(request: Request, share_id: str):
    """Share results page."""
    # Check if this is a batch share ID
    if share_id.startswith('batch_'):
        # For batch results, use the local shared_results_service and batch template
        from services.shared_results_service import shared_results_service
        result = shared_results_service.get_shared_result(share_id)

        if result:
            return templates.TemplateResponse(
                "share_batch.html",
                {"request": request, "share_id": share_id}
            )
        else:
            # Result not found, show error page
            return templates.TemplateResponse(
                "share_batch.html",
                {"request": request, "share_id": share_id, "error": "Shared batch result not found or has expired"}
            )
    else:
        # For regular shares, use the vercel service and regular share template
        result = vercel_shared_results_service.get_shared_result(share_id)

        if result:
            return templates.TemplateResponse(
                "share.html",
                {"request": request, "share_id": share_id}
            )
        else:
            # Result not found, show error page
            return templates.TemplateResponse(
                "share.html",
                {"request": request, "share_id": share_id, "error": "Shared result not found or has expired"}
            )


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
