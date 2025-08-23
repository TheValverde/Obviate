#!/usr/bin/env python3
"""
Interactive Kanban Explorer

A simple interactive script to explore the Kanban For Agents system.
Run this script to interactively explore workspaces, boards, columns, and cards.

Usage:
    python explore_kanban.py
"""

import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import get_db, init_db
from app.repositories import WorkspaceRepository, BoardRepository, ColumnRepository, CardRepository
from app.schemas import WorkspaceCreate, BoardCreate, CardCreate


class KanbanExplorer:
    """Interactive explorer for the Kanban system."""
    
    def __init__(self):
        self.session = None
        self.workspace_repo = None
        self.board_repo = None
        self.column_repo = None
        self.card_repo = None
        self.tenant_id = "default"
        
    async def initialize(self):
        """Initialize the explorer with database connection."""
        await init_db()
        self.session = get_db()
        async for session in self.session:
            self.workspace_repo = WorkspaceRepository(session)
            self.board_repo = BoardRepository(session)
            self.column_repo = ColumnRepository(session)
            self.card_repo = CardRepository(session)
            break
    
    def print_header(self, title: str):
        """Print a formatted header."""
        print("\n" + "=" * 60)
        print(f" {title}")
        print("=" * 60)
    
    def print_menu(self, options: List[Dict[str, str]]):
        """Print a menu with options."""
        print("\nOptions:")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option['title']}")
        print(f"  0. Exit")
    
    async def list_workspaces(self):
        """List all workspaces."""
        self.print_header("WORKSPACES")
        workspaces = await self.workspace_repo.list(tenant_id=self.tenant_id, include_deleted=False)
        
        if not workspaces:
            print("No workspaces found.")
            return
        
        for i, workspace in enumerate(workspaces, 1):
            print(f"\n{i}. {workspace.name}")
            print(f"   ID: {workspace.id}")
            print(f"   Description: {workspace.description}")
            print(f"   Created: {workspace.created_at}")
            print(f"   Archived: {workspace.archived}")
    
    async def list_boards(self, workspace_id: Optional[str] = None):
        """List boards, optionally filtered by workspace."""
        self.print_header("BOARDS")
        
        if workspace_id:
            boards = await self.board_repo.list_by_workspace(workspace_id, self.tenant_id)
        else:
            boards = await self.board_repo.list(tenant_id=self.tenant_id, include_deleted=False)
        
        if not boards:
            print("No boards found.")
            return
        
        for i, board in enumerate(boards, 1):
            print(f"\n{i}. {board.name}")
            print(f"   ID: {board.id}")
            print(f"   Description: {board.description}")
            print(f"   Workspace ID: {board.workspace_id}")
            print(f"   Created: {board.created_at}")
            print(f"   Archived: {board.archived}")
    
    async def list_columns(self, board_id: Optional[str] = None):
        """List columns, optionally filtered by board."""
        self.print_header("COLUMNS")
        
        if board_id:
            columns = await self.column_repo.list_by_board(board_id, self.tenant_id)
        else:
            columns = await self.column_repo.list(tenant_id=self.tenant_id, include_deleted=False)
        
        if not columns:
            print("No columns found.")
            return
        
        for i, column in enumerate(columns, 1):
            print(f"\n{i}. {column.name}")
            print(f"   ID: {column.id}")
            print(f"   Board ID: {column.board_id}")
            print(f"   Position: {column.position}")
            print(f"   WIP Limit: {column.wip_limit or 'No limit'}")
            print(f"   Created: {column.created_at}")
    
    async def list_cards(self, board_id: Optional[str] = None, column_id: Optional[str] = None):
        """List cards, optionally filtered by board or column."""
        self.print_header("CARDS")
        
        if board_id:
            cards = await self.card_repo.list_by_board(board_id, self.tenant_id)
        elif column_id:
            cards = await self.card_repo.list_by_column(column_id, self.tenant_id)
        else:
            cards = await self.card_repo.list(tenant_id=self.tenant_id, include_deleted=False)
        
        if not cards:
            print("No cards found.")
            return
        
        for i, card in enumerate(cards, 1):
            print(f"\n{i}. {card.title}")
            print(f"   ID: {card.id}")
            print(f"   Board ID: {card.board_id}")
            print(f"   Column ID: {card.column_id}")
            print(f"   Position: {card.position}")
            print(f"   Priority: {card.priority}")
            print(f"   Labels: {card.labels or 'None'}")
            print(f"   Assignees: {card.assignees or 'None'}")
            print(f"   Created: {card.created_at}")
    
    async def show_board_details(self, board_id: str):
        """Show detailed information about a board including its columns and cards."""
        self.print_header("BOARD DETAILS")
        
        # Get board
        board = await self.board_repo.get_by_id(board_id, self.tenant_id)
        if not board:
            print(f"Board with ID {board_id} not found.")
            return
        
        print(f"Board: {board.name}")
        print(f"ID: {board.id}")
        print(f"Description: {board.description}")
        print(f"Created: {board.created_at}")
        
        # Get columns
        columns = await self.column_repo.list_by_board(board_id, self.tenant_id)
        print(f"\nColumns ({len(columns)}):")
        
        for column in columns:
            print(f"\n  📋 {column.name} (Position: {column.position})")
            print(f"     ID: {column.id}")
            print(f"     WIP Limit: {column.wip_limit or 'No limit'}")
            
            # Get cards in this column
            cards = await self.card_repo.list_by_column(column.id, self.tenant_id)
            print(f"     Cards ({len(cards)}):")
            
            for card in cards:
                priority_emoji = "🔴" if card.priority == 5 else "🟠" if card.priority == 4 else "🟡" if card.priority == 3 else "🟢" if card.priority == 2 else "⚪"
                print(f"       {priority_emoji} {card.title} (Priority: {card.priority})")
                if card.labels:
                    print(f"         Labels: {', '.join(card.labels)}")
    
    async def create_test_data(self):
        """Create some test data for exploration."""
        self.print_header("CREATING TEST DATA")
        
        try:
            # Create workspace
            workspace_data = WorkspaceCreate(
                name="Test Workspace",
                description="Workspace for testing the explorer"
            )
            workspace = await self.workspace_repo.create(
                data=workspace_data.model_dump(),
                tenant_id=self.tenant_id
            )
            print(f"✅ Created workspace: {workspace.name}")
            
            # Create board
            board_data = BoardCreate(
                name="Test Board",
                description="Board for testing the explorer",
                workspace_id=workspace.id
            )
            board = await self.board_repo.create(
                data=board_data.model_dump(),
                tenant_id=self.tenant_id
            )
            print(f"✅ Created board: {board.name}")
            
            # Create columns
            column_names = ["Backlog", "In Progress", "Review", "Done"]
            for i, name in enumerate(column_names):
                column_data = {
                    "name": name,
                    "board_id": board.id,
                    "position": i,
                    "wip_limit": 5 if name == "In Progress" else None
                }
                column = await self.column_repo.create(
                    data=column_data,
                    tenant_id=self.tenant_id
                )
                print(f"✅ Created column: {column.name}")
            
            # Create some cards
            cards_data = [
                {"title": "Design User Interface", "description": "Create wireframes and mockups", "priority": 4, "labels": ["design", "ui/ux"]},
                {"title": "Implement API Endpoints", "description": "Build REST API with FastAPI", "priority": 5, "labels": ["backend", "api"]},
                {"title": "Write Documentation", "description": "Create comprehensive docs", "priority": 3, "labels": ["documentation"]},
                {"title": "Set up CI/CD", "description": "Configure automated testing", "priority": 2, "labels": ["devops"]},
            ]
            
            columns = await self.column_repo.list_by_board(board.id, self.tenant_id)
            for i, card_data in enumerate(cards_data):
                column = columns[i % len(columns)]  # Distribute cards across columns
                card = CardCreate(
                    title=card_data["title"],
                    description=card_data["description"],
                    board_id=board.id,
                    column_id=column.id,
                    position=i,
                    priority=card_data["priority"],
                    labels=card_data["labels"]
                )
                created_card = await self.card_repo.create(
                    data=card.model_dump(),
                    tenant_id=self.tenant_id
                )
                print(f"✅ Created card: {created_card.title}")
            
            print(f"\n🎉 Test data created successfully!")
            print(f"Workspace ID: {workspace.id}")
            print(f"Board ID: {board.id}")
            
        except Exception as e:
            print(f"❌ Error creating test data: {str(e)}")
    
    async def main_menu(self):
        """Main interactive menu."""
        while True:
            self.print_header("KANBAN EXPLORER")
            print(f"Tenant ID: {self.tenant_id}")
            print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            options = [
                {"title": "List Workspaces", "action": self.list_workspaces},
                {"title": "List Boards", "action": self.list_boards},
                {"title": "List Columns", "action": self.list_columns},
                {"title": "List Cards", "action": self.list_cards},
                {"title": "Show Board Details", "action": self.show_board_details},
                {"title": "Create Test Data", "action": self.create_test_data},
            ]
            
            self.print_menu(options)
            
            try:
                choice = input("\nEnter your choice (0-6): ").strip()
                
                if choice == "0":
                    print("\n👋 Goodbye!")
                    break
                elif choice == "1":
                    await self.list_workspaces()
                elif choice == "2":
                    await self.list_boards()
                elif choice == "3":
                    await self.list_columns()
                elif choice == "4":
                    await self.list_cards()
                elif choice == "5":
                    board_id = input("Enter board ID: ").strip()
                    if board_id:
                        await self.show_board_details(board_id)
                elif choice == "6":
                    await self.create_test_data()
                else:
                    print("❌ Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
            
            input("\nPress Enter to continue...")


async def main():
    """Main function."""
    print("🚀 Starting Kanban Explorer...")
    
    explorer = KanbanExplorer()
    await explorer.initialize()
    
    print("✅ Explorer initialized successfully!")
    await explorer.main_menu()


if __name__ == "__main__":
    asyncio.run(main())
