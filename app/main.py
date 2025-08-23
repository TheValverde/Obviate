"""
Kanban For Agents - FastAPI Application

Main application entry point with FastAPI configuration, middleware setup,
and API route registration.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.api import api_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Kanban For Agents application")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Kanban For Agents application")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="A Kanban board system designed specifically for AI agents",
        docs_url="/docs" if settings.ENABLE_SWAGGER_UI else None,
        redoc_url="/redoc" if settings.ENABLE_SWAGGER_UI else None,
        openapi_url="/openapi.json" if settings.ENABLE_SWAGGER_UI else None,
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
    )
    
    # Add request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all incoming requests."""
        logger.info(
            "Incoming request",
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host if request.client else None,
        )
        
        response = await call_next(request)
        
        logger.info(
            "Request completed",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
        )
        
        return response
    
    # Add exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler for unhandled exceptions."""
        logger.error(
            "Unhandled exception",
            method=request.method,
            url=str(request.url),
            exception=str(exc),
            exc_info=True,
        )
        
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
    
    # Include API router
    app.include_router(api_router, prefix="/v1")
    
    return app


# Create the application instance
app = create_application()


@app.get("/")
async def root():
    """Root endpoint with basic application information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "A Kanban board system designed specifically for AI agents",
        "docs": "/docs" if settings.ENABLE_SWAGGER_UI else None,
    }


@app.get("/healthz")
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return {"status": "healthy", "service": settings.APP_NAME}


@app.get("/readyz")
async def readiness_check():
    """Readiness check endpoint to verify the application is ready to serve traffic."""
    # TODO: Add database connectivity check
    return {"status": "ready", "service": settings.APP_NAME}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENABLE_RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )
