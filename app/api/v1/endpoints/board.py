"""
Board API endpoints for Kanban For Agents.

Provides CRUD operations for board entities with proper tenant isolation
and optimistic concurrency control.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.core.exceptions import (
    BoardNotFoundException, OptimisticConcurrencyException, BadRequestException
)
from app.repositories import BoardRepository, ColumnRepository, CardRepository
from app.schemas import (
    BoardCreate, BoardResponse, BoardUpdate, BoardListResponse,
    BoardArchiveRequest, BoardFilterParams, SuccessResponse, PaginatedResponse, ErrorResponse,
    ColumnCreate, ColumnListResponse, CardListResponse
)
from app.schemas.base import PaginationInfo

router = APIRouter()

async def get_board_repository(session: AsyncSession = Depends(get_db_session)) -> BoardRepository:
    return BoardRepository(session)

async def get_column_repository(session: AsyncSession = Depends(get_db_session)) -> ColumnRepository:
    return ColumnRepository(session)

async def get_card_repository(session: AsyncSession = Depends(get_db_session)) -> CardRepository:
    return CardRepository(session)

async def get_tenant_id() -> str:
    return "default"  # TODO: Implement proper tenant resolution

@router.post("/", response_model=SuccessResponse[BoardResponse], status_code=201)
async def create_board(
    board_data: BoardCreate,
    board_repo: BoardRepository = Depends(get_board_repository),
    column_repo: ColumnRepository = Depends(get_column_repository),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a new board with default columns."""
    # Create the board
    board = await board_repo.create(
        data=board_data.model_dump(),
        tenant_id=tenant_id
    )
    
    # Create default columns
    default_columns = [
        {"name": "To Do", "position": 0, "wip_limit": None},
        {"name": "In Progress", "position": 1, "wip_limit": 5},
        {"name": "Done", "position": 2, "wip_limit": None}
    ]
    
    for column_data in default_columns:
        column_create_data = ColumnCreate(
            name=column_data["name"],
            board_id=board.id,
            position=column_data["position"],
            wip_limit=column_data["wip_limit"]
        )
        await column_repo.create(
            data=column_create_data.model_dump(),
            tenant_id=tenant_id
        )
    
    return SuccessResponse(
        data=BoardResponse.model_validate(board),
        message="Board created successfully with default columns"
    )

@router.get("/{board_id}", response_model=SuccessResponse[BoardResponse])
async def get_board(
    board_id: str,
    repo: BoardRepository = Depends(get_board_repository),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get a board by ID."""
    board = await repo.get_by_id(board_id, tenant_id)
    if not board:
        raise BoardNotFoundException(board_id)
    
    return SuccessResponse(data=BoardResponse.model_validate(board))

@router.get("/", response_model=PaginatedResponse[BoardListResponse])
async def list_boards(
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    workspace_id: Optional[str] = Query(None, description="Filter by workspace ID"),
    archived: Optional[bool] = Query(None, description="Filter by archived status"),
    include_deleted: bool = Query(False, description="Include soft-deleted boards"),
    order_by: str = Query("created_at", description="Field to order by"),
    order_direction: str = Query("desc", description="Order direction (asc/desc)"),
    repo: BoardRepository = Depends(get_board_repository),
    tenant_id: str = Depends(get_tenant_id)
):
    """List boards with optional filtering and pagination."""
    # Build filters
    filters = {}
    if workspace_id:
        filters["workspace_id"] = workspace_id
    
    if archived is not None:
        filters["is_archived"] = archived
    
    # Get boards
    boards = await repo.list(
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
    board_responses = [BoardListResponse.model_validate(board) for board in boards]
    
    # Calculate pagination info
    pages = (total + limit - 1) // limit
    current_page = (offset // limit) + 1
    
    return PaginatedResponse(
        data=board_responses,
        pagination={
            "page": current_page,
            "limit": limit,
            "total": total,
            "pages": pages,
            "has_next": current_page < pages,
            "has_prev": current_page > 1
        }
    )

@router.put("/{board_id}", response_model=SuccessResponse[BoardResponse])
async def update_board(
    board_id: str,
    board_data: BoardUpdate,
    if_match: Optional[str] = Header(None, description="ETag for optimistic concurrency"),
    repo: BoardRepository = Depends(get_board_repository),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update a board."""
    # Get current version if If-Match header is provided
    version = None
    if if_match:
        try:
            version = int(if_match.strip('"'))
        except ValueError:
            raise BadRequestException(detail="Invalid If-Match header format")
    
    # Update board
    board = await repo.update(
        entity_id=board_id,
        tenant_id=tenant_id,
        data=board_data.model_dump(exclude_unset=True),
        version=version
    )
    
    if not board:
        if version is not None:
            raise OptimisticConcurrencyException("Board has been modified by another request")
        else:
            raise BoardNotFoundException(board_id)
    
    return SuccessResponse(
        data=BoardResponse.model_validate(board),
        message="Board updated successfully"
    )

@router.delete("/{board_id}", response_model=SuccessResponse[dict])
async def delete_board(
    board_id: str,
    if_match: Optional[str] = Header(None, description="ETag for optimistic concurrency"),
    repo: BoardRepository = Depends(get_board_repository),
    tenant_id: str = Depends(get_tenant_id)
):
    """Soft delete a board."""
    # Get current version if If-Match header is provided
    version = None
    if if_match:
        try:
            version = int(if_match.strip('"'))
        except ValueError:
            raise BadRequestException(detail="Invalid If-Match header format")
    
    # Delete board
    deleted = await repo.delete(
        entity_id=board_id,
        tenant_id=tenant_id,
        version=version,
        hard_delete=False
    )
    
    if not deleted:
        if version is not None:
            raise OptimisticConcurrencyException("Board has been modified by another request")
        else:
            raise BoardNotFoundException(board_id)
    
    return SuccessResponse(
        data={"deleted": True},
        message="Board deleted successfully"
    )

@router.post("/{board_id}/archive", response_model=SuccessResponse[BoardResponse])
async def archive_board(
    board_id: str,
    archive_request: BoardArchiveRequest,
    if_match: Optional[str] = Header(None, description="ETag for optimistic concurrency"),
    repo: BoardRepository = Depends(get_board_repository),
    tenant_id: str = Depends(get_tenant_id)
):
    """Archive or unarchive a board."""
    # Get current version if If-Match header is provided
    version = None
    if if_match:
        try:
            version = int(if_match.strip('"'))
        except ValueError:
            raise BadRequestException(detail="Invalid If-Match header format")
    
    # Archive/unarchive board
    if archive_request.archived:
        board = await repo.archive(board_id, tenant_id, version)
        message = "Board archived successfully"
    else:
        board = await repo.unarchive(board_id, tenant_id, version)
        message = "Board unarchived successfully"
    
    if not board:
        if version is not None:
            raise OptimisticConcurrencyException("Board has been modified by another request")
        else:
            raise BoardNotFoundException(board_id)
    
    return SuccessResponse(
        data=BoardResponse.model_validate(board),
        message=message
    )

@router.get("/{board_id}/columns", response_model=PaginatedResponse[ColumnListResponse])
async def get_board_columns(
    board_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    repo: ColumnRepository = Depends(get_column_repository),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get all columns for a specific board."""
    # Get columns with pagination
    columns = await repo.list_by_board(board_id, tenant_id, limit=limit, offset=offset)
    total_count = await repo.count_by_board(board_id, tenant_id)
    
    # Convert to response models
    column_responses = [ColumnListResponse.model_validate(column.to_dict()) for column in columns]
    
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

@router.get("/{board_id}/cards", response_model=PaginatedResponse[CardListResponse])
async def get_board_cards(
    board_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    repo: CardRepository = Depends(get_card_repository),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get all cards for a specific board."""
    # Get cards with pagination
    cards = await repo.list_by_board(board_id, tenant_id, limit=limit, offset=offset)
    total_count = await repo.count_by_board(board_id, tenant_id)
    
    # Convert to response models
    card_responses = [CardListResponse.model_validate(card.to_dict()) for card in cards]
    
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
        data=card_responses,
        pagination=pagination_info
    )
