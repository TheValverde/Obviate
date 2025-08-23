#!/usr/bin/env python3
"""
Update script to modify the project tracking board priorities and remove unwanted cards.

This script will:
1. Delete "Create Mobile App" and "Add Real-time Collaboration" cards
2. Update priorities for remaining cards
3. Reorder cards based on new priorities

Usage:
    python debug/scripts/update_project_priorities.py
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
from app.schemas import CardUpdate


async def update_project_priorities():
    """Update the project tracking board with new priorities and remove unwanted cards."""
    print("=" * 80)
    print("UPDATING PROJECT TRACKING BOARD PRIORITIES")
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
            # Find the project tracking board
            print("\n1. Finding project tracking board...")
            workspaces = await workspace_repo.list(tenant_id=tenant_id, include_deleted=False)
            workspace = next((w for w in workspaces if w.name == "AI Agent Development"), None)
            
            if not workspace:
                print("❌ AI Agent Development workspace not found!")
                return False
            
            boards = await board_repo.list_by_workspace(workspace.id, tenant_id)
            board = next((b for b in boards if b.name == "Kanban For Agents Development"), None)
            
            if not board:
                print("❌ Kanban For Agents Development board not found!")
                return False
            
            print(f"✅ Found board: {board.name} ({board.id})")
            
            # Get all cards on the board
            print("\n2. Getting all cards on the board...")
            all_cards = await card_repo.list_by_board(board.id, tenant_id)
            print(f"Found {len(all_cards)} cards")
            
            # Cards to delete
            cards_to_delete = [
                "Create Mobile App",
                "Add Real-time Collaboration"
            ]
            
            # Delete unwanted cards
            print("\n3. Deleting unwanted cards...")
            for card in all_cards:
                if card.title in cards_to_delete:
                    await card_repo.delete(card.id, tenant_id, hard_delete=True)
                    print(f"🗑️  Deleted: {card.title}")
            
            # Get updated card list
            all_cards = await card_repo.list_by_board(board.id, tenant_id)
            
            # New priorities mapping
            priority_updates = {
                "Implement Authentication System": 3,  # Between frontend and search
                "Create React Frontend": 2,  # Lower priority
                "Add Search Functionality": 4,  # Higher priority
                "Set up CI/CD Pipeline": 1,  # Ultra low priority
                "Fix CardListResponse Import Issue": 5,  # Critical (keep as is)
                "Add Production Error Handling": 4,  # Keep as is
            }
            
            # Update priorities
            print("\n4. Updating card priorities...")
            for card in all_cards:
                if card.title in priority_updates:
                    new_priority = priority_updates[card.title]
                    if card.priority != new_priority:
                        update_data = CardUpdate(priority=new_priority)
                        await card_repo.update(card.id, tenant_id, update_data.model_dump(exclude_unset=True))
                        print(f"📊 Updated priority for '{card.title}': {card.priority} → {new_priority}")
                    else:
                        print(f"ℹ️  '{card.title}' already has correct priority: {card.priority}")
                else:
                    print(f"ℹ️  Keeping '{card.title}' with current priority: {card.priority}")
            
            # Get final card list and show summary
            print("\n5. Final project status:")
            print("=" * 60)
            
            columns = await column_repo.list_by_board(board.id, tenant_id)
            todo_column = next((col for col in columns if col.name == "To Do"), None)
            in_progress_column = next((col for col in columns if col.name == "In Progress"), None)
            done_column = next((col for col in columns if col.name == "Done"), None)
            
            if todo_column:
                todo_cards = await card_repo.list_by_column(todo_column.id, tenant_id)
                print(f"\n📋 TO DO ({len(todo_cards)} cards):")
                for card in sorted(todo_cards, key=lambda c: c.priority, reverse=True):
                    priority_emoji = "🔴" if card.priority == 5 else "🟠" if card.priority == 4 else "🟡" if card.priority == 3 else "🟢" if card.priority == 2 else "⚪"
                    print(f"  {priority_emoji} {card.title} (Priority: {card.priority})")
            
            if in_progress_column:
                in_progress_cards = await card_repo.list_by_column(in_progress_column.id, tenant_id)
                print(f"\n🔄 IN PROGRESS ({len(in_progress_cards)} cards):")
                for card in sorted(in_progress_cards, key=lambda c: c.priority, reverse=True):
                    priority_emoji = "🔴" if card.priority == 5 else "🟠" if card.priority == 4 else "🟡" if card.priority == 3 else "🟢" if card.priority == 2 else "⚪"
                    print(f"  {priority_emoji} {card.title} (Priority: {card.priority})")
            
            if done_column:
                done_cards = await card_repo.list_by_column(done_column.id, tenant_id)
                print(f"\n✅ DONE ({len(done_cards)} cards):")
                for card in sorted(done_cards, key=lambda c: c.priority, reverse=True):
                    priority_emoji = "🔴" if card.priority == 5 else "🟠" if card.priority == 4 else "🟡" if card.priority == 3 else "🟢" if card.priority == 2 else "⚪"
                    print(f"  {priority_emoji} {card.title} (Priority: {card.priority})")
            
            print(f"\n🎯 Project tracking board updated successfully!")
            print(f"📋 Board ID: {board.id}")
            print(f"🌐 Access at: http://localhost:8000/docs")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error updating project priorities: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Main function."""
    print(f"Starting project priority updates at {datetime.now()}")
    
    success = await update_project_priorities()
    
    if success:
        print("\n✅ Project priorities updated successfully!")
        sys.exit(0)
    else:
        print("\n❌ Project priority updates failed.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
