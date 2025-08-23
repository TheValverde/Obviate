"""
Custom exception classes for API error handling.

This module contains custom exceptions used throughout the API for consistent
error handling and HTTP status code mapping.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class KanbanAPIException(HTTPException):
    """Base exception for Kanban API errors."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class NotFoundException(KanbanAPIException):
    """Exception raised when a resource is not found."""
    
    def __init__(self, detail: str = "Resource not found", error_code: str = "NOT_FOUND"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code
        )


class ConflictException(KanbanAPIException):
    """Exception raised when there's a conflict (e.g., optimistic concurrency)."""
    
    def __init__(self, detail: str = "Resource conflict", error_code: str = "CONFLICT"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=error_code
        )


class ValidationException(KanbanAPIException):
    """Exception raised when request validation fails."""
    
    def __init__(self, detail: str = "Validation error", error_code: str = "VALIDATION_ERROR"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code=error_code
        )


class UnauthorizedException(KanbanAPIException):
    """Exception raised when authentication is required but not provided."""
    
    def __init__(self, detail: str = "Authentication required", error_code: str = "UNAUTHORIZED"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code
        )


class ForbiddenException(KanbanAPIException):
    """Exception raised when the user doesn't have permission to access a resource."""
    
    def __init__(self, detail: str = "Access forbidden", error_code: str = "FORBIDDEN"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code
        )


class BadRequestException(KanbanAPIException):
    """Exception raised when the request is malformed."""
    
    def __init__(self, detail: str = "Bad request", error_code: str = "BAD_REQUEST"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code
        )


class InternalServerException(KanbanAPIException):
    """Exception raised for internal server errors."""
    
    def __init__(self, detail: str = "Internal server error", error_code: str = "INTERNAL_ERROR"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code=error_code
        )


class DatabaseException(KanbanAPIException):
    """Exception raised for database-related errors."""
    
    def __init__(self, detail: str = "Database error", error_code: str = "DATABASE_ERROR"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code=error_code
        )


class OptimisticConcurrencyException(ConflictException):
    """Exception raised when optimistic concurrency check fails."""
    
    def __init__(self, detail: str = "Version conflict - resource has been modified", error_code: str = "VERSION_CONFLICT"):
        super().__init__(detail=detail, error_code=error_code)


class TenantNotFoundException(NotFoundException):
    """Exception raised when tenant is not found."""
    
    def __init__(self, tenant_id: str, error_code: str = "TENANT_NOT_FOUND"):
        super().__init__(
            detail=f"Tenant '{tenant_id}' not found",
            error_code=error_code
        )


class WorkspaceNotFoundException(NotFoundException):
    """Exception raised when workspace is not found."""
    
    def __init__(self, workspace_id: str, error_code: str = "WORKSPACE_NOT_FOUND"):
        super().__init__(
            detail=f"Workspace '{workspace_id}' not found",
            error_code=error_code
        )


class BoardNotFoundException(NotFoundException):
    """Exception raised when board is not found."""
    
    def __init__(self, board_id: str, error_code: str = "BOARD_NOT_FOUND"):
        super().__init__(
            detail=f"Board '{board_id}' not found",
            error_code=error_code
        )


class ColumnNotFoundException(NotFoundException):
    """Exception raised when column is not found."""
    
    def __init__(self, column_id: str, error_code: str = "COLUMN_NOT_FOUND"):
        super().__init__(
            detail=f"Column '{column_id}' not found",
            error_code=error_code
        )


class CardNotFoundException(NotFoundException):
    """Exception raised when card is not found."""
    
    def __init__(self, card_id: str, error_code: str = "CARD_NOT_FOUND"):
        super().__init__(
            detail=f"Card '{card_id}' not found",
            error_code=error_code
        )


class CommentNotFoundException(NotFoundException):
    """Exception raised when comment is not found."""
    
    def __init__(self, comment_id: str, error_code: str = "COMMENT_NOT_FOUND"):
        super().__init__(
            detail=f"Comment '{comment_id}' not found",
            error_code=error_code
        )


class AttachmentNotFoundException(NotFoundException):
    """Exception raised when attachment is not found."""
    
    def __init__(self, attachment_id: str, error_code: str = "ATTACHMENT_NOT_FOUND"):
        super().__init__(
            detail=f"Attachment '{attachment_id}' not found",
            error_code=error_code
        )


class ServiceTokenNotFoundException(NotFoundException):
    """Exception raised when service token is not found."""
    
    def __init__(self, token_id: str, error_code: str = "SERVICE_TOKEN_NOT_FOUND"):
        super().__init__(
            detail=f"Service token '{token_id}' not found",
            error_code=error_code
        )


class InvalidTokenException(UnauthorizedException):
    """Exception raised when service token is invalid."""
    
    def __init__(self, detail: str = "Invalid service token", error_code: str = "INVALID_TOKEN"):
        super().__init__(detail=detail, error_code=error_code)


class TokenExpiredException(UnauthorizedException):
    """Exception raised when service token has expired."""
    
    def __init__(self, detail: str = "Service token has expired", error_code: str = "TOKEN_EXPIRED"):
        super().__init__(detail=detail, error_code=error_code)


class InsufficientPermissionsException(ForbiddenException):
    """Exception raised when user doesn't have sufficient permissions."""
    
    def __init__(self, required_scope: str, error_code: str = "INSUFFICIENT_PERMISSIONS"):
        super().__init__(
            detail=f"Insufficient permissions. Required scope: {required_scope}",
            error_code=error_code
        )
