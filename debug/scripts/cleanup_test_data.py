#!/usr/bin/env python3
"""
Cleanup script to remove all test data from the database.

This script performs a hard delete of all test workspaces, boards, columns, and cards
to clean up the database for production use.

Usage:
    python debug/scripts/cleanup_test_data.py
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


async def cleanup_test_data():
    """Remove all test data from the database."""
    print("=" * 80)
    print("CLEANING UP TEST DATA FROM DATABASE")
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
            print("\n1. Counting existing data...")
            
            # Count existing data
            workspaces = await workspace_repo.list(tenant_id=tenant_id, include_deleted=False)
            boards = await board_repo.list(tenant_id=tenant_id, include_deleted=False)
            columns = await column_repo.list(tenant_id=tenant_id, include_deleted=False)
            cards = await card_repo.list(tenant_id=tenant_id, include_deleted=False)
            
            print(f"Found {len(workspaces)} workspaces")
            print(f"Found {len(boards)} boards")
            print(f"Found {len(columns)} columns")
            print(f"Found {len(cards)} cards")
            
            if len(workspaces) == 0:
                print("\nDatabase is already clean!")
                return True
            
            print(f"\n2. Hard deleting all test data...")
            
            # Hard delete all cards first (due to foreign key constraints)
            for card in cards:
                await card_repo.delete(
                    entity_id=card.id,
                    tenant_id=tenant_id,
                    hard_delete=True
                )
                print(f"  - Deleted card: {card.title}")
            
            # Hard delete all columns
            for column in columns:
                await column_repo.delete(
                    entity_id=column.id,
                    tenant_id=tenant_id,
                    hard_delete=True
                )
                print(f"  - Deleted column: {column.name}")
            
            # Hard delete all boards
            for board in boards:
                await board_repo.delete(
                    entity_id=board.id,
                    tenant_id=tenant_id,
                    hard_delete=True
                )
                print(f"  - Deleted board: {board.name}")
            
            # Hard delete all workspaces
            for workspace in workspaces:
                await workspace_repo.delete(
                    entity_id=workspace.id,
                    tenant_id=tenant_id,
                    hard_delete=True
                )
                print(f"  - Deleted workspace: {workspace.name}")
            
            print(f"\n3. Verification...")
            
            # Verify cleanup
            remaining_workspaces = await workspace_repo.list(tenant_id=tenant_id, include_deleted=False)
            remaining_boards = await board_repo.list(tenant_id=tenant_id, include_deleted=False)
            remaining_columns = await column_repo.list(tenant_id=tenant_id, include_deleted=False)
            remaining_cards = await card_repo.list(tenant_id=tenant_id, include_deleted=False)
            
            print(f"Remaining workspaces: {len(remaining_workspaces)}")
            print(f"Remaining boards: {len(remaining_boards)}")
            print(f"Remaining columns: {len(remaining_columns)}")
            print(f"Remaining cards: {len(remaining_cards)}")
            
            if len(remaining_workspaces) == 0 and len(remaining_boards) == 0 and len(remaining_columns) == 0 and len(remaining_cards) == 0:
                print("\nSUCCESS: Database cleaned successfully!")
                return True
            else:
                print("\nWARNING: Some data may still remain")
                return False
            
        except Exception as e:
            print(f"\nFAILED: Error during cleanup: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Main function."""
    print(f"Starting database cleanup at {datetime.now()}")
    
    success = await cleanup_test_data()
    
    if success:
        print("\nDatabase cleanup completed successfully!")
        sys.exit(0)
    else:
        print("\nDatabase cleanup failed.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
