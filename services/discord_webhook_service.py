"""
Discord webhook service for sending shared calculation results.
"""
import os
import json
import logging
from typing import Optional, Dict, Any
import aiohttp
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)


class DiscordWebhookService:
    """Service for sending Discord webhooks with calculation results."""
    
    def __init__(self):
        """Initialize the Discord webhook service."""
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        self.enabled = bool(self.webhook_url)
        
        if self.enabled:
            logger.info("Discord webhook service initialized")
        else:
            logger.warning("Discord webhook service disabled - DISCORD_WEBHOOK_URL not set")
    
    async def send_calculation_result(self, share_data: Dict[str, Any]) -> bool:
        """Send a calculation result to Discord webhook."""
        if not self.enabled:
            logger.info("Discord webhook disabled, skipping notification")
            return False
        
        try:
            embed = self._create_calculation_embed(share_data)
            
            webhook_data = {
                "embeds": [embed],
                "username": "Grow Calculator 🌱",
                "avatar_url": "https://www.fruitcalculator.dohmboy64.com/static/img/calcsymbol.png"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=webhook_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 204:
                        logger.info(f"Discord webhook sent successfully for share: {share_data.get('share_id', 'unknown')}")
                        return True
                    else:
                        logger.error(f"Discord webhook failed with status {response.status}: {await response.text()}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending Discord webhook: {e}")
            return False
    
    def _create_calculation_embed(self, share_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Discord embed for the calculation result."""
        # Get plant image URL
        plant_name = share_data.get('plant', 'Unknown Plant')
        plant_image_url = f"https://www.fruitcalculator.dohmboy64.com/static/img/crop-{plant_name.lower().replace(' ', '-')}.webp"
        
        # Format mutations for display with bullet points
        mutations = share_data.get('mutations', [])
        mutations_text = "\n".join([f"• {mutation}" for mutation in mutations]) if mutations else "None"
        
        # Use the specific color from your example (3447003 = 0x3498DB - blue)
        color = 3447003
        
        # Create embed matching your exact format
        embed = {
            "title": f"🌱 {plant_name} (Gold) Calculation Shared!",
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
                    "value": f"**Per Plant:** `{share_data.get('result_value', '0')}` sheckles\n**Total:** `{share_data.get('total_value', '0')}` sheckles\n**Multiplier:** `{share_data.get('total_multiplier', '1x')}`",
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


# Create a single instance
discord_webhook_service = DiscordWebhookService()
