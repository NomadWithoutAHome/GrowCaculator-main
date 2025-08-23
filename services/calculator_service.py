"""
Calculator service containing the core business logic.
"""
import json
import os
from typing import Dict, List
from pathlib import Path

from models.calculator import PlantData, VariantData, MutationData, CalculationResponse


class CalculatorService:
    """Service class for plant value calculations."""
    
    def __init__(self):
        """Initialize the service by loading data files."""
        self.data_dir = Path(__file__).parent.parent / "data"
        self.plants: Dict[str, PlantData] = {}
        self.variants: Dict[str, VariantData] = {}
        self.mutations: Dict[str, MutationData] = {}
        self._load_data()
    
    def _load_data(self) -> None:
        """Load plant, variant, and mutation data from JSON files."""
        # Load plants
        plants_file = self.data_dir / "plants.json"
        with open(plants_file, 'r', encoding='utf-8') as f:
            plants_data = json.load(f)
            for name, data in plants_data.items():
                self.plants[name] = PlantData(
                    name=name,
                    base_weight=data["base_weight"],
                    base_price=data["base_price"],
                    rarity=data["rarity"]
                )
        
        # Load variants
        variants_file = self.data_dir / "variants.json"
        with open(variants_file, 'r', encoding='utf-8') as f:
            variants_data = json.load(f)
            for name, data in variants_data.items():
                self.variants[name] = VariantData(
                    name=name,
                    multiplier=data["multiplier"]
                )
        
        # Load mutations
        mutations_file = self.data_dir / "mutations.json"
        with open(mutations_file, 'r', encoding='utf-8') as f:
            mutations_data = json.load(f)
            for name, data in mutations_data.items():
                self.mutations[name] = MutationData(
                    name=name,
                    value_multi=data["value_multi"]
                )
    
    def calculate_mutation_multiplier(self, selected_mutations: List[str]) -> float:
        """
        Calculate mutation multiplier using the additive game formula.
        Formula: total = 1 + (mut1-1) + (mut2-1) + (mut3-1) + ...
        """
        if not selected_mutations:
            return 1.0
        
        total = 1.0
        for mutation_name in selected_mutations:
            mutation_data = self.mutations.get(mutation_name)
            if not mutation_data:
                continue
            
            value_multi = mutation_data.value_multi
            # Add (ValueMulti - 1) to total, as per game source code
            total = total + (value_multi - 1)
        
        # Ensure minimum value is 1
        return max(1.0, total)
    
    def calculate_plant_value(
        self,
        plant_name: str,
        variant: str,
        weight: float,
        mutation_multi: float,
        plant_amount: int = 1
    ) -> CalculationResponse:
        """
        Calculate plant value using the exact formula from the game.
        """
        plant_data = self.plants[plant_name]
        variant_data = self.variants[variant]
        
        # Calculate base value
        base_price = plant_data.base_price
        base_weight = plant_data.base_weight
        variant_multiplier = variant_data.multiplier
        
        # Base value = base_price * mutation_multi * variant_multi
        base_value = base_price * mutation_multi * variant_multiplier
        
        # Weight ratio calculation
        weight_ratio = weight / base_weight
        
        # Clamp weight ratio (minimum 0.95, maximum 100000000)
        clamped_ratio = max(0.95, min(weight_ratio, 100000000))
        
        # Final value = base_value * (clamped_ratio^2)
        final_value = base_value * (clamped_ratio * clamped_ratio)
        
        # Calculate bulk totals
        total_value = round(final_value) * plant_amount
        
        return CalculationResponse(
            plant_name=plant_name,
            variant=variant,
            weight=weight,
            mutations=[],  # Will be filled by the calling function
            mutation_multiplier=mutation_multi,
            base_value=base_value,
            weight_ratio=weight_ratio,
            final_value=round(final_value),
            plant_amount=plant_amount,
            total_value=total_value
        )
    
    def calculate_full_value(
        self,
        plant_name: str,
        variant: str,
        weight: float,
        mutations: List[str],
        plant_amount: int = 1
    ) -> CalculationResponse:
        """
        Calculate full plant value including mutations.
        """
        # Calculate mutation multiplier
        mutation_multi = self.calculate_mutation_multiplier(mutations)
        
        # Calculate plant value
        result = self.calculate_plant_value(
            plant_name, variant, weight, mutation_multi, plant_amount
        )
        
        # Add mutations to response
        result.mutations = mutations
        
        return result
    
    def get_plants(self) -> List[PlantData]:
        """Get sorted list of all plant data objects."""
        return sorted(self.plants.values(), key=lambda x: x.name)
    
    def get_variants(self) -> List[VariantData]:
        """Get list of all variants."""
        return list(self.variants.values())
    
    def get_mutations(self) -> List[MutationData]:
        """Get sorted list of all mutations."""
        return sorted(self.mutations.values(), key=lambda x: x.name)
    
    def get_plant_data(self, plant_name: str) -> PlantData:
        """Get data for a specific plant."""
        return self.plants[plant_name]
    
    def get_weight_range(self, plant_name: str) -> Dict[str, float]:
        """
        Get expected weight range for a plant (base_weight * 0.7 to base_weight * 1.4).
        Based on the UI version's weight range calculation.
        """
        plant_data = self.plants.get(plant_name)
        if not plant_data:
            return {"min": 0.0, "max": 0.0}
        
        base_weight = plant_data.base_weight
        min_weight = round(base_weight * 0.7, 4)
        max_weight = round(base_weight * 1.4, 4)
        
        return {
            "min": min_weight,
            "max": max_weight,
            "base": base_weight
        }


# Global service instance
calculator_service = CalculatorService()
