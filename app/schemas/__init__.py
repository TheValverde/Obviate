"""
Pydantic schemas for request/response models.

This package contains all Pydantic schemas used for API request/response validation
and serialization.
"""

from .base import (
    BaseResponse,
    ErrorResponse,
    PaginatedResponse,
    SuccessResponse,
)
from .workspace import (
    WorkspaceCreate,
    WorkspaceResponse,
    WorkspaceUpdate,
    WorkspaceListResponse,
    WorkspaceArchiveRequest,
    WorkspaceFilterParams,
)
from .board import (
    BoardCreate,
    BoardResponse,
    BoardUpdate,
)
from .column import (
    ColumnCreate,
    ColumnResponse,
    ColumnUpdate,
)
from .card import (
    CardCreate,
    CardResponse,
    CardUpdate,
)
from .comment import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
)
from .attachment import (
    AttachmentCreate,
    AttachmentResponse,
    AttachmentUpdate,
)
from .audit_event import (
    AuditEventResponse,
)
from .service_token import (
    ServiceTokenCreate,
    ServiceTokenResponse,
    ServiceTokenUpdate,
)

__all__ = [
    # Base schemas
    "BaseResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "SuccessResponse",
    # Workspace schemas
    "WorkspaceCreate",
    "WorkspaceResponse",
    "WorkspaceUpdate",
    "WorkspaceListResponse",
    "WorkspaceArchiveRequest",
    "WorkspaceFilterParams",
    # Board schemas
    "BoardCreate",
    "BoardResponse",
    "BoardUpdate",
    # Column schemas
    "ColumnCreate",
    "ColumnResponse",
    "ColumnUpdate",
    # Card schemas
    "CardCreate",
    "CardResponse",
    "CardUpdate",
    # Comment schemas
    "CommentCreate",
    "CommentResponse",
    "CommentUpdate",
    # Attachment schemas
    "AttachmentCreate",
    "AttachmentResponse",
    "AttachmentUpdate",
    # Audit event schemas
    "AuditEventResponse",
    # Service token schemas
    "ServiceTokenCreate",
    "ServiceTokenResponse",
    "ServiceTokenUpdate",
]
