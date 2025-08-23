"""
Board repository for board-specific database operations.
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from .base import BaseRepository
from app.models.board import Board


class BoardRepository(BaseRepository[Board]):
    """
    Repository for board operations with tenant isolation.
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(Board, session)
    
    async def get_by_name(
        self, 
        name: str, 
        workspace_id: str,
        tenant_id: str,
        include_deleted: bool = False
    ) -> Optional[Board]:
        """
        Get board by name within a workspace with tenant isolation.
        
        Args:
            name: Board name
            workspace_id: Workspace ID
            tenant_id: Tenant ID for isolation
            include_deleted: Whether to include soft-deleted boards
            
        Returns:
            Board instance or None if not found
        """
        query = select(self.model).where(
            and_(
                self.model.name == name,
                self.model.workspace_id == workspace_id,
                self.model.tenant_id == tenant_id
            )
        )
        
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def list_by_workspace(
        self,
        workspace_id: str,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0,
        include_archived: bool = False,
        include_deleted: bool = False
    ) -> List[Board]:
        """
        List boards within a workspace with tenant isolation.
        
        Args:
            workspace_id: Workspace ID
            tenant_id: Tenant ID for isolation
            limit: Maximum number of boards to return
            offset: Number of boards to skip
            include_archived: Whether to include archived boards
            include_deleted: Whether to include soft-deleted boards
            
        Returns:
            List of board instances
        """
        filters = {"workspace_id": workspace_id}
        
        if not include_archived:
            filters["is_archived"] = False
        
        return await self.list(
            tenant_id=tenant_id,
            limit=limit,
            offset=offset,
            include_deleted=include_deleted,
            filters=filters
        )
    
    async def list_active(
        self,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Board]:
        """
        List active (non-archived) boards with tenant isolation.
        
        Args:
            tenant_id: Tenant ID for isolation
            limit: Maximum number of boards to return
            offset: Number of boards to skip
            
        Returns:
            List of active board instances
        """
        return await self.list(
            tenant_id=tenant_id,
            limit=limit,
            offset=offset,
            include_deleted=False,
            filters={"is_archived": False}
        )
    
    async def archive(
        self,
        board_id: str,
        tenant_id: str,
        version: Optional[int] = None
    ) -> Optional[Board]:
        """
        Archive a board with optimistic concurrency support.
        
        Args:
            board_id: Board ID
            tenant_id: Tenant ID for isolation
            version: Expected version for optimistic concurrency
            
        Returns:
            Archived board instance or None if not found
        """
        return await self.update(
            entity_id=board_id,
            tenant_id=tenant_id,
            data={"is_archived": True},
            version=version
        )
    
    async def unarchive(
        self,
        board_id: str,
        tenant_id: str,
        version: Optional[int] = None
    ) -> Optional[Board]:
        """
        Unarchive a board with optimistic concurrency support.
        
        Args:
            board_id: Board ID
            tenant_id: Tenant ID for isolation
            version: Expected version for optimistic concurrency
            
        Returns:
            Unarchived board instance or None if not found
        """
        return await self.update(
            entity_id=board_id,
            tenant_id=tenant_id,
            data={"is_archived": False},
            version=version
        )
    
    async def count_by_workspace(
        self,
        workspace_id: str,
        tenant_id: str,
        include_archived: bool = False,
        include_deleted: bool = False
    ) -> int:
        """
        Count boards within a workspace with tenant isolation.
        
        Args:
            workspace_id: Workspace ID
            tenant_id: Tenant ID for isolation
            include_archived: Whether to include archived boards
            include_deleted: Whether to include soft-deleted boards
            
        Returns:
            Number of boards
        """
        filters = {"workspace_id": workspace_id}
        
        if not include_archived:
            filters["is_archived"] = False
        
        return await self.count(
            tenant_id=tenant_id,
            include_deleted=include_deleted,
            filters=filters
        )
