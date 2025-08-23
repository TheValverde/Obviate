"""
Board model for Kanban For Agents.

Boards are the main containers for columns and cards, representing
a Kanban board with template and metadata support.
"""

from typing import Any, Dict, Optional

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Board(BaseModel):
    """
    Board entity representing a Kanban board.
    
    Boards contain columns and cards, with support for templates
    and metadata for extensibility.
    """
    
    __tablename__ = "boards"
    
    # Foreign key to workspace (optional for MVP)
    workspace_id: Mapped[Optional[str]] = mapped_column(
        String(26),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Reference to workspace (optional for MVP)"
    )
    
    # Board properties
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Board display name"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Board description"
    )
    
    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether the board is archived"
    )
    
    # JSONB fields for extensibility
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Custom metadata for board-level configuration"
    )
    
    template: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Board template with default columns, labels, priorities"
    )
    
    # Relationships
    workspace = relationship(
        "Workspace",
        back_populates="boards",
        lazy="selectin"
    )
    
    columns = relationship(
        "Column",
        back_populates="board",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Column.position"
    )
    
    cards = relationship(
        "Card",
        back_populates="board",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Board(id='{self.id}', name='{self.name}', tenant_id='{self.tenant_id}')>"
    
    def to_dict(self) -> dict:
        """Convert board to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            'workspace_id': self.workspace_id,
            'name': self.name,
            'description': self.description,
            'is_archived': self.is_archived,
            'meta_data': self.meta_data,
            'template': self.template,
        })
        return base_dict
    
    def archive(self) -> None:
        """Archive the board."""
        self.is_archived = True
        self.increment_version()
    
    def unarchive(self) -> None:
        """Unarchive the board."""
        self.is_archived = False
        self.increment_version()

