"""
Service Token model for Kanban For Agents.

Service tokens provide authentication for API and MCP access,
with scope-based authorization and tenant isolation.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class ServiceToken(BaseModel):
    """
    Service token entity for API/MCP authentication.
    
    Service tokens provide bearer token authentication with scope-based
    authorization. Only hashes are stored, never the actual tokens.
    """
    
    __tablename__ = "service_tokens"
    
    # Token properties
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Human-readable token name"
    )
    
    token_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        comment="Argon2id hash of the token (never store actual tokens)"
    )
    
    scopes: Mapped[List[str]] = mapped_column(
        JSONB,  # Using JSONB for array storage
        nullable=False,
        comment="List of scopes: read, write, admin"
    )
    
    # Token lifecycle
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Revocation timestamp (UTC), null if active"
    )
    
    def __repr__(self) -> str:
        return f"<ServiceToken(id='{self.id}', name='{self.name}', tenant_id='{self.tenant_id}')>"
    
    def to_dict(self) -> dict:
        """Convert service token to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'scopes': self.scopes,
            'revoked_at': self.revoked_at.isoformat() if self.revoked_at else None,
        })
        return base_dict
    
    @property
    def is_active(self) -> bool:
        """Check if the token is active (not revoked)."""
        return self.revoked_at is None
    
    @property
    def has_read_scope(self) -> bool:
        """Check if the token has read scope."""
        return 'read' in self.scopes
    
    @property
    def has_write_scope(self) -> bool:
        """Check if the token has write scope."""
        return 'write' in self.scopes
    
    @property
    def has_admin_scope(self) -> bool:
        """Check if the token has admin scope."""
        return 'admin' in self.scopes
    
    def can_read(self) -> bool:
        """Check if the token can perform read operations."""
        return self.is_active and self.has_read_scope
    
    def can_write(self) -> bool:
        """Check if the token can perform write operations."""
        return self.is_active and self.has_write_scope
    
    def can_admin(self) -> bool:
        """Check if the token can perform admin operations."""
        return self.is_active and self.has_admin_scope
    
    def revoke(self) -> None:
        """Revoke the token."""
        self.revoked_at = datetime.now()
        self.increment_version()

