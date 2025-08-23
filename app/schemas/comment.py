"""
Pydantic schemas for comment request/response models.

This module contains schemas for comment CRUD operations including create,
update, and response models with proper validation.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

from .base import BaseResponse


class CommentBase(BaseModel):
    """Base comment model with common fields."""
    
    card_id: str = Field(..., description="Card ID")
    author: str = Field(..., min_length=1, max_length=255, description="Comment author")
    body: str = Field(..., min_length=1, max_length=10000, description="Comment body")
    meta_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class CommentCreate(CommentBase):
    """Schema for creating a new comment."""
    
    pass


class CommentUpdate(BaseModel):
    """Schema for updating an existing comment."""
    
    body: Optional[str] = Field(None, min_length=1, max_length=10000, description="Comment body")
    meta_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class CommentResponse(CommentBase, BaseResponse):
    """Schema for comment response."""
    
    id: str = Field(description="Comment ID")
    tenant_id: str = Field(description="Tenant ID")
    version: int = Field(description="Version number for optimistic concurrency")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(default=None, description="Soft delete timestamp")


class CommentListResponse(BaseResponse):
    """Schema for comment list response."""
    
    id: str = Field(description="Comment ID")
    card_id: str = Field(description="Card ID")
    author: str = Field(description="Comment author")
    body: str = Field(description="Comment body")
    tenant_id: str = Field(description="Tenant ID")
    version: int = Field(description="Version number")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    meta_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class CommentFilterParams(BaseModel):
    """Filter parameters for comment list endpoint."""
    
    card_id: Optional[str] = Field(None, description="Filter by card ID")
    author: Optional[str] = Field(None, description="Filter by author")
    include_deleted: bool = Field(default=False, description="Whether to include soft-deleted comments")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of comments to return")
    offset: int = Field(default=0, ge=0, description="Number of comments to skip")
    order_by: str = Field(default="created_at", description="Field to order by")
    order_direction: str = Field(default="desc", pattern="^(asc|desc)$", description="Order direction")
