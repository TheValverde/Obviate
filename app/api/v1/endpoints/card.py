"""
Card API endpoints for Kanban For Agents.

Provides CRUD operations for card entities with proper tenant isolation,
optimistic concurrency control, and card movement/reordering functionality.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.core.exceptions import (
    CardNotFoundException, OptimisticConcurrencyException, BadRequestException
)
from app.repositories import CardRepository
from app.schemas import (
    CardCreate, CardResponse, CardUpdate, CardListResponse,
    SuccessResponse, PaginatedResponse, ErrorResponse
)
from app.schemas.base import PaginationInfo

router = APIRouter()

async def get_card_repository(session: AsyncSession = Depends(get_db_session)) -> CardRepository:
    return CardRepository(session)


async def get_tenant_id() -> str:
    """Get tenant ID from request context (for now, using default)."""
    # TODO: Implement proper tenant resolution from authentication
    return "default"


@router.post("/", response_model=CardResponse, status_code=201)
async def create_card(
    card_data: CardCreate,
    repo: CardRepository = Depends(get_card_repository),
    tenant_id: str = Depends(get_tenant_id)
) -> CardResponse:
    """
    Create a new card.
    
    Args:
        card_data: Card creation data
        repo: Card repository instance
        tenant_id: Tenant ID for isolation
        
    Returns:
        CardResponse: Created card data
        
    Raises:
        BadRequestException: If card data is invalid
    """
    try:
        card = await repo.create(data=card_data.model_dump(), tenant_id=tenant_id)
        return CardResponse.model_validate(card.to_dict())
    except Exception as e:
        raise BadRequestException(f"Failed to create card: {str(e)}")


@router.get("/{card_id}", response_model=CardResponse)
async def get_card(
    card_id: str,
    repo: CardRepository = Depends(get_card_repository),
    tenant_id: str = Depends(get_tenant_id)
) -> CardResponse:
    """
    Get a card by ID.
    
    Args:
        card_id: Card ID
        repo: Card repository instance
        tenant_id: Tenant ID for isolation
        
    Returns:
        CardResponse: Card data
        
    Raises:
        CardNotFoundException: If card not found
    """
    card = await repo.get_by_id(card_id, tenant_id)
    if not card:
        raise CardNotFoundException(f"Card with ID {card_id} not found")
    
    return CardResponse.model_validate(card.to_dict())


@router.get("/", response_model=PaginatedResponse[CardListResponse])
async def list_cards(
    board_id: Optional[str] = Query(None, description="Filter by board ID"),
    column_id: Optional[str] = Query(None, description="Filter by column ID"),
    assignee_id: Optional[str] = Query(None, description="Filter by assignee ID"),
    priority: Optional[int] = Query(None, ge=1, le=5, description="Filter by priority (1-5)"),
    labels: Optional[str] = Query(None, description="Filter by labels (comma-separated)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of cards to return"),
    offset: int = Query(0, ge=0, description="Number of cards to skip"),
    repo: CardRepository = Depends(get_card_repository),
    tenant_id: str = Depends(get_tenant_id)
) -> PaginatedResponse[CardListResponse]:
    """
    List cards with optional filtering.
    
    Args:
        board_id: Optional board ID filter
        column_id: Optional column ID filter
        assignee_id: Optional assignee ID filter
        priority: Optional priority filter (1-5)
        labels: Optional labels filter (comma-separated)
        limit: Maximum number of cards to return
        offset: Number of cards to skip
        repo: Card repository instance
        tenant_id: Tenant ID for isolation
        
    Returns:
        PaginatedResponse[CardListResponse]: Paginated list of cards
    """
    # Build filter criteria
    filters = {}
    if board_id:
        filters["board_id"] = board_id
    if column_id:
        filters["column_id"] = column_id
    if assignee_id:
        filters["assignee_id"] = assignee_id
    if priority:
        filters["priority"] = priority
    if labels:
        # Parse comma-separated labels
        label_list = [label.strip() for label in labels.split(",") if label.strip()]
        if label_list:
            filters["labels"] = label_list
    
    # Get cards with pagination
    cards = await repo.list(tenant_id, limit=limit, offset=offset, **filters)
    total_count = await repo.count(tenant_id, **filters)
    
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


@router.put("/{card_id}", response_model=CardResponse)
async def update_card(
    card_id: str,
    card_data: CardUpdate,
    if_match: Optional[str] = Header(None, alias="If-Match"),
    repo: CardRepository = Depends(get_card_repository),
    tenant_id: str = Depends(get_tenant_id)
) -> CardResponse:
    """
    Update a card.
    
    Args:
        card_id: Card ID
        card_data: Card update data
        if_match: ETag for optimistic concurrency control
        repo: Card repository instance
        tenant_id: Tenant ID for isolation
        
    Returns:
        CardResponse: Updated card data
        
    Raises:
        CardNotFoundException: If card not found
        OptimisticConcurrencyException: If version mismatch
    """
    # Get current card to check version
    current_card = await repo.get_by_id(card_id, tenant_id)
    if not current_card:
        raise CardNotFoundException(f"Card with ID {card_id} not found")
    
    # Check optimistic concurrency
    if if_match and str(current_card.version) != if_match:
        raise OptimisticConcurrencyException("Card has been modified by another request")
    
    # Update card
    updated_card = await repo.update(card_id, card_data.model_dump(exclude_unset=True))
    return CardResponse.model_validate(updated_card.to_dict())


@router.delete("/{card_id}", response_model=SuccessResponse)
async def delete_card(
    card_id: str,
    repo: CardRepository = Depends(get_card_repository),
    tenant_id: str = Depends(get_tenant_id)
) -> SuccessResponse:
    """
    Delete a card (soft delete).
    
    Args:
        card_id: Card ID
        repo: Card repository instance
        tenant_id: Tenant ID for isolation
        
    Returns:
        SuccessResponse: Success confirmation
        
    Raises:
        CardNotFoundException: If card not found
    """
    card = await repo.get_by_id(card_id, tenant_id)
    if not card:
        raise CardNotFoundException(f"Card with ID {card_id} not found")
    
    await repo.delete(card_id)
    return SuccessResponse(data={"deleted": True})


@router.post("/{card_id}/move", response_model=CardResponse)
async def move_card(
    card_id: str,
    column_id: str,
    position: Optional[int] = Query(None, ge=0, description="New position in column (optional)"),
    repo: CardRepository = Depends(get_card_repository),
    tenant_id: str = Depends(get_tenant_id)
) -> CardResponse:
    """
    Move a card to a different column.
    
    Args:
        card_id: Card ID
        column_id: Target column ID
        position: Optional new position in the column
        repo: Card repository instance
        tenant_id: Tenant ID for isolation
        
    Returns:
        CardResponse: Updated card data
        
    Raises:
        CardNotFoundException: If card not found
        BadRequestException: If column_id is invalid
    """
    # Get current card
    card = await repo.get_by_id(card_id, tenant_id)
    if not card:
        raise CardNotFoundException(f"Card with ID {card_id} not found")
    
    # Update card with new column_id and optional position
    update_data = {"column_id": column_id}
    if position is not None:
        update_data["position"] = position
    
    updated_card = await repo.update(card_id, update_data)
    return CardResponse.model_validate(updated_card.to_dict())


@router.post("/{card_id}/reorder", response_model=CardResponse)
async def reorder_card(
    card_id: str,
    new_position: int,
    repo: CardRepository = Depends(get_card_repository),
    tenant_id: str = Depends(get_tenant_id)
) -> CardResponse:
    """
    Reorder a card within its current column.
    
    Args:
        card_id: Card ID
        new_position: New position for the card
        repo: Card repository instance
        tenant_id: Tenant ID for isolation
        
    Returns:
        CardResponse: Updated card data
        
    Raises:
        CardNotFoundException: If card not found
        BadRequestException: If position is invalid
    """
    if new_position < 0:
        raise BadRequestException("Position must be non-negative")
    
    card = await repo.get_by_id(card_id, tenant_id)
    if not card:
        raise CardNotFoundException(f"Card with ID {card_id} not found")
    
    # Update card position
    updated_card = await repo.update(card_id, {"position": new_position})
    return CardResponse.model_validate(updated_card.to_dict())


@router.get("/column/{column_id}", response_model=List[CardListResponse])
async def get_column_cards(
    column_id: str,
    repo: CardRepository = Depends(get_card_repository),
    tenant_id: str = Depends(get_tenant_id)
) -> List[CardListResponse]:
    """
    Get all cards for a specific column.
    
    Args:
        column_id: Column ID
        repo: Card repository instance
        tenant_id: Tenant ID for isolation
        
    Returns:
        List[CardListResponse]: List of cards for the column
    """
    cards = await repo.list(tenant_id, column_id=column_id, limit=1000)  # Get all cards for column
    return [CardListResponse.model_validate(card.to_dict()) for card in cards]


@router.get("/board/{board_id}", response_model=List[CardListResponse])
async def get_board_cards(
    board_id: str,
    repo: CardRepository = Depends(get_card_repository),
    tenant_id: str = Depends(get_tenant_id)
) -> List[CardListResponse]:
    """
    Get all cards for a specific board.
    
    Args:
        board_id: Board ID
        repo: Card repository instance
        tenant_id: Tenant ID for isolation
        
    Returns:
        List[CardListResponse]: List of cards for the board
    """
    cards = await repo.list(tenant_id, board_id=board_id, limit=1000)  # Get all cards for board
    return [CardListResponse.model_validate(card.to_dict()) for card in cards]
