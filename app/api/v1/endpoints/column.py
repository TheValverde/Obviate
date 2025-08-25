"""
Column API endpoints for Kanban For Agents.

Provides CRUD operations for column entities with proper tenant isolation
and optimistic concurrency control.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.core.exceptions import (
    ColumnNotFoundException, OptimisticConcurrencyException, BadRequestException
)
from app.repositories import ColumnRepository
from app.schemas import (
    ColumnCreate, ColumnResponse, ColumnUpdate, ColumnListResponse,
    SuccessResponse, PaginatedResponse, ErrorResponse
)
from app.schemas.base import PaginationInfo

router = APIRouter()

async def get_column_repository(session: AsyncSession = Depends(get_db_session)) -> ColumnRepository:
    return ColumnRepository(session)


async def get_tenant_id() -> str:
    """Get tenant ID from request context (for now, using default)."""
    # TODO: Implement proper tenant resolution from authentication
    return "default"


@router.post("/", response_model=ColumnResponse, status_code=201)
async def create_column(
    column_data: ColumnCreate,
    repo: ColumnRepository = Depends(get_column_repository),
    tenant_id: str = Depends(get_tenant_id)
) -> ColumnResponse:
    """
    Create a new column.
    
    Args:
        column_data: Column creation data
        repo: Column repository instance
        
    Returns:
        ColumnResponse: Created column data
        
    Raises:
        BadRequestException: If column data is invalid
    """
    try:
        column = await repo.create(data=column_data.model_dump(), tenant_id=tenant_id)
        return ColumnResponse.model_validate(column.to_dict())
    except Exception as e:
        raise BadRequestException(f"Failed to create column: {str(e)}")


@router.get("/{column_id}", response_model=ColumnResponse)
async def get_column(
    column_id: str,
    repo: ColumnRepository = Depends(get_column_repository),
    tenant_id: str = Depends(get_tenant_id)
) -> ColumnResponse:
    """
    Get a column by ID.
    
    Args:
        column_id: Column ID
        repo: Column repository instance
        
    Returns:
        ColumnResponse: Column data
        
    Raises:
        ColumnNotFoundException: If column not found
    """
    column = await repo.get_by_id(column_id, tenant_id)
    if not column:
        raise ColumnNotFoundException(f"Column with ID {column_id} not found")
    
    return ColumnResponse.model_validate(column.to_dict())


@router.get("/", response_model=PaginatedResponse[ColumnListResponse])
async def list_columns(
    board_id: Optional[str] = Query(None, description="Filter by board ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of columns to return"),
    offset: int = Query(0, ge=0, description="Number of columns to skip"),
    repo: ColumnRepository = Depends(get_column_repository),
    tenant_id: str = Depends(get_tenant_id)
) -> PaginatedResponse[ColumnListResponse]:
    """
    List columns with optional filtering.
    
    Args:
        board_id: Optional board ID filter
        limit: Maximum number of columns to return
        offset: Number of columns to skip
        repo: Column repository instance
        
    Returns:
        PaginatedResponse[ColumnListResponse]: Paginated list of columns
    """
    # Build filter criteria
    filters = {}
    if board_id:
        filters["board_id"] = board_id
    
    # Get columns with pagination
    columns = await repo.list(tenant_id, limit=limit, offset=offset, **filters)
    total_count = await repo.count(tenant_id, **filters)
    
    # Convert to response models
    column_responses = [ColumnListResponse.model_validate(col.to_dict()) for col in columns]
    
    # Build pagination info
    page = (offset // limit) + 1
    pages = (total_count + limit - 1) // limit
    pagination_info = {
        "page": page,
        "limit": limit,
        "total": total_count,
        "pages": pages,
        "has_next": offset + limit < total_count,
        "has_prev": offset > 0
    }
    
    return PaginatedResponse(
        data=column_responses,
        pagination=pagination_info
    )


@router.put("/{column_id}", response_model=ColumnResponse)
async def update_column(
    column_id: str,
    column_data: ColumnUpdate,
    if_match: Optional[str] = Header(None, alias="If-Match"),
    repo: ColumnRepository = Depends(get_column_repository),
    tenant_id: str = Depends(get_tenant_id)
) -> ColumnResponse:
    """
    Update a column.
    
    Args:
        column_id: Column ID
        column_data: Column update data
        if_match: ETag for optimistic concurrency control
        repo: Column repository instance
        
    Returns:
        ColumnResponse: Updated column data
        
    Raises:
        ColumnNotFoundException: If column not found
        OptimisticConcurrencyException: If version mismatch
    """
    # Get current column to check version
    current_column = await repo.get_by_id(column_id, tenant_id)
    if not current_column:
        raise ColumnNotFoundException(f"Column with ID {column_id} not found")
    
    # Check optimistic concurrency
    if if_match and str(current_column.version) != if_match:
        raise OptimisticConcurrencyException("Column has been modified by another request")
    
    # Update column
    updated_column = await repo.update(column_id, column_data.model_dump(exclude_unset=True))
    return ColumnResponse.model_validate(updated_column.to_dict())


@router.delete("/{column_id}", response_model=SuccessResponse)
async def delete_column(
    column_id: str,
    repo: ColumnRepository = Depends(get_column_repository),
    tenant_id: str = Depends(get_tenant_id)
) -> SuccessResponse:
    """
    Delete a column (soft delete).
    
    Args:
        column_id: Column ID
        repo: Column repository instance
        
    Returns:
        SuccessResponse: Success confirmation
        
    Raises:
        ColumnNotFoundException: If column not found
    """
    column = await repo.get_by_id(column_id, tenant_id)
    if not column:
        raise ColumnNotFoundException(f"Column with ID {column_id} not found")
    
    await repo.delete(entity_id=column_id, tenant_id=tenant_id)
    return SuccessResponse(data={"deleted": True})


@router.post("/{column_id}/reorder", response_model=SuccessResponse)
async def reorder_columns(
    column_id: str,
    new_position: int,
    repo: ColumnRepository = Depends(get_column_repository),
    tenant_id: str = Depends(get_tenant_id)
) -> SuccessResponse:
    """
    Reorder a column within its board using "insert and shift" logic.
    
    This endpoint implements proper reordering where:
    1. The target column is moved to the new position
    2. Other columns are shifted to accommodate the move
    3. Positions are clamped to valid bounds
    
    Args:
        column_id: Column ID
        new_position: New position for the column (will be clamped to valid range)
        repo: Column repository instance
        
    Returns:
        SuccessResponse: Success confirmation with actual position used
        
    Raises:
        ColumnNotFoundException: If column not found
        BadRequestException: If position is invalid
    """
    if new_position < 0:
        raise BadRequestException("Position must be non-negative")
    
    column = await repo.get_by_id(column_id, tenant_id)
    if not column:
        raise ColumnNotFoundException(f"Column with ID {column_id} not found")
    
    # Use the improved reordering logic with shift
    success = await repo.reorder_column_with_shift(
        column_id=column_id,
        board_id=column.board_id,
        new_position=new_position,
        tenant_id=tenant_id
    )
    
    if not success:
        raise BadRequestException("Failed to reorder column")
    
    # Get the updated column to return the actual position used
    updated_column = await repo.get_by_id(column_id, tenant_id)
    actual_position = updated_column.position if updated_column else new_position
    
    return SuccessResponse(data={
        "reordered": True, 
        "requested_position": new_position,
        "actual_position": actual_position,
        "message": f"Column moved to position {actual_position}"
    })


@router.get("/board/{board_id}", response_model=PaginatedResponse[ColumnListResponse])
async def get_board_columns(
    board_id: str,
    repo: ColumnRepository = Depends(get_column_repository),
    tenant_id: str = Depends(get_tenant_id)
) -> PaginatedResponse[ColumnListResponse]:
    """
    Get all columns for a specific board.
    
    Args:
        board_id: Board ID
        repo: Column repository instance
        
    Returns:
        PaginatedResponse[ColumnListResponse]: Paginated list of columns for the board
    """
    columns = await repo.list(tenant_id, limit=1000, filters={"board_id": board_id})  # Get all columns for board
    total_count = await repo.count(tenant_id, filters={"board_id": board_id})
    
    # Convert to response models
    column_responses = [ColumnListResponse.model_validate(col.to_dict()) for col in columns]
    
    # Build pagination info
    pagination_info = {
        "page": 1,
        "limit": 1000,
        "total": total_count,
        "pages": 1,
        "has_next": False,
        "has_prev": False
    }
    
    return PaginatedResponse(
        success=True,
        data=column_responses,
        pagination=pagination_info
    )
