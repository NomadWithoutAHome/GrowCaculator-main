#!/usr/bin/env python3
"""
Test script for the tracking service environment variable setup
"""
import os
import sys
sys.path.append('.')

from services.tracking_service import TrackingService

def test_environment_variable():
    """Test that the tracking service properly handles the environment variable"""

    print("🧪 Testing Tracking Service Environment Variable Setup")
    print("=" * 60)

    # Test 1: Check if environment variable is set
    webhook_url = os.environ.get('TRACKING_WEBHOOK')
    print(f"📋 TRACKING_WEBHOOK environment variable: {'✅ Set' if webhook_url else '❌ Not set'}")

    if webhook_url:
        print(f"   URL: {webhook_url[:50]}...")
    else:
        print("   Note: Set TRACKING_WEBHOOK environment variable to enable Discord notifications")
        print("   Example: export TRACKING_WEBHOOK='https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN'")

    # Test 2: Check webhook sending (won't actually send if URL not set)
    print("\n📤 Testing webhook functionality:")

    test_embed = {
        "title": "🧪 Test Notification",
        "description": "This is a test of the tracking service",
        "color": 5763719,  # Green
        "fields": [
            {"name": "Status", "value": "Environment variable test", "inline": True},
            {"name": "Webhook URL", "value": "Set" if webhook_url else "Not set", "inline": True}
        ]
    }

    # Set the environment variable for testing
    if not webhook_url:
        os.environ['TRACKING_WEBHOOK'] = 'https://httpbin.org/post'  # Test endpoint
        print("   📝 Set test webhook URL for demonstration")

    try:
        TrackingService.send_webhook(test_embed)
        print("   ✅ Webhook method executed successfully")
    except Exception as e:
        print(f"   ❌ Webhook failed: {e}")

    # Test 3: Check bot detection
    print("\n🤖 Testing bot detection:")

    class MockRequest:
        def __init__(self, user_agent, headers=None):
            self.headers = headers or {}
            self.headers['User-Agent'] = user_agent
            self.remote_addr = '127.0.0.1'

    # Test with known bot user agent
    bot_request = MockRequest('Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)')
    is_bot, reason = TrackingService.is_bot(bot_request)
    print(f"   Googlebot detection: {'✅ Detected' if is_bot else '❌ Not detected'} ({reason})")

    # Test with normal browser
    normal_request = MockRequest('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    is_bot, reason = TrackingService.is_bot(normal_request)
    print(f"   Normal browser detection: {'❌ Incorrectly flagged' if is_bot else '✅ Not flagged'}")

    print("\n" + "=" * 60)
    print("🎉 Tracking service test completed!")

    if not webhook_url:
        print("\n💡 To enable Discord notifications:")
        print("   1. Create a Discord webhook in your server")
        print("   2. Set the environment variable:")
        print("      export TRACKING_WEBHOOK='your_webhook_url_here'")
        print("   3. Restart your application")

if __name__ == "__main__":
    test_environment_variable()
