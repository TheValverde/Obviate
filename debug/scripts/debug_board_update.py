#!/usr/bin/env python3
"""
Debug script to trace board update issues.
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Dict, Any

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_board_update.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def debug_board_update():
    """Debug the board update process step by step."""
    
    try:
        logger.info("=== Starting Board Update Debug ===")
        
        # Import after logging setup
        from app.core.database import get_db, init_db
        from app.repositories import BoardRepository
        from app.schemas import BoardUpdate
        from app.models.board import Board
        
        logger.info("Imports successful")
        
        # Initialize database
        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialized")
        
        # Test data
        board_id = "AGMNKBN63IPKMVPSFOVVHSPNHA"  # Use existing board ID
        tenant_id = "default"
        update_data = {
            "name": "Debug Updated Board",
            "description": "Updated via debug script"
        }
        
        logger.info(f"Testing board update for ID: {board_id}")
        logger.info(f"Update data: {update_data}")
        
        # Get database session
        async for session in get_db():
            try:
                logger.info("Database session obtained")
                
                # Create repository
                repo = BoardRepository(session)
                logger.info("Repository created")
                
                # Test 1: Get the board first
                logger.info("=== Test 1: Getting existing board ===")
                existing_board = await repo.get_by_id(board_id, tenant_id)
                if existing_board:
                    logger.info(f"Existing board found: {existing_board.name}")
                    logger.info(f"Current updated_at: {existing_board.updated_at}")
                    logger.info(f"Current updated_at type: {type(existing_board.updated_at)}")
                else:
                    logger.error("Board not found!")
                    return
                
                # Test 2: Check the model's updated_at field
                logger.info("=== Test 2: Checking model field ===")
                logger.info(f"Board model updated_at field: {Board.updated_at}")
                logger.info(f"Board model updated_at type: {type(Board.updated_at)}")
                
                if hasattr(Board.updated_at.property, 'columns'):
                    column = Board.updated_at.property.columns[0]
                    logger.info(f"Column: {column}")
                    logger.info(f"Column default: {column.default}")
                    logger.info(f"Column default type: {type(column.default)}")
                    if hasattr(column.default, 'arg'):
                        logger.info(f"Column default arg: {column.default.arg}")
                        logger.info(f"Column default arg type: {type(column.default.arg)}")
                
                # Test 3: Create BoardUpdate schema
                logger.info("=== Test 3: Creating BoardUpdate schema ===")
                board_update = BoardUpdate(**update_data)
                logger.info(f"BoardUpdate created: {board_update}")
                logger.info(f"BoardUpdate dict: {board_update.model_dump(exclude_unset=True)}")
                
                # Test 4: Manually build update data like the repository does
                logger.info("=== Test 4: Building update data ===")
                data = board_update.model_dump(exclude_unset=True)
                logger.info(f"Initial data: {data}")
                
                # Add updated_at timestamp like the repository does
                updated_at_value = Board.updated_at.property.columns[0].default.arg
                logger.info(f"Updated_at value to be added: {updated_at_value}")
                logger.info(f"Updated_at value type: {type(updated_at_value)}")
                
                data['updated_at'] = updated_at_value
                logger.info(f"Final data with updated_at: {data}")
                
                # Test 5: Try to call the function if it's a lambda
                if callable(updated_at_value):
                    logger.info("Updated_at value is callable, trying to call it...")
                    try:
                        actual_datetime = updated_at_value()
                        logger.info(f"Called function result: {actual_datetime}")
                        logger.info(f"Called function result type: {type(actual_datetime)}")
                        data['updated_at'] = actual_datetime
                    except Exception as e:
                        logger.error(f"Error calling updated_at function: {e}")
                
                # Test 6: Try the actual update
                logger.info("=== Test 6: Attempting repository update ===")
                try:
                    updated_board = await repo.update(
                        entity_id=board_id,
                        tenant_id=tenant_id,
                        data=data,
                        version=None
                    )
                    if updated_board:
                        logger.info(f"Update successful! New name: {updated_board.name}")
                        logger.info(f"New updated_at: {updated_board.updated_at}")
                    else:
                        logger.error("Update returned None")
                except Exception as e:
                    logger.error(f"Update failed with error: {e}")
                    logger.exception("Full traceback:")
                
            except Exception as e:
                logger.error(f"Error in session: {e}")
                logger.exception("Full traceback:")
            finally:
                break  # Exit the async generator
                
    except Exception as e:
        logger.error(f"Error in debug function: {e}")
        logger.exception("Full traceback:")
    
    logger.info("=== Debug Complete ===")

if __name__ == "__main__":
    asyncio.run(debug_board_update())
