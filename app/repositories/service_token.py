"""
Service token repository for service token-specific database operations.
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from .base import BaseRepository
from app.models.service_token import ServiceToken


class ServiceTokenRepository(BaseRepository[ServiceToken]):
    """
    Repository for service token operations with tenant isolation.
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(ServiceToken, session)
    
    async def get_by_token_hash(
        self,
        token_hash: str,
        tenant_id: str,
        include_deleted: bool = False
    ) -> Optional[ServiceToken]:
        """
        Get service token by token hash with tenant isolation.
        
        Args:
            token_hash: Hashed token value
            tenant_id: Tenant ID for isolation
            include_deleted: Whether to include soft-deleted tokens
            
        Returns:
            Service token instance or None if not found
        """
        query = select(self.model).where(
            and_(
                self.model.token_hash == token_hash,
                self.model.tenant_id == tenant_id
            )
        )
        
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def list_active(
        self,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False
    ) -> List[ServiceToken]:
        """
        List active (non-expired) service tokens with tenant isolation.
        
        Args:
            tenant_id: Tenant ID for isolation
            limit: Maximum number of tokens to return
            offset: Number of tokens to skip
            include_deleted: Whether to include soft-deleted tokens
            
        Returns:
            List of active service token instances
        """
        from sqlalchemy import func
        
        query = select(self.model).where(
            and_(
                self.model.tenant_id == tenant_id,
                or_(
                    self.model.expires_at.is_(None),
                    self.model.expires_at > func.now()
                )
            )
        )
        
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        
        query = query.order_by(self.model.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def list_by_scope(
        self,
        scope: str,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False
    ) -> List[ServiceToken]:
        """
        List service tokens by scope with tenant isolation.
        
        Args:
            scope: Token scope (e.g., 'read', 'write', 'admin')
            tenant_id: Tenant ID for isolation
            limit: Maximum number of tokens to return
            offset: Number of tokens to skip
            include_deleted: Whether to include soft-deleted tokens
            
        Returns:
            List of service token instances with matching scope
        """
        return await self.list(
            tenant_id=tenant_id,
            limit=limit,
            offset=offset,
            include_deleted=include_deleted,
            filters={"scope": scope}
        )
    
    async def count_active(
        self,
        tenant_id: str,
        include_deleted: bool = False
    ) -> int:
        """
        Count active (non-expired) service tokens with tenant isolation.
        
        Args:
            tenant_id: Tenant ID for isolation
            include_deleted: Whether to include soft-deleted tokens
            
        Returns:
            Number of active service tokens
        """
        from sqlalchemy import func
        
        query = select(func.count(self.model.id)).where(
            and_(
                self.model.tenant_id == tenant_id,
                or_(
                    self.model.expires_at.is_(None),
                    self.model.expires_at > func.now()
                )
            )
        )
        
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        
        result = await self.session.execute(query)
        return result.scalar()
