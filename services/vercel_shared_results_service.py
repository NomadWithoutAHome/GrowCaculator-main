"""
Vercel-compatible service for managing shared calculation results.
Uses Redis for permanent storage.
"""
import json
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import logging

# Set up logging
logging.basicConfig(level=logging.WARNING)  # Reduced from INFO to WARNING
logger = logging.getLogger(__name__)

try:
    import redis
    REDIS_AVAILABLE = True
    logger.info("Redis is available")
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, falling back to in-memory storage")


class VercelSharedResultsService:
    """Vercel-compatible service for managing results with permanent storage."""
    
    def __init__(self):
        """Initialize the service with Redis or fallback to in-memory."""
        self.shared_results: Dict[str, dict] = {}
        self.use_redis = REDIS_AVAILABLE and self._get_redis_client()
        
        if self.use_redis:
            logger.info("VercelSharedResultsService initialized with Redis storage")
        else:
            logger.info("VercelSharedResultsService initialized with in-memory storage (fallback)")
    
    def _get_redis_client(self) -> Optional['redis.Redis']:
        """Get Redis client from environment variables."""
        try:
            redis_url = os.getenv('REDIS_URL') or os.getenv('REDIS_RV_URL')
            if redis_url:
                return redis.from_url(redis_url)
            return None
        except Exception as e:
            logger.error(f"Error creating Redis client: {e}")
            return None
    
    def create_shared_result(self, share_data: dict) -> bool:
        """Create a new shared result entry."""
        try:
            # Generate share ID if not provided
            if 'share_id' not in share_data:
                share_data['share_id'] = f"share_{int(datetime.utcnow().timestamp())}_{hash(str(share_data)) % 10000}"
            
            # Set expiration to 30 days from now (much longer than before)
            share_data['expires_at'] = (datetime.utcnow() + timedelta(days=30)).isoformat()
            
            # Store in Redis if available, otherwise in memory
            if self.use_redis:
                redis_client = self._get_redis_client()
                if redis_client:
                    key = f"shared_result:{share_data['share_id']}"
                    # Store with 30 days expiration (in seconds)
                    redis_client.setex(
                        key, 
                        30 * 24 * 60 * 60,  # 30 days in seconds
                        json.dumps(share_data)
                    )
            else:
                self.shared_results[share_data['share_id']] = share_data.copy()
            
            logger.info(f"Created shared result: {share_data['share_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating shared result: {e}")
            return False
    
    def get_shared_result(self, share_id: str) -> Optional[dict]:
        """Retrieve a shared result by ID."""
        try:
            if self.use_redis:
                redis_client = self._get_redis_client()
                if redis_client:
                    key = f"shared_result:{share_id}"
                    result_data = redis_client.get(key)
                    if not result_data:
                        return None
                    
                    result = json.loads(result_data)
                    
                    # Check if expired (Redis handles expiration automatically, but we can double-check)
                    expires_at = datetime.fromisoformat(result['expires_at'])
                    if datetime.utcnow() > expires_at:
                        logger.info(f"Shared result expired: {share_id}")
                        self.delete_shared_result(share_id)
                        return None
                    
                    return result
            else:
                result = self.shared_results.get(share_id)
                if not result:
                    return None
                
                # Check if expired
                expires_at = datetime.fromisoformat(result['expires_at'])
                if datetime.utcnow() > expires_at:
                    logger.info(f"Shared result expired: {share_id}")
                    self.delete_shared_result(share_id)
                    return None
                
                return result
            
        except Exception as e:
            logger.error(f"Error retrieving shared result: {e}")
            return None
    
    def delete_shared_result(self, share_id: str) -> bool:
        """Delete a shared result by ID."""
        try:
            if self.use_redis:
                redis_client = self._get_redis_client()
                if redis_client:
                    key = f"shared_result:{share_id}"
                    redis_client.delete(key)
            else:
                if share_id in self.shared_results:
                    del self.shared_results[share_id]
            
            logger.info(f"Deleted shared result: {share_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting shared result: {e}")
            return False
    
    def cleanup_expired_results(self) -> int:
        """Remove all expired shared results and return count of deleted items."""
        try:
            if self.use_redis:
                # Redis handles expiration automatically, so no manual cleanup needed
                return 0
            else:
                # Manual cleanup for in-memory storage
                current_time = datetime.utcnow()
                expired_keys = []
                
                for share_id, result in self.shared_results.items():
                    try:
                        expires_at = datetime.fromisoformat(result['expires_at'])
                        if current_time > expires_at:
                            expired_keys.append(share_id)
                    except:
                        # If we can't parse the date, consider it expired
                        expired_keys.append(share_id)
                
                # Delete expired results
                for share_id in expired_keys:
                    del self.shared_results[share_id]
                
                if expired_keys:
                    logger.info(f"Cleaned up {len(expired_keys)} expired shared results")
                
                return len(expired_keys)
            
        except Exception as e:
            logger.error(f"Error cleaning up expired results: {e}")
            return 0
    
    def get_all_shared_results(self) -> List[dict]:
        """Get all shared results (for admin purposes)."""
        try:
            if self.use_redis:
                # Note: This is a simplified approach. In production, you might want to maintain a separate index
                # For now, we'll return an empty list as Redis doesn't support listing all keys efficiently
                logger.warning("Getting all shared results not supported with Redis in this implementation")
                return []
            else:
                return list(self.shared_results.values())
        except Exception as e:
            logger.error(f"Error getting all shared results: {e}")
            return []
    
    def get_database_stats(self) -> dict:
        """Get database statistics."""
        try:
            if self.use_redis:
                redis_client = self._get_redis_client()
                if redis_client:
                    # Count keys matching our pattern
                    keys = redis_client.keys("shared_result:*")
                    total_results = len(keys)
                else:
                    total_results = 0
            else:
                total_results = len(self.shared_results)
            
            return {
                "total_shared_results": total_results,
                "storage_type": "Redis" if self.use_redis else "In-Memory"
            }
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {
                "total_shared_results": 0,
                "storage_type": "Error",
                "error": str(e)
            }

# Create a single instance
vercel_shared_results_service = VercelSharedResultsService()
