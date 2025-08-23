"""
Base model for all entities in the Kanban For Agents system.

This module provides the base SQLAlchemy model with common fields and utilities
for all entities: id, tenant_id, version, timestamps, and soft delete support.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import BigInteger, DateTime, String, Text, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        return cls.__name__.lower() + "s"


class BaseModel(Base):
    """
    Base model with common fields for all entities.
    
    Provides:
    - ULID/UUIDv7-ish ID generation for lexicographic ordering
    - Tenant isolation with tenant_id field
    - Optimistic concurrency with version field
    - Soft delete with deleted_at timestamp
    - Standard timestamps (created_at, updated_at)
    """
    
    __abstract__ = True
    
    # Primary key: ULID/UUIDv7-ish for lexicographic ordering
    id: Mapped[str] = mapped_column(
        String(26),  # ULID length
        primary_key=True,
        default=lambda: BaseModel.generate_ulid(),
        index=True
    )
    
    # Tenant isolation (mandatory for all queries)
    tenant_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Tenant identifier for multi-tenancy support"
    )
    
    # Optimistic concurrency control
    version: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=1,
        comment="Version for optimistic concurrency control"
    )
    
    # Standard timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        comment="Creation timestamp (UTC)"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        comment="Last update timestamp (UTC)"
    )
    
    # Soft delete support
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Soft delete timestamp (UTC), null if not deleted"
    )
    
    @staticmethod
    def generate_ulid() -> str:
        """
        Generate a ULID/UUIDv7-ish identifier for lexicographic ordering.
        
        For MVP, we'll use a simplified approach that provides similar benefits:
        - Time-ordered (first 10 chars based on timestamp)
        - Lexicographically sortable
        - URL-safe
        
        In production, consider using a proper ULID library like `ulid-py`.
        """
        # Get current timestamp in milliseconds since epoch
        timestamp_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        
        # Convert to base32 (ULID format)
        timestamp_part = BaseModel._encode_timestamp(timestamp_ms)
        
        # Generate random part (16 chars)
        random_part = BaseModel._generate_random_part()
        
        return timestamp_part + random_part
    
    @staticmethod
    def _encode_timestamp(timestamp_ms: int) -> str:
        """Encode timestamp to base32 for ULID format."""
        # Simplified base32 encoding for timestamp
        # In production, use proper ULID encoding
        import base64
        timestamp_bytes = timestamp_ms.to_bytes(6, 'big')
        encoded = base64.b32encode(timestamp_bytes).decode('ascii')
        return encoded[:10]  # ULID timestamp is 10 chars
    
    @staticmethod
    def _generate_random_part() -> str:
        """Generate random part for ULID."""
        # Simplified random generation
        # In production, use proper ULID random generation
        import base64
        random_bytes = uuid.uuid4().bytes
        encoded = base64.b32encode(random_bytes).decode('ascii')
        return encoded[:16]  # ULID random part is 16 chars
    
    def increment_version(self) -> None:
        """Increment the version for optimistic concurrency."""
        self.version += 1
    
    def soft_delete(self) -> None:
        """Mark the entity as deleted (soft delete)."""
        self.deleted_at = datetime.now(timezone.utc)
        self.increment_version()
    
    def restore(self) -> None:
        """Restore a soft-deleted entity."""
        self.deleted_at = None
        self.increment_version()
    
    @property
    def is_deleted(self) -> bool:
        """Check if the entity is soft-deleted."""
        return self.deleted_at is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
        }

