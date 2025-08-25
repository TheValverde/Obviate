"""
Base repository providing common CRUD operations with tenant isolation,
optimistic concurrency, and soft delete support.
"""

from typing import TypeVar, Generic, Optional, List, Dict, Any, Union
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError, NoResultFound
from pydantic import BaseModel

from app.models.base import BaseModel as DBBaseModel

# Type variables for generic repository
T = TypeVar('T', bound=DBBaseModel)
CreateSchema = TypeVar('CreateSchema', bound=BaseModel)
UpdateSchema = TypeVar('UpdateSchema', bound=BaseModel)


class BaseRepository(Generic[T]):
    """
    Base repository providing common CRUD operations with tenant isolation,
    optimistic concurrency, and soft delete support.
    """
    
    def __init__(self, model: type[T], session: AsyncSession):
        self.model = model
        self.session = session
    
    async def create(
        self, 
        data: Union[Dict[str, Any], CreateSchema], 
        tenant_id: str
    ) -> T:
        """
        Create a new entity with tenant isolation.
        
        Args:
            data: Entity data (dict or Pydantic model)
            tenant_id: Tenant ID for isolation
            
        Returns:
            Created entity instance
        """
        if isinstance(data, BaseModel):
            data = data.model_dump()
        
        # Ensure tenant_id is set
        data['tenant_id'] = tenant_id
        
        # Create entity instance
        entity = self.model(**data)
        self.session.add(entity)
        
        try:
            await self.session.commit()
            await self.session.refresh(entity)
            return entity
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f"Failed to create {self.model.__name__}: {str(e)}")
    
    async def get_by_id(
        self, 
        entity_id: str, 
        tenant_id: str,
        include_deleted: bool = False
    ) -> Optional[T]:
        """
        Get entity by ID with tenant isolation.
        
        Args:
            entity_id: Entity ID
            tenant_id: Tenant ID for isolation
            include_deleted: Whether to include soft-deleted entities
            
        Returns:
            Entity instance or None if not found
        """
        query = select(self.model).where(
            and_(
                self.model.id == entity_id,
                self.model.tenant_id == tenant_id
            )
        )
        
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_id_with_version(
        self, 
        entity_id: str, 
        tenant_id: str,
        version: int,
        include_deleted: bool = False
    ) -> Optional[T]:
        """
        Get entity by ID with version check for optimistic concurrency.
        
        Args:
            entity_id: Entity ID
            tenant_id: Tenant ID for isolation
            version: Expected version number
            include_deleted: Whether to include soft-deleted entities
            
        Returns:
            Entity instance or None if not found or version mismatch
        """
        query = select(self.model).where(
            and_(
                self.model.id == entity_id,
                self.model.tenant_id == tenant_id,
                self.model.version == version
            )
        )
        
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def list(
        self,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
        order_by: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[T]:
        """
        List entities with tenant isolation and pagination.
        
        Args:
            tenant_id: Tenant ID for isolation
            limit: Maximum number of entities to return
            offset: Number of entities to skip
            include_deleted: Whether to include soft-deleted entities
            order_by: Field to order by (defaults to created_at desc)
            filters: Additional filters to apply
            
        Returns:
            List of entity instances
        """
        query = select(self.model).where(self.model.tenant_id == tenant_id)
        
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        
        # Apply additional filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, (list, tuple)):
                        query = query.where(getattr(self.model, field).in_(value))
                    else:
                        query = query.where(getattr(self.model, field) == value)
        
        # Apply ordering
        if order_by:
            if hasattr(self.model, order_by):
                order_field = getattr(self.model, order_by)
                query = query.order_by(order_field.desc())
        else:
            # Default ordering by created_at desc
            query = query.order_by(self.model.created_at.desc())
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update(
        self,
        entity_id: str,
        tenant_id: str,
        data: Union[Dict[str, Any], UpdateSchema],
        version: Optional[int] = None
    ) -> Optional[T]:
        """
        Update entity with optimistic concurrency support.
        
        Args:
            entity_id: Entity ID
            tenant_id: Tenant ID for isolation
            data: Update data (dict or Pydantic model)
            version: Expected version for optimistic concurrency
            
        Returns:
            Updated entity instance or None if not found
        """
        if isinstance(data, BaseModel):
            data = data.model_dump(exclude_unset=True)
        
        # Build update query
        update_query = update(self.model).where(
            and_(
                self.model.id == entity_id,
                self.model.tenant_id == tenant_id
            )
        )
        
        # Add version check if provided
        if version is not None:
            update_query = update_query.where(self.model.version == version)
            data['version'] = version + 1
        
        # Add updated_at timestamp
        data['updated_at'] = datetime.now(timezone.utc)
        
        # Execute update
        result = await self.session.execute(update_query.values(**data))
        await self.session.commit()
        
        if result.rowcount == 0:
            return None
        
        # Return updated entity
        return await self.get_by_id(entity_id, tenant_id)
    
    async def delete(
        self,
        entity_id: str,
        tenant_id: str,
        version: Optional[int] = None,
        hard_delete: bool = False
    ) -> bool:
        """
        Delete entity (soft delete by default) with optimistic concurrency support.
        
        Args:
            entity_id: Entity ID
            tenant_id: Tenant ID for isolation
            version: Expected version for optimistic concurrency
            hard_delete: Whether to perform hard delete instead of soft delete
            
        Returns:
            True if entity was deleted, False if not found
        """
        if hard_delete:
            # Hard delete
            delete_query = delete(self.model).where(
                and_(
                    self.model.id == entity_id,
                    self.model.tenant_id == tenant_id
                )
            )
            
            if version is not None:
                delete_query = delete_query.where(self.model.version == version)
        else:
            # Soft delete
            update_query = update(self.model).where(
                and_(
                    self.model.id == entity_id,
                    self.model.tenant_id == tenant_id
                )
            )
            
            if version is not None:
                update_query = update_query.where(self.model.version == version)
                update_query = update_query.values(version=version + 1)
            
            # Set deleted_at timestamp
            update_query = update_query.values(
                deleted_at=datetime.now(timezone.utc)
            )
            
            result = await self.session.execute(update_query)
            await self.session.commit()
            return result.rowcount > 0
        
        result = await self.session.execute(delete_query)
        await self.session.commit()
        return result.rowcount > 0
    
    async def count(
        self,
        tenant_id: str,
        include_deleted: bool = False,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count entities with tenant isolation.
        
        Args:
            tenant_id: Tenant ID for isolation
            include_deleted: Whether to include soft-deleted entities
            filters: Additional filters to apply
            
        Returns:
            Number of entities
        """
        from sqlalchemy import func
        
        query = select(func.count(self.model.id)).where(
            self.model.tenant_id == tenant_id
        )
        
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        
        # Apply additional filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, (list, tuple)):
                        query = query.where(getattr(self.model, field).in_(value))
                    else:
                        query = query.where(getattr(self.model, field) == value)
        
        result = await self.session.execute(query)
        return result.scalar()
    
    async def exists(
        self,
        entity_id: str,
        tenant_id: str,
        include_deleted: bool = False
    ) -> bool:
        """
        Check if entity exists with tenant isolation.
        
        Args:
            entity_id: Entity ID
            tenant_id: Tenant ID for isolation
            include_deleted: Whether to include soft-deleted entities
            
        Returns:
            True if entity exists, False otherwise
        """
        from sqlalchemy import func
        
        query = select(func.count(self.model.id)).where(
            and_(
                self.model.id == entity_id,
                self.model.tenant_id == tenant_id
            )
        )
        
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        
        result = await self.session.execute(query)
        return result.scalar() > 0
