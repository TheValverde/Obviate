"""
Column model for Kanban For Agents.

Columns represent ordered lanes within a board, with position tracking
and WIP limits for workflow management.
"""

from typing import Any, Dict, Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Column(BaseModel):
    """
    Column entity representing a lane within a board.
    
    Columns are ordered lanes that contain cards, with support for
    WIP limits and metadata for workflow management.
    """
    
    __tablename__ = "columns"
    
    # Foreign key to board
    board_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to parent board"
    )
    
    # Column properties
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Column display name"
    )
    
    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Position within board (gaps ok, rebalance on large diffs)"
    )
    
    wip_limit: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Work-in-progress limit (null for unlimited)"
    )
    
    # JSONB field for extensibility
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Custom metadata for column configuration"
    )
    
    # Relationships
    board = relationship(
        "Board",
        back_populates="columns",
        lazy="selectin"
    )
    
    cards = relationship(
        "Card",
        back_populates="column",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Card.position"
    )
    
    def __repr__(self) -> str:
        return f"<Column(id='{self.id}', name='{self.name}', board_id='{self.board_id}', position={self.position})>"
    
    def to_dict(self) -> dict:
        """Convert column to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            'board_id': self.board_id,
            'name': self.name,
            'position': self.position,
            'wip_limit': self.wip_limit,
            'meta_data': self.meta_data,
        })
        return base_dict
    
    @property
    def card_count(self) -> int:
        """Get the number of cards in this column."""
        return len([card for card in self.cards if not card.is_deleted])
    
    @property
    def is_at_wip_limit(self) -> bool:
        """Check if the column is at its WIP limit."""
        if self.wip_limit is None:
            return False
        return self.card_count >= self.wip_limit
    
    def can_accept_card(self) -> bool:
        """Check if the column can accept a new card."""
        return not self.is_at_wip_limit

