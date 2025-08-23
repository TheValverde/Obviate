"""
Audit event repository for audit event-specific database operations.
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from .base import BaseRepository
from app.models.audit_event import AuditEvent


class AuditEventRepository(BaseRepository[AuditEvent]):
    """
    Repository for audit event operations with tenant isolation.
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(AuditEvent, session)
    
    async def list_by_entity(
        self,
        entity_type: str,
        entity_id: str,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False
    ) -> List[AuditEvent]:
        """
        List audit events for a specific entity with tenant isolation.
        
        Args:
            entity_type: Entity type (e.g., 'card', 'board', 'column')
            entity_id: Entity ID
            tenant_id: Tenant ID for isolation
            limit: Maximum number of events to return
            offset: Number of events to skip
            include_deleted: Whether to include soft-deleted events
            
        Returns:
            List of audit event instances ordered by creation date
        """
        return await self.list(
            tenant_id=tenant_id,
            limit=limit,
            offset=offset,
            include_deleted=include_deleted,
            order_by="created_at",
            filters={
                "entity_type": entity_type,
                "entity_id": entity_id
            }
        )
    
    async def list_by_board(
        self,
        board_id: str,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False
    ) -> List[AuditEvent]:
        """
        List audit events for a board with tenant isolation.
        
        Args:
            board_id: Board ID
            tenant_id: Tenant ID for isolation
            limit: Maximum number of events to return
            offset: Number of events to skip
            include_deleted: Whether to include soft-deleted events
            
        Returns:
            List of audit event instances ordered by creation date
        """
        return await self.list_by_entity(
            entity_type="board",
            entity_id=board_id,
            tenant_id=tenant_id,
            limit=limit,
            offset=offset,
            include_deleted=include_deleted
        )
    
    async def list_by_card(
        self,
        card_id: str,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False
    ) -> List[AuditEvent]:
        """
        List audit events for a card with tenant isolation.
        
        Args:
            card_id: Card ID
            tenant_id: Tenant ID for isolation
            limit: Maximum number of events to return
            offset: Number of events to skip
            include_deleted: Whether to include soft-deleted events
            
        Returns:
            List of audit event instances ordered by creation date
        """
        return await self.list_by_entity(
            entity_type="card",
            entity_id=card_id,
            tenant_id=tenant_id,
            limit=limit,
            offset=offset,
            include_deleted=include_deleted
        )
    
    async def count_by_entity(
        self,
        entity_type: str,
        entity_id: str,
        tenant_id: str,
        include_deleted: bool = False
    ) -> int:
        """
        Count audit events for a specific entity with tenant isolation.
        
        Args:
            entity_type: Entity type (e.g., 'card', 'board', 'column')
            entity_id: Entity ID
            tenant_id: Tenant ID for isolation
            include_deleted: Whether to include soft-deleted events
            
        Returns:
            Number of audit events
        """
        return await self.count(
            tenant_id=tenant_id,
            include_deleted=include_deleted,
            filters={
                "entity_type": entity_type,
                "entity_id": entity_id
            }
        )
