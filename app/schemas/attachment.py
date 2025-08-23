"""
Pydantic schemas for attachment request/response models.

This module contains schemas for attachment metadata operations (no blob storage).
"""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

from .base import BaseResponse


class AttachmentBase(BaseModel):
    """Base attachment model with common fields."""
    
    card_id: str = Field(..., description="Card ID")
    filename: str = Field(..., min_length=1, max_length=255, description="Original filename")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    mime_type: str = Field(..., description="MIME type of the file")
    url: str = Field(..., description="URL to the file (external storage)")
    meta_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class AttachmentCreate(AttachmentBase):
    """Schema for creating a new attachment."""
    
    pass


class AttachmentUpdate(BaseModel):
    """Schema for updating an existing attachment."""
    
    filename: Optional[str] = Field(None, min_length=1, max_length=255, description="Original filename")
    url: Optional[str] = Field(None, description="URL to the file (external storage)")
    meta_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class AttachmentResponse(AttachmentBase, BaseResponse):
    """Schema for attachment response."""
    
    id: str = Field(description="Attachment ID")
    tenant_id: str = Field(description="Tenant ID")
    version: int = Field(description="Version number for optimistic concurrency")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(default=None, description="Soft delete timestamp")


class AttachmentListResponse(BaseResponse):
    """Schema for attachment list response."""
    
    id: str = Field(description="Attachment ID")
    card_id: str = Field(description="Card ID")
    filename: str = Field(description="Original filename")
    file_size: int = Field(description="File size in bytes")
    mime_type: str = Field(description="MIME type of the file")
    url: str = Field(description="URL to the file")
    tenant_id: str = Field(description="Tenant ID")
    version: int = Field(description="Version number")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    meta_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class AttachmentFilterParams(BaseModel):
    """Filter parameters for attachment list endpoint."""
    
    card_id: Optional[str] = Field(None, description="Filter by card ID")
    mime_type: Optional[str] = Field(None, description="Filter by MIME type")
    filename: Optional[str] = Field(None, description="Filter by filename (partial match)")
    include_deleted: bool = Field(default=False, description="Whether to include soft-deleted attachments")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of attachments to return")
    offset: int = Field(default=0, ge=0, description="Number of attachments to skip")
    order_by: str = Field(default="created_at", description="Field to order by")
    order_direction: str = Field(default="desc", pattern="^(asc|desc)$", description="Order direction")
