"""
Models package for Kanban For Agents.

This package exports all SQLAlchemy models for use throughout the application
and for Alembic migration discovery.
"""

from app.models.attachment import Attachment
from app.models.audit_event import AuditEvent
from app.models.base import Base, BaseModel
from app.models.board import Board
from app.models.card import Card
from app.models.column import Column
from app.models.comment import Comment
from app.models.service_token import ServiceToken
from app.models.workspace import Workspace

# Export all models for Alembic discovery
__all__ = [
    "Base",
    "BaseModel",
    "Workspace",
    "Board", 
    "Column",
    "Card",
    "Comment",
    "Attachment",
    "AuditEvent",
    "ServiceToken",
]

# Model registry for easy access
MODELS = {
    "workspace": Workspace,
    "board": Board,
    "column": Column,
    "card": Card,
    "comment": Comment,
    "attachment": Attachment,
    "audit_event": AuditEvent,
    "service_token": ServiceToken,
}

