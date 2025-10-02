"""
Column repository for column-specific database operations.
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, update
from datetime import datetime, timezone

from .base import BaseRepository
from app.models.column import Column
from app.models.card import Card


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

    async def delete(
        self,
        entity_id: str,
        tenant_id: str,
        version: Optional[int] = None,
        hard_delete: bool = False
    ) -> bool:
        """
        Delete a column with cascade deletion of its cards.
        
        This method ensures that when a column is deleted, all cards in that column
        are also deleted to prevent orphaned records.
        
        Args:
            entity_id: Column ID
            tenant_id: Tenant ID for isolation
            version: Expected version for optimistic concurrency
            hard_delete: Whether to perform hard delete instead of soft delete
            
        Returns:
            True if column was deleted, False if not found
        """
        # First, get the column to verify it exists and get its board_id
        column = await self.get_by_id(entity_id, tenant_id)
        if not column:
            return False
        
        # If version check is required, verify it matches
        if version is not None and column.version != version:
            return False
        
        try:
            if hard_delete:
                # Hard delete: Delete cards first, then column
                # Delete all cards in this column
                card_delete_query = delete(Card).where(
                    and_(
                        Card.column_id == entity_id,
                        Card.tenant_id == tenant_id
                    )
                )
                await self.session.execute(card_delete_query)
                
                # Delete the column
                column_delete_query = delete(self.model).where(
                    and_(
                        self.model.id == entity_id,
                        self.model.tenant_id == tenant_id
                    )
                )
                if version is not None:
                    column_delete_query = column_delete_query.where(self.model.version == version)
                
                result = await self.session.execute(column_delete_query)
                await self.session.commit()
                return result.rowcount > 0
            else:
                # Soft delete: Mark cards as deleted first, then column
                # Soft delete all cards in this column
                card_update_query = update(Card).where(
                    and_(
                        Card.column_id == entity_id,
                        Card.tenant_id == tenant_id,
                        Card.deleted_at.is_(None)  # Only update non-deleted cards
                    )
                ).values(
                    deleted_at=datetime.now(timezone.utc),
                    version=Card.version + 1
                )
                await self.session.execute(card_update_query)
                
                # Soft delete the column
                column_update_query = update(self.model).where(
                    and_(
                        self.model.id == entity_id,
                        self.model.tenant_id == tenant_id
                    )
                )
                
                if version is not None:
                    column_update_query = column_update_query.where(self.model.version == version)
                    column_update_query = column_update_query.values(version=version + 1)
                
                # Set deleted_at timestamp
                column_update_query = column_update_query.values(
                    deleted_at=datetime.now(timezone.utc)
                )
                
                result = await self.session.execute(column_update_query)
                await self.session.commit()
                return result.rowcount > 0
                
        except Exception:
            await self.session.rollback()
            return False
