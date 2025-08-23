"""
FastAPI dependencies for database sessions and repository injection.
"""

from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to get database session.
    
    Yields:
        AsyncSession: Database session
    """
    async for session in get_db():
        yield session


# Export the dependency for use in endpoints
__all__ = ["get_db_session"]
