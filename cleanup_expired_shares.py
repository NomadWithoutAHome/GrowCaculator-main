#!/usr/bin/env python3
"""
Cleanup script for expired shared results.
This script can be run manually or scheduled to clean up expired shared results.
"""
import sys
import os
from pathlib import Path

# Add the Website directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from services.shared_results_service import shared_results_service
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main cleanup function."""
    try:
        logger.info("Starting cleanup of expired shared results...")
        
        # Get current stats
        stats_before = shared_results_service.get_database_stats()
        logger.info(f"Database stats before cleanup: {stats_before}")
        
        # Clean up expired results
        deleted_count = shared_results_service.cleanup_expired_results()
        
        # Get stats after cleanup
        stats_after = shared_results_service.get_database_stats()
        logger.info(f"Database stats after cleanup: {stats_after}")
        
        if deleted_count > 0:
            logger.info(f"Successfully cleaned up {deleted_count} expired shared results")
        else:
            logger.info("No expired results found to clean up")
            
        return 0
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
