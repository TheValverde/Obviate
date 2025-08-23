"""
Comment model for Kanban For Agents.

Comments provide discussion and context for cards, with support for
agent-authored content and metadata.
"""

from typing import Any, Dict, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Comment(BaseModel):
    """
    Comment entity for card discussions.
    
    Comments provide context and discussion for cards, with support
    for agent-authored content and metadata.
    """
    
    __tablename__ = "comments"
    
    # Foreign key to card
    card_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("cards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to parent card"
    )
    
    # Comment properties
    author: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Agent/service/user identifier"
    )
    
    body: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Comment content (limited to 8KB as per README)"
    )
    
    # JSONB field for extensibility
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Custom metadata for comment"
    )
    
    # Relationships
    card = relationship(
        "Card",
        back_populates="comments",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Comment(id='{self.id}', author='{self.author}', card_id='{self.card_id}')>"
    
    def to_dict(self) -> dict:
        """Convert comment to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            'card_id': self.card_id,
            'author': self.author,
            'body': self.body,
            'meta_data': self.meta_data,
        })
        return base_dict

