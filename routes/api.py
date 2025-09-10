"""
API routes for calculator functionality.
"""
from typing import List
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta

from models.calculator import (
    CalculationRequest,
    CalculationResponse,
    PlantListResponse,
    VariantListResponse,
    MutationListResponse
)
from services.calculator_service import calculator_service

router = APIRouter()


@router.post("/calculate", response_model=CalculationResponse)
async def calculate_plant_value(request: CalculationRequest):
    """Calculate plant value based on provided parameters."""
    try:
        result = calculator_service.calculate_full_value(
            plant_name=request.plant_name,
            variant=request.variant,
            weight=request.weight,
            mutations=request.mutations,
            plant_amount=request.plant_amount
        )
        return result
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.get("/plants", response_model=PlantListResponse)
async def get_plants():
    """Get list of all available plants."""
    plants_data = calculator_service.get_plants()
    plant_names = [plant.name for plant in plants_data]
    return PlantListResponse(plants=plant_names)


@router.get("/variants", response_model=VariantListResponse)
async def get_variants():
    """Get list of all available variants."""
    return VariantListResponse(variants=calculator_service.get_variants())


@router.get("/mutations", response_model=MutationListResponse)
async def get_mutations():
    """Get list of all available mutations."""
    return MutationListResponse(mutations=calculator_service.get_mutations())


@router.get("/plant/{plant_name}")
async def get_plant_data(plant_name: str):
    """Get data for a specific plant."""
    try:
        plant_data = calculator_service.get_plant_data(plant_name)
        return {
            "name": plant_data.name,
            "base_weight": plant_data.base_weight,
            "base_price": plant_data.base_price,
            "rarity": plant_data.rarity
        }
    except KeyError:
        raise HTTPException(status_code=404, detail="Plant not found")


@router.post("/mutation-multiplier")
async def calculate_mutation_multiplier(mutations: List[str]):
    """Calculate mutation multiplier for given mutations."""
    try:
        multiplier = calculator_service.calculate_mutation_multiplier(mutations)
        return {
            "mutations": mutations,
            "multiplier": multiplier,
            "total_mutations": len(mutations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.get("/weight-range/{plant_name}")
async def get_weight_range(plant_name: str):
    """Get expected weight range for a plant."""
    try:
        weight_range = calculator_service.get_weight_range(plant_name)
        return weight_range
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Plant '{plant_name}' not found")


@router.post("/share-batch")
async def share_batch_results(request: dict):
    """Share batch calculation results."""
    try:
        from services.shared_results_service import shared_results_service
        from services.discord_webhook_service import discord_webhook_service
        import time
        import random

        # Generate unique share ID
        share_id = f"batch_{int(time.time())}_{random.randint(1000, 9999)}"

        # Create batch share data
        batch_data = {
            "share_id": share_id,
            "type": "batch",
            "plants": request.get("plants", []),
            "total_value": sum(plant.get("total", 0) for plant in request.get("plants", [])),
            "total_plants": sum(plant.get("quantity", 0) for plant in request.get("plants", [])),
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }

        # Save to database
        success = shared_results_service.create_shared_result(batch_data)

        if success:
            # Send Discord webhook notification (non-blocking)
            try:
                webhook_data = batch_data.copy()
                webhook_data['result_type'] = 'batch'
                await discord_webhook_service.send_calculation_result(webhook_data)
            except Exception as e:
                # Don't fail the share creation if webhook fails
                print(f"Failed to send Discord webhook: {e}")

            return {
                "share_id": share_id,
                "message": "Batch results shared successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save batch results")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to share batch results: {str(e)}")


@router.post("/js-detection")
async def js_detection_check(request: dict):
    """Endpoint to detect JavaScript-enabled browsers for bot analysis."""
    # This endpoint helps distinguish real browsers from bots
    # Real browsers will execute JavaScript and call this endpoint
    return {"status": "ok", "js_detected": True}


@router.get("/logs")
async def get_tracking_logs():
    """Get tracking service logs for debugging."""
    try:
        from services.tracking_service import get_log_entries
        logs = get_log_entries()
        return {
            "logs": logs,
            "total_entries": len(logs),
            "max_entries": 100
        }
    except Exception as e:
        return {
            "error": f"Failed to retrieve logs: {str(e)}",
            "logs": [],
            "total_entries": 0
        }
