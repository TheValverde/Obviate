"""
Card model for Kanban For Agents.

Cards are the main work items in the Kanban system, with support for
agent context, workflow state, and extensive metadata for agent workflows.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Card(BaseModel):
    """
    Card entity representing a work item in the Kanban system.
    
    Cards are the main work items that move through columns, with extensive
    support for agent context, workflow state, and metadata.
    """
    
    __tablename__ = "cards"
    
    # Foreign keys
    board_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to parent board"
    )
    
    column_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("columns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to current column"
    )
    
    # Basic card properties
    title: Mapped[str] = mapped_column(
        String(256),  # Limited to 256 chars as per README
        nullable=False,
        comment="Card title"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Card description (limited to 16KB as per README)"
    )
    
    # Arrays for assignees and labels
    assignees: Mapped[Optional[List[str]]] = mapped_column(
        JSONB,  # Using JSONB for array storage
        nullable=True,
        comment="List of agent/human identifiers"
    )
    
    labels: Mapped[Optional[List[str]]] = mapped_column(
        JSONB,  # Using JSONB for array storage
        nullable=True,
        comment="List of lightweight tags"
    )
    
    # Priority and status
    priority: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
        comment="Priority: 0=none, 1=low, 2=med, 3=high, 4=urgent"
    )
    
    status: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Status hint: todo|doing|done|blocked (column is source of truth)"
    )
    
    # Position and timing
    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Order within column"
    )
    
    due_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Due date (UTC)"
    )
    
    # JSONB fields for extensibility
    fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Structured, agent-defined per-card fields (limited to 16KB)"
    )
    
    links: Mapped[Optional[List[Dict[str, str]]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Array of {type, url, title} pointing to PRs, docs, etc."
    )
    
    # Agent-specific JSONB fields
    agent_context: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Agent reasoning and context: reasoning, next_steps, dependencies, estimated_complexity, agent_notes"
    )
    
    workflow_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Workflow tracking: phase, blockers, progress_percentage, time_spent_minutes, estimated_remaining_minutes"
    )
    
    # Relationships
    board = relationship(
        "Board",
        back_populates="cards",
        lazy="selectin"
    )
    
    column = relationship(
        "Column",
        back_populates="cards",
        lazy="selectin"
    )
    
    comments = relationship(
        "Comment",
        back_populates="card",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    attachments = relationship(
        "Attachment",
        back_populates="card",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Card(id='{self.id}', title='{self.title}', column_id='{self.column_id}')>"
    
    def to_dict(self) -> dict:
        """Convert card to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            'board_id': self.board_id,
            'column_id': self.column_id,
            'title': self.title,
            'description': self.description,
            'assignees': self.assignees,
            'labels': self.labels,
            'priority': self.priority,
            'status': self.status,
            'position': self.position,
            'due_at': self.due_at.isoformat() if self.due_at else None,
            'fields': self.fields,
            'links': self.links,
            'agent_context': self.agent_context,
            'workflow_state': self.workflow_state,
        })
        return base_dict
    
    def move_to_column(self, new_column_id: str, new_position: Optional[int] = None) -> None:
        """Move card to a different column."""
        self.column_id = new_column_id
        if new_position is not None:
            self.position = new_position
        self.increment_version()
    
    def update_position(self, new_position: int) -> None:
        """Update card position within the same column."""
        self.position = new_position
        self.increment_version()
    
    def add_assignee(self, assignee: str) -> None:
        """Add an assignee to the card."""
        if self.assignees is None:
            self.assignees = []
        if assignee not in self.assignees:
            self.assignees.append(assignee)
            self.increment_version()
    
    def remove_assignee(self, assignee: str) -> None:
        """Remove an assignee from the card."""
        if self.assignees and assignee in self.assignees:
            self.assignees.remove(assignee)
            self.increment_version()
    
    def add_label(self, label: str) -> None:
        """Add a label to the card."""
        if self.labels is None:
            self.labels = []
        if label not in self.labels:
            self.labels.append(label)
            self.increment_version()
    
    def remove_label(self, label: str) -> None:
        """Remove a label from the card."""
        if self.labels and label in self.labels:
            self.labels.remove(label)
            self.increment_version()
    
    @property
    def is_overdue(self) -> bool:
        """Check if the card is overdue."""
        if self.due_at is None:
            return False
        return datetime.now(self.due_at.tzinfo) > self.due_at
    
    @property
    def priority_label(self) -> str:
        """Get human-readable priority label."""
        priority_labels = {
            0: "none",
            1: "low",
            2: "medium",
            3: "high",
            4: "urgent"
        }
        return priority_labels.get(self.priority, "unknown")

