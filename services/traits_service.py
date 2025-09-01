"""
Traits service for managing plant trait data and searches.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

class TraitsService:
    def __init__(self):
        self.traits_data: Dict[str, List[str]] = {}
        self.trait_counts: Dict[str, int] = {}
        self.plants_by_trait_count: List[Tuple[str, int]] = []
        self._load_traits()
    
    def _load_traits(self) -> None:
        """Load plant traits data from JSON file."""
        try:
            # Use the same path resolution as calculator_service.py
            current_file = Path(__file__)
            data_dir = current_file.parent.parent / "data"
            traits_file = data_dir / "traits.json"
            
            logger.info(f"Loading traits from: {traits_file}")
            
            if not traits_file.exists():
                logger.error(f"Traits file not found: {traits_file}")
                return
            
            with open(traits_file, 'r', encoding='utf-8') as f:
                self.traits_data = json.load(f)
            
            logger.info(f"Loaded {len(self.traits_data)} plants with traits")
            
            # Calculate trait statistics
            self._calculate_trait_counts()
            self._calculate_plants_by_trait_count()
            
        except Exception as e:
            logger.error(f"Failed to load traits: {e}")
    
    def _calculate_trait_counts(self) -> None:
        """Calculate how many times each trait appears."""
        self.trait_counts = {}
        for plant, traits in self.traits_data.items():
            for trait in traits:
                self.trait_counts[trait] = self.trait_counts.get(trait, 0) + 1
        
        logger.info(f"Calculated counts for {len(self.trait_counts)} unique traits")
    
    def _calculate_plants_by_trait_count(self) -> None:
        """Sort plants by number of traits (most to least)."""
        self.plants_by_trait_count = [
            (plant, len(traits)) 
            for plant, traits in self.traits_data.items()
        ]
        self.plants_by_trait_count.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Sorted {len(self.plants_by_trait_count)} plants by trait count")
    
    def get_plant_traits(self, plant_name: str) -> List[str]:
        """Get traits for a specific plant."""
        decoded_name = self._decode_plant_name(plant_name)
        
        # Try exact match first
        traits = self.traits_data.get(decoded_name, [])
        
        # If no exact match, try case-insensitive search
        if not traits:
            for stored_name in self.traits_data.keys():
                if stored_name.lower() == decoded_name.lower():
                    traits = self.traits_data[stored_name]
                    decoded_name = stored_name  # Use the actual stored name
                    break
        
        return traits
    
    def get_plants_by_trait(self, trait: str) -> List[str]:
        """Get all plants that have a specific trait."""
        trait = trait.strip().lower()
        matching_plants = []
        
        for plant, traits in self.traits_data.items():
            if any(t.lower() == trait for t in traits):
                # Decode plant name before adding to results
                decoded_plant = self._decode_plant_name(plant)
                matching_plants.append(decoded_plant)
        
        return matching_plants
    
    def get_trait_statistics(self) -> Dict:
        """Get comprehensive trait statistics."""
        # Most common traits
        most_common_traits = sorted(
            self.trait_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        # Plants with most traits
        plants_most_traits = self.plants_by_trait_count[:10]
        
        # Total counts
        total_plants = len(self.traits_data)
        total_unique_traits = len(self.trait_counts)
        total_trait_assignments = sum(self.trait_counts.values())
        
        return {
            "most_common_traits": most_common_traits,
            "plants_most_traits": plants_most_traits,
            "total_plants": total_plants,
            "total_unique_traits": total_unique_traits,
            "total_trait_assignments": total_trait_assignments,
            "average_traits_per_plant": round(total_trait_assignments / total_plants, 2) if total_plants > 0 else 0
        }
    
    def get_all_plants_traits(self) -> Dict[str, List[str]]:
        """Get all plants with their traits."""
        # Decode all plant names to ensure consistency
        decoded_data = {}
        for plant_name, traits in self.traits_data.items():
            decoded_name = self._decode_plant_name(plant_name)
            decoded_data[decoded_name] = traits
        return decoded_data
    
    def search_plants(self, query: str) -> List[str]:
        """Search plants by name (partial match)."""
        query = query.strip().lower()
        matching_plants = []
        
        for plant_name in self.traits_data.keys():
            if query in plant_name.lower():
                # Decode plant name before adding to results
                decoded_plant = self._decode_plant_name(plant_name)
                matching_plants.append(decoded_plant)
        
        return matching_plants
    
    def search_traits(self, query: str) -> List[str]:
        """Search traits by name (partial match)."""
        query = query.strip().lower()
        matching_traits = []
        
        for trait in self.trait_counts.keys():
            if query in trait.lower():
                matching_traits.append(trait)
        
        return matching_traits
    
    def _decode_plant_name(self, plant_name: str) -> str:
        """Decode URL-encoded plant names (e.g., 'Blue%20Lollipop' -> 'Blue Lollipop')."""
        from urllib.parse import unquote
        decoded_name = unquote(plant_name)
        if decoded_name != plant_name:
            logger.info(f"Decoded plant name: '{plant_name}' -> '{decoded_name}'")
        return decoded_name

# Global instance
traits_service = TraitsService()
