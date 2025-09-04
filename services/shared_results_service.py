"""
Service for managing shared calculation results in the database.
"""
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, List
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SharedResultsService:
    """Service for managing shared results in SQLite database."""
    
    def __init__(self, db_path: str = "shared_results.db"):
        """Initialize the service with database path."""
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create shared results table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS shared_results (
                        share_id TEXT PRIMARY KEY,
                        plant TEXT NOT NULL,
                        variant TEXT NOT NULL,
                        mutations TEXT NOT NULL,  -- JSON string
                        weight REAL NOT NULL,
                        amount INTEGER NOT NULL,
                        result_value TEXT NOT NULL,
                        final_sheckles TEXT NOT NULL,
                        total_value TEXT NOT NULL,
                        total_multiplier TEXT NOT NULL,
                        mutation_breakdown TEXT NOT NULL,
                        weight_min TEXT NOT NULL,
                        weight_max TEXT NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        expires_at TIMESTAMP NOT NULL
                    )
                """)
                
                # Create index on expires_at for efficient cleanup
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_expires_at 
                    ON shared_results(expires_at)
                """)
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def create_shared_result(self, share_data: dict) -> bool:
        """Create a new shared result entry."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if this is a batch result
                if share_data.get('type') == 'batch':
                    # For batch results, store batch data in mutations field as JSON
                    batch_data = {
                        'type': 'batch',
                        'plants': share_data.get('plants', []),
                        'total_value': share_data.get('total_value', 0),
                        'total_plants': share_data.get('total_plants', 0)
                    }
                    mutations_json = json.dumps(batch_data)

                    cursor.execute("""
                        INSERT INTO shared_results (
                            share_id, plant, variant, mutations, weight, amount,
                            result_value, final_sheckles, total_value, total_multiplier,
                            mutation_breakdown, weight_min, weight_max, created_at, expires_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        share_data['share_id'],
                        'BATCH',  # Special marker for batch results
                        'BATCH',  # Special marker for batch results
                        mutations_json,
                        0.0,  # Not applicable for batch
                        0,    # Not applicable for batch
                        '',   # Not applicable for batch
                        '',   # Not applicable for batch
                        str(share_data.get('total_value', 0)),
                        '1.00',  # Not applicable for batch
                        '',   # Not applicable for batch
                        '',   # Not applicable for batch
                        '',   # Not applicable for batch
                        share_data['created_at'],
                        share_data['expires_at']
                    ))
                else:
                    # Handle single plant results as before
                    mutations_json = json.dumps(share_data.get('mutations', []))

                    cursor.execute("""
                        INSERT INTO shared_results (
                            share_id, plant, variant, mutations, weight, amount,
                            result_value, final_sheckles, total_value, total_multiplier,
                            mutation_breakdown, weight_min, weight_max, created_at, expires_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        share_data['share_id'],
                        share_data['plant'],
                        share_data['variant'],
                        mutations_json,
                        float(share_data['weight']),
                        int(share_data['amount']),
                        share_data['result_value'],
                        share_data['final_sheckles'],
                        share_data['total_value'],
                        share_data['total_multiplier'],
                        share_data['mutation_breakdown'],
                        share_data['weight_min'],
                        share_data['weight_max'],
                        share_data['created_at'],
                        share_data['expires_at']
                    ))

                conn.commit()
                logger.info(f"Created shared result: {share_data['share_id']}")
                return True

        except Exception as e:
            logger.error(f"Error creating shared result: {e}")
            return False
    
    def get_shared_result(self, share_id: str) -> Optional[dict]:
        """Retrieve a shared result by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT * FROM shared_results WHERE share_id = ?
                """, (share_id,))

                row = cursor.fetchone()
                if not row:
                    return None

                # Convert row to dictionary
                columns = [description[0] for description in cursor.description]
                result = dict(zip(columns, row))

                # Parse mutations JSON
                mutations_data = json.loads(result['mutations'])

                # Check if this is a batch result
                if result['plant'] == 'BATCH' and isinstance(mutations_data, dict) and mutations_data.get('type') == 'batch':
                    # Return batch data in the expected format
                    return {
                        'share_id': result['share_id'],
                        'type': 'batch',
                        'plants': mutations_data.get('plants', []),
                        'total_value': mutations_data.get('total_value', 0),
                        'total_plants': mutations_data.get('total_plants', 0),
                        'created_at': result['created_at'],
                        'expires_at': result['expires_at']
                    }
                else:
                    # Handle single plant results as before
                    result['mutations'] = mutations_data
                    return result

        except Exception as e:
            logger.error(f"Error retrieving shared result: {e}")
            return None
    
    def delete_shared_result(self, share_id: str) -> bool:
        """Delete a shared result by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM shared_results WHERE share_id = ?
                """, (share_id,))
                
                conn.commit()
                logger.info(f"Deleted shared result: {share_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting shared result: {e}")
            return False
    
    def cleanup_expired_results(self) -> int:
        """Remove all expired shared results and return count of deleted items."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get count of expired results
                cursor.execute("""
                    SELECT COUNT(*) FROM shared_results 
                    WHERE expires_at < ?
                """, (datetime.utcnow().isoformat(),))
                
                expired_count = cursor.fetchone()[0]
                
                if expired_count > 0:
                    # Delete expired results
                    cursor.execute("""
                        DELETE FROM shared_results 
                        WHERE expires_at < ?
                    """, (datetime.utcnow().isoformat(),))
                    
                    conn.commit()
                    logger.info(f"Cleaned up {expired_count} expired shared results")
                
                return expired_count
                
        except Exception as e:
            logger.error(f"Error cleaning up expired results: {e}")
            return 0
    
    def get_database_stats(self) -> dict:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total shared results
                cursor.execute("SELECT COUNT(*) FROM shared_results")
                total_count = cursor.fetchone()[0]
                
                # Expired results
                cursor.execute("""
                    SELECT COUNT(*) FROM shared_results 
                    WHERE expires_at < ?
                """, (datetime.utcnow().isoformat(),))
                expired_count = cursor.fetchone()[0]
                
                # Active results
                active_count = total_count - expired_count
                
                return {
                    'total_count': total_count,
                    'active_count': active_count,
                    'expired_count': expired_count
                }
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {'total_count': 0, 'active_count': 0, 'expired_count': 0}


# Global instance
shared_results_service = SharedResultsService()
