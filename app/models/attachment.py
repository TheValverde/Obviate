"""
Attachment model for Kanban For Agents.

Attachments provide metadata for external files, with no blob storage
in the database. Files are referenced by URL only.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseModel


class Attachment(Base):
    """
    Attachment entity for file metadata.
    
    Attachments store metadata for external files only. No blob storage
    in the database - files are referenced by URL. Treat as immutable;
    replace to update.
    """
    
    __tablename__ = "attachments"
    
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
    
    # Standard timestamps (no updated_at for immutability)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        comment="Creation timestamp (UTC)"
    )
    
    # Soft delete support
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Soft delete timestamp (UTC), null if not deleted"
    )
    
    # Foreign key to card
    card_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("cards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to parent card"
    )
    
    # Attachment properties
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="File name"
    )
    
    content_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="MIME content type"
    )
    
    size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="File size in bytes"
    )
    
    url: Mapped[str] = mapped_column(
        String(2048),  # URL length limit
        nullable=False,
        comment="URL to the file (must be pre-signed or stable)"
    )
    
    # Note: No updated_at field - treat as immutable
    # Inherit from Base instead of BaseModel to exclude updated_at
    
    # Relationships
    card = relationship(
        "Card",
        back_populates="attachments",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Attachment(id='{self.id}', name='{self.name}', card_id='{self.card_id}')>"
    
    def to_dict(self) -> dict:
        """Convert attachment to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            'card_id': self.card_id,
            'name': self.name,
            'content_type': self.content_type,
            'size_bytes': self.size_bytes,
            'url': self.url,
        })
        return base_dict
    
    @property
    def size_mb(self) -> float:
        """Get file size in megabytes."""
        return self.size_bytes / (1024 * 1024)
    
    @property
    def is_image(self) -> bool:
        """Check if the attachment is an image."""
        return self.content_type.startswith('image/')
    
    @property
    def is_document(self) -> bool:
        """Check if the attachment is a document."""
        return self.content_type.startswith(('application/pdf', 'text/', 'application/msword'))
