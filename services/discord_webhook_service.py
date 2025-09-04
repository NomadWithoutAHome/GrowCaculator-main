"""
Discord webhook service for sending shared calculation results.
"""
import os
import json
import logging
from typing import Optional, Dict, Any
import httpx
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)


class DiscordWebhookService:
    """Service for sending Discord webhooks with calculation results."""
    
    def __init__(self):
        """Initialize the Discord webhook service."""
        # Main fruit calculation webhook
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        self.enabled = bool(self.webhook_url)
        
        # Recipe webhook (separate channel)
        self.recipe_webhook_url = os.getenv('RECIPE_DISCORD_WEBHOOK_URL', 'https://discord.com/api/webhooks/1412235342479753297/8fpw0FlVyv89SOTVr0ItnGmMM_5j3sMxJ6AnuC-EiNCbvMU1Ib-cfq3ben4bsQXbm12E')
        self.recipe_enabled = bool(self.recipe_webhook_url)
        
        if self.enabled:
            logger.info("Discord webhook service initialized for fruit calculations")
        else:
            logger.warning("Fruit calculation Discord webhook disabled - DISCORD_WEBHOOK_URL not set")
        
        if self.recipe_enabled:
            logger.info("Recipe Discord webhook service initialized")
        else:
            logger.warning("Recipe Discord webhook service disabled")
    
    async def send_calculation_result(self, share_data: Dict[str, Any]) -> bool:
        """Send a calculation result to Discord webhook."""
        # Check the result type and create appropriate embed
        result_type = share_data.get('result_type', 'calculation')
        
        if result_type == 'recipe':
            # Use recipe webhook for recipes
            if not self.recipe_enabled:
                logger.info("Recipe Discord webhook disabled, skipping notification")
                return False
            webhook_url = self.recipe_webhook_url
            embed = self._create_recipe_embed(share_data)
        else:
            # Use main webhook for fruit calculations
            if not self.enabled:
                logger.info("Fruit calculation Discord webhook disabled, skipping notification")
                return False
            webhook_url = self.webhook_url
            if result_type == 'batch':
                embed = self._create_batch_calculation_embed(share_data)
            else:
                embed = self._create_calculation_embed(share_data)
        
        try:
            webhook_data = {"embeds": [embed]}

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,  # type: ignore
                    json=webhook_data,
                    headers={"Content-Type": "application/json"}
                )
            if response.status_code == 204:
                logger.info(f"Discord webhook sent successfully for share: {share_data.get('share_id', 'unknown')}")
                return True
            else:
                logger.error(f"Discord webhook failed with status {response.status_code}: {response.text}")
                return False
                        
        except Exception as e:
            logger.error(f"Error sending Discord webhook: {e}")
            return False
    
    def _format_large_number(self, num: float) -> str:
        """Format large numbers into readable abbreviations (Python equivalent of JavaScript formatLargeNumber)."""
        if num >= 1e21:
            return f"{num / 1e21:.2f} Sextillion"
        elif num >= 1e18:
            return f"{num / 1e18:.2f} Quintillion"
        elif num >= 1e15:
            return f"{num / 1e15:.2f} Quadrillion"
        elif num >= 1e12:
            return f"{num / 1e12:.2f} Trillion"
        elif num >= 1e9:
            return f"{num / 1e9:.2f} Billion"
        elif num >= 1e6:
            return f"{num / 1e6:.2f} Million"
        elif num >= 1e3:
            return f"{num / 1e3:.2f}K"
        else:
            return f"{num:.2f}"
    
    def _format_number_with_commas(self, num: float) -> str:
        """Format numbers with commas (Python equivalent of JavaScript formatNumber)."""
        return f"{int(num):,}"
    
    def _create_calculation_embed(self, share_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Discord embed for the calculation result."""
        # Get plant image URL
        plant_name = share_data.get('plant', 'Unknown Plant')
        plant_image_url = f"https://www.fruitcalculator.dohmboy64.com/static/img/crop-{plant_name.lower().replace(' ', '-')}.webp"
        
        # Format mutations for display with bullet points (show first 4, then +X more)
        mutations = share_data.get('mutations', [])
        if mutations:
            if len(mutations) <= 4:
                # Show all mutations if 4 or fewer
                mutations_text = "\n".join([f"• {mutation}" for mutation in mutations])
            else:
                # Show first 4 mutations, then +X more
                first_four = mutations[:4]
                remaining_count = len(mutations) - 4
                mutations_text = "\n".join([f"• {mutation}" for mutation in first_four]) + f"\n+{remaining_count} more"
        else:
            mutations_text = "None"
        
        # Use the specific color from your example (3447003 = 0x3498DB - blue)
        color = 3447003
        
        # Format values using the same logic as the website
        try:
            # Extract numeric values from the formatted strings
            result_value_str = share_data.get('result_value', '0')
            total_value_str = share_data.get('total_value', '0')
            
            # Try to extract numbers and format them
            result_value_num = float(''.join(filter(str.isdigit, result_value_str)))
            total_value_num = float(''.join(filter(str.isdigit, total_value_str)))
            
            # Apply the same formatting as the website
            formatted_result = self._format_large_number(result_value_num)
            formatted_total = self._format_large_number(total_value_num)
        except:
            # Fallback to original values if parsing fails
            formatted_result = share_data.get('result_value', '0')
            formatted_total = share_data.get('total_value', '0')
        
        # Create embed matching your exact format with proper number formatting
        embed = {
            "title": f"🌱 {plant_name} Calculation Shared!",
            "description": "Someone just shared their calculation results!",
            "url": f"https://www.fruitcalculator.dohmboy64.com/share/{share_data.get('share_id', '')}",
            "color": color,
            "thumbnail": {
                "url": plant_image_url
            },
            "fields": [
                {
                    "name": "🏷️ Plant Details",
                    "value": f"**Plant:** {plant_name}\n**Variant:** {share_data.get('variant', 'Normal')}\n**Amount:** {share_data.get('amount', 1)}\n**Weight:** {share_data.get('weight', 0)} kg",
                    "inline": True
                },
                {
                    "name": "🧬 Mutations",
                    "value": mutations_text,
                    "inline": True
                },
                {
                    "name": "💰 Value Breakdown",
                    "value": f"**Per Plant:** `{formatted_result}` sheckles\n**Total:** `{formatted_total}` sheckles\n**Multiplier:** `{share_data.get('total_multiplier', '1x')}`",
                    "inline": False
                },
                {
                    "name": "📊 Weight Range",
                    "value": f"**Min:** {share_data.get('weight_min', '0')} kg | **Max:** {share_data.get('weight_max', '0')} kg",
                    "inline": True
                }
            ],
            "footer": {
                "text": "Grow Calculator • Share your results with others!",
                "icon_url": "https://www.fruitcalculator.dohmboy64.com/static/img/calcsymbol.png"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return embed

    def _create_batch_calculation_embed(self, share_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Discord embed for batch calculation results."""
        plants = share_data.get('plants', [])
        total_value = share_data.get('total_value', 0)
        total_plants = share_data.get('total_plants', 0)

        # Format total value using the same logic as the website
        try:
            formatted_total = self._format_large_number(total_value)
        except:
            formatted_total = f"{total_value:,}"

        # Calculate average per plant
        avg_per_plant = total_value / total_plants if total_plants > 0 else 0
        try:
            formatted_avg = self._format_large_number(avg_per_plant)
        except:
            formatted_avg = f"{avg_per_plant:,}"

        # Get the most valuable plant for the thumbnail
        most_valuable_plant = None
        if plants:
            most_valuable_plant = max(plants, key=lambda p: p.get('total', 0))
            plant_name = most_valuable_plant.get('plant', 'Unknown Plant')
            plant_image_url = f"https://www.fruitcalculator.dohmboy64.com/static/img/crop-{plant_name.lower().replace(' ', '-')}.webp"
        else:
            plant_image_url = "https://www.fruitcalculator.dohmboy64.com/static/img/calcsymbol.png"

        # Create detailed plant breakdown (show top 2-3 plants with full details)
        plant_details = []
        sorted_plants = sorted(plants, key=lambda p: p.get('total', 0), reverse=True)

        for i, plant in enumerate(sorted_plants[:2]):  # Show top 2 plants
            plant_name = plant.get('plant', 'Unknown Plant')
            variant = plant.get('variant', 'Normal')
            quantity = plant.get('quantity', 1)
            weight = round(float(plant.get('weight', 0)), 4)
            mutations = plant.get('mutations', [])
            plant_value = plant.get('total', 0)

            # Format plant value
            try:
                formatted_plant_value = self._format_large_number(plant_value)
            except:
                formatted_plant_value = f"{plant_value:,}"

            # Format mutations
            if mutations:
                if len(mutations) <= 3:
                    mutations_text = ", ".join(mutations)
                else:
                    mutations_text = ", ".join(mutations[:3]) + f" (+{len(mutations) - 3} more)"
            else:
                mutations_text = "None"

            plant_details.append(
                f"**{plant_name}** ({variant})\n"
                f"• Weight: {weight}kg × {quantity}\n"
                f"• Value: `{formatted_plant_value}` sheckles\n"
                f"• Mutations: {mutations_text}"
            )

        if len(plants) > 2:
            remaining_value = sum(p.get('total', 0) for p in sorted_plants[2:])
            try:
                formatted_remaining = self._format_large_number(remaining_value)
            except:
                formatted_remaining = f"{remaining_value:,}"
            plant_details.append(f"*+{len(plants) - 2} more plants worth `{formatted_remaining}` sheckles*")

        plants_text = "\n\n".join(plant_details)

        # Create title based on batch composition
        if len(plants) == 1:
            plant_name = plants[0].get('plant', 'Unknown Plant')
            title = f"🌱 {plant_name} Batch Shared!"
        elif len(set(p.get('plant') for p in plants)) == 1:
            # All same plant
            plant_name = plants[0].get('plant', 'Unknown Plant')
            title = f"🌱 {plant_name} ×{total_plants} Batch Shared!"
        else:
            # Mixed plants
            title = f"📊 Mixed Batch ({len(plants)} types) Shared!"

        embed = {
            "title": title,
            "description": "Someone just shared their batch calculation results!",
            "url": f"https://www.fruitcalculator.dohmboy64.com/share/{share_data.get('share_id', '')}",
            "color": 3447003,  # Same blue color
            "thumbnail": {
                "url": plant_image_url
            },
            "fields": [
                {
                    "name": "📦 Batch Summary",
                    "value": f"**Total Value:** `{formatted_total}` sheckles\n**Total Plants:** {total_plants}\n**Average per Plant:** `{formatted_avg}` sheckles",
                    "inline": False
                },
                {
                    "name": "🌱 Top Plants",
                    "value": plants_text,
                    "inline": False
                }
            ],
            "footer": {
                "text": "Grow Calculator • Share your results with others!",
                "icon_url": "https://www.fruitcalculator.dohmboy64.com/static/img/calcsymbol.png"
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        return embed

    def _create_recipe_embed(self, share_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Discord embed for recipe sharing."""
        recipe_name = share_data.get('recipe_name', 'Unknown Recipe')
        recipe_data = share_data.get('recipe_data', {})
        ingredients = share_data.get('ingredients', {})
        shop_seeds_only = share_data.get('shop_seeds_only', False)
        description = share_data.get('description', recipe_data.get('description', ''))
        share_id = share_data.get('share_id', 'unknown')
        
        # Get food image URL
        food_image_name = recipe_name.lower().replace(' ', '_')
        food_image_url = f"https://www.fruitcalculator.dohmboy64.com/static/img/food_{food_image_name}.webp"
        
        # Format ingredients for display
        ingredients_text = ""
        for category, items in ingredients.items():
            if isinstance(items, list):
                items_text = []
                for item in items:
                    item_name = item.get('item', 'Unknown')
                    traits = item.get('traits', [])
                    traits_str = f" ({', '.join(traits)})" if traits else ""
                    shop_seed_indicator = "🌱 " if shop_seeds_only else ""
                    items_text.append(f"• {shop_seed_indicator}{item_name}{traits_str}")
                ingredients_text += f"**{category}:**\n" + "\n".join(items_text) + "\n\n"
        
        # Determine embed color based on recipe priority
        priority = recipe_data.get('priority', 10)
        if priority <= 3:
            color = 0x00ff00  # Green for high priority
        elif priority <= 6:
            color = 0xffa500  # Orange for medium priority
        else:
            color = 0xff0000  # Red for low priority
        
        # Create embed
        embed = {
            "title": f"🍽️ {recipe_name} Recipe Generated!",
            "description": f"Someone just generated a random recipe!\n\n{description}",
            "url": f"https://www.fruitcalculator.dohmboy64.com/share/recipe_{share_id}",
            "color": color,
            "thumbnail": {
                "url": food_image_url
            },
            "fields": [
                {
                    "name": "⏱️ Recipe Details",
                    "value": f"**Cooking Time:** {recipe_data.get('base_time', 0)}s\n**Weight:** {recipe_data.get('base_weight', 0)}kg\n**Priority:** {priority}",
                    "inline": True
                },
                {
                    "name": "🌱 Shop Seeds Mode",
                    "value": "✅ Enabled" if shop_seeds_only else "❌ Disabled",
                    "inline": True
                },
                {
                    "name": "🧪 Generated Ingredients",
                    "value": ingredients_text.strip() if ingredients_text else "No ingredients generated",
                    "inline": False
                }
            ],
            "footer": {
                "text": "Grow Calculator • Share your recipes with others!",
                "icon_url": "https://www.fruitcalculator.dohmboy64.com/static/img/calcsymbol.png"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return embed


# Create a single instance
discord_webhook_service = DiscordWebhookService()
