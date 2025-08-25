#!/usr/bin/env python3
"""
Debug script to test specific issues found in the main API test script.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import get_db, init_db
from app.repositories import (
    WorkspaceRepository, BoardRepository, ColumnRepository, CardRepository
)
from app.schemas import (
    WorkspaceCreate, WorkspaceUpdate, BoardCreate, BoardUpdate,
    ColumnCreate, ColumnUpdate, CardCreate, CardUpdate
)


async def test_board_update():
    """Test board update functionality."""
    print("Testing Board Update...")
    
    await init_db()
    
    async for session in get_db():
        workspace_repo = WorkspaceRepository(session)
        board_repo = BoardRepository(session)
        column_repo = ColumnRepository(session)
        
        tenant_id = "default"
        
        try:
            # Create workspace
            workspace_data = WorkspaceCreate(
                name="Debug Test Workspace",
                description="Workspace for debugging"
            )
            workspace = await workspace_repo.create(
                data=workspace_data.model_dump(),
                tenant_id=tenant_id
            )
            print(f"Created workspace: {workspace.name}")
            
            # Create board
            board_data = BoardCreate(
                name="Debug Test Board",
                description="Board for debugging",
                workspace_id=workspace.id
            )
            
            from app.api.v1.endpoints.board import create_board
            response = await create_board(
                board_data=board_data,
                board_repo=board_repo,
                column_repo=column_repo,
                tenant_id=tenant_id
            )
            board = response.data
            print(f"Created board: {board.name}")
            
            # Test update
            update_data = BoardUpdate(
                name="Updated Debug Test Board",
                description="Updated description for debugging"
            )
            
            print(f"Update data: {update_data.model_dump(exclude_unset=True)}")
            
            updated_board = await board_repo.update(
                board.id,
                data=update_data.model_dump(exclude_unset=True),
                tenant_id=tenant_id
            )
            
            print(f"Updated board name: '{updated_board.name}'")
            print(f"Expected name: 'Updated Debug Test Board'")
            print(f"Match: {updated_board.name == 'Updated Debug Test Board'}")
            
            # Cleanup
            await workspace_repo.delete(workspace.id, tenant_id)
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        
        break


async def test_card_creation():
    """Test card creation functionality."""
    print("\nTesting Card Creation...")
    
    await init_db()
    
    async for session in get_db():
        workspace_repo = WorkspaceRepository(session)
        board_repo = BoardRepository(session)
        column_repo = ColumnRepository(session)
        card_repo = CardRepository(session)
        
        tenant_id = "default"
        
        try:
            # Create workspace
            workspace_data = WorkspaceCreate(
                name="Debug Test Workspace",
                description="Workspace for debugging"
            )
            workspace = await workspace_repo.create(
                data=workspace_data.model_dump(),
                tenant_id=tenant_id
            )
            print(f"Created workspace: {workspace.name}")
            
            # Create board
            board_data = BoardCreate(
                name="Debug Test Board",
                description="Board for debugging",
                workspace_id=workspace.id
            )
            
            from app.api.v1.endpoints.board import create_board
            response = await create_board(
                board_data=board_data,
                board_repo=board_repo,
                column_repo=column_repo,
                tenant_id=tenant_id
            )
            board = response.data
            print(f"Created board: {board.name}")
            
            # Get columns
            columns = await column_repo.list_by_board(board.id, tenant_id)
            print(f"Found {len(columns)} columns: {[col.name for col in columns]}")
            
            # Find To Do column
            todo_column = None
            for col in columns:
                if col.name == "To Do":
                    todo_column = col
                    break
            
            if not todo_column:
                print("ERROR: To Do column not found!")
                return
            
            print(f"Found To Do column: {todo_column.id}")
            
            # Test card creation
            card_data = CardCreate(
                title="Debug Test Card",
                description="Test card for debugging",
                board_id=board.id,
                column_id=todo_column.id,
                position=0,
                priority=3,
                labels=["test", "debug"],
                assignees=["test@example.com"]
            )
            
            print(f"Card data: {card_data.model_dump()}")
            
            card = await card_repo.create(
                data=card_data.model_dump(),
                tenant_id=tenant_id
            )
            
            print(f"Created card: {card.title}")
            
            # Cleanup
            await workspace_repo.delete(workspace.id, tenant_id)
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        
        break


async def main():
    """Main debug function."""
    print("=" * 60)
    print("DEBUGGING API TEST ISSUES")
    print("=" * 60)
    
    await test_board_update()
    await test_card_creation()


if __name__ == "__main__":
    asyncio.run(main())
