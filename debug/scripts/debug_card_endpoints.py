#!/usr/bin/env python3
"""
Debug script for card endpoints.

Tests card repository operations and identifies issues.
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
from app.models.card import Card
from app.repositories.card import CardRepository

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

async def debug_card_endpoints():
    """Debug card endpoints step by step."""
    
    logger = setup_logging("debug_card_endpoints")
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialized successfully")
        
        # Test 1: Check if cards table exists
        logger.info("Test 1: Checking if cards table exists...")
        async for session in get_db():
            result = await session.execute(text("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'cards')"))
            table_exists = result.scalar()
            logger.info(f"Cards table exists: {table_exists}")
            break
        
        if not table_exists:
            logger.error("Cards table does not exist! Need to run migrations.")
            return
        
        # Test 2: Test CardRepository instantiation
        logger.info("Test 2: Testing CardRepository instantiation...")
        async for session in get_db():
            repo = CardRepository(session)
            logger.info(f"CardRepository created successfully: {repo}")
            break
        
        # Test 3: Test list method
        logger.info("Test 3: Testing list method...")
        async for session in get_db():
            repo = CardRepository(session)
            try:
                cards = await repo.list("default", limit=10, offset=0)
                logger.info(f"List method successful, found {len(cards)} cards")
                
                # Log first few cards for inspection
                for i, card in enumerate(cards[:3]):
                    logger.info(f"Card {i+1}: {card.title} (ID: {card.id}, Board: {card.board_id}, Column: {card.column_id})")
                    
            except Exception as e:
                logger.error(f"List method failed: {e}")
                import traceback
                logger.error(traceback.format_exc())
            break
        
        # Test 4: Test count method
        logger.info("Test 4: Testing count method...")
        async for session in get_db():
            repo = CardRepository(session)
            try:
                count = await repo.count("default")
                logger.info(f"Count method successful, total cards: {count}")
            except Exception as e:
                logger.error(f"Count method failed: {e}")
                import traceback
                logger.error(traceback.format_exc())
            break
            
        # Test 5: Test get_by_id method
        logger.info("Test 5: Testing get_by_id method...")
        async for session in get_db():
            repo = CardRepository(session)
            try:
                # Get first card ID
                cards = await repo.list("default", limit=1, offset=0)
                if cards:
                    first_card = cards[0]
                    logger.info(f"Testing get_by_id with card: {first_card.id}")
                    
                    retrieved_card = await repo.get_by_id(first_card.id, "default")
                    if retrieved_card:
                        logger.info(f"get_by_id successful: {retrieved_card.title}")
                    else:
                        logger.error("get_by_id returned None")
                else:
                    logger.warning("No cards found to test get_by_id")
                    
            except Exception as e:
                logger.error(f"get_by_id method failed: {e}")
                import traceback
                logger.error(traceback.format_exc())
            break
            
        logger.info("SUCCESS: All card endpoint tests completed successfully!")
            
    except Exception as e:
        logger.error(f"Debug failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(debug_card_endpoints())
