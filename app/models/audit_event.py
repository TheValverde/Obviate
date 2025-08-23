"""
Audit Event model for Kanban For Agents.

Audit events track all changes to entities for compliance and debugging,
with support for agent context and detailed payload information.
"""

from typing import Any, Dict, Optional

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class AuditEvent(BaseModel):
    """
    Audit event entity for tracking all changes.
    
    Audit events track all mutations to entities for compliance,
    debugging, and audit trails. Includes agent context for
    understanding agent reasoning.
    """
    
    __tablename__ = "audit_events"
    
    # Audit event properties
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Type of entity: board|column|card|comment|attachment"
    )
    
    entity_id: Mapped[str] = mapped_column(
        String(26),
        nullable=False,
        index=True,
        comment="ID of the affected entity"
    )
    
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Action performed: create|update|delete|move|reorder|archive|restore"
    )
    
    actor: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Service/agent identifier that performed the action"
    )
    
    # JSONB fields for extensibility
    payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Diff or snapshot of the change (sized to keep <8KB)"
    )
    
    agent_context: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Agent reasoning: reasoning, confidence, alternative_actions, user_approval_required"
    )
    
    def __repr__(self) -> str:
        return f"<AuditEvent(id='{self.id}', entity_type='{self.entity_type}', entity_id='{self.entity_id}', action='{self.action}')>"
    
    def to_dict(self) -> dict:
        """Convert audit event to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'action': self.action,
            'actor': self.actor,
            'payload': self.payload,
            'agent_context': self.agent_context,
        })
        return base_dict
    
    @property
    def is_agent_action(self) -> bool:
        """Check if this action was performed by an agent."""
        return self.actor.startswith('agent://')
    
    @property
    def requires_user_approval(self) -> bool:
        """Check if the agent action requires user approval."""
        if not self.agent_context:
            return False
        return self.agent_context.get('user_approval_required', False)

