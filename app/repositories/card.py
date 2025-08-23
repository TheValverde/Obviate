"""
Card repository for card-specific database operations.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from .base import BaseRepository
from app.models.card import Card


class CardRepository(BaseRepository[Card]):
    """
    Repository for card operations with tenant isolation.
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(Card, session)
    
    async def list_by_board(
        self,
        board_id: str,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Card]:
        """
        List cards within a board with tenant isolation and filtering.
        
        Args:
            board_id: Board ID
            tenant_id: Tenant ID for isolation
            limit: Maximum number of cards to return
            offset: Number of cards to skip
            include_deleted: Whether to include soft-deleted cards
            filters: Additional filters (column_id, labels, assignees, priority, etc.)
            
        Returns:
            List of card instances
        """
        base_filters = {"board_id": board_id}
        if filters:
            base_filters.update(filters)
        
        return await self.list(
            tenant_id=tenant_id,
            limit=limit,
            offset=offset,
            include_deleted=include_deleted,
            order_by="position",
            filters=base_filters
        )
    
    async def list_by_column(
        self,
        column_id: str,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False
    ) -> List[Card]:
        """
        List cards within a column with tenant isolation, ordered by position.
        
        Args:
            column_id: Column ID
            tenant_id: Tenant ID for isolation
            limit: Maximum number of cards to return
            offset: Number of cards to skip
            include_deleted: Whether to include soft-deleted cards
            
        Returns:
            List of card instances ordered by position
        """
        return await self.list(
            tenant_id=tenant_id,
            limit=limit,
            offset=offset,
            include_deleted=include_deleted,
            order_by="position",
            filters={"column_id": column_id}
        )
    
    async def get_by_position(
        self,
        column_id: str,
        position: int,
        tenant_id: str,
        include_deleted: bool = False
    ) -> Optional[Card]:
        """
        Get card by position within a column with tenant isolation.
        
        Args:
            column_id: Column ID
            position: Card position
            tenant_id: Tenant ID for isolation
            include_deleted: Whether to include soft-deleted cards
            
        Returns:
            Card instance or None if not found
        """
        query = select(self.model).where(
            and_(
                self.model.column_id == column_id,
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
        column_id: str,
        tenant_id: str,
        include_deleted: bool = False
    ) -> int:
        """
        Get the maximum position value for cards in a column.
        
        Args:
            column_id: Column ID
            tenant_id: Tenant ID for isolation
            include_deleted: Whether to include soft-deleted cards
            
        Returns:
            Maximum position value (0 if no cards exist)
        """
        query = select(func.max(self.model.position)).where(
            and_(
                self.model.column_id == column_id,
                self.model.tenant_id == tenant_id
            )
        )
        
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        
        result = await self.session.execute(query)
        max_position = result.scalar()
        return max_position if max_position is not None else 0
    
    async def move_card(
        self,
        card_id: str,
        column_id: str,
        position: int,
        tenant_id: str,
        version: Optional[int] = None
    ) -> Optional[Card]:
        """
        Move a card to a new column and position.
        
        Args:
            card_id: Card ID
            column_id: Target column ID
            position: Target position
            tenant_id: Tenant ID for isolation
            version: Expected version for optimistic concurrency
            
        Returns:
            Updated card instance or None if not found
        """
        return await self.update(
            entity_id=card_id,
            tenant_id=tenant_id,
            data={
                "column_id": column_id,
                "position": position
            },
            version=version
        )
    
    async def reorder_cards(
        self,
        column_id: str,
        tenant_id: str,
        card_positions: List[tuple[str, int]]
    ) -> bool:
        """
        Reorder cards within a column by updating their positions.
        
        Args:
            column_id: Column ID
            tenant_id: Tenant ID for isolation
            card_positions: List of (card_id, new_position) tuples
            
        Returns:
            True if reordering was successful
        """
        try:
            for card_id, new_position in card_positions:
                await self.update(
                    entity_id=card_id,
                    tenant_id=tenant_id,
                    data={"position": new_position}
                )
            return True
        except Exception:
            await self.session.rollback()
            return False
    
    async def search_cards(
        self,
        board_id: str,
        tenant_id: str,
        search_term: str,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False
    ) -> List[Card]:
        """
        Search cards by title and description within a board.
        
        Args:
            board_id: Board ID
            tenant_id: Tenant ID for isolation
            search_term: Search term to match against title and description
            limit: Maximum number of cards to return
            offset: Number of cards to skip
            include_deleted: Whether to include soft-deleted cards
            
        Returns:
            List of matching card instances
        """
        query = select(self.model).where(
            and_(
                self.model.board_id == board_id,
                self.model.tenant_id == tenant_id,
                or_(
                    self.model.title.ilike(f"%{search_term}%"),
                    self.model.description.ilike(f"%{search_term}%")
                )
            )
        )
        
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        
        query = query.order_by(self.model.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def filter_by_labels(
        self,
        board_id: str,
        tenant_id: str,
        labels: List[str],
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False
    ) -> List[Card]:
        """
        Filter cards by labels within a board.
        
        Args:
            board_id: Board ID
            tenant_id: Tenant ID for isolation
            labels: List of labels to filter by
            limit: Maximum number of cards to return
            offset: Number of cards to skip
            include_deleted: Whether to include soft-deleted cards
            
        Returns:
            List of matching card instances
        """
        # This would need to be implemented based on how labels are stored
        # For now, assuming labels are stored as a JSONB array
        query = select(self.model).where(
            and_(
                self.model.board_id == board_id,
                self.model.tenant_id == tenant_id
            )
        )
        
        # Add label filtering when labels field is implemented
        # query = query.where(self.model.labels.overlap(labels))
        
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        
        query = query.order_by(self.model.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def count_by_board(
        self,
        board_id: str,
        tenant_id: str,
        include_deleted: bool = False,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count cards within a board with tenant isolation.
        
        Args:
            board_id: Board ID
            tenant_id: Tenant ID for isolation
            include_deleted: Whether to include soft-deleted cards
            filters: Additional filters to apply
            
        Returns:
            Number of cards
        """
        base_filters = {"board_id": board_id}
        if filters:
            base_filters.update(filters)
        
        return await self.count(
            tenant_id=tenant_id,
            include_deleted=include_deleted,
            filters=base_filters
        )
    
    async def count_by_column(
        self,
        column_id: str,
        tenant_id: str,
        include_deleted: bool = False
    ) -> int:
        """
        Count cards within a column with tenant isolation.
        
        Args:
            column_id: Column ID
            tenant_id: Tenant ID for isolation
            include_deleted: Whether to include soft-deleted cards
            
        Returns:
            Number of cards
        """
        return await self.count(
            tenant_id=tenant_id,
            include_deleted=include_deleted,
            filters={"column_id": column_id}
        )
