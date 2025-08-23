#!/usr/bin/env python3
"""
Debug script template for Kanban For Agents.

This template provides a standardized way to create debug scripts with:
- Proper logging setup
- Database initialization
- Error handling
- Timestamped log files
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import init_db

# Set up logging
def setup_logging(script_name: str) -> logging.Logger:
    """Set up logging with file and console output."""
    
    # Create logs directory if it doesn't exist
    logs_dir = project_root / "debug" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"{script_name}_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(script_name)
    logger.info(f"Debug script started: {script_name}")
    logger.info(f"Log file: {log_file}")
    
    return logger

async def debug_main():
    """Main debug function - override this in your script."""
    logger = setup_logging("debug_template")
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialized successfully")
        
        # Your debug logic goes here
        logger.info("Template debug script completed")
        
    except Exception as e:
        logger.error(f"Debug script failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    asyncio.run(debug_main())
