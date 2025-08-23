"""
Configuration management for Kanban For Agents.

This module handles all application configuration through environment variables
using Pydantic Settings for type safety and validation.
"""

from typing import List
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Settings
    APP_NAME: str = "Kanban For Agents"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    RELOAD: bool = False
    
    # Database Settings
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://kanban_user:kanban_password@localhost:5432/kanban_dev",
        description="Database connection URL"
    )
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600
    
    # Test Database
    TEST_DATABASE_URL: str = Field(
        default="postgresql+asyncpg://kanban_user:kanban_password@localhost:5433/kanban_test",
        description="Test database connection URL"
    )
    
    # Security Settings
    SECRET_KEY: str = Field(
        default="your-super-secret-key-change-this-in-production",
        description="Secret key for JWT token signing"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    ALLOWED_METHODS: List[str] = Field(
        default=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        description="Allowed HTTP methods"
    )
    ALLOWED_HEADERS: List[str] = Field(
        default=["*"],
        description="Allowed HTTP headers"
    )
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "logs/app.log"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=["image/jpeg", "image/png", "image/gif", "application/pdf", "text/plain"],
        description="Allowed file types for attachments"
    )
    
    # Agent Settings
    DEFAULT_AGENT_ID: str = "default-agent"
    AGENT_SESSION_TIMEOUT: int = 3600  # 1 hour
    
    # Audit Settings
    AUDIT_ENABLED: bool = True
    AUDIT_RETENTION_DAYS: int = 90
    
    # Metrics Settings
    METRICS_ENABLED: bool = True
    METRICS_INTERVAL: int = 300  # 5 minutes
    
    # Development Settings
    CREATE_SEED_DATA: bool = False
    ENABLE_SWAGGER_UI: bool = True
    ENABLE_RELOAD: bool = False
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v: str) -> str:
        """Validate that secret key is not the default value in production."""
        if v == "your-super-secret-key-change-this-in-production" and cls.ENVIRONMENT == "production":
            raise ValueError("SECRET_KEY must be changed in production")
        return v
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("DATABASE_URL must be a PostgreSQL URL")
        return v
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_allowed_origins(cls, v):
        """Parse allowed origins from string or list."""
        if isinstance(v, str):
            # Handle comma-separated string
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    @validator("ALLOWED_METHODS", pre=True)
    def parse_allowed_methods(cls, v):
        """Parse allowed methods from string or list."""
        if isinstance(v, str):
            # Handle comma-separated string
            return [method.strip().upper() for method in v.split(",") if method.strip()]
        return v
    
    @validator("ALLOWED_HEADERS", pre=True)
    def parse_allowed_headers(cls, v):
        """Parse allowed headers from string or list."""
        if isinstance(v, str):
            # Handle comma-separated string
            return [header.strip() for header in v.split(",") if header.strip()]
        return v
    
    @validator("ALLOWED_FILE_TYPES", pre=True)
    def parse_allowed_file_types(cls, v):
        """Parse allowed file types from string or list."""
        if isinstance(v, str):
            # Handle comma-separated string
            return [file_type.strip() for file_type in v.split(",") if file_type.strip()]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create global settings instance
settings = Settings()
