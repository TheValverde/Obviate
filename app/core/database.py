"""
Database configuration and session management for Kanban For Agents.

This module handles SQLAlchemy async database setup, session management,
and connection pooling configuration.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)
from sqlalchemy.pool import NullPool
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# Global engine and session factory
engine: AsyncEngine | None = None
AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None


def get_database_url() -> str:
    """Get the appropriate database URL based on environment."""
    if settings.ENVIRONMENT == "test":
        return settings.TEST_DATABASE_URL
    return settings.DATABASE_URL


async def init_db() -> None:
    """Initialize the database engine and session factory."""
    global engine, AsyncSessionLocal
    
    database_url = get_database_url()
    
    logger.info("Initializing database connection", url=database_url)
    
    # Create async engine
    engine = create_async_engine(
        database_url,
        echo=settings.DEBUG,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_timeout=settings.DATABASE_POOL_TIMEOUT,
        pool_recycle=settings.DATABASE_POOL_RECYCLE,
        pool_pre_ping=True,
        # Use NullPool for testing to avoid connection pooling issues
        poolclass=NullPool if settings.ENVIRONMENT == "test" else None,
    )
    
    # Create session factory
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    logger.info("Database connection initialized successfully")


async def close_db() -> None:
    """Close the database engine."""
    global engine
    
    if engine:
        await engine.dispose()
        logger.info("Database connection closed")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    if not AsyncSessionLocal:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_engine() -> AsyncEngine:
    """Get the database engine."""
    if not engine:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get the session factory."""
    if not AsyncSessionLocal:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return AsyncSessionLocal
