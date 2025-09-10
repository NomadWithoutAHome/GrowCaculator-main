"""
FastAPI middleware for tracking website analytics and bot detection
"""
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from services.tracking_service import TrackingService

class TrackingMiddleware(BaseHTTPMiddleware):
    """Middleware to track visitor analytics and detect bots"""

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process each request and track analytics"""
        start_time = time.time()

        # Track the page visit for GET requests (excluding static files)
        if request.method == "GET" and not self._is_static_file(request.url.path):
            TrackingService.track_visitor(request, request.url.path)

        # Track feature usage for specific routes
        if request.method == "GET":
            self._track_feature_usage(request)

        # Process the request
        response = await call_next(request)

        # Track API performance for API endpoints
        if request.url.path.startswith("/api/"):
            end_time = time.time()
            response_time = end_time - start_time
            TrackingService.track_performance(request, request.url.path, response_time, response.status_code)

        return response

    def _is_static_file(self, path: str) -> bool:
        """Check if the path is for a static file that shouldn't be tracked"""
        static_extensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff', '.woff2', '.ttf', '.eot']
        return any(path.endswith(ext) for ext in static_extensions) or path.startswith('/static/')

    def _track_feature_usage(self, request: Request):
        """Track usage of specific features"""
        path = request.url.path

        # Track traits explorer usage
        if path == "/traits":
            TrackingService.track_feature_usage(request, "Traits Explorer", "Viewed plant traits page")

        # Track recipes page usage
        elif path == "/recipes":
            TrackingService.track_feature_usage(request, "Recipe Generator", "Viewed recipes page")

        # Track mutation calculator usage
        elif path == "/mutation-calculator":
            TrackingService.track_feature_usage(request, "Mutation Calculator", "Viewed mutation calculator")

        # Track about page
        elif path == "/about":
            TrackingService.track_feature_usage(request, "About Page", "Viewed about page")

        # Track shared results
        elif path.startswith("/share/"):
            TrackingService.track_feature_usage(request, "Shared Results", f"Viewed shared result: {path}")

    async def track_error_response(self, request: Request, error_message: str, status_code: int):
        """Track error responses"""
        TrackingService.track_error(request, f"HTTP {status_code}: {error_message}", "http_error")

    async def track_outbound_link(self, request: Request, destination: str, link_type: str = "external"):
        """Track outbound link clicks"""
        TrackingService.track_outbound_click(request, destination, link_type)
