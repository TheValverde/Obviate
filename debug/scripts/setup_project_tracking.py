#!/usr/bin/env python3
"""
Setup script to create a project tracking board for Kanban For Agents development.

This creates a workspace and board to track the development of the Kanban system itself.
Meta as hell! 😄

Usage:
    python debug/scripts/setup_project_tracking.py
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
from app.api.v1.endpoints.board import create_board


async def setup_project_tracking():
    """Set up project tracking for Kanban For Agents development."""
    print("=" * 80)
    print("SETTING UP PROJECT TRACKING FOR KANBAN FOR AGENTS")
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
            # Step 1: Create Development Workspace
            print("\n1. Creating Development Workspace...")
            workspace_data = WorkspaceCreate(
                name="AI Agent Development",
                description="Workspace for tracking AI agent and automation projects"
            )
            workspace = await workspace_repo.create(
                data=workspace_data.model_dump(),
                tenant_id=tenant_id
            )
            print(f"SUCCESS: Created workspace '{workspace.name}' with ID: {workspace.id}")
            
            # Step 2: Create Kanban For Agents Project Board
            print("\n2. Creating Kanban For Agents Project Board...")
            board_data = BoardCreate(
                name="Kanban For Agents Development",
                description="Track the development of the Kanban For Agents system itself - META! 😄",
                workspace_id=workspace.id
            )
            
            # Use the API endpoint to create board with default columns
            response = await create_board(
                board_data=board_data,
                board_repo=board_repo,
                column_repo=column_repo,
                tenant_id=tenant_id
            )
            board = response.data
            print(f"SUCCESS: Created board '{board.name}' with ID: {board.id}")
            
            # Step 3: Get the default columns
            print("\n3. Getting default columns...")
            columns = await column_repo.list_by_board(
                board_id=board.id,
                tenant_id=tenant_id
            )
            
            todo_column = next(col for col in columns if col.name == "To Do")
            in_progress_column = next(col for col in columns if col.name == "In Progress")
            done_column = next(col for col in columns if col.name == "Done")
            
            print(f"Found columns: {[col.name for col in columns]}")
            
            # Step 4: Create project tracking cards
            print("\n4. Creating project tracking cards...")
            
            # Cards for "To Do" column
            todo_cards = [
                {
                    "title": "Implement Authentication System",
                    "description": "Add JWT-based authentication with user registration, login, and OAuth integration",
                    "priority": 4,
                    "labels": ["backend", "security", "high-priority"]
                },
                {
                    "title": "Create React Frontend",
                    "description": "Build React 18 frontend with TypeScript, Vite, and Tailwind CSS",
                    "priority": 3,
                    "labels": ["frontend", "ui/ux"]
                },
                {
                    "title": "Add Search Functionality",
                    "description": "Implement semantic search endpoints and advanced filtering capabilities",
                    "priority": 3,
                    "labels": ["backend", "search"]
                },
                {
                    "title": "Set up CI/CD Pipeline",
                    "description": "Configure GitHub Actions for automated testing and deployment",
                    "priority": 2,
                    "labels": ["devops", "automation"]
                },
                {
                    "title": "Add Real-time Collaboration",
                    "description": "Implement WebSocket support for real-time board updates",
                    "priority": 2,
                    "labels": ["backend", "real-time"]
                },
                {
                    "title": "Create Mobile App",
                    "description": "Develop React Native mobile app for iOS and Android",
                    "priority": 1,
                    "labels": ["mobile", "frontend"]
                }
            ]
            
            # Cards for "In Progress" column
            in_progress_cards = [
                {
                    "title": "Fix CardListResponse Import Issue",
                    "description": "Resolve the recurring import error for CardListResponse in schemas",
                    "priority": 5,
                    "labels": ["bug", "backend", "critical"]
                },
                {
                    "title": "Add Production Error Handling",
                    "description": "Implement comprehensive error handling and validation for all endpoints",
                    "priority": 4,
                    "labels": ["backend", "production"]
                }
            ]
            
            # Cards for "Done" column
            done_cards = [
                {
                    "title": "Core Kanban API Implementation",
                    "description": "Complete CRUD operations for workspaces, boards, columns, and cards",
                    "priority": 5,
                    "labels": ["backend", "core-feature", "completed"]
                },
                {
                    "title": "Database Schema Design",
                    "description": "Design and implement PostgreSQL schema with proper relationships",
                    "priority": 5,
                    "labels": ["database", "core-feature", "completed"]
                },
                {
                    "title": "Repository Pattern Implementation",
                    "description": "Implement repository pattern with tenant isolation and async operations",
                    "priority": 4,
                    "labels": ["backend", "architecture", "completed"]
                },
                {
                    "title": "Default Column Creation",
                    "description": "Auto-create default columns when boards are created",
                    "priority": 3,
                    "labels": ["backend", "feature", "completed"]
                },
                {
                    "title": "API Documentation",
                    "description": "Create comprehensive API documentation with examples and guides",
                    "priority": 3,
                    "labels": ["documentation", "completed"]
                }
            ]
            
            # Create cards in "To Do" column
            for i, card_data in enumerate(todo_cards):
                card = CardCreate(
                    title=card_data["title"],
                    description=card_data["description"],
                    board_id=board.id,
                    column_id=todo_column.id,
                    position=i,
                    priority=card_data["priority"],
                    labels=card_data["labels"]
                )
                created_card = await card_repo.create(
                    data=card.model_dump(),
                    tenant_id=tenant_id
                )
                print(f"  - Created card: {created_card.title} (Priority: {created_card.priority})")
            
            # Create cards in "In Progress" column
            for i, card_data in enumerate(in_progress_cards):
                card = CardCreate(
                    title=card_data["title"],
                    description=card_data["description"],
                    board_id=board.id,
                    column_id=in_progress_column.id,
                    position=i,
                    priority=card_data["priority"],
                    labels=card_data["labels"]
                )
                created_card = await card_repo.create(
                    data=card.model_dump(),
                    tenant_id=tenant_id
                )
                print(f"  - Created card: {created_card.title} (Priority: {created_card.priority})")
            
            # Create cards in "Done" column
            for i, card_data in enumerate(done_cards):
                card = CardCreate(
                    title=card_data["title"],
                    description=card_data["description"],
                    board_id=board.id,
                    column_id=done_column.id,
                    position=i,
                    priority=card_data["priority"],
                    labels=card_data["labels"]
                )
                created_card = await card_repo.create(
                    data=card.model_dump(),
                    tenant_id=tenant_id
                )
                print(f"  - Created card: {created_card.title} (Priority: {created_card.priority})")
            
            # Step 5: Summary
            print("\n" + "=" * 80)
            print("PROJECT TRACKING SETUP COMPLETE!")
            print("=" * 80)
            print(f"\nWorkspace: {workspace.name} ({workspace.id})")
            print(f"Board: {board.name} ({board.id})")
            print(f"Columns: {len(columns)} (To Do, In Progress, Done)")
            print(f"Total Cards: {len(todo_cards) + len(in_progress_cards) + len(done_cards)}")
            print(f"  - To Do: {len(todo_cards)} cards")
            print(f"  - In Progress: {len(in_progress_cards)} cards")
            print(f"  - Done: {len(done_cards)} cards")
            
            print(f"\n🎯 You can now track the Kanban For Agents development using the system itself!")
            print(f"🌐 Access the API at: http://localhost:8000/docs")
            print(f"📋 Use the board ID: {board.id}")
            
            return True
            
        except Exception as e:
            print(f"\nFAILED: Error during project setup: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Main function."""
    print(f"Starting project tracking setup at {datetime.now()}")
    
    success = await setup_project_tracking()
    
    if success:
        print("\nProject tracking setup completed successfully!")
        sys.exit(0)
    else:
        print("\nProject tracking setup failed.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
