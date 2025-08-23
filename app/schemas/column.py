"""
Pydantic schemas for column request/response models.

This module contains schemas for column CRUD operations including create,
update, and response models with proper validation.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

from .base import BaseResponse


class ColumnBase(BaseModel):
    """Base column model with common fields."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Column name")
    board_id: str = Field(..., description="Board ID")
    position: int = Field(..., ge=0, description="Column position (0-based)")
    wip_limit: Optional[int] = Field(None, ge=0, description="Work-in-progress limit")
    meta_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ColumnCreate(ColumnBase):
    """Schema for creating a new column."""
    
    pass


class ColumnUpdate(BaseModel):
    """Schema for updating an existing column."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Column name")
    position: Optional[int] = Field(None, ge=0, description="Column position (0-based)")
    wip_limit: Optional[int] = Field(None, ge=0, description="Work-in-progress limit")
    meta_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ColumnResponse(ColumnBase, BaseResponse):
    """Schema for column response."""
    
    id: str = Field(description="Column ID")
    tenant_id: str = Field(description="Tenant ID")
    version: int = Field(description="Version number for optimistic concurrency")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(default=None, description="Soft delete timestamp")


class ColumnListResponse(BaseResponse):
    """Schema for column list response."""
    
    id: str = Field(description="Column ID")
    name: str = Field(description="Column name")
    board_id: str = Field(description="Board ID")
    position: int = Field(description="Column position")
    wip_limit: Optional[int] = Field(default=None, description="Work-in-progress limit")
    tenant_id: str = Field(description="Tenant ID")
    version: int = Field(description="Version number")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    meta_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ColumnMoveRequest(BaseModel):
    """Schema for moving a column to a new position."""
    
    position: int = Field(..., ge=0, description="New position for the column")


class ColumnReorderRequest(BaseModel):
    """Schema for reordering multiple columns."""
    
    column_positions: list[tuple[str, int]] = Field(..., description="List of (column_id, new_position) tuples")


class ColumnFilterParams(BaseModel):
    """Filter parameters for column list endpoint."""
    
    board_id: Optional[str] = Field(None, description="Filter by board ID")
    name: Optional[str] = Field(None, description="Filter by column name (partial match)")
    include_deleted: bool = Field(default=False, description="Whether to include soft-deleted columns")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of columns to return")
    offset: int = Field(default=0, ge=0, description="Number of columns to skip")
    order_by: str = Field(default="position", description="Field to order by")
    order_direction: str = Field(default="asc", pattern="^(asc|desc)$", description="Order direction")


class ColumnWithCardsResponse(ColumnResponse):
    """Schema for column response with cards."""
    
    cards: list[Dict[str, Any]] = Field(default=[], description="List of cards in the column")
    card_count: int = Field(description="Number of cards in the column")
