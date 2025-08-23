"""
Pydantic schemas for workspace request/response models.

This module contains schemas for workspace CRUD operations including create,
update, and response models with proper validation.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

from .base import BaseResponse, AuditInfo


class WorkspaceBase(BaseModel):
    """Base workspace model with common fields."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Workspace name")
    meta_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class WorkspaceCreate(WorkspaceBase):
    """Schema for creating a new workspace."""
    
    pass


class WorkspaceUpdate(BaseModel):
    """Schema for updating an existing workspace."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Workspace name")
    meta_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class WorkspaceResponse(WorkspaceBase, BaseResponse):
    """Schema for workspace response."""
    
    id: str = Field(description="Workspace ID")
    tenant_id: str = Field(description="Tenant ID")
    version: int = Field(description="Version number for optimistic concurrency")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(default=None, description="Soft delete timestamp")


class WorkspaceListResponse(BaseResponse):
    """Schema for workspace list response."""
    
    id: str = Field(description="Workspace ID")
    name: str = Field(description="Workspace name")
    tenant_id: str = Field(description="Tenant ID")
    version: int = Field(description="Version number")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    meta_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class WorkspaceArchiveRequest(BaseModel):
    """Schema for archiving/unarchiving a workspace."""
    
    is_archived: bool = Field(description="Whether to archive or unarchive the workspace")


class WorkspaceFilterParams(BaseModel):
    """Filter parameters for workspace list endpoint."""
    
    name: Optional[str] = Field(None, description="Filter by workspace name (partial match)")
    include_archived: bool = Field(default=False, description="Whether to include archived workspaces")
    include_deleted: bool = Field(default=False, description="Whether to include soft-deleted workspaces")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of workspaces to return")
    offset: int = Field(default=0, ge=0, description="Number of workspaces to skip")
    order_by: str = Field(default="created_at", description="Field to order by")
    order_direction: str = Field(default="desc", pattern="^(asc|desc)$", description="Order direction")
