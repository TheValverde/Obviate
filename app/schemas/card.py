"""
Pydantic schemas for card request/response models.

This module contains schemas for card CRUD operations including create,
update, and response models with proper validation for agent context
and workflow state.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict

from .base import BaseResponse


class CardBase(BaseModel):
    """Base card model with common fields."""
    
    title: str = Field(..., min_length=1, max_length=255, description="Card title")
    description: Optional[str] = Field(None, max_length=5000, description="Card description")
    board_id: str = Field(..., description="Board ID")
    column_id: str = Field(..., description="Column ID")
    priority: int = Field(default=2, ge=1, le=5, description="Card priority (1=lowest, 5=highest)")
    labels: Optional[List[str]] = Field(default=None, description="Card labels")
    assignees: Optional[List[str]] = Field(default=None, description="List of assignees")
    agent_context: Optional[Dict[str, Any]] = Field(default=None, description="Agent-specific context and capabilities")
    workflow_state: Optional[Dict[str, Any]] = Field(default=None, description="Current workflow state and metadata")
    fields: Optional[Dict[str, Any]] = Field(default=None, description="Custom fields and metadata")
    meta_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class CardCreate(CardBase):
    """Schema for creating a new card."""
    
    position: Optional[int] = Field(None, ge=0, description="Card position within column (0-based). If not provided, card will be appended to the end of the column.")


class CardUpdate(BaseModel):
    """Schema for updating an existing card (position changes must use move/reorder endpoints)."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Card title")
    description: Optional[str] = Field(None, max_length=5000, description="Card description")
    priority: Optional[int] = Field(None, ge=1, le=5, description="Card priority")
    labels: Optional[List[str]] = Field(default=None, description="Card labels")
    assignees: Optional[List[str]] = Field(default=None, description="List of assignees")
    agent_context: Optional[Dict[str, Any]] = Field(default=None, description="Agent-specific context")
    workflow_state: Optional[Dict[str, Any]] = Field(default=None, description="Workflow state")
    fields: Optional[Dict[str, Any]] = Field(default=None, description="Custom fields")
    meta_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class CardResponse(CardBase, BaseResponse):
    """Schema for card response."""
    
    position: int = Field(description="Card position within column (0-based)")
    id: str = Field(description="Card ID")
    tenant_id: str = Field(description="Tenant ID")
    version: int = Field(description="Version number for optimistic concurrency")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(default=None, description="Soft delete timestamp")


class CardListResponse(BaseResponse):
    """Schema for card list response."""
    
    id: str = Field(description="Card ID")
    title: str = Field(description="Card title")
    description: Optional[str] = Field(default=None, description="Card description")
    board_id: str = Field(description="Board ID")
    column_id: str = Field(description="Column ID")
    position: int = Field(description="Card position")
    priority: int = Field(description="Card priority")
    labels: Optional[List[str]] = Field(default=None, description="Card labels")
    assignees: Optional[List[str]] = Field(default=None, description="List of assignees")
    tenant_id: str = Field(description="Tenant ID")
    version: int = Field(description="Version number")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    agent_context: Optional[Dict[str, Any]] = Field(default=None, description="Agent-specific context")
    workflow_state: Optional[Dict[str, Any]] = Field(default=None, description="Workflow state")
    fields: Optional[Dict[str, Any]] = Field(default=None, description="Custom fields")
    meta_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")





class CardSearchRequest(BaseModel):
    """Schema for card search request."""
    
    search_term: str = Field(..., min_length=1, description="Search term")
    board_id: Optional[str] = Field(None, description="Limit search to specific board")
    column_id: Optional[str] = Field(None, description="Limit search to specific column")
    labels: Optional[List[str]] = Field(None, description="Filter by labels")
    assignees: Optional[List[str]] = Field(None, description="Filter by assignees")
    priority: Optional[int] = Field(None, ge=1, le=5, description="Filter by priority")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of cards to return")
    offset: int = Field(default=0, ge=0, description="Number of cards to skip")


class CardFilterParams(BaseModel):
    """Filter parameters for card list endpoint."""
    
    board_id: Optional[str] = Field(None, description="Filter by board ID")
    column_id: Optional[str] = Field(None, description="Filter by column ID")
    title: Optional[str] = Field(None, description="Filter by card title (partial match)")
    labels: Optional[List[str]] = Field(None, description="Filter by labels")
    assignees: Optional[List[str]] = Field(None, description="Filter by assignees")
    priority: Optional[int] = Field(None, ge=1, le=5, description="Filter by priority")
    include_deleted: bool = Field(default=False, description="Whether to include soft-deleted cards")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of cards to return")
    offset: int = Field(default=0, ge=0, description="Number of cards to skip")
    order_by: str = Field(default="position", description="Field to order by")
    order_direction: str = Field(default="asc", pattern="^(asc|desc)$", description="Order direction")


class CardWithCommentsResponse(CardResponse):
    """Schema for card response with comments."""
    
    comments: list[Dict[str, Any]] = Field(default=[], description="List of comments on the card")
    comment_count: int = Field(description="Number of comments on the card")


class CardWithAttachmentsResponse(CardResponse):
    """Schema for card response with attachments."""
    
    attachments: list[Dict[str, Any]] = Field(default=[], description="List of attachments on the card")
    attachment_count: int = Field(description="Number of attachments on the card")


class AgentContextSchema(BaseModel):
    """Schema for agent context within cards."""
    
    agent_id: str = Field(description="Agent identifier")
    capabilities: List[str] = Field(description="List of agent capabilities")
    estimated_duration: Optional[str] = Field(None, description="Estimated time to complete")
    requirements: Optional[List[str]] = Field(None, description="Requirements for the agent")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Agent constraints")


class WorkflowStateSchema(BaseModel):
    """Schema for workflow state within cards."""
    
    status: str = Field(description="Current workflow status")
    blocked_by: Optional[List[str]] = Field(default=None, description="List of blocking items")
    dependencies: Optional[List[str]] = Field(default=None, description="List of dependencies")
    completed_at: Optional[datetime] = Field(default=None, description="Completion timestamp")
    started_at: Optional[datetime] = Field(default=None, description="Start timestamp")
