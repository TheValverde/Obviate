"""
Base Pydantic schemas for common response patterns and utilities.

This module contains base schemas used across all API endpoints for consistent
response formatting, error handling, and pagination.
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field, ConfigDict

# Type variable for generic response models
T = TypeVar('T')


class BaseResponse(BaseModel):
    """Base response model with common fields."""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class SuccessResponse(BaseResponse, Generic[T]):
    """Standard success response wrapper."""
    
    success: bool = Field(default=True, description="Always true for success responses")
    data: T = Field(description="The response data")
    message: Optional[str] = Field(default=None, description="Optional success message")


class ErrorResponse(BaseResponse):
    """Standard error response wrapper."""
    
    success: bool = Field(default=False, description="Always false for error responses")
    error: str = Field(description="Error message")
    error_code: Optional[str] = Field(default=None, description="Optional error code")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")


class PaginationInfo(BaseResponse):
    """Pagination metadata for list responses."""
    
    page: int = Field(description="Current page number")
    limit: int = Field(description="Number of items per page")
    total: int = Field(description="Total number of items")
    pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")


class PaginatedResponse(BaseResponse, Generic[T]):
    """Paginated response wrapper for list endpoints."""
    
    success: bool = Field(default=True, description="Always true for success responses")
    data: List[T] = Field(description="List of items")
    pagination: PaginationInfo = Field(description="Pagination metadata")


class HealthCheckResponse(BaseResponse):
    """Health check response model."""
    
    status: str = Field(description="Service status")
    version: str = Field(description="API version")
    timestamp: datetime = Field(description="Current timestamp")
    database: str = Field(description="Database connection status")


class BulkOperationResponse(BaseResponse):
    """Response for bulk operations (create, update, delete)."""
    
    success: bool = Field(default=True, description="Whether the operation was successful")
    created: int = Field(description="Number of items created")
    updated: int = Field(description="Number of items updated")
    deleted: int = Field(description="Number of items deleted")
    failed: int = Field(description="Number of items that failed")
    errors: Optional[List[Dict[str, Any]]] = Field(default=None, description="List of errors for failed items")


class FilterParams(BaseModel):
    """Base filter parameters for list endpoints."""
    
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of items to return")
    offset: int = Field(default=0, ge=0, description="Number of items to skip")
    include_deleted: bool = Field(default=False, description="Whether to include soft-deleted items")
    order_by: Optional[str] = Field(default=None, description="Field to order by")
    order_direction: str = Field(default="desc", pattern="^(asc|desc)$", description="Order direction")


class SearchParams(FilterParams):
    """Search parameters for search endpoints."""
    
    q: str = Field(description="Search query")
    search_fields: Optional[List[str]] = Field(default=None, description="Fields to search in")


class VersionInfo(BaseResponse):
    """Version information for optimistic concurrency."""
    
    version: int = Field(description="Current version number")
    etag: str = Field(description="ETag for version validation")


class AuditInfo(BaseResponse):
    """Audit information for tracking changes."""
    
    created_at: datetime = Field(description="Creation timestamp")
    created_by: Optional[str] = Field(default=None, description="User who created the item")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    updated_by: Optional[str] = Field(default=None, description="User who last updated the item")
