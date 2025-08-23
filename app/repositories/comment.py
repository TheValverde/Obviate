"""
Comment repository for comment-specific database operations.
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from .base import BaseRepository
from app.models.comment import Comment


class CommentRepository(BaseRepository[Comment]):
    """
    Repository for comment operations with tenant isolation.
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(Comment, session)
    
    async def list_by_card(
        self,
        card_id: str,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False
    ) -> List[Comment]:
        """
        List comments for a card with tenant isolation, ordered by creation date.
        
        Args:
            card_id: Card ID
            tenant_id: Tenant ID for isolation
            limit: Maximum number of comments to return
            offset: Number of comments to skip
            include_deleted: Whether to include soft-deleted comments
            
        Returns:
            List of comment instances ordered by creation date
        """
        return await self.list(
            tenant_id=tenant_id,
            limit=limit,
            offset=offset,
            include_deleted=include_deleted,
            order_by="created_at",
            filters={"card_id": card_id}
        )
    
    async def count_by_card(
        self,
        card_id: str,
        tenant_id: str,
        include_deleted: bool = False
    ) -> int:
        """
        Count comments for a card with tenant isolation.
        
        Args:
            card_id: Card ID
            tenant_id: Tenant ID for isolation
            include_deleted: Whether to include soft-deleted comments
            
        Returns:
            Number of comments
        """
        return await self.count(
            tenant_id=tenant_id,
            include_deleted=include_deleted,
            filters={"card_id": card_id}
        )
