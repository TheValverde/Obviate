"""
Card repository for card-specific database operations.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, update, delete
from datetime import datetime, timezone

from .base import BaseRepository
from app.models.card import Card
from app.models.comment import Comment
from app.models.attachment import Attachment


class CardRepository(BaseRepository[Card]):
    """
    Repository for card operations with tenant isolation.
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(Card, session)
    
    async def delete(
        self,
        entity_id: str,
        tenant_id: str,
        version: Optional[int] = None,
        hard_delete: bool = False
    ) -> bool:
        """
        Delete a card with cascade deletion of its comments and attachments.
        
        This method ensures that when a card is deleted, all comments and attachments
        associated with that card are also deleted to prevent orphaned records.
        
        Args:
            entity_id: Card ID
            tenant_id: Tenant ID for isolation
            version: Expected version for optimistic concurrency
            hard_delete: Whether to perform hard delete instead of soft delete
            
        Returns:
            True if card was deleted, False if not found
        """
        # First, get the card to verify it exists
        card = await self.get_by_id(entity_id, tenant_id)
        if not card:
            return False
        
        # If version check is required, verify it matches
        if version is not None and card.version != version:
            return False
        
        try:
            if hard_delete:
                # Hard delete: Delete comments and attachments first, then card
                # Delete all comments for this card
                comment_delete_query = delete(Comment).where(
                    and_(
                        Comment.card_id == entity_id,
                        Comment.tenant_id == tenant_id
                    )
                )
                await self.session.execute(comment_delete_query)
                
                # Delete all attachments for this card
                attachment_delete_query = delete(Attachment).where(
                    and_(
                        Attachment.card_id == entity_id,
                        Attachment.tenant_id == tenant_id
                    )
                )
                await self.session.execute(attachment_delete_query)
                
                # Delete the card
                card_delete_query = delete(self.model).where(
                    and_(
                        self.model.id == entity_id,
                        self.model.tenant_id == tenant_id
                    )
                )
                if version is not None:
                    card_delete_query = card_delete_query.where(self.model.version == version)
                
                result = await self.session.execute(card_delete_query)
                await self.session.commit()
                return result.rowcount > 0
            else:
                # Soft delete: Mark comments and attachments as deleted first, then card
                # Soft delete all comments for this card
                comment_update_query = update(Comment).where(
                    and_(
                        Comment.card_id == entity_id,
                        Comment.tenant_id == tenant_id,
                        Comment.deleted_at.is_(None)  # Only update non-deleted comments
                    )
                ).values(
                    deleted_at=datetime.now(timezone.utc),
                    version=Comment.version + 1
                )
                await self.session.execute(comment_update_query)
                
                # Soft delete all attachments for this card
                attachment_update_query = update(Attachment).where(
                    and_(
                        Attachment.card_id == entity_id,
                        Attachment.tenant_id == tenant_id,
                        Attachment.deleted_at.is_(None)  # Only update non-deleted attachments
                    )
                ).values(
                    deleted_at=datetime.now(timezone.utc),
                    version=Attachment.version + 1
                )
                await self.session.execute(attachment_update_query)
                
                # Soft delete the card
                card_update_query = update(self.model).where(
                    and_(
                        self.model.id == entity_id,
                        self.model.tenant_id == tenant_id
                    )
                )
                
                if version is not None:
                    card_update_query = card_update_query.where(self.model.version == version)
                    card_update_query = card_update_query.values(version=version + 1)
                
                # Set deleted_at timestamp
                card_update_query = card_update_query.values(
                    deleted_at=datetime.now(timezone.utc)
                )
                
                result = await self.session.execute(card_update_query)
                await self.session.commit()
                return result.rowcount > 0
                
        except Exception:
            await self.session.rollback()
            return False
    
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
    

    
    async def batch_update_positions(
        self,
        column_id: str,
        tenant_id: str,
        card_positions: List[tuple[str, int]]
    ) -> bool:
        """
        Batch update card positions within a column (internal helper).
        
        Args:
            column_id: Column ID
            tenant_id: Tenant ID for isolation
            card_positions: List of (card_id, new_position) tuples
            
        Returns:
            True if batch update was successful
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
    
    async def reorder_card(
        self,
        card_id: str,
        column_id: str,
        new_position: int,
        tenant_id: str
    ) -> bool:
        """
        Reorder a card within its column using "insert and shift" logic.
        
        This method implements proper reordering where:
        1. The target card is moved to the new position
        2. Other cards are shifted to accommodate the move
        3. Positions are clamped to valid bounds
        
        Args:
            card_id: Card ID to reorder
            column_id: Column ID
            new_position: Target position (will be clamped to valid range)
            tenant_id: Tenant ID for isolation
            
        Returns:
            True if reordering was successful
        """
        try:
            # Get all cards in the column, ordered by position
            cards = await self.list_by_column(
                column_id=column_id,
                tenant_id=tenant_id,
                limit=1000,
                offset=0
            )
            
            if not cards:
                return False
            
            # Find the card to move
            target_card = None
            old_position = -1
            for card in cards:
                if card.id == card_id:
                    target_card = card
                    old_position = card.position
                    break
            
            if not target_card:
                return False
            
            # Clamp new_position to valid range [0, max_position]
            max_position = len(cards) - 1
            new_position = max(0, min(new_position, max_position))
            
            # If position hasn't changed, no need to reorder
            if old_position == new_position:
                return True
            
            # Create new position mapping
            new_positions = []
            
            if old_position < new_position:
                # Moving forward: shift cards in range [old_pos+1, new_pos] left by 1
                for card in cards:
                    if card.id == card_id:
                        # Target card gets new position
                        new_positions.append((card.id, new_position))
                    elif old_position < card.position <= new_position:
                        # Shift left by 1
                        new_positions.append((card.id, card.position - 1))
                    else:
                        # Keep same position
                        new_positions.append((card.id, card.position))
            else:
                # Moving backward: shift cards in range [new_pos, old_pos-1] right by 1
                for card in cards:
                    if card.id == card_id:
                        # Target card gets new position
                        new_positions.append((card.id, new_position))
                    elif new_position <= card.position < old_position:
                        # Shift right by 1
                        new_positions.append((card.id, card.position + 1))
                    else:
                        # Keep same position
                        new_positions.append((card.id, card.position))
            
            # Batch update all positions
            return await self.batch_update_positions(column_id, tenant_id, new_positions)
            
        except Exception:
            await self.session.rollback()
            return False

    async def move_card(
        self,
        card_id: str,
        target_column_id: str,
        target_position: Optional[int],
        tenant_id: str
    ) -> bool:
        """
        Move a card to a different column with intelligent positioning.
        
        This method handles cross-column movement where:
        1. The card is moved to the target column
        2. If target_position is specified: card is placed at that position with shifting
        3. If target_position is None: card is appended to the end of target column
        4. All position changes are batched and atomic
        
        Args:
            card_id: Card ID to move
            target_column_id: Target column ID
            target_position: Target position (None = append to end)
            tenant_id: Tenant ID for isolation
            
        Returns:
            True if move was successful
        """
        try:
            # Get the card to move
            card = await self.get_by_id(card_id, tenant_id)
            if not card:
                return False
            
            old_column_id = card.column_id
            
            # If moving to same column, just reorder
            if old_column_id == target_column_id:
                if target_position is not None:
                    return await self.reorder_card(card_id, target_column_id, target_position, tenant_id)
                return True  # No change needed
            
            # Get cards in target column
            target_cards = await self.list_by_column(
                column_id=target_column_id,
                tenant_id=tenant_id,
                limit=1000,
                offset=0
            )
            
            # Determine target position
            if target_position is None:
                # Append to end
                target_position = len(target_cards)
            else:
                # Clamp to valid range
                target_position = max(0, min(target_position, len(target_cards)))
            
            # Prepare position updates for target column
            target_positions = []
            for i, target_card in enumerate(target_cards):
                if i >= target_position:
                    # Shift right by 1 to make room
                    target_positions.append((target_card.id, i + 1))
                else:
                    # Keep same position
                    target_positions.append((target_card.id, i))
            
            # Add the moved card at target position
            target_positions.append((card_id, target_position))
            
            # Update all positions in target column
            success = await self.batch_update_positions(target_column_id, tenant_id, target_positions)
            if not success:
                return False
            
            # Update the card's column_id
            await self.update(
                entity_id=card_id,
                tenant_id=tenant_id,
                data={"column_id": target_column_id}
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
