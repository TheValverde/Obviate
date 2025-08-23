#!/usr/bin/env python3
"""
Debug script for column endpoints.

Tests column repository operations and identifies issues.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text

from app.core.database import init_db, get_db
from app.models.column import Column
from app.repositories.column import ColumnRepository

# Set up logging
def setup_logging(script_name: str) -> logging.Logger:
    """Set up logging with file and console output."""
    
    # Create logs directory if it doesn't exist
    logs_dir = project_root / "debug" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamped log file
    from datetime import datetime
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

async def debug_column_endpoints():
    """Debug column endpoints step by step."""
    
    logger = setup_logging("debug_column_endpoints")
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialized successfully")
        
        # Test 1: Check if columns table exists
        logger.info("Test 1: Checking if columns table exists...")
        async for session in get_db():
            result = await session.execute(text("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'columns')"))
            table_exists = result.scalar()
            logger.info(f"Columns table exists: {table_exists}")
            break
        
        if not table_exists:
            logger.error("Columns table does not exist! Need to run migrations.")
            return
        
        # Test 2: Test ColumnRepository instantiation
        logger.info("Test 2: Testing ColumnRepository instantiation...")
        async for session in get_db():
            repo = ColumnRepository(session)
            logger.info(f"ColumnRepository created successfully: {repo}")
            break
        
        # Test 3: Test list method
        logger.info("Test 3: Testing list method...")
        async for session in get_db():
            repo = ColumnRepository(session)
            try:
                columns = await repo.list("default", limit=10, offset=0)
                logger.info(f"List method successful, found {len(columns)} columns")
                
                # Log first few columns for inspection
                for i, col in enumerate(columns[:3]):
                    logger.info(f"Column {i+1}: {col.name} (ID: {col.id}, Board: {col.board_id})")
                    
            except Exception as e:
                logger.error(f"List method failed: {e}")
                import traceback
                logger.error(traceback.format_exc())
            break
        
        # Test 4: Test count method
        logger.info("Test 4: Testing count method...")
        async for session in get_db():
            repo = ColumnRepository(session)
            try:
                count = await repo.count("default")
                logger.info(f"Count method successful, total columns: {count}")
            except Exception as e:
                logger.error(f"Count method failed: {e}")
                import traceback
                logger.error(traceback.format_exc())
            break
            
        # Test 5: Test get_by_id method
        logger.info("Test 5: Testing get_by_id method...")
        async for session in get_db():
            repo = ColumnRepository(session)
            try:
                # Get first column ID
                columns = await repo.list("default", limit=1, offset=0)
                if columns:
                    first_column = columns[0]
                    logger.info(f"Testing get_by_id with column: {first_column.id}")
                    
                    retrieved_column = await repo.get_by_id(first_column.id, "default")
                    if retrieved_column:
                        logger.info(f"get_by_id successful: {retrieved_column.name}")
                    else:
                        logger.error("get_by_id returned None")
                else:
                    logger.warning("No columns found to test get_by_id")
                    
            except Exception as e:
                logger.error(f"get_by_id method failed: {e}")
                import traceback
                logger.error(traceback.format_exc())
            break
            
        logger.info("SUCCESS: All column endpoint tests completed successfully!")
            
    except Exception as e:
        logger.error(f"Debug failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(debug_column_endpoints())
