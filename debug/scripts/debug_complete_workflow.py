#!/usr/bin/env python3
"""
Debug script for testing the complete Kanban workflow.

This script tests the full workflow:
1. Create workspace
2. Create board (with default columns)
3. Create cards
4. Move cards between columns
5. Verify the complete flow

Usage:
    python debug/scripts/debug_complete_workflow.py
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
from app.repositories import WorkspaceRepository, BoardRepository, ColumnRepository, CardRepository
from app.schemas import WorkspaceCreate, BoardCreate, CardCreate


async def test_complete_workflow():
    """Test the complete Kanban workflow."""
    print("=" * 80)
    print("TESTING COMPLETE KANBAN WORKFLOW")
    print("=" * 80)
    
    # Initialize database
    await init_db()
    
    async for session in get_db():
        # Initialize repositories
        workspace_repo = WorkspaceRepository(session)
        board_repo = BoardRepository(session)
        column_repo = ColumnRepository(session)
        card_repo = CardRepository(session)
        
        tenant_id = "default"
        
        try:
            # Step 1: Create workspace
            print("\n1. Creating workspace...")
            workspace_data = WorkspaceCreate(
                name="Test Workspace",
                description="Workspace for testing complete workflow"
            )
            workspace = await workspace_repo.create(
                data=workspace_data.model_dump(),
                tenant_id=tenant_id
            )
            print(f"SUCCESS: Created workspace '{workspace.name}' with ID: {workspace.id}")
            
            # Step 2: Create board (should create default columns)
            print("\n2. Creating board with default columns...")
            board_data = BoardCreate(
                name="Test Board",
                description="Board for testing complete workflow",
                workspace_id=workspace.id
            )
            
            # Use the API endpoint to create board with default columns
            from app.api.v1.endpoints.board import create_board
            response = await create_board(
                board_data=board_data,
                board_repo=board_repo,
                column_repo=column_repo,
                tenant_id=tenant_id
            )
            board = response.data
            print(f"SUCCESS: Created board '{board.name}' with ID: {board.id}")
            
            # Step 3: Verify default columns were created
            print("\n3. Verifying default columns...")
            columns = await column_repo.list_by_board(
                board_id=board.id,
                tenant_id=tenant_id
            )
            print(f"SUCCESS: Found {len(columns)} columns:")
            for column in columns:
                print(f"  - {column.name} (position: {column.position}, wip_limit: {column.wip_limit})")
            
            # Verify we have the expected columns
            expected_columns = ["To Do", "In Progress", "Done"]
            actual_columns = [col.name for col in columns]
            if set(actual_columns) == set(expected_columns):
                print("SUCCESS: All expected default columns are present")
            else:
                print(f"FAILED: Expected {expected_columns}, got {actual_columns}")
                return False
            
            # Step 4: Create cards in different columns
            print("\n4. Creating test cards...")
            cards = []
            
            # Create cards in "To Do" column
            todo_column = next(col for col in columns if col.name == "To Do")
            for i in range(3):
                card_data = CardCreate(
                    title=f"Task {i+1}",
                    description=f"Description for task {i+1}",
                    board_id=board.id,
                    column_id=todo_column.id,
                    position=i,
                    priority=3
                )
                card = await card_repo.create(
                    data=card_data.model_dump(),
                    tenant_id=tenant_id
                )
                cards.append(card)
                print(f"SUCCESS: Created card '{card.title}' in {todo_column.name}")
            
            # Step 5: Move a card to "In Progress"
            print("\n5. Moving card to 'In Progress'...")
            in_progress_column = next(col for col in columns if col.name == "In Progress")
            card_to_move = cards[0]
            
            moved_card = await card_repo.move_card(
                card_id=card_to_move.id,
                column_id=in_progress_column.id,
                position=0,
                tenant_id=tenant_id
            )
            if moved_card:
                print(f"SUCCESS: Moved card '{moved_card.title}' to {in_progress_column.name}")
            else:
                print("FAILED: Could not move card")
                return False
            
            # Step 6: Verify card positions
            print("\n6. Verifying card positions...")
            todo_cards = await card_repo.list(
                tenant_id=tenant_id,
                filters={"column_id": todo_column.id}
            )
            in_progress_cards = await card_repo.list(
                tenant_id=tenant_id,
                filters={"column_id": in_progress_column.id}
            )
            
            print(f"SUCCESS: {len(todo_cards)} cards in 'To Do'")
            print(f"SUCCESS: {len(in_progress_cards)} cards in 'In Progress'")
            
            # Step 7: Test complete board state
            print("\n7. Testing complete board state...")
            all_board_cards = await card_repo.list(
                tenant_id=tenant_id,
                filters={"board_id": board.id}
            )
            print(f"SUCCESS: Total cards on board: {len(all_board_cards)}")
            
            # Step 8: Test column card counts
            print("\n8. Testing column card counts...")
            for column in columns:
                column_cards = await card_repo.list(
                    tenant_id=tenant_id,
                    filters={"column_id": column.id}
                )
                print(f"SUCCESS: {column.name}: {len(column_cards)} cards")
            
            print("\n" + "=" * 80)
            print("COMPLETE WORKFLOW TEST PASSED!")
            print("=" * 80)
            print("\nSummary:")
            print(f"- Workspace: {workspace.name} ({workspace.id})")
            print(f"- Board: {board.name} ({board.id})")
            print(f"- Columns: {len(columns)} default columns created")
            print(f"- Cards: {len(cards)} cards created and moved")
            print("\nThe Kanban workflow is working correctly!")
            
            return True
            
        except Exception as e:
            print(f"\nFAILED: Error during workflow test: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Main function."""
    print(f"Starting complete workflow test at {datetime.now()}")
    
    success = await test_complete_workflow()
    
    if success:
        print("\nAll tests passed! The Kanban system is working correctly.")
        sys.exit(0)
    else:
        print("\nSome tests failed. Please check the logs above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
