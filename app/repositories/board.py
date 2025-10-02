"""
Board repository for board-specific database operations.
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update, delete
from datetime import datetime, timezone

from .base import BaseRepository
from app.models.board import Board
from app.models.column import Column
from app.models.card import Card


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

    async def delete(
        self,
        entity_id: str,
        tenant_id: str,
        version: Optional[int] = None,
        hard_delete: bool = False
    ) -> bool:
        """
        Delete a board with cascade deletion of its columns and cards.
        
        This method ensures that when a board is deleted, all columns and cards
        in that board are also deleted to prevent orphaned records.
        
        Args:
            entity_id: Board ID
            tenant_id: Tenant ID for isolation
            version: Expected version for optimistic concurrency
            hard_delete: Whether to perform hard delete instead of soft delete
            
        Returns:
            True if board was deleted, False if not found
        """
        # First, get the board to verify it exists
        board = await self.get_by_id(entity_id, tenant_id)
        if not board:
            return False
        
        # If version check is required, verify it matches
        if version is not None and board.version != version:
            return False
        
        try:
            if hard_delete:
                # Hard delete: Delete cards first, then columns, then board
                # Delete all cards in this board
                card_delete_query = delete(Card).where(
                    and_(
                        Card.board_id == entity_id,
                        Card.tenant_id == tenant_id
                    )
                )
                await self.session.execute(card_delete_query)
                
                # Delete all columns in this board
                column_delete_query = delete(Column).where(
                    and_(
                        Column.board_id == entity_id,
                        Column.tenant_id == tenant_id
                    )
                )
                await self.session.execute(column_delete_query)
                
                # Delete the board
                board_delete_query = delete(self.model).where(
                    and_(
                        self.model.id == entity_id,
                        self.model.tenant_id == tenant_id
                    )
                )
                if version is not None:
                    board_delete_query = board_delete_query.where(self.model.version == version)
                
                result = await self.session.execute(board_delete_query)
                await self.session.commit()
                return result.rowcount > 0
            else:
                # Soft delete: Mark cards as deleted first, then columns, then board
                # Soft delete all cards in this board
                card_update_query = update(Card).where(
                    and_(
                        Card.board_id == entity_id,
                        Card.tenant_id == tenant_id,
                        Card.deleted_at.is_(None)  # Only update non-deleted cards
                    )
                ).values(
                    deleted_at=datetime.now(timezone.utc),
                    version=Card.version + 1
                )
                await self.session.execute(card_update_query)
                
                # Soft delete all columns in this board
                column_update_query = update(Column).where(
                    and_(
                        Column.board_id == entity_id,
                        Column.tenant_id == tenant_id,
                        Column.deleted_at.is_(None)  # Only update non-deleted columns
                    )
                ).values(
                    deleted_at=datetime.now(timezone.utc),
                    version=Column.version + 1
                )
                await self.session.execute(column_update_query)
                
                # Soft delete the board
                board_update_query = update(self.model).where(
                    and_(
                        self.model.id == entity_id,
                        self.model.tenant_id == tenant_id
                    )
                )
                
                if version is not None:
                    board_update_query = board_update_query.where(self.model.version == version)
                    board_update_query = board_update_query.values(version=version + 1)
                
                # Set deleted_at timestamp
                board_update_query = board_update_query.values(
                    deleted_at=datetime.now(timezone.utc)
                )
                
                result = await self.session.execute(board_update_query)
                await self.session.commit()
                return result.rowcount > 0
                
        except Exception:
            await self.session.rollback()
            return False
