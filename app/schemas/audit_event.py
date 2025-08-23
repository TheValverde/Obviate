"""
Pydantic schemas for audit event response models.

This module contains schemas for audit event operations (read-only).
"""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

from .base import BaseResponse


class AuditEventResponse(BaseResponse):
    """Schema for audit event response."""
    
    id: str = Field(description="Audit event ID")
    entity_type: str = Field(description="Type of entity being audited")
    entity_id: str = Field(description="ID of the entity being audited")
    action: str = Field(description="Action performed")
    actor: str = Field(description="Actor who performed the action")
    tenant_id: str = Field(description="Tenant ID")
    agent_context: Optional[Dict[str, Any]] = Field(default=None, description="Agent context information")
    payload: Optional[Dict[str, Any]] = Field(default=None, description="Action payload data")
    version: int = Field(description="Version number")
    created_at: datetime = Field(description="Creation timestamp")


class AuditEventListResponse(BaseResponse):
    """Schema for audit event list response."""
    
    id: str = Field(description="Audit event ID")
    entity_type: str = Field(description="Type of entity being audited")
    entity_id: str = Field(description="ID of the entity being audited")
    action: str = Field(description="Action performed")
    actor: str = Field(description="Actor who performed the action")
    tenant_id: str = Field(description="Tenant ID")
    version: int = Field(description="Version number")
    created_at: datetime = Field(description="Creation timestamp")
    agent_context: Optional[Dict[str, Any]] = Field(default=None, description="Agent context information")
    payload: Optional[Dict[str, Any]] = Field(default=None, description="Action payload data")


class AuditEventFilterParams(BaseModel):
    """Filter parameters for audit event list endpoint."""
    
    entity_type: Optional[str] = Field(None, description="Filter by entity type")
    entity_id: Optional[str] = Field(None, description="Filter by entity ID")
    action: Optional[str] = Field(None, description="Filter by action")
    actor: Optional[str] = Field(None, description="Filter by actor")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of audit events to return")
    offset: int = Field(default=0, ge=0, description="Number of audit events to skip")
    order_by: str = Field(default="created_at", description="Field to order by")
    order_direction: str = Field(default="desc", pattern="^(asc|desc)$", description="Order direction")
