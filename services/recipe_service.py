"""
Recipe service for managing food recipes and generating random ingredient combinations.
"""
import json
import logging
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

class RecipeService:
    def __init__(self):
        self.recipes_data: Dict = {}
        self.cooking_data: Dict = {}
        self.traits_data: Dict = {}
        self.category_to_items: Dict[str, List[str]] = {}
        self._load_data()
        self._build_category_mapping()
    
    def _load_data(self) -> None:
        """Load recipe, cooking, and traits data from JSON files."""
        try:
            # Try multiple path resolution strategies for Vercel compatibility
            possible_paths = [
                Path(__file__).parent.parent / "data",  # Local development
                Path("/var/task/data"),  # Vercel serverless
                Path("data"),  # Current working directory
            ]
            
            data_dir = None
            for path in possible_paths:
                if path.exists():
                    data_dir = path
                    logger.info(f"Found data directory at: {data_dir}")
                    break
            
            if not data_dir:
                logger.error("Could not find data directory in any of the expected locations")
                return
            
            # Load recipes data
            recipes_file = data_dir / "recipes.json"
            if recipes_file.exists():
                with open(recipes_file, 'r', encoding='utf-8') as f:
                    self.recipes_data = json.load(f)
                logger.info(f"Loaded {len(self.recipes_data)} recipes")
            else:
                logger.error(f"Recipes file not found at: {recipes_file}")
            
            # Load cooking data
            cooking_file = data_dir / "cooking.json"
            if cooking_file.exists():
                with open(cooking_file, 'r', encoding='utf-8') as f:
                    self.cooking_data = json.load(f)
                logger.info(f"Loaded {len(self.cooking_data)} cooking items")
            else:
                logger.error(f"Cooking file not found at: {cooking_file}")
            
            # Load traits data
            traits_file = data_dir / "traits.json"
            if traits_file.exists():
                with open(traits_file, 'r', encoding='utf-8') as f:
                    self.traits_data = json.load(f)
                logger.info(f"Loaded {len(self.traits_data)} plants with traits")
            else:
                logger.error(f"Traits file not found at: {traits_file}")
            
        except Exception as e:
            logger.error(f"Failed to load recipe data: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _build_category_mapping(self) -> None:
        """Build reverse mapping: category -> items from cooking.json."""
        try:
            logger.info(f"Building category mapping from {len(self.cooking_data)} cooking items")
            self.category_to_items = {}
            for item, cats in self.cooking_data.items():
                for cat in cats:
                    self.category_to_items.setdefault(cat, []).append(item)
            logger.info(f"Built category mapping for {len(self.category_to_items)} categories")
            logger.info(f"Category keys: {list(self.category_to_items.keys())}")
        except Exception as e:
            logger.error(f"Failed to build category mapping: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.category_to_items = {}
    
    def resolve_trait(self, trait: str) -> List[str]:
        """Return all items in traits.json that have a given trait."""
        return [item for item, ts in self.traits_data.items() if trait in ts]
    
    def resolve_herbalbase(self) -> List[str]:
        """Return flowers that are not toxic, plus Mint if available."""
        items = [item for item, ts in self.traits_data.items() 
                 if "Flower" in ts and "Toxic" not in ts]
        if "Mint" in self.traits_data:
            items.append("Mint")
        return items
    
    def resolve_filling(self) -> List[str]:
        """Filling = all vegetables + meat items (composite category)."""
        vegetable_items = self.resolve_trait("Vegetable")
        meat_items = self.category_to_items.get("Meat", [])
        return list(set(vegetable_items + meat_items))
    
    def resolve_category(self, cat: str) -> List[str]:
        """
        Return all possible items for a category.
        Merges cooking.json fixed items and traits.json items for trait-based categories.
        """
        # Category resolvers (exact copy from Python tool)
        CATEGORY_RESOLVERS = {
            "Bread": lambda: self.category_to_items.get("Bread", []),
            "Meat": lambda: self.category_to_items.get("Meat", []),
            "Leafy": lambda: self.category_to_items.get("Leafy", []),
            "Pastry": lambda: self.category_to_items.get("Pastry", []),
            "Tomato": lambda: self.category_to_items.get("Tomato", []),
            "Fruit": lambda: self.resolve_trait("Fruit"),
            "Vegetable": lambda: self.resolve_trait("Vegetable"),
            "Sweet": lambda: self.resolve_trait("Sweet"),
            "Sauce": lambda: self.resolve_trait("Fruit"),
            "Cone": lambda: self.category_to_items.get("Bread", []),
            "Cream": lambda: self.category_to_items.get("Bread", []),
            "Base": lambda: self.category_to_items.get("Bread", []),
            "Stick": lambda: self.resolve_trait("Woody"),
            "Icing": lambda: self.resolve_trait("Sweet"),
            "Sprinkles": lambda: self.resolve_trait("Sweet"),
            "CandyCoating": lambda: self.resolve_trait("Sweet"),
            "Sweetener": lambda: self.resolve_trait("Sweet"),
            "HerbalBase": lambda: self.resolve_herbalbase(),
            "Filling": lambda: self.resolve_filling(),
            "Bamboo": lambda: self.category_to_items.get("Bamboo", []),
            "Wrap": lambda: self.category_to_items.get("Wrap", []),
            "Rice": lambda: self.category_to_items.get("Rice", []),
            "Woody": lambda: self.resolve_trait("Woody"),  # Woody trait for Stick ingredients
            "Apple": lambda: self.category_to_items.get("Apple", []),
            "Batter": lambda: self.category_to_items.get("Batter", []),
            "Pasta": lambda: self.category_to_items.get("Bread", []),  # Pasta uses same plants as Bread
            "Vegetables": lambda: self.resolve_trait("Vegetable"),
            "Main": lambda: list(set(self.category_to_items.get("Meat", []) + self.resolve_trait("Vegetable")))
        }
        
        resolver = CATEGORY_RESOLVERS.get(cat)
        items = resolver() if callable(resolver) else []
        
        # Merge with cooking.json fixed items if not already included
        fixed_items = self.category_to_items.get(cat, [])
        return list(set(items) | set(fixed_items))
    
    def pick_items(self, cat: str, count: int) -> List[Dict]:
        """Randomly pick items for a category, respecting count."""
        items = self.resolve_category(cat)
        if not items:
            return []
        picks = random.sample(items, min(count, len(items)))
        return [{"item": p, "traits": self.traits_data.get(p, [])} for p in picks]
    
    def generate_random_recipe(self, recipe_name: str) -> Dict:
        """Generate a random recipe with random ingredient combinations."""
        # Handle URL-encoded recipe names (e.g., "Corn%20Dog" -> "Corn Dog")
        import urllib.parse
        decoded_recipe_name = urllib.parse.unquote(recipe_name)
        
        if decoded_recipe_name not in self.recipes_data:
            raise ValueError(f"Recipe '{decoded_recipe_name}' not found")
        
        recipe = self.recipes_data[decoded_recipe_name]
        requirements = recipe["ingredients"]
        
        chosen = {}
        for cat, count in requirements.items():
            if cat == "Any":
                # For "Any" category, pick from all available plants
                items = random.sample(list(self.traits_data.keys()), min(count, len(self.traits_data)))
                chosen[cat] = [{"item": p, "traits": self.traits_data.get(p, [])} for p in items]
            else:
                chosen[cat] = self.pick_items(cat, count)
        
        return {
            "recipe_name": recipe_name,
            "recipe_data": recipe,
            "ingredients": chosen
        }
    
    def get_all_recipes(self) -> Dict:
        """Get all available recipes."""
        return self.recipes_data
    
    def get_recipe(self, recipe_name: str) -> Optional[Dict]:
        """Get a specific recipe by name."""
        # Handle URL-encoded recipe names (e.g., "Corn%20Dog" -> "Corn Dog")
        import urllib.parse
        decoded_recipe_name = urllib.parse.unquote(recipe_name)
        return self.recipes_data.get(decoded_recipe_name)
    
    def get_recipe_categories(self) -> Dict[str, List[str]]:
        """Get all ingredient categories and their available items."""
        try:
            logger.info("get_recipe_categories called")
            logger.info(f"category_to_items keys: {list(self.category_to_items.keys())}")
            logger.info(f"cooking_data loaded: {len(self.cooking_data)} items")
            logger.info(f"traits_data loaded: {len(self.traits_data)} items")
            
            # Safety check - if category_to_items is empty, rebuild it
            if not self.category_to_items:
                logger.warning("category_to_items is empty, rebuilding...")
                self._build_category_mapping()
                logger.info(f"Rebuilt category mapping: {len(self.category_to_items)} categories")
            
            categories = {}
            # Only include categories that actually have resolvers defined
            # This ensures we don't try to resolve categories that don't exist
            all_categories = set(self.category_to_items.keys()) | {
                "Fruit", "Vegetable", "Sweet", "Filling", "Main",
                "Sauce", "Cone", "Cream", "Base", "Icing", "Sprinkles", 
                "CandyCoating", "Sweetener", "HerbalBase", "Bamboo", "Wrap",
                "Rice", "Apple", "Batter", "Vegetables", "Stick", "Woody", "Pasta"
            }
            
            logger.info(f"Processing {len(all_categories)} categories")
            
            for cat in all_categories:
                try:
                    categories[cat] = self.resolve_category(cat)
                    logger.debug(f"Category {cat}: {len(categories[cat])} items")
                except Exception as e:
                    logger.warning(f"Failed to resolve category '{cat}': {e}")
                    categories[cat] = []  # Return empty list for failed categories
            
            logger.info(f"Successfully processed {len(categories)} categories")
            return categories
            
        except Exception as e:
            logger.error(f"get_recipe_categories failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def get_recipes_by_difficulty(self, difficulty: str = None) -> List[Tuple[str, Dict]]:
        """Get recipes filtered by difficulty (Easy: 1-2 ingredients, Medium: 3-4, Hard: 5+)"""
        recipes = []
        for name, recipe in self.recipes_data.items():
            ingredient_count = recipe["count"]
            if difficulty == "Easy" and ingredient_count <= 2:
                recipes.append((name, recipe))
            elif difficulty == "Medium" and 3 <= ingredient_count <= 4:
                recipes.append((name, recipe))
            elif difficulty == "Hard" and ingredient_count >= 5:
                recipes.append((name, recipe))
            elif difficulty is None:
                recipes.append((name, recipe))
        
        # Sort by priority (lower number = higher priority)
        recipes.sort(key=lambda x: x[1]["priority"])
        return recipes
    
    def search_recipes(self, query: str) -> List[Tuple[str, Dict]]:
        """Search recipes by name or description."""
        query = query.lower()
        results = []
        
        for name, recipe in self.recipes_data.items():
            if (query in name.lower() or 
                query in recipe.get("description", "").lower()):
                results.append((name, recipe))
        
        return results
    
    def get_cooking_mechanics(self) -> Dict:
        """Get information about how cooking works in the game."""
        return {
            "base_time": "Cooking time in seconds (base value)",
            "base_weight": "Weight of the cooked food in kg",
            "priority": "Recipe priority (lower number = higher priority)",
            "count": "Number of ingredient categories required",
            "ingredients": "Ingredient categories and quantities needed",
            "categories": "Available ingredient categories and what plants can be used"
        }
    
    def calculate_recipe_combinations(self, recipe_name: str) -> int:
        """Calculate total possible combinations for a recipe."""
        if recipe_name not in self.recipes_data:
            return 0
        
        recipe = self.recipes_data[recipe_name]
        total_combinations = 1
        
        for category, count in recipe["ingredients"].items():
            if category == "Any":
                # For "Any" category, use all available plants
                available_items = len(self.traits_data)
                # Calculate combinations: C(n, r) = n! / (r! * (n-r)!)
                if count <= available_items:
                    combinations = self._calculate_combinations(available_items, count)
                    total_combinations *= combinations
            else:
                available_items = len(self.resolve_category(category))
                if available_items > 0 and count <= available_items:
                    combinations = self._calculate_combinations(available_items, count)
                    total_combinations *= combinations
        
        return total_combinations
    
    def _calculate_combinations(self, n: int, r: int) -> int:
        """Calculate C(n,r) = n! / (r! * (n-r)!)"""
        if r > n:
            return 0
        if r == 0 or r == n:
            return 1
        
        # Use a more efficient calculation to avoid large numbers
        r = min(r, n - r)
        result = 1
        for i in range(r):
            result = result * (n - i) // (i + 1)
        return result
    
    def get_all_recipes_with_stats(self) -> Dict:
        """Get all recipes with combination statistics."""
        recipes_with_stats = {}
        
        for name, recipe in self.recipes_data.items():
            combinations = self.calculate_recipe_combinations(name)
            recipes_with_stats[name] = {
                **recipe,
                "possible_combinations": combinations,
                "combinations_formatted": self._format_large_number(combinations)
            }
        
        return recipes_with_stats
    
    def _format_large_number(self, num: int) -> str:
        """Format large numbers with K, M, B suffixes."""
        if num < 1000:
            return str(num)
        elif num < 1000000:
            return f"{num/1000:.1f}K"
        elif num < 1000000000:
            return f"{num/1000000:.1f}M"
        else:
            return f"{num/1000000000:.1f}B"

# Global instance
recipe_service = RecipeService()
