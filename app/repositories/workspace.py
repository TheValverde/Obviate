"""
Workspace repository for workspace-specific database operations.
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from .base import BaseRepository
from app.models.workspace import Workspace


class WorkspaceRepository(BaseRepository[Workspace]):
    """
    Repository for workspace operations with tenant isolation.
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(Workspace, session)
    
    async def get_by_name(
        self, 
        name: str, 
        tenant_id: str,
        include_deleted: bool = False
    ) -> Optional[Workspace]:
        """
        Get workspace by name with tenant isolation.
        
        Args:
            name: Workspace name
            tenant_id: Tenant ID for isolation
            include_deleted: Whether to include soft-deleted workspaces
            
        Returns:
            Workspace instance or None if not found
        """
        query = select(self.model).where(
            and_(
                self.model.name == name,
                self.model.tenant_id == tenant_id
            )
        )
        
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def list_active(
        self,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Workspace]:
        """
        List active (non-archived) workspaces with tenant isolation.
        
        Args:
            tenant_id: Tenant ID for isolation
            limit: Maximum number of workspaces to return
            offset: Number of workspaces to skip
            
        Returns:
            List of active workspace instances
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
        workspace_id: str,
        tenant_id: str,
        version: Optional[int] = None
    ) -> Optional[Workspace]:
        """
        Archive a workspace with optimistic concurrency support.
        
        Args:
            workspace_id: Workspace ID
            tenant_id: Tenant ID for isolation
            version: Expected version for optimistic concurrency
            
        Returns:
            Archived workspace instance or None if not found
        """
        return await self.update(
            entity_id=workspace_id,
            tenant_id=tenant_id,
            data={"is_archived": True},
            version=version
        )
    
    async def unarchive(
        self,
        workspace_id: str,
        tenant_id: str,
        version: Optional[int] = None
    ) -> Optional[Workspace]:
        """
        Unarchive a workspace with optimistic concurrency support.
        
        Args:
            workspace_id: Workspace ID
            tenant_id: Tenant ID for isolation
            version: Expected version for optimistic concurrency
            
        Returns:
            Unarchived workspace instance or None if not found
        """
        return await self.update(
            entity_id=workspace_id,
            tenant_id=tenant_id,
            data={"is_archived": False},
            version=version
        )
