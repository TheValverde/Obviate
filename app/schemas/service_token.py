"""
Pydantic schemas for service token request/response models.

This module contains schemas for service token CRUD operations including create,
update, and response models with proper validation.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict

from .base import BaseResponse


class ServiceTokenBase(BaseModel):
    """Base service token model with common fields."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Token name")
    token_hash: str = Field(..., description="Hashed token value")
    scopes: List[str] = Field(..., description="List of token scopes")
    revoked_at: Optional[datetime] = Field(default=None, description="Token revocation timestamp")
    meta_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ServiceTokenCreate(ServiceTokenBase):
    """Schema for creating a new service token."""
    
    pass


class ServiceTokenUpdate(BaseModel):
    """Schema for updating an existing service token."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Token name")
    scopes: Optional[List[str]] = Field(default=None, description="List of token scopes")
    revoked_at: Optional[datetime] = Field(default=None, description="Token revocation timestamp")
    meta_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ServiceTokenResponse(ServiceTokenBase, BaseResponse):
    """Schema for service token response."""
    
    id: str = Field(description="Service token ID")
    tenant_id: str = Field(description="Tenant ID")
    version: int = Field(description="Version number for optimistic concurrency")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(default=None, description="Soft delete timestamp")


class ServiceTokenListResponse(BaseResponse):
    """Schema for service token list response."""
    
    id: str = Field(description="Service token ID")
    name: str = Field(description="Token name")
    scopes: List[str] = Field(description="List of token scopes")
    tenant_id: str = Field(description="Tenant ID")
    version: int = Field(description="Version number")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    revoked_at: Optional[datetime] = Field(default=None, description="Token revocation timestamp")
    meta_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ServiceTokenRevokeRequest(BaseModel):
    """Schema for revoking a service token."""
    
    revoked_at: datetime = Field(description="Revocation timestamp")


class ServiceTokenFilterParams(BaseModel):
    """Filter parameters for service token list endpoint."""
    
    name: Optional[str] = Field(None, description="Filter by token name (partial match)")
    scope: Optional[str] = Field(None, description="Filter by scope")
    include_revoked: bool = Field(default=False, description="Whether to include revoked tokens")
    include_deleted: bool = Field(default=False, description="Whether to include soft-deleted tokens")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of tokens to return")
    offset: int = Field(default=0, ge=0, description="Number of tokens to skip")
    order_by: str = Field(default="created_at", description="Field to order by")
    order_direction: str = Field(default="desc", pattern="^(asc|desc)$", description="Order direction")
