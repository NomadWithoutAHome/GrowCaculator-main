"""
Vercel-compatible service for managing shared calculation results.
Uses in-memory storage since Vercel serverless functions don't persist data.
"""
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VercelSharedResultsService:
    """Vercel-compatible service for managing results in memory."""
    
    def __init__(self):
        """Initialize the service with in-memory storage."""
        self.shared_results: Dict[str, dict] = {}
        logger.info("VercelSharedResultsService initialized with in-memory storage")
    
    def create_shared_result(self, share_data: dict) -> bool:
        """Create a new shared result entry."""
        try:
            # Generate share ID if not provided
            if 'share_id' not in share_data:
                share_data['share_id'] = f"share_{int(datetime.utcnow().timestamp())}_{hash(str(share_data)) % 10000}"
            
            # Set expiration to 24 hours from now
            share_data['expires_at'] = (datetime.utcnow() + timedelta(hours=24)).isoformat()
            
            # Store in memory
            self.shared_results[share_data['share_id']] = share_data.copy()
            
            logger.info(f"Created shared result: {share_data['share_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating shared result: {e}")
            return False
    
    def get_shared_result(self, share_id: str) -> Optional[dict]:
        """Retrieve a shared result by ID."""
        try:
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
            if share_id in self.shared_results:
                del self.shared_results[share_id]
                logger.info(f"Deleted shared result: {share_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting shared result: {e}")
            return False
    
    def cleanup_expired_results(self) -> int:
        """Remove all expired shared results and return count of deleted items."""
        try:
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
    
    def get_database_stats(self) -> dict:
        """Get database statistics."""
        try:
            current_time = datetime.utcnow()
            expired_count = 0
            
            for result in self.shared_results.values():
                try:
                    expires_at = datetime.fromisoformat(result['expires_at'])
                    if current_time > expires_at:
                        expired_count += 1
                except:
                    expired_count += 1
            
            total_count = len(self.shared_results)
            active_count = total_count - expired_count
            
            return {
                'total_count': total_count,
                'active_count': active_count,
                'expired_count': expired_count
            }
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {'total_count': 0, 'active_count': 0, 'expired_count': 0}


# Global instance for Vercel
vercel_shared_results_service = VercelSharedResultsService()
