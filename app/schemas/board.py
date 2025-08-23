"""
Pydantic schemas for board request/response models.

This module contains schemas for board CRUD operations including create,
update, and response models with proper validation.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict

from .base import BaseResponse


class BoardBase(BaseModel):
    """Base board model with common fields."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Board name")
    description: Optional[str] = Field(None, max_length=1000, description="Board description")
    template: Optional[Dict[str, Any]] = Field(default=None, description="Board template configuration")
    meta_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class BoardCreate(BoardBase):
    """Schema for creating a new board."""
    
    workspace_id: str = Field(..., description="Workspace ID")


class BoardUpdate(BaseModel):
    """Schema for updating an existing board."""
    
    pass


class BoardResponse(BoardBase, BaseResponse):
    """Schema for board response."""
    
    id: str = Field(description="Board ID")
    workspace_id: str = Field(description="Workspace ID")
    tenant_id: str = Field(description="Tenant ID")
    version: int = Field(description="Version number for optimistic concurrency")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(default=None, description="Soft delete timestamp")


class BoardListResponse(BoardBase, BaseResponse):
    """Schema for board list response."""
    
    id: str = Field(description="Board ID")
    workspace_id: str = Field(description="Workspace ID")
    tenant_id: str = Field(description="Tenant ID")
    version: int = Field(description="Version number")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")


class BoardArchiveRequest(BaseModel):
    """Schema for archiving/unarchiving a board."""
    
    archived: bool = Field(description="Whether to archive or unarchive the board")


class BoardFilterParams(BaseModel):
    """Filter parameters for board list endpoint."""
    
    workspace_id: Optional[str] = Field(None, description="Filter by workspace ID")
    name: Optional[str] = Field(None, description="Filter by board name (partial match)")
    include_archived: bool = Field(default=False, description="Whether to include archived boards")
    include_deleted: bool = Field(default=False, description="Whether to include soft-deleted boards")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of boards to return")
    offset: int = Field(default=0, ge=0, description="Number of boards to skip")
    order_by: str = Field(default="created_at", description="Field to order by")
    order_direction: str = Field(default="desc", pattern="^(asc|desc)$", description="Order direction")


class BoardWithColumnsResponse(BoardResponse):
    """Schema for board response with columns."""
    
    columns: List[Dict[str, Any]] = Field(default=[], description="List of columns in the board")


class BoardStatsResponse(BaseResponse):
    """Schema for board statistics response."""
    
    board_id: str = Field(description="Board ID")
    total_cards: int = Field(description="Total number of cards")
    total_columns: int = Field(description="Total number of columns")
    cards_by_column: Dict[str, int] = Field(description="Number of cards per column")
    created_at: datetime = Field(description="Board creation timestamp")
    last_activity: Optional[datetime] = Field(default=None, description="Last activity timestamp")
