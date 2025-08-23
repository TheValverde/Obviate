"""
Workspace API endpoints.

This module contains FastAPI endpoints for workspace CRUD operations including
create, read, update, delete, and list operations with tenant isolation and
optimistic concurrency support.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.core.exceptions import (
    WorkspaceNotFoundException,
    OptimisticConcurrencyException,
    BadRequestException
)
from app.repositories import WorkspaceRepository
from app.schemas import (
    WorkspaceCreate,
    WorkspaceResponse,
    WorkspaceUpdate,
    WorkspaceListResponse,
    WorkspaceArchiveRequest,
    WorkspaceFilterParams,
    SuccessResponse,
    PaginatedResponse,
    ErrorResponse
)

router = APIRouter()


async def get_workspace_repository(session: AsyncSession = Depends(get_db_session)) -> WorkspaceRepository:
    """Get workspace repository instance."""
    return WorkspaceRepository(session)


async def get_tenant_id() -> str:
    """Get tenant ID from request context (for now, using default)."""
    # TODO: Implement proper tenant resolution from authentication
    return "default"


@router.post("/", response_model=SuccessResponse[WorkspaceResponse], status_code=201)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    repo: WorkspaceRepository = Depends(get_workspace_repository),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Create a new workspace.
    
    Args:
        workspace_data: Workspace creation data
        repo: Workspace repository
        tenant_id: Tenant ID for isolation
        
    Returns:
        Created workspace response
    """
    try:
        workspace = await repo.create(data=workspace_data.model_dump(), tenant_id=tenant_id)
        return SuccessResponse(
            data=WorkspaceResponse.model_validate(workspace),
            message="Workspace created successfully"
        )
    except ValueError as e:
        raise BadRequestException(detail=str(e))


@router.get("/{workspace_id}", response_model=SuccessResponse[WorkspaceResponse])
async def get_workspace(
    workspace_id: str,
    repo: WorkspaceRepository = Depends(get_workspace_repository),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get a workspace by ID.
    
    Args:
        workspace_id: Workspace ID
        repo: Workspace repository
        tenant_id: Tenant ID for isolation
        
    Returns:
        Workspace response
    """
    workspace = await repo.get_by_id(workspace_id, tenant_id)
    if not workspace:
        raise WorkspaceNotFoundException(workspace_id)
    
    return SuccessResponse(data=WorkspaceResponse.model_validate(workspace))


@router.get("/", response_model=PaginatedResponse[WorkspaceListResponse])
async def list_workspaces(
    name: Optional[str] = Query(None, description="Filter by workspace name"),
    include_archived: bool = Query(False, description="Include archived workspaces"),
    include_deleted: bool = Query(False, description="Include soft-deleted workspaces"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of workspaces to return"),
    offset: int = Query(0, ge=0, description="Number of workspaces to skip"),
    order_by: str = Query("created_at", description="Field to order by"),
    order_direction: str = Query("desc", description="Order direction (asc/desc)"),
    repo: WorkspaceRepository = Depends(get_workspace_repository),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    List workspaces with filtering and pagination.
    
    Args:
        name: Filter by workspace name
        include_archived: Include archived workspaces
        include_deleted: Include soft-deleted workspaces
        limit: Maximum number of workspaces to return
        offset: Number of workspaces to skip
        order_by: Field to order by
        order_direction: Order direction
        repo: Workspace repository
        tenant_id: Tenant ID for isolation
        
    Returns:
        Paginated list of workspaces
    """
    # Build filters
    filters = {}
    if name:
        # For now, we'll use the base list method and filter in Python
        # TODO: Implement proper name filtering in repository
        pass
    
    if not include_archived:
        filters["is_archived"] = False
    
    # Get workspaces
    workspaces = await repo.list(
        tenant_id=tenant_id,
        limit=limit,
        offset=offset,
        include_deleted=include_deleted,
        order_by=order_by,
        filters=filters
    )
    
    # Get total count
    total = await repo.count(tenant_id=tenant_id, include_deleted=include_deleted, filters=filters)
    
    # Convert to response models
    workspace_responses = [WorkspaceListResponse.model_validate(w) for w in workspaces]
    
    # Calculate pagination info
    pages = (total + limit - 1) // limit
    current_page = (offset // limit) + 1
    
    return PaginatedResponse(
        data=workspace_responses,
        pagination={
            "page": current_page,
            "limit": limit,
            "total": total,
            "pages": pages,
            "has_next": current_page < pages,
            "has_prev": current_page > 1
        }
    )


@router.put("/{workspace_id}", response_model=SuccessResponse[WorkspaceResponse])
async def update_workspace(
    workspace_id: str,
    workspace_data: WorkspaceUpdate,
    if_match: Optional[str] = Header(None, description="ETag for optimistic concurrency"),
    repo: WorkspaceRepository = Depends(get_workspace_repository),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Update a workspace.
    
    Args:
        workspace_id: Workspace ID
        workspace_data: Workspace update data
        if_match: ETag for optimistic concurrency
        repo: Workspace repository
        tenant_id: Tenant ID for isolation
        
    Returns:
        Updated workspace response
    """
    # Get current version if If-Match header is provided
    version = None
    if if_match:
        try:
            version = int(if_match.strip('"'))
        except ValueError:
            raise BadRequestException(detail="Invalid If-Match header format")
    
    # Update workspace
    workspace = await repo.update(
        entity_id=workspace_id,
        tenant_id=tenant_id,
        data=workspace_data.model_dump(exclude_unset=True),
        version=version
    )
    
    if not workspace:
        if version is not None:
            raise OptimisticConcurrencyException()
        else:
            raise WorkspaceNotFoundException(workspace_id)
    
    return SuccessResponse(
        data=WorkspaceResponse.model_validate(workspace),
        message="Workspace updated successfully"
    )


@router.delete("/{workspace_id}", response_model=SuccessResponse[dict])
async def delete_workspace(
    workspace_id: str,
    if_match: Optional[str] = Header(None, description="ETag for optimistic concurrency"),
    hard_delete: bool = Query(False, description="Perform hard delete instead of soft delete"),
    repo: WorkspaceRepository = Depends(get_workspace_repository),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Delete a workspace (soft delete by default).
    
    Args:
        workspace_id: Workspace ID
        if_match: ETag for optimistic concurrency
        hard_delete: Perform hard delete instead of soft delete
        repo: Workspace repository
        tenant_id: Tenant ID for isolation
        
    Returns:
        Success response
    """
    # Get current version if If-Match header is provided
    version = None
    if if_match:
        try:
            version = int(if_match.strip('"'))
        except ValueError:
            raise BadRequestException(detail="Invalid If-Match header format")
    
    # Delete workspace
    deleted = await repo.delete(
        entity_id=workspace_id,
        tenant_id=tenant_id,
        version=version,
        hard_delete=hard_delete
    )
    
    if not deleted:
        if version is not None:
            raise OptimisticConcurrencyException()
        else:
            raise WorkspaceNotFoundException(workspace_id)
    
    return SuccessResponse(
        data={"deleted": True},
        message="Workspace deleted successfully"
    )


@router.post("/{workspace_id}/archive", response_model=SuccessResponse[WorkspaceResponse])
async def archive_workspace(
    workspace_id: str,
    archive_data: WorkspaceArchiveRequest,
    if_match: Optional[str] = Header(None, description="ETag for optimistic concurrency"),
    repo: WorkspaceRepository = Depends(get_workspace_repository),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Archive or unarchive a workspace.
    
    Args:
        workspace_id: Workspace ID
        archive_data: Archive/unarchive data
        if_match: ETag for optimistic concurrency
        repo: Workspace repository
        tenant_id: Tenant ID for isolation
        
    Returns:
        Updated workspace response
    """
    # Get current version if If-Match header is provided
    version = None
    if if_match:
        try:
            version = int(if_match.strip('"'))
        except ValueError:
            raise BadRequestException(detail="Invalid If-Match header format")
    
    # Archive/unarchive workspace
    if archive_data.is_archived:
        workspace = await repo.archive(workspace_id, tenant_id, version)
        message = "Workspace archived successfully"
    else:
        workspace = await repo.unarchive(workspace_id, tenant_id, version)
        message = "Workspace unarchived successfully"
    
    if not workspace:
        if version is not None:
            raise OptimisticConcurrencyException()
        else:
            raise WorkspaceNotFoundException(workspace_id)
    
    return SuccessResponse(
        data=WorkspaceResponse.model_validate(workspace),
        message=message
    )


@router.get("/name/{name}", response_model=SuccessResponse[WorkspaceResponse])
async def get_workspace_by_name(
    name: str,
    repo: WorkspaceRepository = Depends(get_workspace_repository),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get a workspace by name.
    
    Args:
        name: Workspace name
        repo: Workspace repository
        tenant_id: Tenant ID for isolation
        
    Returns:
        Workspace response
    """
    workspace = await repo.get_by_name(name, tenant_id)
    if not workspace:
        raise WorkspaceNotFoundException(f"name: {name}")
    
    return SuccessResponse(data=WorkspaceResponse.model_validate(workspace))
