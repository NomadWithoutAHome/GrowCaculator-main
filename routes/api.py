"""
API routes for calculator functionality.
"""
from typing import List
from fastapi import APIRouter, HTTPException

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
    return PlantListResponse(plants=calculator_service.get_plant_names())


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
