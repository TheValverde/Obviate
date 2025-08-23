#!/usr/bin/env python3
"""
Debug script for testing board creation API endpoint.

This script tests the board creation API endpoint to see if default columns
are automatically created when a new board is created via the API.

Usage:
    python debug/scripts/debug_api_board_creation.py
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
from app.api.v1.endpoints.board import create_board
from app.api.v1.endpoints.workspace import create_workspace
from fastapi import Request
from unittest.mock import AsyncMock


async def test_api_board_creation():
    """Test board creation via API endpoint."""
    print("=" * 80)
    print("TESTING BOARD CREATION VIA API ENDPOINT")
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
            # Step 1: Create workspace via repository
            print("\n1. Creating workspace...")
            workspace_data = WorkspaceCreate(
                name="API Test Workspace",
                description="Workspace for testing API board creation"
            )
            workspace = await workspace_repo.create(
                data=workspace_data.model_dump(),
                tenant_id=tenant_id
            )
            print(f"SUCCESS: Created workspace '{workspace.name}' with ID: {workspace.id}")
            
            # Step 2: Create board via API endpoint
            print("\n2. Creating board via API endpoint...")
            board_data = BoardCreate(
                name="API Test Board",
                description="Board for testing API default columns",
                workspace_id=workspace.id
            )
            
            # Mock the dependencies
            mock_board_repo = AsyncMock()
            mock_column_repo = AsyncMock()
            mock_tenant_id = "default"
            
            # Call the API endpoint function directly
            response = await create_board(
                board_data=board_data,
                board_repo=board_repo,
                column_repo=column_repo,
                tenant_id=mock_tenant_id
            )
            
            print(f"SUCCESS: API response: {response.message}")
            board_id = response.data.id
            print(f"SUCCESS: Created board '{response.data.name}' with ID: {board_id}")
            
            # Step 3: Check if columns were created
            print("\n3. Checking for default columns...")
            columns = await column_repo.list_by_board(
                board_id=board_id,
                tenant_id=tenant_id
            )
            print(f"Found {len(columns)} columns:")
            for column in columns:
                print(f"  - {column.name} (position: {column.position}, wip_limit: {column.wip_limit})")
            
            # Step 4: Verify expected columns
            expected_columns = ["To Do", "In Progress", "Done"]
            actual_columns = [col.name for col in columns]
            if set(actual_columns) == set(expected_columns):
                print("SUCCESS: All expected default columns are present")
                return True
            else:
                print(f"FAILED: Expected {expected_columns}, got {actual_columns}")
                return False
            
        except Exception as e:
            print(f"\nFAILED: Error during API board creation test: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Main function."""
    print(f"Starting API board creation test at {datetime.now()}")
    
    success = await test_api_board_creation()
    
    if success:
        print("\nAPI board creation test passed!")
        sys.exit(0)
    else:
        print("\nAPI board creation test failed.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
