"""
Calculator service containing the core business logic.
"""
import json
import os
from typing import Dict, List
from pathlib import Path
import logging

from models.calculator import PlantData, VariantData, MutationData, CalculationResponse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CalculatorService:
    """Service class for plant value calculations."""
    
    def __init__(self):
        """Initialize the service by loading data files."""
        self.data_dir = Path(__file__).parent.parent / "data"
        self.plants: Dict[str, PlantData] = {}
        self.variants: Dict[str, VariantData] = {}
        self.mutations: Dict[str, MutationData] = {}
        
        logger.info(f"CalculatorService initializing...")
        logger.info(f"Current file: {__file__}")
        logger.info(f"Data directory: {self.data_dir}")
        logger.info(f"Data directory exists: {self.data_dir.exists()}")
        logger.info(f"Working directory: {Path.cwd()}")
        
        # List all files in data directory if it exists
        if self.data_dir.exists():
            logger.info("Files found in data directory:")
            for file in self.data_dir.iterdir():
                logger.info(f"  - {file.name}")
        else:
            logger.error(f"Data directory does not exist: {self.data_dir}")
        
        self._load_data()
    
    def _load_data(self) -> None:
        """Load plant, variant, and mutation data from JSON files."""
        logger.info("Starting data loading process...")
        
        try:
            # Load plants
            plants_file = self.data_dir / "plants.json"
            logger.info(f"Loading plants from: {plants_file}")
            logger.info(f"Plants file exists: {plants_file.exists()}")
            
            if not plants_file.exists():
                logger.error(f"Plants file not found: {plants_file}")
                return
            
            with open(plants_file, 'r', encoding='utf-8') as f:
                plants_data = json.load(f)
                logger.info(f"Successfully loaded plants.json with {len(plants_data)} plants")
                
                for name, data in plants_data.items():
                    try:
                        # Check if all required fields exist
                        if "base_weight" not in data:
                            logger.error(f"Plant {name} missing base_weight field")
                            logger.error(f"Plant data: {data}")
                            continue
                        if "base_price" not in data:
                            logger.error(f"Plant {name} missing base_price field")
                            logger.error(f"Plant data: {data}")
                            continue
                        if "rarity" not in data:
                            logger.error(f"Plant {name} missing rarity field")
                            logger.error(f"Plant data: {data}")
                            continue
                        
                        self.plants[name] = PlantData(
                            name=name,
                            base_weight=data["base_weight"],
                            base_price=data["base_price"],
                            rarity=data["rarity"]
                        )
                        logger.debug(f"Successfully loaded plant: {name}")
                        
                    except KeyError as e:
                        logger.error(f"Plant {name} missing required field: {e}")
                        logger.error(f"Plant data: {data}")
                    except Exception as e:
                        logger.error(f"Error loading plant {name}: {e}")
                        logger.error(f"Plant data: {data}")
                
                logger.info(f"Successfully loaded {len(self.plants)} plants")
                
        except FileNotFoundError as e:
            logger.error(f"Plants file not found: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in plants file: {e}")
        except Exception as e:
            logger.error(f"Failed to load plants: {e}")
            logger.error(f"Data directory: {self.data_dir}")
            logger.error(f"Current working directory: {Path.cwd()}")
        
        try:
            # Load variants
            variants_file = self.data_dir / "variants.json"
            logger.info(f"Loading variants from: {variants_file}")
            logger.info(f"Variants file exists: {variants_file.exists()}")
            
            if not variants_file.exists():
                logger.error(f"Variants file not found: {variants_file}")
                return
            
            with open(variants_file, 'r', encoding='utf-8') as f:
                variants_data = json.load(f)
                logger.info(f"Successfully loaded variants.json with {len(variants_data)} variants")
                
                for name, data in variants_data.items():
                    try:
                        if "multiplier" not in data:
                            logger.error(f"Variant {name} missing multiplier field")
                            logger.error(f"Variant data: {data}")
                            continue
                        
                        self.variants[name] = VariantData(
                            name=name,
                            multiplier=data["multiplier"]
                        )
                        logger.debug(f"Successfully loaded variant: {name}")
                        
                    except KeyError as e:
                        logger.error(f"Variant {name} missing required field: {e}")
                        logger.error(f"Variant data: {data}")
                    except Exception as e:
                        logger.error(f"Error loading variant {name}: {e}")
                        logger.error(f"Variant data: {data}")
                
                logger.info(f"Successfully loaded {len(self.variants)} variants")
                
        except FileNotFoundError as e:
            logger.error(f"Variants file not found: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in variants file: {e}")
        except Exception as e:
            logger.error(f"Failed to load variants: {e}")
        
        try:
            # Load mutations
            mutations_file = self.data_dir / "mutations.json"
            logger.info(f"Loading mutations from: {mutations_file}")
            logger.info(f"Mutations file exists: {mutations_file.exists()}")
            
            if not mutations_file.exists():
                logger.error(f"Mutations file not found: {mutations_file}")
                return
            
            with open(mutations_file, 'r', encoding='utf-8') as f:
                mutations_data = json.load(f)
                logger.info(f"Successfully loaded mutations.json with {len(mutations_data)} mutations")
                
                for name, data in mutations_data.items():
                    try:
                        if "value_multi" not in data:
                            logger.error(f"Mutation {name} missing value_multi field")
                            logger.error(f"Mutation data: {data}")
                            continue
                        
                        self.mutations[name] = MutationData(
                            name=name,
                            value_multi=data["value_multi"]
                        )
                        logger.debug(f"Successfully loaded mutation: {name}")
                        
                    except KeyError as e:
                        logger.error(f"Mutation {name} missing required field: {e}")
                        logger.error(f"Mutation data: {data}")
                    except Exception as e:
                        logger.error(f"Error loading mutation {name}: {e}")
                        logger.error(f"Mutation data: {data}")
                
                logger.info(f"Successfully loaded {len(self.mutations)} mutations")
                
        except FileNotFoundError as e:
            logger.error(f"Mutations file not found: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in mutations file: {e}")
        except Exception as e:
            logger.error(f"Failed to load mutations: {e}")
        
        # Final summary
        logger.info("=== Data Loading Summary ===")
        logger.info(f"Plants loaded: {len(self.plants)}")
        logger.info(f"Variants loaded: {len(self.variants)}")
        logger.info(f"Mutations loaded: {len(self.mutations)}")
        logger.info(f"Data directory: {self.data_dir}")
        logger.info(f"Data directory exists: {self.data_dir.exists()}")
        logger.info("==========================")
    
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
        logger.info(f"calculate_plant_value called for plant: {plant_name}, variant: {variant}")
        
        # Check if plant exists
        if plant_name not in self.plants:
            logger.error(f"Plant '{plant_name}' not found in plants dictionary!")
            logger.error(f"Available plants: {list(self.plants.keys())[:10]}...")
            raise KeyError(f"Plant '{plant_name}' not found")
        
        # Check if variant exists
        if variant not in self.variants:
            logger.error(f"Variant '{variant}' not found in variants dictionary!")
            logger.error(f"Available variants: {list(self.variants.keys())}")
            raise KeyError(f"Variant '{variant}' not found")
        
        plant_data = self.plants[plant_name]
        variant_data = self.variants[variant]
        
        logger.info(f"Plant data for {plant_name}: base_weight={plant_data.base_weight}, base_price={plant_data.base_price}")
        logger.info(f"Variant data for {variant}: multiplier={variant_data.multiplier}")
        
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
        
        logger.info(f"Calculation complete for {plant_name}: final_value={final_value}, total_value={total_value}")
        
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
        plants_list = sorted(self.plants.values(), key=lambda x: x.name)
        logger.info(f"get_plants() called - returning {len(plants_list)} plants")
        logger.debug(f"Plant names: {[p.name for p in plants_list[:5]]}...")  # First 5 plants
        return plants_list
    
    def get_variants(self) -> List[VariantData]:
        """Get list of all variants."""
        variants_list = list(self.variants.values())
        logger.info(f"get_variants() called - returning {len(variants_list)} variants")
        logger.debug(f"Variant names: {[v.name for v in variants_list]}")
        return variants_list
    
    def get_mutations(self) -> List[MutationData]:
        """Get sorted list of all mutations."""
        mutations_list = sorted(self.mutations.values(), key=lambda x: x.name)
        logger.info(f"get_mutations() called - returning {len(mutations_list)} mutations")
        logger.debug(f"Mutation names: {[m.name for m in mutations_list[:5]]}...")  # First 5 mutations
        return mutations_list
    
    def get_plant_data(self, plant_name: str) -> PlantData:
        """Get data for a specific plant."""
        plant_data = self.plants.get(plant_name)
        if plant_data:
            logger.info(f"get_plant_data('{plant_name}') - found plant with base_weight: {plant_data.base_weight}")
        else:
            logger.error(f"get_plant_data('{plant_name}') - plant not found!")
            logger.error(f"Available plants: {list(self.plants.keys())[:10]}...")  # First 10 plant names
        return plant_data
    
    def get_weight_range(self, plant_name: str) -> Dict[str, float]:
        """
        Get expected weight range for a plant (base_weight * 0.7 to base_weight * 1.4).
        Based on the UI version's weight range calculation.
        """
        logger.info(f"get_weight_range('{plant_name}') called")
        
        plant_data = self.plants.get(plant_name)
        if not plant_data:
            logger.error(f"get_weight_range('{plant_name}') - plant not found!")
            logger.error(f"Available plants: {list(self.plants.keys())[:10]}...")  # First 10 plant names
            return {"min": 0.0, "max": 0.0}
        
        base_weight = plant_data.base_weight
        logger.info(f"get_weight_range('{plant_name}') - base_weight: {base_weight}")
        
        min_weight = round(base_weight * 0.7, 4)
        max_weight = round(base_weight * 1.4, 4)
        
        result = {
            "min": min_weight,
            "max": max_weight,
            "base": base_weight
        }
        
        logger.info(f"get_weight_range('{plant_name}') - returning: {result}")
        return result


# Global service instance
calculator_service = CalculatorService()
