"""
Column repository for column-specific database operations.
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from .base import BaseRepository
from app.models.column import Column


class ColumnRepository(BaseRepository[Column]):
    """
    Repository for column operations with tenant isolation.
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(Column, session)
    
    async def list_by_board(
        self,
        board_id: str,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False
    ) -> List[Column]:
        """
        List columns within a board with tenant isolation, ordered by position.
        
        Args:
            board_id: Board ID
            tenant_id: Tenant ID for isolation
            limit: Maximum number of columns to return
            offset: Number of columns to skip
            include_deleted: Whether to include soft-deleted columns
            
        Returns:
            List of column instances ordered by position
        """
        return await self.list(
            tenant_id=tenant_id,
            limit=limit,
            offset=offset,
            include_deleted=include_deleted,
            order_by="position",
            filters={"board_id": board_id}
        )
    
    async def get_by_position(
        self,
        board_id: str,
        position: int,
        tenant_id: str,
        include_deleted: bool = False
    ) -> Optional[Column]:
        """
        Get column by position within a board with tenant isolation.
        
        Args:
            board_id: Board ID
            position: Column position
            tenant_id: Tenant ID for isolation
            include_deleted: Whether to include soft-deleted columns
            
        Returns:
            Column instance or None if not found
        """
        query = select(self.model).where(
            and_(
                self.model.board_id == board_id,
                self.model.position == position,
                self.model.tenant_id == tenant_id
            )
        )
        
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_max_position(
        self,
        board_id: str,
        tenant_id: str,
        include_deleted: bool = False
    ) -> int:
        """
        Get the maximum position value for columns in a board.
        
        Args:
            board_id: Board ID
            tenant_id: Tenant ID for isolation
            include_deleted: Whether to include soft-deleted columns
            
        Returns:
            Maximum position value (0 if no columns exist)
        """
        query = select(func.max(self.model.position)).where(
            and_(
                self.model.board_id == board_id,
                self.model.tenant_id == tenant_id
            )
        )
        
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        
        result = await self.session.execute(query)
        max_position = result.scalar()
        return max_position if max_position is not None else 0
    
    async def reorder_columns(
        self,
        board_id: str,
        tenant_id: str,
        column_positions: List[tuple[str, int]]
    ) -> bool:
        """
        Reorder columns within a board by updating their positions.
        
        Args:
            board_id: Board ID
            tenant_id: Tenant ID for isolation
            column_positions: List of (column_id, new_position) tuples
            
        Returns:
            True if reordering was successful
        """
        try:
            for column_id, new_position in column_positions:
                await self.update(
                    entity_id=column_id,
                    tenant_id=tenant_id,
                    data={"position": new_position}
                )
            return True
        except Exception:
            await self.session.rollback()
            return False
    
    async def move_column(
        self,
        column_id: str,
        board_id: str,
        new_position: int,
        tenant_id: str,
        version: Optional[int] = None
    ) -> Optional[Column]:
        """
        Move a column to a new position within a board.
        
        Args:
            column_id: Column ID
            board_id: Board ID
            new_position: New position
            tenant_id: Tenant ID for isolation
            version: Expected version for optimistic concurrency
            
        Returns:
            Updated column instance or None if not found
        """
        return await self.update(
            entity_id=column_id,
            tenant_id=tenant_id,
            data={
                "board_id": board_id,
                "position": new_position
            },
            version=version
        )
    
    async def count_by_board(
        self,
        board_id: str,
        tenant_id: str,
        include_deleted: bool = False
    ) -> int:
        """
        Count columns within a board with tenant isolation.
        
        Args:
            board_id: Board ID
            tenant_id: Tenant ID for isolation
            include_deleted: Whether to include soft-deleted columns
            
        Returns:
            Number of columns
        """
        return await self.count(
            tenant_id=tenant_id,
            include_deleted=include_deleted,
            filters={"board_id": board_id}
        )
