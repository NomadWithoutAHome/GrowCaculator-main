"""
Tracking service for Grow Calculator website analytics and bot detection
"""
import requests
import json
import re
import time
import os
from datetime import datetime
from collections import defaultdict
from typing import Tuple, Optional

# You'll need to add these imports when you set up Redis
# from services.redis_service import redis
# from utils.logging_config import app_logger as logger

# Get webhook URL from environment variable
WEBHOOK_URL = os.environ.get('TRACKING_WEBHOOK')

class TrackingService:
    """Comprehensive tracking service with bot detection"""

    # Known bot user agents
    BOT_USER_AGENTS = [
        'googlebot', 'bingbot', 'slurp', 'duckduckbot', 'baiduspider',
        'yandexbot', 'sogou', 'exabot', 'facebot', 'ia_archiver',
        'crawler', 'spider', 'bot', 'scraper', 'headless', 'selenium',
        'chrome-lighthouse', 'gtmetrix', 'pingdom', 'uptimerobot',
        'ahrefsbot', 'mj12bot', 'dotbot', 'semrushbot'
    ]

    # Suspicious patterns in user agents
    SUSPICIOUS_PATTERNS = [
        r'\b(?:curl|wget|python|scrapy|beautifulsoup|requests)\b',
        r'\b(?:headless|selenium|phantomjs|puppeteer|playwright)\b',
        r'\b(?:bot|crawler|spider|scraper|harvest)\b'
    ]

    # Rate limiting storage (use Redis in production)
    request_counts = defaultdict(list)

    # Map routes to friendly names
    PATH_NAMES = {
        '/': 'Home - Plant Calculator',
        '/mutation-calculator': 'Mutation Calculator',
        '/traits': 'Plant Traits Explorer',
        '/recipes': 'Recipe Generator',
        '/about': 'About Page',
        '/share/': 'Shared Results Page',
        '/api/plants': 'Plants API',
        '/api/mutations': 'Mutations API',
        '/api/variants': 'Variants API',
        '/api/traits/': 'Traits API'
    }

    @staticmethod
    def get_friendly_path_name(path: str) -> str:
        """Convert raw paths to readable names"""
        return TrackingService.PATH_NAMES.get(path, path)

    @staticmethod
    def is_bot(request) -> Tuple[bool, Optional[str]]:
        """Comprehensive bot detection"""
        user_agent = request.headers.get('User-Agent', '').lower()
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)

        # 1. User-Agent Analysis
        if TrackingService._check_user_agent(user_agent):
            return True, "user_agent"

        # 2. Suspicious Patterns
        if TrackingService._check_suspicious_patterns(user_agent):
            return True, "suspicious_pattern"

        # 3. Rate Limiting Check
        if TrackingService._check_rate_limit(ip):
            return True, "rate_limit"

        # 4. Missing Common Headers
        if TrackingService._check_missing_headers(request):
            return True, "missing_headers"

        return False, None

    @staticmethod
    def _check_user_agent(user_agent: str) -> bool:
        """Check against known bot user agents"""
        for bot_ua in TrackingService.BOT_USER_AGENTS:
            if bot_ua in user_agent:
                return True
        return False

    @staticmethod
    def _check_suspicious_patterns(user_agent: str) -> bool:
        """Check for suspicious patterns in user agent"""
        for pattern in TrackingService.SUSPICIOUS_PATTERNS:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def _check_rate_limit(ip: str) -> bool:
        """Check if IP is making requests too frequently"""
        current_time = time.time()
        window_start = current_time - 60  # 1 minute window

        # Clean old requests
        TrackingService.request_counts[ip] = [
            req_time for req_time in TrackingService.request_counts[ip]
            if req_time > window_start
        ]

        # Add current request
        TrackingService.request_counts[ip].append(current_time)

        # Check rate (more than 30 requests per minute = suspicious)
        if len(TrackingService.request_counts[ip]) > 30:
            return True

        return False

    @staticmethod
    def _check_missing_headers(request) -> bool:
        """Check for missing headers that real browsers usually have"""
        headers = request.headers

        # Real browsers usually have these headers
        required_headers = ['Accept', 'Accept-Language']

        for header in required_headers:
            if not headers.get(header):
                return True

        # Check for suspicious Accept header
        accept = headers.get('Accept', '')
        if accept == '*/*' and not headers.get('Referer'):
            # Generic accept without referrer might be a bot
            return True

        return False

    @staticmethod
    def send_webhook(embed: dict):
        """Send embed to Discord webhook"""
        if not WEBHOOK_URL:
            print("Warning: TRACKING_WEBHOOK environment variable not set")
            return

        try:
            payload = {"embeds": [embed]}
            response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
            response.raise_for_status()
        except Exception as e:
            # In production, you'd use proper logging
            print(f"Failed to send webhook: {str(e)}")

    @staticmethod
    def track_visitor(request, path: str):
        """Track new and returning visitors with bot detection"""
        # Check if this is a bot
        is_bot, bot_reason = TrackingService.is_bot(request)

        if is_bot:
            # Log bot activity but don't track as visitor
            TrackingService._log_bot_activity(request, path, bot_reason)
            return

        # Continue with normal visitor tracking
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', 'Unknown')
        referrer = request.headers.get('Referer', 'Direct')

        # Determine navigation type
        is_internal = False
        if referrer != 'Direct':
            is_internal = (
                referrer.startswith(request.host_url) or
                referrer.startswith('/') or
                'dohmboy64.com' in referrer or
                request.host in referrer
            )

        navigation_type = "Internal Navigation" if is_internal else "External Visit"

        # Get friendly path name
        friendly_path = TrackingService.get_friendly_path_name(path)

        # Get location data
        try:
            geo_response = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
            geo_data = geo_response.json()
            location = f"{geo_data.get('city', 'Unknown')}, {geo_data.get('country', 'Unknown')}"
        except:
            location = "Unknown"

        # For now, we'll use a simple in-memory storage
        # In production, you'd use Redis or a database
        visitor_key = f"visitor:{ip}"

        # Check if this is a returning visitor (simplified - you'd use Redis)
        is_returning = hasattr(TrackingService, '_visitor_cache') and \
                       ip in TrackingService._visitor_cache

        if not hasattr(TrackingService, '_visitor_cache'):
            TrackingService._visitor_cache = {}

        if is_returning:
            # Returning visitor
            visitor_data = TrackingService._visitor_cache[ip]
            previous_path = visitor_data.get('current_path')

            visitor_data['visit_count'] += 1
            visitor_data['last_visit'] = datetime.now().isoformat()
            visitor_data['paths'].append(friendly_path)
            visitor_data['location'] = location
            visitor_data['current_path'] = path

            # Send webhook for page changes (except refreshes)
            if previous_path != path:
                embed = {
                    "title": f"🔄 {navigation_type}",
                    "color": 3447003,  # Blue
                    "fields": [
                        {"name": "IP Address", "value": ip, "inline": True},
                        {"name": "Location", "value": location, "inline": True},
                        {"name": "Visit Count", "value": str(visitor_data['visit_count']), "inline": True},
                        {"name": "Previous Page", "value": TrackingService.get_friendly_path_name(previous_path or 'None'), "inline": True},
                        {"name": "Current Page", "value": friendly_path, "inline": True},
                        {"name": "Referrer", "value": referrer, "inline": True},
                        {"name": "User Agent", "value": user_agent[:100], "inline": False}
                    ],
                    "timestamp": datetime.now().isoformat()
                }
                TrackingService.send_webhook(embed)
        else:
            # New visitor
            visitor_data = {
                'ip': ip,
                'first_visit': datetime.now().isoformat(),
                'last_visit': datetime.now().isoformat(),
                'visit_count': 1,
                'paths': [friendly_path],
                'current_path': path,
                'location': location
            }

            embed = {
                "title": "👋 New Visitor",
                "color": 5763719,  # Green
                "fields": [
                    {"name": "IP Address", "value": ip, "inline": True},
                    {"name": "Location", "value": location, "inline": True},
                    {"name": "First Page", "value": friendly_path, "inline": True},
                    {"name": "Navigation", "value": navigation_type, "inline": True},
                    {"name": "Referrer", "value": referrer, "inline": True},
                    {"name": "User Agent", "value": user_agent[:100], "inline": False}
                ],
                "timestamp": datetime.now().isoformat()
            }
            TrackingService.send_webhook(embed)

        # Store visitor data (in production, use Redis with expiration)
        TrackingService._visitor_cache[ip] = visitor_data

    @staticmethod
    def _log_bot_activity(request, path: str, detection_reason: Optional[str]):
        """Log bot activity for monitoring"""
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', 'Unknown')[:200]

        embed = {
            "title": "🤖 Bot Detected",
            "color": 15158332,  # Red
            "fields": [
                {"name": "IP Address", "value": ip, "inline": True},
                {"name": "Detection Method", "value": detection_reason or "Unknown", "inline": True},
                {"name": "Requested Path", "value": path, "inline": True},
                {"name": "User Agent", "value": user_agent, "inline": False}
            ],
            "timestamp": datetime.now().isoformat()
        }

        TrackingService.send_webhook(embed)

    @staticmethod
    def track_feature_usage(request, feature_name: str, details: Optional[str] = None):
        """Track usage of specific features (excluding calculations, batches, and sharing)"""
        # Check if this is a bot
        is_bot, _ = TrackingService.is_bot(request)
        if is_bot:
            return

        ip = request.headers.get('X-Forwarded-For', request.remote_addr)

        try:
            geo_response = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
            geo_data = geo_response.json()
            location = f"{geo_data.get('city', 'Unknown')}, {geo_data.get('country', 'Unknown')}"
        except:
            location = "Unknown"

        embed = {
            "title": f"⚡ Feature Used: {feature_name}",
            "color": 16776960,  # Yellow
            "fields": [
                {"name": "Feature", "value": feature_name, "inline": True},
                {"name": "IP Address", "value": ip, "inline": True},
                {"name": "Location", "value": location, "inline": True},
                {"name": "Details", "value": details or "N/A", "inline": False}
            ],
            "timestamp": datetime.now().isoformat()
        }

        TrackingService.send_webhook(embed)

    @staticmethod
    def track_error(request, error_message: str, context: str = "general"):
        """Track application errors"""
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)

        try:
            geo_response = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
            geo_data = geo_response.json()
            location = f"{geo_data.get('city', 'Unknown')}, {geo_data.get('country', 'Unknown')}"
        except:
            location = "Unknown"

        embed = {
            "title": "❌ Application Error",
            "color": 15158332,  # Red
            "fields": [
                {"name": "Context", "value": context, "inline": True},
                {"name": "IP Address", "value": ip, "inline": True},
                {"name": "Location", "value": location, "inline": True},
                {"name": "Error", "value": error_message[:1000], "inline": False}
            ],
            "timestamp": datetime.now().isoformat()
        }

        TrackingService.send_webhook(embed)

    @staticmethod
    def track_performance(request, endpoint: str, response_time: float, status_code: int):
        """Track API performance"""
        # Check if this is a bot
        is_bot, _ = TrackingService.is_bot(request)
        if is_bot:
            return

        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        color = 5763719 if status_code < 400 else 15158332  # Green for success, red for error

        embed = {
            "title": "⚡ API Performance",
            "color": color,
            "fields": [
                {"name": "Endpoint", "value": endpoint, "inline": True},
                {"name": "Response Time", "value": f"{response_time:.2f}s", "inline": True},
                {"name": "Status Code", "value": str(status_code), "inline": True},
                {"name": "IP Address", "value": ip, "inline": True}
            ],
            "timestamp": datetime.now().isoformat()
        }

        TrackingService.send_webhook(embed)

    @staticmethod
    def track_outbound_click(request, destination: str, link_type: str):
        """Track when users click external links"""
        # Check if this is a bot
        is_bot, _ = TrackingService.is_bot(request)
        if is_bot:
            return

        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        referrer = request.headers.get('Referer', 'Direct')

        try:
            geo_response = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
            geo_data = geo_response.json()
            location = f"{geo_data.get('city', 'Unknown')}, {geo_data.get('country', 'Unknown')}"
        except:
            location = "Unknown"

        embed = {
            "title": "🔗 Outbound Click",
            "color": 10181046,  # Purple
            "fields": [
                {"name": "Link Type", "value": link_type, "inline": True},
                {"name": "Destination", "value": destination, "inline": True},
                {"name": "IP Address", "value": ip, "inline": True},
                {"name": "Location", "value": location, "inline": True},
                {"name": "From Page", "value": referrer, "inline": True}
            ],
            "timestamp": datetime.now().isoformat()
        }

        TrackingService.send_webhook(embed)
