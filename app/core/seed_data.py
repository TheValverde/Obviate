"""
Seed data script for development environment.
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories import (
    WorkspaceRepository,
    BoardRepository,
    ColumnRepository,
    CardRepository,
    CommentRepository,
    AttachmentRepository,
    AuditEventRepository,
    ServiceTokenRepository,
)


async def create_seed_data(tenant_id: str = "default") -> None:
    """
    Create seed data for development environment.
    
    Args:
        tenant_id: Tenant ID for the seed data
    """
    async for session in get_db():
        try:
            # Create repositories
            workspace_repo = WorkspaceRepository(session)
            board_repo = BoardRepository(session)
            column_repo = ColumnRepository(session)
            card_repo = CardRepository(session)
            comment_repo = CommentRepository(session)
            attachment_repo = AttachmentRepository(session)
            audit_repo = AuditEventRepository(session)
            token_repo = ServiceTokenRepository(session)
            
            print(f"Creating seed data for tenant: {tenant_id}")
            
            # 1. Create default workspace
            print("Creating default workspace...")
            workspace = await workspace_repo.create(
                data={
                    "name": "Default Workspace",
                },
                tenant_id=tenant_id
            )
            print(f"Created workspace: {workspace.name} (ID: {workspace.id})")
            
            # 2. Create sample board
            print("Creating sample board...")
            board = await board_repo.create(
                data={
                    "name": "Agent Backlog",
                    "description": "Sample board for agent task management",
                    "workspace_id": workspace.id,
                    "is_archived": False,
                    "template": {
                        "type": "kanban",
                        "columns": ["Todo", "Doing", "Done"]
                    },
                    "meta_data": {
                        "created_by": "system",
                        "purpose": "development"
                    }
                },
                tenant_id=tenant_id
            )
            print(f"Created board: {board.name} (ID: {board.id})")
            
            # 3. Create columns
            print("Creating columns...")
            columns = []
            column_names = ["Todo", "Doing", "Done"]
            
            for i, name in enumerate(column_names):
                column = await column_repo.create(
                    data={
                        "name": name,
                        "board_id": board.id,
                        "position": i + 1,
                        "wip_limit": None if name == "Done" else 5,
                        "meta_data": {
                            "color": "#3B82F6" if name == "Todo" else "#F59E0B" if name == "Doing" else "#10B981"
                        }
                    },
                    tenant_id=tenant_id
                )
                columns.append(column)
                print(f"Created column: {column.name} (ID: {column.id})")
            
            # 4. Create sample cards
            print("Creating sample cards...")
            sample_cards = [
                {
                    "title": "Implement API authentication",
                    "description": "Add bearer token authentication to all API endpoints",
                    "board_id": board.id,
                    "column_id": columns[0].id,  # Todo
                    "position": 1,
                    "priority": 3,  # 3 = high priority
                    "labels": ["backend", "security"],
                    "assignees": ["agent:auth-specialist"],
                    "agent_context": {
                        "agent_id": "auth-specialist",
                        "capabilities": ["authentication", "security"],
                        "estimated_duration": "2-3 hours"
                    },
                    "workflow_state": {
                        "status": "pending",
                        "blocked_by": [],
                        "dependencies": []
                    },
                    "fields": {
                        "story_points": 5,
                        "epic": "Security Implementation"
                    }
                },
                {
                    "title": "Design database schema",
                    "description": "Create comprehensive database schema for the Kanban system",
                    "board_id": board.id,
                    "column_id": columns[1].id,  # Doing
                    "position": 1,
                    "priority": 2,  # 2 = medium priority
                    "labels": ["database", "design"],
                    "assignees": ["agent:db-architect"],
                    "agent_context": {
                        "agent_id": "db-architect",
                        "capabilities": ["database_design", "sql"],
                        "estimated_duration": "4-6 hours"
                    },
                    "workflow_state": {
                        "status": "in_progress",
                        "blocked_by": [],
                        "dependencies": []
                    },
                    "fields": {
                        "story_points": 8,
                        "epic": "Database Foundation"
                    }
                },
                {
                    "title": "Set up CI/CD pipeline",
                    "description": "Configure GitHub Actions for automated testing and deployment",
                    "board_id": board.id,
                    "column_id": columns[2].id,  # Done
                    "position": 1,
                    "priority": 3,  # 3 = high priority
                    "labels": ["devops", "automation"],
                    "assignees": ["agent:devops-engineer"],
                    "agent_context": {
                        "agent_id": "devops-engineer",
                        "capabilities": ["ci_cd", "github_actions"],
                        "estimated_duration": "3-4 hours"
                    },
                    "workflow_state": {
                        "status": "completed",
                        "blocked_by": [],
                        "dependencies": [],
                        "completed_at": "2024-01-15T10:00:00Z"
                    },
                    "fields": {
                        "story_points": 6,
                        "epic": "DevOps Setup"
                    }
                },
                {
                    "title": "Create frontend components",
                    "description": "Build React components for the Kanban board interface",
                    "board_id": board.id,
                    "column_id": columns[0].id,  # Todo
                    "position": 2,
                    "priority": 2,  # 2 = medium priority
                    "labels": ["frontend", "react"],
                    "assignees": ["agent:frontend-developer"],
                    "agent_context": {
                        "agent_id": "frontend-developer",
                        "capabilities": ["react", "typescript", "ui_design"],
                        "estimated_duration": "8-10 hours"
                    },
                    "workflow_state": {
                        "status": "pending",
                        "blocked_by": ["Implement API authentication"],
                        "dependencies": ["api-auth"]
                    },
                    "fields": {
                        "story_points": 13,
                        "epic": "Frontend Development"
                    }
                }
            ]
            
            created_cards = []
            for card_data in sample_cards:
                card = await card_repo.create(
                    data=card_data,
                    tenant_id=tenant_id
                )
                created_cards.append(card)
                print(f"Created card: {card.title} (ID: {card.id})")
            
            # 5. Create sample comments
            print("Creating sample comments...")
            sample_comments = [
                {
                    "card_id": created_cards[0].id,
                    "author": "agent:auth-specialist",
                    "body": "Starting implementation of JWT token validation",
                    "meta_data": {
                        "agent_context": "auth-specialist",
                        "timestamp": "2024-01-15T09:00:00Z"
                    }
                },
                {
                    "card_id": created_cards[1].id,
                    "author": "agent:db-architect",
                    "body": "Database schema design completed. Ready for review.",
                    "meta_data": {
                        "agent_context": "db-architect",
                        "timestamp": "2024-01-15T11:30:00Z"
                    }
                }
            ]
            
            for comment_data in sample_comments:
                comment = await comment_repo.create(
                    data=comment_data,
                    tenant_id=tenant_id
                )
                print(f"Created comment: {comment.body[:50]}... (ID: {comment.id})")
            
            # 6. Create sample audit events
            print("Creating sample audit events...")
            sample_audit_events = [
                {
                    "entity_type": "board",
                    "entity_id": board.id,
                    "action": "created",
                    "actor": "system",
                    "agent_context": {
                        "agent_id": "system",
                        "action": "seed_data_creation"
                    },
                    "payload": {
                        "board_name": board.name,
                        "workspace_id": workspace.id
                    }
                },
                {
                    "entity_type": "card",
                    "entity_id": created_cards[0].id,
                    "action": "created",
                    "actor": "system",
                    "agent_context": {
                        "agent_id": "system",
                        "action": "seed_data_creation"
                    },
                    "payload": {
                        "card_title": created_cards[0].title,
                        "column_id": created_cards[0].column_id
                    }
                }
            ]
            
            for audit_data in sample_audit_events:
                audit_event = await audit_repo.create(
                    data=audit_data,
                    tenant_id=tenant_id
                )
                print(f"Created audit event: {audit_event.action} (ID: {audit_event.id})")
            
            # 7. Create sample service token
            print("Creating sample service token...")
            service_token = await token_repo.create(
                data={
                    "name": "Development API Token",
                    "token_hash": "dev_token_hash_placeholder",  # In real app, this would be hashed
                    "scopes": ["read", "write"],  # Array of scopes
                    "revoked_at": None,  # Not revoked
                },
                tenant_id=tenant_id
            )
            print(f"Created service token: {service_token.name} (ID: {service_token.id})")
            
            print("\n✅ Seed data creation completed successfully!")
            print(f"Created:")
            print(f"  - 1 workspace")
            print(f"  - 1 board")
            print(f"  - {len(columns)} columns")
            print(f"  - {len(created_cards)} cards")
            print(f"  - {len(sample_comments)} comments")
            print(f"  - {len(sample_audit_events)} audit events")
            print(f"  - 1 service token")
            
        except Exception as e:
            print(f"❌ Error creating seed data: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def main():
    """Main function to run seed data creation."""
    from app.core.database import init_db
    
    # Initialize database
    await init_db()
    
    # Create seed data
    await create_seed_data()


if __name__ == "__main__":
    asyncio.run(main())
