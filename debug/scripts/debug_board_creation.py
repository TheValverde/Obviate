#!/usr/bin/env python3
"""
Debug script for testing board creation with default columns.

This script tests the board creation process to see if default columns
are automatically created when a new board is created.

Usage:
    python debug/scripts/debug_board_creation.py
"""

import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import get_db, init_db
from app.repositories import WorkspaceRepository, BoardRepository, ColumnRepository
from app.schemas import WorkspaceCreate, BoardCreate


async def test_board_creation():
    """Test board creation with default columns."""
    print("=" * 80)
    print("TESTING BOARD CREATION WITH DEFAULT COLUMNS")
    print("=" * 80)
    
    # Initialize database
    await init_db()
    
    async for session in get_db():
        # Initialize repositories
        workspace_repo = WorkspaceRepository(session)
        board_repo = BoardRepository(session)
        column_repo = ColumnRepository(session)
        
        tenant_id = "default"
        
        try:
            # Step 1: Create workspace
            print("\n1. Creating workspace...")
            workspace_data = WorkspaceCreate(
                name="Debug Workspace",
                description="Workspace for debugging board creation"
            )
            workspace = await workspace_repo.create(
                data=workspace_data.model_dump(),
                tenant_id=tenant_id
            )
            print(f"SUCCESS: Created workspace '{workspace.name}' with ID: {workspace.id}")
            
            # Step 2: Create board
            print("\n2. Creating board...")
            board_data = BoardCreate(
                name="Debug Board",
                description="Board for debugging default columns",
                workspace_id=workspace.id
            )
            board = await board_repo.create(
                data=board_data.model_dump(),
                tenant_id=tenant_id
            )
            print(f"SUCCESS: Created board '{board.name}' with ID: {board.id}")
            
            # Step 3: Check if columns were created
            print("\n3. Checking for default columns...")
            columns = await column_repo.list_by_board(
                board_id=board.id,
                tenant_id=tenant_id
            )
            print(f"Found {len(columns)} columns:")
            for column in columns:
                print(f"  - {column.name} (position: {column.position}, wip_limit: {column.wip_limit})")
            
            # Step 4: Try to create columns manually to see if there's an issue
            print("\n4. Testing manual column creation...")
            try:
                column_data = {
                    "name": "Test Column",
                    "board_id": board.id,
                    "position": 0,
                    "wip_limit": None
                }
                test_column = await column_repo.create(
                    data=column_data,
                    tenant_id=tenant_id
                )
                print(f"SUCCESS: Manually created column '{test_column.name}'")
                
                # Clean up test column
                await column_repo.delete(
                    entity_id=test_column.id,
                    tenant_id=tenant_id
                )
                print("SUCCESS: Cleaned up test column")
                
            except Exception as e:
                print(f"FAILED: Manual column creation failed: {str(e)}")
            
            return True
            
        except Exception as e:
            print(f"\nFAILED: Error during board creation test: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Main function."""
    print(f"Starting board creation test at {datetime.now()}")
    
    success = await test_board_creation()
    
    if success:
        print("\nBoard creation test completed.")
        sys.exit(0)
    else:
        print("\nBoard creation test failed.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
