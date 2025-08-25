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
    
    async def batch_update_positions(
        self,
        board_id: str,
        tenant_id: str,
        column_positions: List[tuple[str, int]]
    ) -> bool:
        """
        Batch update column positions within a board (internal helper).
        
        Args:
            board_id: Board ID
            tenant_id: Tenant ID for isolation
            column_positions: List of (column_id, new_position) tuples
            
        Returns:
            True if batch update was successful
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

    async def reorder_column(
        self,
        column_id: str,
        board_id: str,
        new_position: int,
        tenant_id: str
    ) -> bool:
        """
        Reorder a column using "insert and shift" logic.
        
        This method implements proper reordering where:
        1. The target column is moved to the new position
        2. Other columns are shifted to accommodate the move
        3. Positions are clamped to valid bounds
        
        Args:
            column_id: Column ID to reorder
            board_id: Board ID
            new_position: Target position (will be clamped to valid range)
            tenant_id: Tenant ID for isolation
            
        Returns:
            True if reordering was successful
        """
        try:
            # Get all columns in the board, ordered by position
            columns = await self.list_by_board(
                board_id=board_id,
                tenant_id=tenant_id,
                limit=1000,
                offset=0
            )
            
            if not columns:
                return False
            
            # Find the column to move
            target_column = None
            old_position = -1
            for col in columns:
                if col.id == column_id:
                    target_column = col
                    old_position = col.position
                    break
            
            if not target_column:
                return False
            
            # Clamp new_position to valid range [0, max_position]
            max_position = len(columns) - 1
            new_position = max(0, min(new_position, max_position))
            
            # If position hasn't changed, no need to reorder
            if old_position == new_position:
                return True
            
            # Create new position mapping
            new_positions = []
            
            if old_position < new_position:
                # Moving forward: shift columns in range [old_pos+1, new_pos] left by 1
                for col in columns:
                    if col.id == column_id:
                        # Target column gets new position
                        new_positions.append((col.id, new_position))
                    elif old_position < col.position <= new_position:
                        # Shift left by 1
                        new_positions.append((col.id, col.position - 1))
                    else:
                        # Keep same position
                        new_positions.append((col.id, col.position))
            else:
                # Moving backward: shift columns in range [new_pos, old_pos-1] right by 1
                for col in columns:
                    if col.id == column_id:
                        # Target column gets new position
                        new_positions.append((col.id, new_position))
                    elif new_position <= col.position < old_position:
                        # Shift right by 1
                        new_positions.append((col.id, col.position + 1))
                    else:
                        # Keep same position
                        new_positions.append((col.id, col.position))
            
            # Batch update all positions
            return await self.batch_update_positions(board_id, tenant_id, new_positions)
            
        except Exception:
            await self.session.rollback()
            return False
    

    
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
