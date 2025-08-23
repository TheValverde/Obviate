"""
Workspace model for Kanban For Agents.

Workspaces are optional grouping entities for MVP but provide a foundation
for future multi-workspace support.
"""

from typing import Any, Dict, Optional
from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Workspace(BaseModel):
    """
    Workspace entity for organizing boards.
    
    For MVP, this is optional but provides a foundation for future
    multi-workspace support and better organization.
    """
    
    __tablename__ = "workspaces"
    
    # Workspace name
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Workspace display name"
    )
    
    # Custom metadata for workspace-level configuration
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        default=None,
        comment="Custom metadata for workspace-level configuration"
    )
    
    # Relationships
    boards = relationship(
        "Board",
        back_populates="workspace",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Workspace(id='{self.id}', name='{self.name}', tenant_id='{self.tenant_id}')>"
    
    def to_dict(self) -> dict:
        """Convert workspace to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'meta_data': self.meta_data,
        })
        return base_dict

